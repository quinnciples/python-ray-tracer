import math

from AABB import AABB
from Hit import Hit
from Material import Material
from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from TrianglePrimitive import TrianglePrimitive


class CubePrimitive(Primitive):
    """
               _________X rear_top_right (x2, y2, z2)
              /        /|
             /        / |
            /________/  |
            |\       |  |
            |  \     | /
            |     \  |/
            X_______\/
    front_bottom_left
    (x1, y1, z1)
    """
    def __init__(self, front_bottom_left: Q_Vector3d, rear_top_right: Q_Vector3d, material: Material):
        Primitive.__init__(self, position=(rear_top_right + front_bottom_left) * (1 / 2), material=material)
        front = Q_Vector3d(0, 0, front_bottom_left.z)
        bottom = Q_Vector3d(0, front_bottom_left.y, 0)
        left = Q_Vector3d(front_bottom_left.x, 0, 0)
        rear = Q_Vector3d(0, 0, rear_top_right.z)
        top = Q_Vector3d(0, rear_top_right.y, 0)
        right = Q_Vector3d(rear_top_right.x, 0, 0)

        self.faces = (
            # front face
            TrianglePrimitive((front_bottom_left, front + top + left, front + top + right), material=material),
            TrianglePrimitive((front_bottom_left, front + bottom + right, front + top + right), material=material),

            # top face
            TrianglePrimitive((front + top + left, rear + top + left, rear_top_right), material=material),
            TrianglePrimitive((front + top + left, front + top + right, rear_top_right), material=material),

            # bottom face
            TrianglePrimitive((front_bottom_left, front + bottom + right, rear + bottom + right), material=material),
            TrianglePrimitive((front_bottom_left, rear + bottom + left, rear + bottom + right), material=material),

            # rear face
            TrianglePrimitive((rear + top + left, rear_top_right, rear + bottom + right), material=material),
            TrianglePrimitive((rear + top + left, rear + bottom + left, rear + bottom + right), material=material),

            # left face
            TrianglePrimitive((front_bottom_left, rear + bottom + left, rear + top + left), material=material),
            TrianglePrimitive((front_bottom_left, front + top + left, rear + top + left), material=material),

            # right face
            TrianglePrimitive((front + top + right, rear_top_right, rear + bottom + right), material=material),
            TrianglePrimitive((front + top + right, front + bottom + right, rear + bottom + right), material=material),
        )

    def intersect(self, ray: Ray) -> Hit:
        # Call interct for all triangles in all faces
        # Track objects and distances that have collissions
        # Determine closest triangle
        # Return this distance and that normal's triangle
        num_intersections = 0
        min_distance = math.inf
        normal_to_surface = None
        for triangle in self.faces:
            hit = triangle.intersect(ray=ray)
            if hit:
                num_intersections += 1
            if hit and hit.distance < min_distance:
                min_distance = hit.distance
                normal_to_surface = hit.normal_to_surface
            if num_intersections > 1:
                break
        return Hit(distance=min_distance, normal_to_surface=normal_to_surface, is_inside=False)  # Need to update is_inside check

    def intersects_with_bounding_box(self, box: AABB) -> bool:
        return any(triangle.intersects_with_bounding_box(box=box) for triangle in self.faces)
