import math

from Hit import Hit
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
    def __init__(self, front_bottom_left: Q_Vector3d, rear_top_right: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float, emission: Q_Vector3d = Q_Vector3d(0, 0, 0)):
        Primitive.__init__(self, position=(rear_top_right + front_bottom_left) * (1 / 2), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission)
        front = Q_Vector3d(0, 0, front_bottom_left.z)
        bottom = Q_Vector3d(0, front_bottom_left.y, 0)
        left = Q_Vector3d(front_bottom_left.x, 0, 0)
        rear = Q_Vector3d(0, 0, rear_top_right.z)
        top = Q_Vector3d(0, rear_top_right.y, 0)
        right = Q_Vector3d(rear_top_right.x, 0, 0)

        self.faces = (
            # front face
            TrianglePrimitive((front_bottom_left, front + top + left, front + top + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            TrianglePrimitive((front_bottom_left, front + bottom + right, front + top + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            # top face

            TrianglePrimitive((front + top + left, rear + top + left, rear_top_right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            TrianglePrimitive((front + top + left, front + top + right, rear_top_right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),

            # bottom face
            TrianglePrimitive((front_bottom_left, front + bottom + right, rear + bottom + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            TrianglePrimitive((front_bottom_left, rear + bottom + left, rear + bottom + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),

            # rear face
            TrianglePrimitive((rear + top + left, rear_top_right, rear + bottom + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            TrianglePrimitive((rear + top + left, rear + bottom + left, rear + bottom + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),

            # left face
            TrianglePrimitive((front_bottom_left, rear + bottom + left, rear + top + left), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            TrianglePrimitive((front_bottom_left, front + top + left, rear + top + left), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),

            # right face
            TrianglePrimitive((front + top + right, rear_top_right, rear + bottom + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission),
            TrianglePrimitive((front + top + right, front + bottom + right, rear + bottom + right), ambient=ambient, diffuse=diffuse, specular=specular, shininess=shininess, reflection=reflection, emission=emission)
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
