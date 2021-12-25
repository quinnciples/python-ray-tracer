import math
import random
from datetime import datetime as dt
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from Camera import Camera
from Hit import Hit
from Primitive import Primitive
from QFunctions.Q_Functions import Q_buckets, Q_Vector3d
from Ray import Ray
from AABB import AABB


class Scene:
    OFFSET = 1e-5

    def __init__(self, camera_position: Q_Vector3d, objects: list = []):
        self.camera_position = camera_position
        self.objects = objects
        self.bounding_boxes = []

    def generate_bounding_boxes(self):
        print('Allocating objects to bounding boxes... ')
        # min_x = min(obj.position.x for obj in self.objects)
        max_x = max(math.fabs(obj.position.x) for obj in self.objects)
        # min_y = min(obj.position.y for obj in self.objects)
        max_y = max(math.fabs(obj.position.y) for obj in self.objects)
        # min_z = min(obj.position.z for obj in self.objects)
        max_z = max(math.fabs(obj.position.z) for obj in self.objects)
        max_dimension = max(max_x, max_y, max_z) + Scene.OFFSET
        box_positions = {'left_top_front': (-1, 0, 0), 'right_top_front': (0, 0, 0),
                         'left_bottom_front': (-1, -1, 0), 'right_bottom_front': (0, -1, 0),
                         'left_top_rear': (-1, 0, -1), 'right_top_rear': (0, 0, -1),
                         'left_bottom_rear': (-1, -1, -1), 'right_bottom_rear': (0, -1, -1)}
        for label, dim_adjustments in box_positions.items():
            dim_mod_x, dim_mod_y, dim_mod_z = dim_adjustments
            bounding_box = AABB(lower_left_corner=Q_Vector3d(max_dimension * dim_mod_x - Scene.OFFSET, max_dimension * dim_mod_y - Scene.OFFSET, max_dimension * dim_mod_z - Scene.OFFSET), length=max_dimension)
            # print(f'Created bounding box at {bounding_box.min_coordinate} -> {bounding_box.max_coordinate} size {bounding_box.length}')
            self.bounding_boxes.append(bounding_box)

        for obj in self.objects:
            assigned = False
            for bounding_box in self.bounding_boxes:
                # print(f'Tring to assign {obj.position} to bb {bounding_box.min_coordinate} {bounding_box.max_coordinate}...')
                # TODO
                # Need to check if sphere radius crosses boundary
                if obj.position.x >= bounding_box.min_coordinate.x and obj.position.x <= bounding_box.max_coordinate.x and obj.position.y >= bounding_box.min_coordinate.y and obj.position.y <= bounding_box.max_coordinate.y and obj.position.z >= bounding_box.min_coordinate.z and obj.position.z <= bounding_box.max_coordinate.z:
                    bounding_box.add_item(obj)
                    assigned = True
                    # print(f'Assigning {obj.position} to bb {bounding_box.min_coordinate} {bounding_box.max_coordinate}')
            if not assigned:
                raise "Object does not fix in bounding box"
        print('Done.')

    def nearest_intersection(self, ray: Ray) -> tuple[Primitive, Hit]:  # Could this be optimized by asking "does a ray of length(this_distance so far) intersect this object" ?
        min_distance = math.inf
        obj = None
        nearest_hit = None

        for bounding_box in self.bounding_boxes:
            if bounding_box.intersect(ray=ray):
                for this_object in bounding_box.items:  # self.objects:
                    # if (this_object.position - ray.origin).dot_product(ray.direction) < 0:
                    #     continue
                    hit = this_object.intersect(ray=ray)
                    if hit and hit.distance < min_distance:
                        obj = this_object
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
                    pic.write(f"{int(col[0] * 255.999)} {int(col[1] * 255.999)} {int(col[2] * 255.999)} ")
                pic.write("\n")

    def multi_render(self, camera: Camera, width: int, height: int, max_depth: int = 1, lighting_samples: int = 1, cores_to_use: int = 1) -> None:
        number_of_buckets = 10
        cores_to_use = max(cores_to_use, 1) if cores_to_use != 0 else cpu_count()
        pool = Pool(processes=cores_to_use)
        arguments = [(camera, width, height, max_depth, lighting_samples, {'start': start, 'end': end}) for start, end in Q_buckets(number_of_items=height, number_of_buckets=number_of_buckets)]
        start_time = dt.now()
        print(f'Render started @ {width}x{height}x{lighting_samples}spp using {cores_to_use} cores at {start_time}.')
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

    def generate_anti_aliasing_offsets(self, width: int, height: int, number_of_samples: int) -> dict:
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

        ANTI_ALIASING_OFFSETS = {'center': (0, 0)}
        ADDTL_OFFSETS = {}
        if number_of_samples > 1:
            ANTI_ALIASING_X = 1 / width
            ANTI_ALIASING_Y = 1 / height
            ADDTL_OFFSETS = {
                _ + 1: (
                    (random.random() - 0.5) * ANTI_ALIASING_X,
                    (random.random() - 0.5) * ANTI_ALIASING_Y,
                )
                for _ in range(number_of_samples - 1)
            }
        return {**ANTI_ALIASING_OFFSETS, **ADDTL_OFFSETS}

    def render(self, camera: Camera, width: int, height: int, max_depth: int = 1, lighting_samples: int = 1, row_range: dict = {}) -> np.array:
        image = np.zeros((height, width, 3))
        # self.lighting_samples = lighting_samples

        ANTI_ALIASING_OFFSETS = self.generate_anti_aliasing_offsets(width=width, height=height, number_of_samples=lighting_samples)

        if not row_range:
            starting_row = 0
            ending_row = height
        else:
            starting_row = row_range['start']
            ending_row = row_range['end']

        for y in range(starting_row, ending_row):
            print(f'{y + 1}/{ending_row}', end='\n')
            yy = y / height
            for x in range(width):
                xx = x / width
                color_value = Q_Vector3d(0, 0, 0)
                for offset_x, offset_y in ANTI_ALIASING_OFFSETS.values():
                    color_value += self.trace_ray(ray=camera.get_ray_from_camera(xx + offset_x, yy + offset_y), max_depth=max_depth)

                image[y, x] = (color_value * (1 / lighting_samples)).clamp(0, 1).to_tuple()

        return image

    def trace_ray(self, ray: Ray, max_depth: int, current_depth: int = 1) -> Q_Vector3d:
        def environment_color(ray: Ray) -> Q_Vector3d:
            unit_direction = ray.direction.normalized()
            t = 0.5 * (unit_direction.y + 1.0)
            return (1.0 - t) * Q_Vector3d(1.0, 1.0, 1.0) + t * Q_Vector3d(0.5, 0.7, 1.0)

        nearest_object, object_hit = self.nearest_intersection(ray=ray)

        # Did we hit anything?
        if nearest_object is None or current_depth > max_depth:
            return environment_color(ray=ray)
        else:
            color_value, next_ray = nearest_object.material.handle_ray_intersection(incoming_ray=ray, object_hit=object_hit)
            if next_ray is None:
                return color_value if color_value else Q_Vector3d(0, 0, 0)
            else:
                # next_ray = Ray(next_ray.origin + next_ray.direction.normalized() * 1e-5, next_ray.direction)
                return color_value * self.trace_ray(ray=next_ray, max_depth=max_depth, current_depth=current_depth + 1)
