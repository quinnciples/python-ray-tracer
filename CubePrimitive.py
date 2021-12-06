from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Primitive import Primitive
from TrianglePrimitive import TrianglePrimitive
import math


class CubePrimitive(Primitive):
    """
               _________X rear_top_right (x2, y2, z2)
              /        /|
             /        / |
            /________/  |
            |   |   |   |
            |   |   |  /
            |   |   | /
            X--------/
    front_bottom_left
    (x1, y1, z1) 
    """
    def __init__(self, front_bottom_left: Q_Vector3d, rear_top_right: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float):
        Primitive.__init__(self, position=(rear_top_right + front_bottom_left) * (1 / 2), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection)
        front = Q_Vector3d(0, 0, front_bottom_left.z)
        bottom = Q_Vector3d(0, front_bottom_left.y, 0)
        left = Q_Vector3d(front_bottom_left.x, 0, 0)
        rear = Q_Vector3d(0, 0, rear_top_right.z)
        top = Q_Vector3d(0, rear_top_right.y, 0)
        right = Q_Vector3d(rear_top_right.x, 0, 0)

        self.faces = (
            # front face
            TrianglePrimitive((front_bottom_left, front + top + left, front + top + right)),
            TrianglePrimitive((front_bottom_left, front + bottom + right, front + top + right)),
            # top face

            TrianglePrimitive((front + top + left, rear + top + left, rear_top_right)),
            TrianglePrimitive((front + top + left, front + top + right, rear_top_right)),

            # bottom face
            TrianglePrimitive((front_bottom_left, front + bottom + right, rear + bottom + right)),
            TrianglePrimitive((front_bottom_left, rear + bottom + left, rear + bottom + right)),

            # rear face
            TrianglePrimitive((rear + top + left, rear_top_right, rear + bottom + right)),
            TrianglePrimitive((rear + top + left, rear + bottom + left, rear + bottom + right)),

            # left face
            TrianglePrimitive((front_bottom_left, rear + bottom + left, rear + top + left)),
            TrianglePrimitive((front_bottom_left, front + top + left, rear + top + left)),

            # right face
            TrianglePrimitive((front + top + right, rear_top_right, rear + bottom + right)),
            TrianglePrimitive((front + top + right, front + bottom + right, rear + bottom + right))
        )

    def intersect(self, ray: Ray) -> tuple[float, Q_Vector3d]:
        # Call interct for all triangles in all faces
        # Track objects and distances that have collissions
        # Determine closest triangle
        # Return this distance and that normal's triangle
        min_distance = math.inf
        normal_to_surface = None
        for triangle in self.faces:
            this_distance, this_normal_to_surface = triangle.intersect(ray=ray)
            if this_distance and this_distance < min_distance:
                min_distance = this_distance
                normal_to_surface = this_normal_to_surface
        return (min_distance, normal_to_surface)
