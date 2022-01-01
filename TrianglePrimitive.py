import math

from AABB import AABB
from Hit import Hit
from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Material import Material


class TrianglePrimitive(Primitive):

    EPSILON = 0.000000001

    def __init__(self, vertices: tuple, material: Material):
        self.vertices = vertices
        Primitive.__init__(self, position=self._position, material=material)
        self.position = self._position
        self.radius = max((self.vertices[0] - self._position).length, (self.vertices[1] - self._position).length, (self.vertices[2] - self._position).length)

    @staticmethod
    def from_vertices(vertex_1: Q_Vector3d, vertex_2: Q_Vector3d, vertex_3: Q_Vector3d, material: Material):
        return TrianglePrimitive(vertices=(vertex_1, vertex_2, vertex_3), material=material)

    def vertex(self, index: int):
        return self.vertices[index]

    @property
    def u_vector(self) -> Q_Vector3d:
        return self.vertices[1] - self.vertices[0]

    @property
    def v_vector(self) -> Q_Vector3d:
        return self.vertices[2] - self.vertices[0]

    @property
    def face_normal(self) -> Q_Vector3d:
        return self.u_vector.cross_product(self.v_vector).normalized()

    @property
    def _position(self) -> Q_Vector3d:
        return (self.vertices[0] + self.vertices[1] + self.vertices[2]) * (1 / 3)
        # return self.face_normal

    def __repr__(self):
        return f'TrianglePrimitive(vertices={repr(self.vertices)}, material={repr(self.material)})'

    def intersects_with_bounding_box(self, box: AABB) -> bool:
        # Check if any of the triangles vertices are inside the box
        for vertex in self.vertices:
            if (box.min_coordinate.x <= vertex.x <= box.max_coordinate.x) and (box.min_coordinate.y <= vertex.y <= box.max_coordinate.y) and (box.min_coordinate.z <= vertex.z <= box.max_coordinate.z):
                return True
        # Check if a ray fired from any corner of the box to any other corner intersects the triangle
        for starting_corner in box.get_corners():
            for target_corner in box.get_corners():
                if starting_corner == target_corner:
                    continue
                intersection = self.intersect(ray=Ray(origin=starting_corner, direction=(target_corner - starting_corner).normalized()))
                if intersection is not None and intersection.distance < (target_corner - starting_corner).length:
                    return True
        return False

    def intersect(self, ray: Ray) -> Hit:
        # E1 = self.u_vector
        # E2 = self.v_vector
        # N = E1.cross_product(E2)

        # det = -1 * ray.direction.dot_product(other_vector=N)
        # invdet = 1.0 / det

        # A0 = ray.origin - self.vertices[0]
        # DA0 = A0.cross_product(other_vector=ray.direction)

        # u = E2.dot_product(DA0) * invdet
        # v = -1 * E1.dot_product(DA0) * invdet
        # t = A0.dot_product(N) * invdet
        # if (det >= 1e-6 and t >= 0.0 and u >= 0.0 and v >= 0.0 and (u + v) <= 1.0):
        #     return t

        pVec = ray.direction.cross_product(self.v_vector)
        det = self.u_vector.dot_product(pVec)

        # ray and triangle are parallel if det is close to 0
        if (math.fabs(det) < TrianglePrimitive.EPSILON):
            # return None, None
            return None

        backfacing = det < TrianglePrimitive.EPSILON

        invDet = 1.0 / float(det)
        tVec = ray.origin - self.vertices[0]
        u = tVec.dot_product(pVec) * invDet
        qVec = tVec.cross_product(self.u_vector)
        v = ray.direction.dot_product(qVec) * invDet
        if u < 0.0 or u > 1.0 or v < 0.0 or (u + v) > 1.0:
            # return None, None
            return None

        t = self.v_vector.dot_product(qVec) * invDet
        if (t < TrianglePrimitive.EPSILON):
            # return None, None
            return None

        if not backfacing:
            # return t, self.face_normal
            return Hit(position=ray.position_at_distance(t), distance=t, normal_to_surface=self.face_normal, is_inside=False)
        else:
            return Hit(position=ray.position_at_distance(t), distance=t, normal_to_surface=self.face_normal * -1, is_inside=False)
