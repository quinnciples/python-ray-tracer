from Hit import Hit
from Material import Diffuse, Material, Metal
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from AABB import AABB


class Primitive():
    def __init__(self, position: Q_Vector3d, material: Material):
        self.position = position
        self.material = material

    def intersect(self, ray: Ray) -> Hit:
        raise('Intersect function not implemented')

    def intersects_with_bounding_box(self, box: AABB) -> bool:
        raise Exception('Bounding box intersection function not implemented')
