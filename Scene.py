import math
from datetime import datetime as dt
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np
import random

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
        self.generate_random_unit_vectors()

    def generate_random_unit_vectors(self) -> None:
        fail_count = 0

        def random_in_unit_sphere() -> Q_Vector3d:
            nonlocal fail_count
            p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
            while p.length_squared >= 1.0:
                p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
                fail_count += 1
            return p
        self.random_unit_vectors = [random_in_unit_sphere() for _ in range(10_000)]
        # print(fail_count)

    def nearest_intersection(self, ray: Ray) -> tuple[Primitive, Hit]:  # Could this be optimized by asking "does a ray of length(this_distance so far) intersect this object" ?
        min_distance = math.inf
        obj = None
        nearest_hit = None
        for object in self.objects:
            hit = object.intersect(ray=ray)
            if hit and hit.distance < min_distance:
                obj = object
                nearest_hit = hit
                min_distance = hit.distance
        return obj, nearest_hit

    @staticmethod
    def write_ppm_file(image_data) -> None:
        height = len(image_data)
        width = len(image_data[0])
        # PPM format
        with open("image.ppm", "w") as pic:
            pic.write(f"P3\n{width} {height}\n255\n")
            for row in image_data:
                for col in row:
                    pic.write(f"{int(col[0] * 255)} {int(col[1] * 255)} {int(col[2] * 255)} ")
                pic.write("\n")

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
        Scene.write_ppm_file(image_data=image.tolist())

    def render(self, width: int, height: int, max_depth: int = 1, anti_aliasing: bool = False, lighting_samples: int = 1, row_range: dict = {}) -> np.array:
        image = np.zeros((height, width, 3))
        self.lighting_samples = lighting_samples
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
                    color_value += self.trace_ray(ray=Ray(origin=origin, direction=direction), max_depth=max_depth)

                image[y, x] = (color_value * (1 / (num_samples + 1))).clamp(0, 1).to_tuple()

        return image

    def trace_ray(self, ray: Ray, max_depth: int, current_depth: int = 1, reflection: float = 1.0) -> Q_Vector3d:
        # def random_in_unit_sphere() -> Q_Vector3d:
        #     p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
        #     while p.length_squared >= 1.0:
        #         p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
        #     return p
        nearest_object, object_hit = self.nearest_intersection(ray=ray)
        color_value = Q_Vector3d(0, 0, 0)

        # Did we even hit anything?
        if nearest_object is None or current_depth > max_depth:
            unit_direction = ray.direction.normalized()
            t = 0.5 * (unit_direction.y + 1.0)
            return (1.0 - t) * Q_Vector3d(1.0, 1.0, 1.0) + t * Q_Vector3d(0.5, 0.7, 1.0)  # color_value
        else:
            
            target = object_hit.position + object_hit.normal_to_surface + random.choice(self.random_unit_vectors)
            return self.trace_ray(ray=Ray(origin=object_hit.position + (object_hit.normal_to_surface * 0.001), direction=(target - object_hit.position).normalized()), max_depth=max_depth, current_depth=current_depth + 1, reflection=0) * 0.5

        shifted_point = object_hit.position + object_hit.normal_to_surface * 1e-5
        direction_from_intersection_to_light = (self.lights[0]['position'] - shifted_point).normalized()

        # Lighting
        illumination = self.calculate_lighting(this_object=nearest_object, origin=shifted_point, direction_from_intersection_to_light=direction_from_intersection_to_light, object_hit=object_hit)

        # Reflection
        color_value += illumination * reflection

        # Handle reflection and continue
        reflection *= nearest_object.reflection
        if reflection == 0:
            return color_value

        if current_depth == max_depth:
            return color_value

        # Reset origination and direction to this point and continue recursively
        origin = shifted_point
        direction = ray.direction.reflected(other_vector=object_hit.normal_to_surface)
        return color_value + self.trace_ray(Ray(origin=origin, direction=direction), max_depth=max_depth, current_depth=current_depth + 1, reflection=reflection)

    def calculate_lighting(self, this_object: Primitive, origin: Q_Vector3d, direction_from_intersection_to_light: Q_Vector3d, object_hit: Hit) -> Q_Vector3d:
        CONE_THETA = math.pi / 56.0
        illumination = Q_Vector3d(0, 0, 0)
        for u in range(self.lighting_samples):
            for v in range(self.lighting_samples):
                # Fire ray(s) towards where the light source is
                wobbled_direction = OrthoNormalBasis.cone_sample(direction=direction_from_intersection_to_light, cone_theta=CONE_THETA, u=u / self.lighting_samples, v=v / self.lighting_samples)
                ray = Ray(origin=origin, direction=wobbled_direction)
                illumination += self.calculate_illumination(ray=ray, this_object=this_object, hit=object_hit)
        return illumination * (1 / (self.lighting_samples ** 2))

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
