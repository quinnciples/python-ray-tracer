from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Hit import Hit
import random
import math


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

    def handle_ray_intersection(self, incoming_ray: Ray, object_hit: Hit) -> tuple[Q_Vector3d, Ray]:
        def refract(vector: Q_Vector3d, normal: Q_Vector3d, ni_over_nt: float) -> Q_Vector3d:
            uv = vector.normalized()
            dt = uv.dot_product(other_vector=normal)
            discriminant = 1.0 - ni_over_nt * ni_over_nt * (1 - dt * dt)
            if discriminant > 0:
                return ni_over_nt * (uv - normal * dt) - normal * math.sqrt(discriminant)
            return None

        reflect_direction = incoming_ray.direction.reflected(other_vector=object_hit.normal_to_surface)

        if incoming_ray.direction.dot_product(other_vector=object_hit.normal_to_surface) > 0:
            outward_normal = object_hit.normal_to_surface * -1
            ni_over_nt = self.refraction_index
        else:
            outward_normal = object_hit.normal_to_surface
            ni_over_nt = 1.0 / self.refraction_index

        refract_direction = refract(vector=incoming_ray.direction, normal=outward_normal, ni_over_nt=ni_over_nt)
        if refract_direction is not None:
            refracted_ray = Ray(origin=object_hit.position, direction=refract_direction.normalized())
            return (self.attenuation, refracted_ray)
        else:
            reflected_ray = Ray(origin=object_hit.position, direction=reflect_direction.normalized())
            return (self.attenuation, reflected_ray)
