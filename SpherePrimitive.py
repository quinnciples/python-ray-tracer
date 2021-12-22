import math

from Hit import Hit
from Material import Diffuse, Material, Metal
from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray


class SpherePrimitive(Primitive):
    """
    Use this as a test:
    c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2
    c = ((ray.origin - self.center).length ** 2) - (self.radius ** 2)
    """

    EPSILON = 1e-5  # 0.000000001

    def __init__(self, position: Q_Vector3d, material: Material, radius: float):
        # self.center = center
        Primitive.__init__(self, position=position, material=material)
        self.radius = float(radius)

    def intersect(self, ray: Ray) -> Hit:
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
            # return None, None
            return None

        determinant = math.sqrt(determinant)
        minusT = b - determinant
        plusT = b + determinant
        if (minusT < SpherePrimitive.EPSILON and plusT < SpherePrimitive.EPSILON):
            # return None, None
            return None

        t = minusT if minusT > SpherePrimitive.EPSILON else plusT
        hitPosition = ray.origin + (ray.direction * t)
        normal = (hitPosition - self.position).normalized()
        inside = normal.dot_product(ray.direction) > 0

        # It is necessary to comment out the normal flipping code
        # below due to how the material code works for refraction!
        # if inside:
        #     normal = normal * -1

        return Hit(position=ray.position_at_distance(t), distance=t, normal_to_surface=normal, is_inside=inside)
