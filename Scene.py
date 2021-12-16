import math
from datetime import datetime as dt
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from OrthoNormalBasis import OrthoNormalBasis
from QFunctions.Q_Functions import Q_buckets, Q_map, Q_Vector3d
from Ray import Ray
from Primitive import Primitive
from Hit import Hit


class Scene:
    def __init__(self, camera_position: Q_Vector3d, objects: list = [], lights: list = []):
        self.camera_position = camera_position
        self.objects = objects
        self.lights = lights

    def nearest_intersection(self, ray: Ray) -> tuple[Primitive, float, Q_Vector3d]:  # Could this be optimized by asking "does a ray of length(this_distance so far) intersect this object" ?
        min_distance = math.inf
        obj = None
        normal_to_surface = None
        is_inside = None
        for object in self.objects:
            # this_distance, this_normal_to_surface = object.intersect(ray=ray)
            hit = object.intersect(ray=ray)
            if hit and hit.distance < min_distance:
                min_distance = hit.distance
                obj = object
                normal_to_surface = hit.normal_to_surface
                is_inside = hit.is_inside
        return obj, Hit(position=ray.position_at_distance(min_distance), distance=min_distance, normal_to_surface=normal_to_surface, is_inside=is_inside)

    def multi_render(self, width: int, height: int, max_depth: int = 1, anti_aliasing: bool = False, lighting_samples: int = 1, cores_to_use: int = 1) -> None:
        number_of_buckets = 10
        cores_to_use = max(cores_to_use, 1) if cores_to_use != 0 else cpu_count()
        pool = Pool(processes=cores_to_use)
        arguments = [(width, height, max_depth, anti_aliasing, lighting_samples, {'start': start, 'end': end}) for start, end in Q_buckets(number_of_items=height, number_of_buckets=number_of_buckets)]
        start_time = dt.now()
        print(f'Render started @ {width}x{height}x{lighting_samples}spp {"with anti aliasing " if anti_aliasing else ""}using {cores_to_use} cores at {start_time}.')
        print()
        output = [pool.apply_async(self.render, args=(*arg,)) for arg in arguments]
        results = [o.get() for o in output]
        print(f'Render completed in {dt.now() - start_time}.')
        print('Saving image...')
        image = np.zeros((height, width, 3))
        for result in results:
            image += result
        plt.imsave('image.png', image)
        # PPM format
        with open("image.ppm", "w") as pic:
            pic.write(f"P3\n{width} {height}\n255\n")
            image_data = image.tolist()
            for row in image_data:
                for col in row:
                    pic.write(f"{int(col[0] * 255)} {int(col[1] * 255)} {int(col[2] * 255)} ")
                pic.write("\n")

    def render(self, width: int, height: int, max_depth: int = 1, anti_aliasing: bool = False, lighting_samples: int = 1, row_range: dict = {}) -> np.array:
        image = np.zeros((height, width, 3))
        SCREEN_RATIO = float(width) / float(height)
        SCREEN_DIMS = {'left': -1, 'top': 1 / SCREEN_RATIO, 'right': 1, 'bottom': -1 / SCREEN_RATIO}

        ###############################
        #   Anti-aliasing offsets
        #       _____________
        #       | X | X | X |
        #       -------------
        #       | X | X | X |
        #       -------------
        #       | X | X | X |
        #       -------------
        ###############################

        if anti_aliasing:
            ANTI_ALIASING_X = 1 / (2 * width)
            ANTI_ALIASING_Y = 1 / (2 * height)
            ANTI_ALIASING_OFFSETS = {'top-left': (-1 * ANTI_ALIASING_X, ANTI_ALIASING_Y),
                                     'top': (0, ANTI_ALIASING_Y),
                                     'top-right': (ANTI_ALIASING_X, ANTI_ALIASING_Y),
                                     'left': (-1 * ANTI_ALIASING_X, 0),
                                     'center': (0, 0),
                                     'right': (ANTI_ALIASING_X, 0),
                                     'bottom-left': (-1 * ANTI_ALIASING_X, - 1 * ANTI_ALIASING_Y),
                                     'bottom': (0, -1 * ANTI_ALIASING_Y),
                                     'bottom-right': (ANTI_ALIASING_X, - 1 * ANTI_ALIASING_Y)}
        else:
            ANTI_ALIASING_OFFSETS = {'center': (0, 0)}

        if not row_range:
            starting_row = 0
            ending_row = height
        else:
            starting_row = row_range['start']
            ending_row = row_range['end']

        for y in range(starting_row, ending_row):
            print(f'{y + 1}/{ending_row}', end='\n')
            yy = Q_map(value=-y, lower_limit=-(height - 1), upper_limit=0, scaled_lower_limit=SCREEN_DIMS['bottom'], scaled_upper_limit=SCREEN_DIMS['top'])
            for x in range(width):
                xx = Q_map(value=x, lower_limit=0, upper_limit=width - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)
                color_value = Q_Vector3d(0, 0, 0)
                for num_samples, offset in enumerate(ANTI_ALIASING_OFFSETS):
                    # Initial setup
                    pixel = Q_Vector3d(xx + ANTI_ALIASING_OFFSETS[offset][0], yy + ANTI_ALIASING_OFFSETS[offset][1], 0)
                    origin = self.camera_position
                    direction = (pixel - origin).normalized()
                    reflection = 1.0

                    for _ in range(max_depth):

                        ray = Ray(origin=origin, direction=direction)
                        nearest_object, object_hit = self.nearest_intersection(ray=ray)

                        # Did we even hit anything?
                        if nearest_object is None:
                            break

                        # Did we hit a light?
                        # if nearest_object.emission != Q_Vector3d(0, 0, 0):
                        #     color_value = nearest_object.emission  # * reflection?
                        #     break

                        intersection_point = origin + direction * object_hit.distance
                        shifted_point = intersection_point + object_hit.normal_to_surface * 1e-5
                        direction_from_intersection_to_light = (self.lights[0]['position'] - shifted_point).normalized()

                        # Lighting
                        illumination = self.calculate_lighting(lighting_samples=lighting_samples, this_object=nearest_object, origin=shifted_point, direction_from_intersection_to_light=direction_from_intersection_to_light, object_hit=object_hit)

                        # Reflection
                        color_value += illumination * reflection

                        # TODO - testing on whether this is necessary or not.
                        # if not hit_light:
                        #     break

                        # Handle reflection and continue
                        reflection *= nearest_object.reflection
                        if reflection == 0:
                            break

                        # Reset origination and direction to this point and continue recursively
                        origin = shifted_point
                        direction = direction.reflected(other_vector=object_hit.normal_to_surface)

                image[y, x] = (color_value * (1 / (num_samples + 1))).clamp(0, 1).to_tuple()

        return image

    def calculate_lighting(self, lighting_samples: int, this_object: Primitive, origin: Q_Vector3d, direction_from_intersection_to_light: Q_Vector3d, object_hit: Hit) -> Q_Vector3d:
        CONE_THETA = math.pi / 56.0
        illumination = Q_Vector3d(0, 0, 0)
        for u in range(lighting_samples):
            for v in range(lighting_samples):
                # Fire a ray towards where the light source is
                wobbled_direction = OrthoNormalBasis.cone_sample(direction=direction_from_intersection_to_light, cone_theta=CONE_THETA, u=u / lighting_samples, v=v / lighting_samples)
                ray = Ray(origin=origin, direction=wobbled_direction)
                illumination += self.calculate_illumination(ray=ray, this_object=this_object, hit=object_hit)
        return illumination * (1 / (lighting_samples ** 2))

    def calculate_illumination(self, ray: Ray, this_object: Primitive, hit: Hit) -> Q_Vector3d:
        illumination = Q_Vector3d(0, 0, 0)
        nearest_light, _ = self.nearest_intersection(ray=ray)
        is_shadowed = nearest_light is None or nearest_light.emission == Q_Vector3d(0, 0, 0)

        # Is the point we hit able to see a light?
        if is_shadowed:
            return illumination

        # Ambient lighting
        illumination += this_object.ambient * nearest_light.emission

        # Diffuse lighting
        intensity = math.fabs(ray.direction.dot_product(hit.normal_to_surface))
        illumination += this_object.diffuse * nearest_light.emission * intensity

        # Specular lighting
        intersection_to_camera = (self.camera_position - hit.position).normalized()
        H = (ray.direction + intersection_to_camera).normalized()
        illumination += this_object.specular * nearest_light.emission * (hit.normal_to_surface.dot_product(H)) ** (this_object.shininess / 4)
        return illumination
