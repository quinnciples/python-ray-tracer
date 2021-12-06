from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
import math
from Primitive import Primitive
from TrianglePrimitive import TrianglePrimitive

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
        front = front_bottom_left.z
        bottom = front_bottom_left.y
        left = front_bottom_left.x
        rear = rear_top_right.z
        top = rear_top_right.y
        right = rear_top_right.x

        self.faces = [
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
        TrianglePrimitive((front + top + right, front + bottom + right, rear + bottom + right))]