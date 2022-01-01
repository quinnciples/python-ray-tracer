import copy
import math
import random
from datetime import datetime as dt
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

from AABB import AABB
from Camera import Camera
from Hit import Hit
from Material import Diffuse, Glass, Material, Metal
from Primitive import Primitive
from QFunctions.Q_Functions import Q_buckets, Q_Vector3d
from Ray import Ray
from SpherePrimitive import SpherePrimitive


class Scene:
    OFFSET = 1e-5

    def __init__(self, objects: list = []):
        self.objects = objects
        self.bounding_boxes = []

    def generate_bounding_boxes(self):

        print("Creating bounding boxes... ")
        max_x = max(math.fabs(obj.position.x) for obj in self.objects)
        max_y = max(math.fabs(obj.position.y) for obj in self.objects)
        max_z = max(math.fabs(obj.position.z) for obj in self.objects)
        max_dimension = max(max_x, max_y, max_z) + Scene.OFFSET

        # Create initial box
        bounding_box = AABB(
            lower_left_corner=Q_Vector3d(-20.00001, 0.1, -20.00001),
            length=40,
            name="biggie top",
        )
        # print(
        #     f"Created bounding box {bounding_box.name} at {bounding_box.min_coordinate} -> {bounding_box.max_coordinate} size {bounding_box.length}"
        # )
        initial_boxes = [bounding_box]

        # Recursively split existing box(es) into 8 sections
        boxes_to_add = list()
        current_level = initial_boxes
        for box in current_level:
            for bounding_box in box.split(split_level=3):
                boxes_to_add.append(bounding_box)

        boxes_to_add.append(
            AABB(
                lower_left_corner=Q_Vector3d(-20.00001, -40.0000001, -20.00001),
                length=40,
                name="biggie bottom",
            )
        )

        for box in boxes_to_add:
            self.bounding_boxes.append(box)

        print("Allocating objects to bounding boxes... ")
        number_of_objects = len(self.objects)
        current_object = 1
        for obj in self.objects:
            print(f"\r{current_object}/{number_of_objects}", end="")
            assigned = False
            for bounding_box in self.bounding_boxes:
                # # print(
                # #     f"Tring to assign {obj.position} with radius {obj.radius} to {bounding_box.name} {bounding_box.min_coordinate} {bounding_box.max_coordinate}..."
                # # )
                # # TODO
                # # Need to check if sphere radius crosses boundary
                add = False
                # if (
                #     # Check if object is inside the box
                #     (bounding_box.min_coordinate.x <= obj.position.x <= bounding_box.max_coordinate.x)
                #     and (bounding_box.min_coordinate.y <= obj.position.y <= bounding_box.max_coordinate.y)
                #     and (bounding_box.min_coordinate.z <= obj.position.z <= bounding_box.max_coordinate.z)
                # ):
                #     add = True
                #     # print('Object center is inside the box')
                # elif (
                #     # Check if any of the corners are inside the object
                #     sum(
                #         1 if (corner - obj.position).length <= obj.radius else 0
                #         for corner in bounding_box.get_corners()
                #     )
                #     > 0
                # ):
                #     add = True
                #     # print('Box has a corner inside the object')

                # if not add:
                #     # Check if a ray fired along any axis of the AABB intersects the object
                #     corners = bounding_box.get_corners()
                #     for starting_corner in corners:
                #         for ending_corner in corners:
                #             if starting_corner == ending_corner:
                #                 continue
                #             ray = Ray(origin=starting_corner, direction=(ending_corner - starting_corner).normalized())
                #             hit = obj.intersect(ray=ray)
                #             if hit and hit.distance <= (ending_corner - starting_corner).length:
                #                 add = True
                #                 # print('Box intersects object')
                #         #         break
                #         # if add:
                #         #     break

                if not add:
                    if obj.intersects_with_bounding_box(box=bounding_box):
                        add = True

                if add:
                    bounding_box.add_item(obj)
                    assigned = True
                    # print(
                    #     f"Assigning {obj.position} to bb {bounding_box.name} -- {bounding_box.min_coordinate} {bounding_box.max_coordinate}"
                    # )
            if not assigned:
                raise Exception("Object not assigned to any bounding box")
            current_object += 1

        print("Done.")
        print()
        print("Summary")
        boxes_to_remove = list()
        for bounding_box in self.bounding_boxes:
            if not bounding_box.items:
                boxes_to_remove.append(bounding_box)
            else:
                print(f"{bounding_box.name} has {len(bounding_box.items)} items.")
        for box in boxes_to_remove:
            # print(f"{box.name} has {len(box.items)} items and will be removed.")
            self.bounding_boxes.remove(box)
        print(f"{len(self.bounding_boxes)} boxes in this scene.")

    def nearest_intersection(
        self, ray: Ray
    ) -> tuple[
        Primitive, Hit
    ]:  # Could this be optimized by asking "does a ray of length(this_distance so far) intersect this object" ?
        min_distance = math.inf
        obj = None
        nearest_hit = None
        checked_objects = set()

        if self.bounding_boxes:
            for bounding_box in self.bounding_boxes:
                if bounding_box.intersect(ray=ray):  # intersect
                    for this_object in bounding_box.items:  # self.objects:
                        # if (this_object.position - ray.origin).dot_product(ray.direction) < 0:
                        #     continue
                        if this_object not in checked_objects:
                            checked_objects.add(this_object)
                            hit = this_object.intersect(ray=ray)
                            if hit and hit.distance < min_distance:
                                obj = this_object
                                nearest_hit = hit
                                min_distance = hit.distance
            return obj, nearest_hit
        else:
            for this_object in self.objects:  # self.objects:
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

    def multi_render(
        self,
        camera: Camera,
        width: int,
        height: int,
        max_depth: int = 1,
        lighting_samples: int = 1,
        cores_to_use: int = 1,
    ) -> None:
        number_of_buckets = 10
        cores_to_use = max(cores_to_use, 1) if cores_to_use != 0 else cpu_count()
        pool = Pool(processes=cores_to_use)
        arguments = [
            (camera, width, height, max_depth, lighting_samples, {"start": start, "end": end})
            for start, end in Q_buckets(number_of_items=height, number_of_buckets=number_of_buckets)
        ]
        start_time = dt.now()
        print(f"Render started @ {width}x{height}x{lighting_samples}spp using {cores_to_use} cores at {start_time}.")
        print()
        output = [pool.apply_async(self.render, args=(*arg,)) for arg in arguments]
        results = [o.get() for o in output]
        print(f"Render completed in {dt.now() - start_time}.")
        print("Saving image...")
        image = np.zeros((height, width, 3))
        for result in results:
            image += result
        plt.imsave("image.png", image)
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

        ANTI_ALIASING_OFFSETS = {"center": (0, 0)}
        ADDTL_OFFSETS = {}
        if number_of_samples > 1:
            ANTI_ALIASING_X = 1 / width
            ANTI_ALIASING_Y = 1 / height
            ADDTL_OFFSETS = {
                _
                + 1: (
                    (random.random() - 0.5) * ANTI_ALIASING_X,
                    (random.random() - 0.5) * ANTI_ALIASING_Y,
                )
                for _ in range(number_of_samples - 1)
            }
        return {**ANTI_ALIASING_OFFSETS, **ADDTL_OFFSETS}

    def render(
        self,
        camera: Camera,
        width: int,
        height: int,
        max_depth: int = 1,
        lighting_samples: int = 1,
        row_range: dict = {},
    ) -> np.array:
        image = np.zeros((height, width, 3))
        # self.lighting_samples = lighting_samples

        ANTI_ALIASING_OFFSETS = self.generate_anti_aliasing_offsets(
            width=width, height=height, number_of_samples=lighting_samples
        )

        if not row_range:
            starting_row = 0
            ending_row = height
        else:
            starting_row = row_range["start"]
            ending_row = row_range["end"]

        for y in range(starting_row, ending_row):
            print(f"{y + 1}/{ending_row}", end="\n")
            yy = y / height
            for x in range(width):
                xx = x / width
                color_value = Q_Vector3d(0, 0, 0)
                for offset_x, offset_y in ANTI_ALIASING_OFFSETS.values():
                    # print(f'Checking {x}, {y}...')
                    color_value += self.trace_ray(
                        ray=camera.get_ray_from_camera(xx + offset_x, yy + offset_y), max_depth=max_depth
                    )

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
            color_value, next_ray = nearest_object.material.handle_ray_intersection(
                incoming_ray=ray, object_hit=object_hit
            )
            if next_ray is None:
                return color_value if color_value else Q_Vector3d(0, 0, 0)
            else:
                # next_ray = Ray(next_ray.origin + next_ray.direction.normalized() * 1e-5, next_ray.direction)
                return color_value * self.trace_ray(ray=next_ray, max_depth=max_depth, current_depth=current_depth + 1)

    def setup_rtiaw_test_scene(self):
        self.objects.clear()
        random.seed(41365)
        for a in range(-11, 11):
            for b in range(-11, 11):
                # print("\r                 ", end="", flush=True)
                # print(f"\r{a} - {b}", end="", flush=True)
                # Check for collissions
                fail = True
                while fail:
                    fail = False
                    center = Q_Vector3d((a / 1.0) + 1.0 * random.random(), 0.2, (b / 1.0) + 1.0 * random.random() + 4)
                    for sphere in self.objects:
                        if (sphere.position - center).length < 0.22 or (center - Q_Vector3d(4, 0.2, 4)).length <= 1.1 or (center - Q_Vector3d(0, 0.2, 4)).length <= 1.1 or (center - Q_Vector3d(-4, 0.2, 4)).length <= 1.1:
                            fail = True
                            break

                # Create random material
                choose_mat = random.random()
                if choose_mat < 0.65:
                    # Diffuse material
                    # Random color
                    color_value = Q_Vector3d(random.random(), random.random(), random.random())
                    self.objects.append(SpherePrimitive(position=center, material=Diffuse(attenuation=color_value), radius=0.2))
                elif choose_mat < 0.90:
                    # Metal
                    color_value = Q_Vector3d(random.random() / 2.0 + 0.5, random.random() / 2.0 + 0.5, random.random() / 2.0 + 0.5)
                    fuzz = random.random() / 2.0
                    fuzz = 0 if fuzz < 0.15 else fuzz
                    self.objects.append(SpherePrimitive(position=center, material=Metal(attenuation=color_value, fuzziness=float(fuzz)), radius=0.2))
                else:
                    # Glass
                    self.objects.append(SpherePrimitive(position=center, material=Glass(refraction_index=1.5), radius=0.2))

        self.objects.append(SpherePrimitive(position=Q_Vector3d(0, -1000.0001, 4), material=Diffuse(attenuation=Q_Vector3d(0.5, 0.5, 0.5)), radius=1000))
        self.objects.append(SpherePrimitive(position=Q_Vector3d(0, 1, 4), material=Glass(refraction_index=1.5), radius=1.0))
        self.objects.append(SpherePrimitive(position=Q_Vector3d(-4, 1, 4), material=Diffuse(attenuation=Q_Vector3d(0.4, 0.2, 0.1)), radius=1.0))
        self.objects.append(SpherePrimitive(position=Q_Vector3d(4, 1, 4), material=Metal(attenuation=Q_Vector3d(0.7, 0.6, 0.5), fuzziness=0.0), radius=1.0))

        print(f'\n{len(self.objects)} added to scene...')
        print('*' * 40)
        print()
        with open('render_settings.txt', 'w') as f_out:
            for o in self.objects:
                f_out.write(repr(o) + '\n')
