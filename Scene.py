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
    def __init__(self, objects: list = [], lights: list = []):
        self.objects = objects
        self.lights = lights

    def nearest_intersection(self, ray: Ray) -> tuple[Primitive, float, Q_Vector3d]:  # Could this be optimized by asking "does a ray of length(this_distance so far) intersect this object" ?
        min_distance = math.inf
        obj = None
        normal_to_surface = None
        for object in self.objects:
            # this_distance, this_normal_to_surface = object.intersect(ray=ray)
            hit = object.intersect(ray=ray)
            if hit and hit.distance < min_distance:
                min_distance = hit.distance
                obj = object
                normal_to_surface = hit.normal_to_surface
        return (obj, min_distance, normal_to_surface)

    def multi_render(self, camera_position: Q_Vector3d, width: int, height: int, max_depth: int = 1, anti_aliasing: bool = False, lighting_samples: int = 1, cores_to_use: int = 1) -> None:
        number_of_buckets = 10
        cores_to_use = cores_to_use if cores_to_use != 0 else cpu_count()
        pool = Pool(processes=cores_to_use)
        # arguments = [(camera_position, width, height, max_depth, anti_aliasing, lighting_samples, {'start': _ * int(height / num_chunks), 'end': _ * int(height / num_chunks) + int(height / num_chunks)}) for _ in range(num_chunks)]
        arguments = [(camera_position, width, height, max_depth, anti_aliasing, lighting_samples, {'start': start, 'end': end}) for start, end in Q_buckets(number_of_items=height, number_of_buckets=number_of_buckets)]
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

    def render(self, camera_position: Q_Vector3d, width: int, height: int, max_depth: int = 1, anti_aliasing: bool = False, lighting_samples: int = 1, row_range: dict = {}) -> np.array:
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
            yy = Q_map(value=-y, lower_limit=-(height - 1), upper_limit=0, scaled_lower_limit=SCREEN_DIMS['bottom'], scaled_upper_limit=SCREEN_DIMS['top'])  # -((2 * y / float(HEIGHT - 1)) - 1)  # Q_map(value=-y, lower_limit=-(HEIGHT - 1), upper_limit=0, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (-y + (HEIGHT / 2.0)) / HEIGHT  # Need to make sure I did this right
            for x in range(width):
                xx = Q_map(value=x, lower_limit=0, upper_limit=width - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (2 * x / float(WIDTH - 1)) - 1  # Q_map(value=x, lower_limit=0, upper_limit=WIDTH - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (x - (WIDTH / 2.0)) / WIDTH
                color_value = Q_Vector3d(0, 0, 0)
                for num_samples, offset in enumerate(ANTI_ALIASING_OFFSETS):
                    # Initial setup
                    pixel = Q_Vector3d(xx + ANTI_ALIASING_OFFSETS[offset][0], yy + ANTI_ALIASING_OFFSETS[offset][1], 0)
                    origin = camera_position
                    direction = (pixel - origin).normalized()
                    reflection = 1.0

                    for depth in range(max_depth):

                        ray = Ray(origin=origin, direction=direction)
                        nearest_object, distance_to_object, normal_to_surface = self.nearest_intersection(ray=ray)

                        # Did we even hit anything?
                        if nearest_object is None:
                            break

                        # Did we hit a light?
                        # if nearest_object.emission != Q_Vector3d(0, 0, 0):
                        #     color_value = nearest_object.emission  # * reflection?
                        #     break

                        intersection_point = origin + direction * distance_to_object
                        shifted_point = intersection_point + normal_to_surface * 1e-5
                        direction_from_intersection_to_light = (self.lights[0]['position'] - shifted_point).normalized()

                        # Lighting
                        # Fire a ray towards where the light source is
                        NUMBER_OF_LIGHTING_SAMPLES = lighting_samples
                        hit_light = False
                        cone_theta = math.pi / 56.0
                        illumination = Q_Vector3d(0, 0, 0)
                        for u in range(NUMBER_OF_LIGHTING_SAMPLES):
                            for v in range(NUMBER_OF_LIGHTING_SAMPLES):
                                wobbled_direction = OrthoNormalBasis.cone_sample(direction=direction_from_intersection_to_light, cone_theta=cone_theta, u=u / NUMBER_OF_LIGHTING_SAMPLES, v=v / NUMBER_OF_LIGHTING_SAMPLES)
                                # ray = Ray(origin=shifted_point, direction=direction_from_intersection_to_light)
                                ray = Ray(origin=shifted_point, direction=wobbled_direction)
                                nearest_light, distance_to_light, __ = self.nearest_intersection(ray=ray)

                                # distance_to_light = (self.lights[0]['position'] - intersection_point).length
                                is_shadowed = nearest_light is None or nearest_light.emission == Q_Vector3d(0, 0, 0)

                                # Is the point we hit able to see a light?
                                if is_shadowed:
                                    continue
                                hit_light = True

                                # Ambient lighting
                                illumination += nearest_object.ambient * nearest_light.emission

                                # Diffuse lighting
                                intensity = math.fabs(wobbled_direction.dot_product(normal_to_surface))
                                illumination += nearest_object.diffuse * nearest_light.emission * intensity

                                # Specular lighting
                                intersection_to_camera = (camera_position - intersection_point).normalized()
                                H = (wobbled_direction + intersection_to_camera).normalized()
                                illumination += nearest_object.specular * nearest_light.emission * (normal_to_surface.dot_product(H)) ** (nearest_object.shininess / 4)

                        illumination = illumination * (1 / (NUMBER_OF_LIGHTING_SAMPLES ** 2))

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
                        direction = direction.reflected(other_vector=normal_to_surface)

                image[y, x] = (color_value * (1 / (num_samples + 1))).clamp(0, 1).to_tuple()

        return image
