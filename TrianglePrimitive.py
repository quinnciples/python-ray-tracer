import math

from AABB import AABB
from Hit import Hit
from Material import Material
from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray


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
        # https://www.gamedev.net/forums/topic/534655-aabb-triangleplane-intersection--distance-to-plane-is-incorrect-i-have-solved-it/
        # https://gist.github.com/zvonicek/fe73ba9903f49d57314cf7e8e0f05dcf

        triangle = [self.vertices[0], self.vertices[1], self.vertices[2]]
        box_center = (box.max_coordinate + box.min_coordinate) * (1 / 2)
        """
        float e0 = (b.Max.X - b.Min.X) * 0.5f;
        float e1 = (b.Max.Y - b.Min.Y) * 0.5f;
        float e2 = (b.Max.Z - b.Min.Z) * 0.5f;
        """
        box_extents = Q_Vector3d((box.max_coordinate.x - box.min_coordinate.x) * 0.5, (box.max_coordinate.y - box.min_coordinate.y) * 0.5, (box.max_coordinate.z - box.min_coordinate.z) * 0.5)

        # Translate triangle as conceptually moving AABB to origin
        v0 = triangle[0] - box_center
        v1 = triangle[1] - box_center
        v2 = triangle[2] - box_center

        # Compute edge vectors for triangle
        f0 = triangle[1] - triangle[0]
        f1 = triangle[2] - triangle[1]
        f2 = triangle[0] - triangle[2]

        # region Test axes a00..a22 (category 3)

        # Test axis a00
        a00 = Q_Vector3d(0, -f0.z, f0.y)
        p0 = v0.dot_product(a00)
        p1 = v1.dot_product(a00)
        p2 = v2.dot_product(a00)
        r = box_extents.y * abs(f0.z) + box_extents.z * abs(f0.y)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a01
        a01 = Q_Vector3d(0, -f1.z, f1.y)
        p0 = v0.dot_product(a01)
        p1 = v1.dot_product(a01)
        p2 = v2.dot_product(a01)
        r = box_extents.y * abs(f1.z) + box_extents.z * abs(f1.y)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a02
        a02 = Q_Vector3d(0, -f2.z, f2.y)
        p0 = v0.dot_product(a02)
        p1 = v1.dot_product(a02)
        p2 = v2.dot_product(a02)
        r = box_extents.y * abs(f2.z) + box_extents.z * abs(f2.y)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a10
        a10 = Q_Vector3d(f0.z, 0, -f0.x)
        p0 = v0.dot_product(a10)
        p1 = v1.dot_product(a10)
        p2 = v2.dot_product(a10)
        r = box_extents.x * abs(f0.z) + box_extents.z * abs(f0.x)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a11
        a11 = Q_Vector3d(f1.z, 0, -f1.x)
        p0 = v0.dot_product(a11)
        p1 = v1.dot_product(a11)
        p2 = v2.dot_product(a11)
        r = box_extents.x * abs(f1.z) + box_extents.z * abs(f1.x)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a12
        a12 = Q_Vector3d(f2.z, 0, -f2.x)
        p0 = v0.dot_product(a12)
        p1 = v1.dot_product(a12)
        p2 = v2.dot_product(a12)
        r = box_extents.x * abs(f2.z) + box_extents.z * abs(f2.x)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a20
        a20 = Q_Vector3d(-f0.y, f0.x, 0)
        p0 = v0.dot_product(a20)
        p1 = v1.dot_product(a20)
        p2 = v2.dot_product(a20)
        r = box_extents.x * abs(f0.y) + box_extents.y * abs(f0.x)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a21
        a21 = Q_Vector3d(-f1.y, f1.x, 0)
        p0 = v0.dot_product(a21)
        p1 = v1.dot_product(a21)
        p2 = v2.dot_product(a21)
        r = box_extents.x * abs(f1.y) + box_extents.y * abs(f1.x)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # Test axis a22
        a22 = Q_Vector3d(-f2.y, f2.x, 0)
        p0 = v0.dot_product(a22)
        p1 = v1.dot_product(a22)
        p2 = v2.dot_product(a22)
        r = box_extents.x * abs(f2.y) + box_extents.y * abs(f2.x)
        if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
            return False

        # endregion

        # region Test the three axes corresponding to the face normals of AABB b (category 1)

        # Exit if...
        # ... [-extents.X, extents.X] and [min(v0.X,v1.X,v2.X), max(v0.X,v1.X,v2.X)] do not overlap
        if max(v0.x, v1.x, v2.x) < -box_extents.x or min(v0.x, v1.x, v2.x) > box_extents.x:
            return False

        # ... [-extents.Y, extents.Y] and [min(v0.Y,v1.Y,v2.Y), max(v0.Y,v1.Y,v2.Y)] do not overlap
        if max(v0.y, v1.y, v2.y) < -box_extents.y or min(v0.y, v1.y, v2.y) > box_extents.y:
            return False

        # ... [-extents.Z, extents.Z] and [min(v0.Z,v1.Z,v2.Z), max(v0.Z,v1.Z,v2.Z)] do not overlap
        if max(v0.z, v1.z, v2.z) < -box_extents.z or min(v0.z, v1.z, v2.z) > box_extents.z:
            return False

        # endregion

        # region Test separating axis corresponding to triangle face normal (category 2)

        plane_normal = f0.cross_product(f1)
        plane_distance = plane_normal.dot_product(triangle[0])

        # Compute the projection interval radius of b onto L(t) = b.c + t * p.n
        r = box_extents.x * abs(plane_normal.x) + box_extents.y * abs(plane_normal.y) + box_extents.z * abs(plane_normal.z)

        # Intersection occurs when plane distance falls within [-r,+r] interval
        if plane_distance > r:
            return False

        # endregion

        return True

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
