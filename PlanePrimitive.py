import math

from Hit import Hit
from Material import Material
from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from TrianglePrimitive import TrianglePrimitive
from AABB import AABB


class PlanePrimitive(Primitive):
    """
               _________X rear_top_right (x2, y2, z2)
              /        /
             /        /
            X________/
    front_bottom_left
    (x1, y1, z1)
    """
    def __init__(self, front_bottom_left: Q_Vector3d, rear_top_right: Q_Vector3d, material: Material):
        Primitive.__init__(self, position=(front_bottom_left + rear_top_right) * (1 / 2), material=material)
        front = Q_Vector3d(0, 0, front_bottom_left.z)
        bottom = Q_Vector3d(0, front_bottom_left.y, 0)
        left = Q_Vector3d(front_bottom_left.x, 0, 0)
        rear = Q_Vector3d(0, 0, rear_top_right.z)
        top = Q_Vector3d(0, rear_top_right.y, 0)
        right = Q_Vector3d(rear_top_right.x, 0, 0)

        self.faces = (
            TrianglePrimitive((front + bottom + left, rear + top + left, rear_top_right), material=material),
            TrianglePrimitive((front + bottom + left, front + bottom + right, rear_top_right), material=material)
        )

    def intersect(self, ray: Ray) -> Hit:
        # Call interct for all triangles in all faces
        # Track objects and distances that have collissions
        # Determine closest triangle
        # Return this distance and that triangle's normal
        # In theory, this should only have one intersection, but it's
        # possible the vector could be along the plane...
        min_distance = math.inf
        normal_to_surface = None
        for triangle in self.faces:
            # this_distance, this_normal_to_surface = triangle.intersect(ray=ray)
            hit = triangle.intersect(ray=ray)
            if hit and hit.distance < min_distance:
                min_distance = hit.distance
                normal_to_surface = hit.normal_to_surface
        # return (min_distance, normal_to_surface)
        return Hit(position=ray.position_at_distance(min_distance), distance=min_distance, normal_to_surface=normal_to_surface, is_inside=False)

    def intersects_with_bounding_box(self, box: AABB) -> bool:
        return any(triangle.intersects_with_bounding_box(box=box) for triangle in self.faces)
