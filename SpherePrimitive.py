from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
import math
from Primitive import Primitive

class SpherePrimitive(Primitive):
    """
    Use this as a test:
    c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2
    c = ((ray.origin - self.center).length ** 2) - (self.radius ** 2)
    """

    EPSILON = 1e-5  # 0.000000001

    def __init__(self, position: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float, radius: float, emission: Q_Vector3d = Q_Vector3d(0, 0, 0)):
        # self.center = center
        Primitive.__init__(self, position=position, ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission)
        self.radius = float(radius)

    def intersect(self, ray: Ray) -> tuple[float, Q_Vector3d]:
        b = 2 * ray.direction.dot_product(other_vector=(ray.origin - self.position))
        # c = ((ray.origin - self.position).length_squared) - (self.radius ** 2)

        # Test
        # ray_origin = np.array([ray.origin.x, ray.origin.y, ray.origin.z])
        # center = np.array([self.center.x, self.center.y, self.center.z])
        # radius = self.radius
        # c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2

        # delta = b ** 2 - 4 * c
        # if delta > 0:
        #     t1 = (-b + math.sqrt(delta)) / 2
        #     t2 = (-b - math.sqrt(delta)) / 2
        #     print(b, c, delta, t1, t2)
        #     if t1 > 0 and t2 > 0:
        #         distance = min(t1, t2)
        #         intersection_point = ray.origin + ray.direction * distance
        #         normal_to_surface = (intersection_point - self.position).normalized()  # What if we're inside the sphere?
        #         return distance, normal_to_surface

        op = self.position - ray.origin
        radiusSquared = self.radius ** 2
        b = op.dot_product(ray.direction)
        determinant = b * b - (op.length_squared) + radiusSquared
        if (determinant < 0):
            return None, None

        determinant = math.sqrt(determinant)
        minusT = b - determinant
        plusT = b + determinant
        if (minusT < SpherePrimitive.EPSILON and plusT < SpherePrimitive.EPSILON):
            return None, None

        t = minusT if minusT > SpherePrimitive.EPSILON else plusT
        hitPosition = ray.origin + (ray.direction * t)
        normal = (hitPosition - self.position).normalized()
        inside = normal.dot_product(ray.direction) > 0
        if inside:
            normal = normal * -1
        return t, normal
