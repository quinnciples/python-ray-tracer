import math
from Q_Functions import Q_Vector3d, Q_map
import numpy as np
import os
import matplotlib.pyplot as plt


class Ray:
    def __init__(self, origin: Q_Vector3d, direction: Q_Vector3d):
        self.origin = origin
        self.direction = direction


class Scene:
    def __init__(self, objects: list = [], lights: list = []):
        self.objects = objects
        self.lights = lights

    def nearest_intersection(self, ray: Ray):
        min_distance = math.inf
        obj = None
        for object in self.objects:
            intersection = object.intersect(ray=ray)
            if intersection and intersection < min_distance:
                min_distance = intersection
                obj = object

        return obj, min_distance

    def render(self, camera_position: Q_Vector3d, width: int = 64, height: int = 64, max_depth: int = 1):
        image = np.zeros((height, width, 3))
        SCREEN_RATIO = float(width) / float(height)
        SCREEN_DIMS = {'left': -1, 'top': 1 / SCREEN_RATIO, 'right': 1, 'bottom': -1 / SCREEN_RATIO}

        for y in range(height):
            print(f'\r{y + 1}/{height}', end='')
            yy = Q_map(value=-y, lower_limit=-(height - 1), upper_limit=0, scaled_lower_limit=SCREEN_DIMS['bottom'], scaled_upper_limit=SCREEN_DIMS['top'])  # -((2 * y / float(HEIGHT - 1)) - 1)  # Q_map(value=-y, lower_limit=-(HEIGHT - 1), upper_limit=0, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (-y + (HEIGHT / 2.0)) / HEIGHT  # Need to make sure I did this right
            for x in range(width):
                xx = Q_map(value=x, lower_limit=0, upper_limit=width - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (2 * x / float(WIDTH - 1)) - 1  # Q_map(value=x, lower_limit=0, upper_limit=WIDTH - 1, scaled_lower_limit=-1.0, scaled_upper_limit=1.0)  # (x - (WIDTH / 2.0)) / WIDTH
                pixel = Q_Vector3d(xx, yy, 0)

                # Initial setup
                origin = camera_position
                direction = (pixel - origin).normalized()
                color_value = Q_Vector3d(0, 0, 0)
                reflection = 1

                self.actual_max_depth = 0

                for _ in range(max_depth):
                    ray = Ray(origin=origin, direction=direction)
                    nearest_object, distance_to_object = scene.nearest_intersection(ray=ray)

                    self.actual_max_depth = max(self.actual_max_depth, _ + 1)

                    # Did we even hit anything?
                    if nearest_object is None:
                        break

                    intersection_point = origin + direction * distance_to_object
                    normal_to_surface = (intersection_point - nearest_object.position).normalized()
                    shifted_point = intersection_point + normal_to_surface * 1e-5
                    direction_from_intersection_to_light = (self.lights[0]['position'] - shifted_point).normalized()

                    ray = Ray(origin=shifted_point, direction=direction_from_intersection_to_light)
                    _, distance_to_object = scene.nearest_intersection(ray=ray)

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
                    illumination += nearest_object.specular * self.lights[0]['color'] * (normal_to_surface.dot_product(H)) ** (100 / 4)  # nearest_object['shininess']

                    # Reflection
                    color_value += illumination * reflection

                    image[y, x] = color_value.clamp(0, 1).to_tuple()  # nearest_object['color'] if nearest_object else (0, 0, 0)
                    

                    # Handle reflection and continue
                    reflection *= nearest_object.reflection  # Can we say if reflection == 0 then break here?

                    # Reset origination and direction to this point and continue recursively
                    origin = shifted_point
                    direction = direction.reflected(other_vector=normal_to_surface)

        plt.imsave('image.png', image)
        print()
        print(f'Maximum depth allowed: {max_depth} -- Actual depth reached: {self.actual_max_depth}')


class Primitive:
    def __init__(self, position: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float):
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection


class SpherePrimitive(Primitive):
    """
    Use this as a test:
    c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2
    c = ((ray.origin - self.center).length ** 2) - (self.radius ** 2)
    """
    def __init__(self, position: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float, radius: float):
        # self.center = center
        Primitive.__init__(self, position=position, ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection)
        self.radius = float(radius)

    def intersect(self, ray: Ray):
        b = 2 * ray.direction.dot_product(other_vector=(ray.origin - self.position))
        c = ((ray.origin - self.position).length ** 2) - (self.radius ** 2)

        # Test
        # ray_origin = np.array([ray.origin.x, ray.origin.y, ray.origin.z])
        # center = np.array([self.center.x, self.center.y, self.center.z])
        # radius = self.radius
        # c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2

        delta = b ** 2 - 4 * c
        if delta > 0:
            t1 = (-b + math.sqrt(delta)) / 2
            t2 = (-b - math.sqrt(delta)) / 2
            if t1 > 0 and t2 > 0:
                return min(t1, t2)
        return None


WIDTH = 128
HEIGHT = 96
CAMERA = Q_Vector3d(0, 0, -1.75)
MAX_DEPTH = 5

objects = [
    SpherePrimitive(position=Q_Vector3d(x=2.5, y=0, z=15), ambient=Q_Vector3d(0.1, 0, 0.1), diffuse=Q_Vector3d(0.7, 0, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=3),
    SpherePrimitive(position=Q_Vector3d(x=-4.5, y=0, z=15), ambient=Q_Vector3d(0, 0.1, 0.1), diffuse=Q_Vector3d(0, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=2.0),
    SpherePrimitive(position=Q_Vector3d(x=0, y=8, z=40), ambient=Q_Vector3d(0.1, 0.1, 0), diffuse=Q_Vector3d(0.7, 0.7, 0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=8.0),
    SpherePrimitive(position=Q_Vector3d(x=0, y=-1000, z=15), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=990.0),  # Bottom plane
]

lights = [
    {'position': Q_Vector3d(0, 10, 5), 'color': Q_Vector3d(1, 1, 1)}
]

scene = Scene(objects=objects, lights=lights)

os.system('cls')
print()

scene.render(camera_position=CAMERA, width=WIDTH, height=HEIGHT, max_depth=MAX_DEPTH)

# Test
# ray_origin = np.array([0, 0, 0])
# vOrigin = Q_Vector3D(x=0, y=0, z=0)
# radius = 1.0
# for x in range(5):
#     for y in range(-3, 6):
#         for z in range(2, 8):
#             center = np.array([x, y, z])
#             vCenter = Q_Vector3D(x=x, y=y, z=z)
#             if np.linalg.norm(ray_origin - center) != (vOrigin - vCenter).length:
#                 print(np.linalg.norm(ray_origin - center), (vOrigin - vCenter).length, np.linalg.norm(ray_origin - center) == (vOrigin - vCenter).length)
