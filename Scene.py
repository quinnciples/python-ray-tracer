from QFunctions.Q_Functions import Q_Vector3d
from QFunctions.Q_Functions import Q_map
from Ray import Ray
import matplotlib.pyplot as plt
import numpy as np
import math
from datetime import datetime as dt


class Scene:
    def __init__(self, objects: list = [], lights: list = []):
        self.objects = objects
        self.lights = lights

    def nearest_intersection(self, ray: Ray):
        min_distance = math.inf
        obj = None
        normal_to_surface = None
        for object in self.objects:
            this_distance, this_normal_to_surface = object.intersect(ray=ray)
            if this_distance and this_distance < min_distance:
                min_distance = this_distance
                obj = object
                normal_to_surface = this_normal_to_surface
        return (obj, min_distance, normal_to_surface)

    def render(self, camera_position: Q_Vector3d, width: int = 64, height: int = 64, max_depth: int = 1, anti_aliasing: bool = False):
        start_time = dt.now()
        image = np.zeros((height, width, 3))
        SCREEN_RATIO = float(width) / float(height)
        SCREEN_DIMS = {'left': -1, 'top': 1 / SCREEN_RATIO, 'right': 1, 'bottom': -1 / SCREEN_RATIO}
        self.actual_max_depth = 0

        ####################
        #   Anti-aliasing
        #   _____________
        #   | X | X | X |
        #   -------------
        #   | X | X | X |
        #   -------------
        #   | X | X | X |
        #   -------------
        ####################

        if anti_aliasing:
            ANTI_ALIASING_X = 1 / (2 * width)
            ANTI_ALIASING_Y = 1 / (2 * height)
            ANTI_ALIASING_OFFSETS = {'top-left': (-1 * ANTI_ALIASING_X, ANTI_ALIASING_Y),
                                     # 'top': (0, ANTI_ALIASING_Y),
                                     'top-right': (ANTI_ALIASING_X, ANTI_ALIASING_Y),
                                     # 'left': (-1 * ANTI_ALIASING_X, 0),
                                     # 'center': (0, 0),
                                     # 'right': (ANTI_ALIASING_X, 0),
                                     'bottom-left': (-1 * ANTI_ALIASING_X, - 1 * ANTI_ALIASING_Y),
                                     # 'bottom': (0, -1 * ANTI_ALIASING_Y),
                                     'bottom-right': (ANTI_ALIASING_X, - 1 * ANTI_ALIASING_Y)}
        else:
            ANTI_ALIASING_OFFSETS = {'center': (0, 0)}

        for y in range(height):
            print(f'\r{y + 1}/{height}', end='')
            yy = Q_map(value=-y, lower_limit=-(height - 1), upper_limit=0, scaled_lower_limit=SCREEN_DIMS['bottom'], scaled_upper_limit=SCREEN_DIMS['top'])  # -((2 * y / float(HEIGHT - 1)) - 1)  # Q_map(value=-y, lower_limit=-(HEIGHT - 1), upper_limit=0, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (-y + (HEIGHT / 2.0)) / HEIGHT  # Need to make sure I did this right
            for x in range(width):
                xx = Q_map(value=x, lower_limit=0, upper_limit=width - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (2 * x / float(WIDTH - 1)) - 1  # Q_map(value=x, lower_limit=0, upper_limit=WIDTH - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (x - (WIDTH / 2.0)) / WIDTH
                color_value = Q_Vector3d(0, 0, 0)
                for num_samples, offset in enumerate(ANTI_ALIASING_OFFSETS):
                    pixel = Q_Vector3d(xx + ANTI_ALIASING_OFFSETS[offset][0], yy + ANTI_ALIASING_OFFSETS[offset][1], 0)

                    # Initial setup
                    origin = camera_position
                    direction = (pixel - origin).normalized()

                    reflection = 1

                    for depth in range(max_depth):

                        ray = Ray(origin=origin, direction=direction)
                        nearest_object, distance_to_object, normal_to_surface = self.nearest_intersection(ray=ray)

                        # Did we even hit anything?
                        if nearest_object is None:
                            break

                        intersection_point = origin + direction * distance_to_object
                        # Need to create a structure that can return the distance and normal from the object
                        # normal_to_surface = (intersection_point - nearest_object.position).normalized() if type(nearest_object) == SpherePrimitive else nearest_object.face_normal * -1
                        shifted_point = intersection_point + normal_to_surface * 1e-5
                        direction_from_intersection_to_light = (self.lights[0]['position'] - shifted_point).normalized()

                        ray = Ray(origin=shifted_point, direction=direction_from_intersection_to_light)
                        _, distance_to_object, __ = self.nearest_intersection(ray=ray)

                        distance_to_light = (self.lights[0]['position'] - intersection_point).length
                        is_shadowed = distance_to_object < distance_to_light

                        # Is the point we hit able to see a light?
                        if is_shadowed:
                            break

                        # Lighting
                        illumination = Q_Vector3d(0, 0, 0)

                        # Ambient lighting
                        illumination += nearest_object.ambient * self.lights[0]['color']

                        # Diffuse lighting
                        intensity = math.fabs(direction_from_intersection_to_light.dot_product(normal_to_surface))
                        illumination += nearest_object.diffuse * self.lights[0]['color'] * intensity

                        # Specular lighting
                        intersection_to_camera = (camera_position - intersection_point).normalized()
                        H = (direction_from_intersection_to_light + intersection_to_camera).normalized()
                        illumination += nearest_object.specular * self.lights[0]['color'] * (normal_to_surface.dot_product(H)) ** (nearest_object.shininess / 4)  # nearest_object['shininess']

                        # Reflection
                        color_value += illumination * reflection

                        # Handle reflection and continue
                        reflection *= nearest_object.reflection  # Can we say if reflection == 0 then break here?
                        if reflection == 0:
                            break

                        # Reset origination and direction to this point and continue recursively
                        origin = shifted_point
                        direction = direction.reflected(other_vector=normal_to_surface)

                    self.actual_max_depth = max(self.actual_max_depth, depth + 1)

                image[y, x] = (color_value * (1 / (num_samples + 1))).clamp(0, 1).to_tuple()  # nearest_object['color'] if nearest_object else (0, 0, 0)

        plt.imsave('image.png', image)
        print()
        print(f'Maximum depth allowed: {max_depth} -- Actual depth reached: {self.actual_max_depth}')
        print(f'Render completed in {dt.now() - start_time}.')
