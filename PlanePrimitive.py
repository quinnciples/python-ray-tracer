from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Primitive import Primitive
from TrianglePrimitive import TrianglePrimitive
import math


class PlanePrimitive(Primitive):
    """
               _________X rear_top_right (x2, y2, z2)
              /        /
             /        /
            X________/
    front_bottom_left
    (x1, y1, z1)
    """
    def __init__(self, front_bottom_left: Q_Vector3d, rear_top_right: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float, emission: Q_Vector3d = Q_Vector3d(0, 0, 0)):
        Primitive.__init__(self, position=(rear_top_right + front_bottom_left) * (1 / 2), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission)
        front = Q_Vector3d(0, 0, front_bottom_left.z)
        bottom = Q_Vector3d(0, front_bottom_left.y, 0)
        left = Q_Vector3d(front_bottom_left.x, 0, 0)
        rear = Q_Vector3d(0, 0, rear_top_right.z)
        top = Q_Vector3d(0, rear_top_right.y, 0)
        right = Q_Vector3d(rear_top_right.x, 0, 0)

        self.faces = (
            # top face
            TrianglePrimitive((front + bottom + left, rear + top + left, rear_top_right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection),
            TrianglePrimitive((front + bottom + left, front + bottom + right, rear_top_right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection),
        )

    def intersect(self, ray: Ray) -> tuple[float, Q_Vector3d]:
        # Call interct for all triangles in all faces
        # Track objects and distances that have collissions
        # Determine closest triangle
        # Return this distance and that normal's triangle
        # In theory, this should only have one intersection, but it's
        # possible the vector could be along the plane...
        min_distance = math.inf
        normal_to_surface = None
        for triangle in self.faces:
            this_distance, this_normal_to_surface = triangle.intersect(ray=ray)
            if this_distance and this_distance < min_distance:
                min_distance = this_distance
                normal_to_surface = this_normal_to_surface
        return (min_distance, normal_to_surface)
