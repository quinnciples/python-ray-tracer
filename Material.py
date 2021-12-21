from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Hit import Hit


class Material:
    def __init__(self):
        pass

    def handle_ray_intersection(self):
        raise "Not implemented"


class Diffuse(Material):
    def __init__(self, attenuation: Q_Vector3d):
        Material.__init__(self)


class Metal(Material):
    def __init__(self, attenuation: Q_Vector3d):
        Material.__init__(self)
        self.attenuation = attenuation

    def handle_ray_intersection(self, incoming_ray: Ray, object_hit: Hit) -> tuple[Q_Vector3d, Ray]:
        direction = incoming_ray.direction.normalized().reflected(other_vector=object_hit.normal_to_surface)
        reflected_ray = Ray(origin=object_hit.position, direction=direction.normalized())
        color_value = self.attenuation
        if reflected_ray.direction.dot_product(other_vector=object_hit.normal_to_surface) > 0:
            return (color_value, reflected_ray)
        else:
            return (None, None)
