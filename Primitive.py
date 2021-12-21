from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from Hit import Hit


class Primitive():
    def __init__(self, position: Q_Vector3d, ambient: Q_Vector3d, diffuse: Q_Vector3d, specular: Q_Vector3d, shininess: float, reflection: float, emission: Q_Vector3d = Q_Vector3d(0, 0, 0)):
        assert 0 <= shininess <= 100.0
        assert 0 <= reflection <= 1.0
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection
        self.emission = emission

    def intersect(self, ray: Ray) -> Hit:
        raise('Intersect function not implemented')
