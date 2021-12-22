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
        """
        The issue lies within the Sphere intersection code - the code I have will negate
        the normal if a collision occurs within the sphere.
        This refraction code was built on a Sphere model that does not do that for internal
        intersections, so perhaps the normals are being flipped somewhere else?
        """
        def refract(vector: Q_Vector3d, normal: Q_Vector3d, ni_over_nt: float) -> Q_Vector3d:
            ray_in = vector.normalized()
            normal = normal.normalized()
            projection_length = -ray_in.dot_product(other_vector=normal)
            discriminant = 1.0 - ni_over_nt ** 2 * (1.0 - projection_length ** 2)
            if discriminant < 0.0:
                return None
            else:
                p = normal * projection_length
                a = ray_in + p
                b = a * ni_over_nt
                pp = normal * (math.sqrt(discriminant) * -1)
                return (pp + b)
                # return (uv + normal * projection_length ) * ni_over_nt - normal * math.sqrt(discriminant)

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

    # def handle_ray_intersection(self, incoming_ray: Ray, object_hit: Hit) -> tuple[Q_Vector3d, Ray]:
    #     def refract(uv: Q_Vector3d, n: Q_Vector3d, etai_over_etat: float) -> Q_Vector3d:
    #         cos_theta = min(-uv.dot_product(n), 1.0)
    #         r_out_perp = etai_over_etat * (uv + cos_theta * n)
    #         r_out_parallel = -math.sqrt(math.fabs(1.0 - r_out_perp.length_squared)) * n
    #         return r_out_perp + r_out_parallel

    #     if incoming_ray.direction.dot_product(object_hit.normal_to_surface) > 0:
    #         refraction_ratio = self.refraction_index
    #     else:
    #         refraction_ratio = 1.0 / self.refraction_index

    #     unit_direction = incoming_ray.direction.normalized()
    #     refracted = refract(unit_direction, object_hit.normal_to_surface, refraction_ratio)
    #     return (self.attenuation, Ray(object_hit.position, refracted))

    # def handle_ray_intersection(self, incoming_ray: Ray, object_hit: Hit) -> tuple[Q_Vector3d, Ray]:
    #     def Reflect(v, n):
    #         return v - n * (2.0*v.dot_product(n))

    #     def Refract(v, n, ni_over_nt) :
    #         uv = v.normalized()
    #         dt = uv.dot_product(n)
    #         discriminant = 1.0 - ni_over_nt*ni_over_nt*(1.0-dt*dt)
    #         if discriminant > 0.0 :
    #             # refracted.Copy((uv-n.Mul(dt)).Mul(ni_over_nt) - n.Mul(math.sqrt(discriminant)))

    #             return ((uv - n * dt)) * (ni_over_nt) - n * (math.sqrt(discriminant))
    #         else :
    #             return None

    #     def Schlick(cosine, refidx):
    #         r0 = (1.0-refidx)/(1.0+refidx)
    #         r0 = r0*r0
    #         return r0+(1.0-r0)*math.pow(1.0-cosine,5.0)

    #     outward_normal = Q_Vector3d(0, 0, 0)		
    #     ni_over_nt = 0.0
    #     attenuation = Q_Vector3d(1.0,1.0,1.0)
    #     reflect_prob = 0.0
    #     cosine = 0.0
    #     unitDirection = incoming_ray.direction.normalized()
    #     if incoming_ray.direction.dot_product(object_hit.normal_to_surface) > 0.0:
    #         outward_normal = object_hit.normal_to_surface * -1.0
    #         ni_over_nt = self.refraction_index
    #         cosine = self.refraction_index * object_hit.normal_to_surface.dot_product(unitDirection)
    #     else:
    #         outward_normal = object_hit.normal_to_surface * 1.0
    #         ni_over_nt = 1.0/self.refraction_index
    #         cosine = -object_hit.normal_to_surface.dot_product(unitDirection)

    #     reflected = Reflect(incoming_ray.direction, object_hit.normal_to_surface)
    #     refracted = Refract(incoming_ray.direction, outward_normal, ni_over_nt)
    #     if refracted is not None:
    #         reflect_prob = Schlick(cosine, self.refraction_index)
    #     else:
    #         reflect_prob = 1.0

    #     # scatteredRay.Origin.Copy(hitRecord.Point)
    #     if random.random()<reflect_prob:
    #         scatteredRay = Ray(object_hit.position, reflected)
    #     else:
    #         scatteredRay = Ray(object_hit.position, refracted)

    #     return (Q_Vector3d(1.0, 1.0, 1.0), scatteredRay)
