from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
import math
from Primitive import Primitive


class TrianglePrimitive(Primitive):

    EPSILON = 0.000000001

    def __init__(self, vertices: tuple, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float):
        Primitive.__init__(self, position=Q_Vector3d(0, 0, 0), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection)
        self.vertices = vertices
        self.position = self._position

    @staticmethod
    def from_vertices(vertex_1: Q_Vector3d, vertex_2: Q_Vector3d, vertex_3: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float):
        return TrianglePrimitive(vertices=(vertex_1, vertex_2, vertex_3), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection)

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

    def intersect(self, ray: Ray) -> tuple[float, Q_Vector3d]:
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
            return None, None

        backfacing = det < TrianglePrimitive.EPSILON

        invDet = 1.0 / float(det)
        tVec = ray.origin - self.vertices[0]
        u = tVec.dot_product(pVec) * invDet
        qVec = tVec.cross_product(self.u_vector)
        v = ray.direction.dot_product(qVec) * invDet
        if u < 0.0 or u > 1.0 or v < 0.0 or (u + v) > 1.0:
            return None, None

        t = self.v_vector.dot_product(qVec) * invDet
        if (t < TrianglePrimitive.EPSILON):
            return None, None

        if not backfacing:
            return t, self.face_normal
        else:
            return t, self.face_normal * -1
