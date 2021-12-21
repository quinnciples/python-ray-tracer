from QFunctions.Q_Functions import Q_Vector3d


class Material:
    def __init__(self, color: Q_Vector3d, reflection: float, emission: Q_Vector3d = Q_Vector3d(0, 0, 0)):
        self.color = color
        self.reflection = reflection
        self.emission = emission


class Diffuse(Material):
    def __init__(self, color: Q_Vector3d, reflection: float, emission: Q_Vector3d = Q_Vector3d(0, 0, 0)):
        Material.__init__(self, color=color, reflection=reflection, emission=emission)
