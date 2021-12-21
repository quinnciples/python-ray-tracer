from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Hit import Hit
import random

class Material:
    def __init__(self, attenuation: Q_Vector3d):
        self.attenuation = attenuation

    def handle_ray_intersection(self) -> tuple[Q_Vector3d, Ray]:
        raise "Not implemented"


class Diffuse(Material):
    def __init__(self, attenuation: Q_Vector3d):
        Material.__init__(self, attenuation=attenuation)

    def handle_ray_intersection(self, incoming_ray: Ray, object_hit: Hit) -> tuple[Q_Vector3d, Ray]:
        def random_in_unit_sphere() -> Q_Vector3d:
            p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
            while p.length_squared >= 1.0:
                p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
            return p

        target = object_hit.position + object_hit.normal_to_surface + random_in_unit_sphere()
        reflected_ray = Ray(origin=object_hit.position + (object_hit.normal_to_surface * 0.0001), direction=(target - object_hit.position).normalized())
        color_value = self.attenuation
        return (color_value, reflected_ray)


class Metal(Material):
    def __init__(self, attenuation: Q_Vector3d, fuzziness: float = 0):
        Material.__init__(self, attenuation=attenuation)
        self.fuzziness = fuzziness

    def handle_ray_intersection(self, incoming_ray: Ray, object_hit: Hit) -> tuple[Q_Vector3d, Ray]:
        def random_in_unit_sphere() -> Q_Vector3d:
            p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
            while p.length_squared >= 1.0:
                p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
            return p
        direction = incoming_ray.direction.normalized().reflected(other_vector=object_hit.normal_to_surface)
        if self.fuzziness > 0.0:
            reflected_ray = Ray(origin=object_hit.position, direction=direction.normalized() + random_in_unit_sphere() * self.fuzziness)
        else:
            reflected_ray = Ray(origin=object_hit.position, direction=direction.normalized())
        color_value = self.attenuation
        if reflected_ray.direction.dot_product(other_vector=object_hit.normal_to_surface) > 0:
            return (color_value, reflected_ray)
        else:
            return (None, None)


class Glass(Material):
    def __init__(self, refreaction_index: float):
        Material.__init__(self, attenuation=Q_Vector3d(1.0, 1.0, 1.0))
        self.refraction_index = refreaction_index
