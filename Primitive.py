from Hit import Hit
from Material import Diffuse, Material, Metal
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray


class Primitive():
    def __init__(self, position: Q_Vector3d, material: Material):
        self.position = position
        self.material = material

    def intersect(self, ray: Ray) -> Hit:
        raise('Intersect function not implemented')
