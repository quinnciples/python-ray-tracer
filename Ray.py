from QFunctions.Q_Functions import Q_Vector3d


class Ray:
    def __init__(self, origin: Q_Vector3d, direction: Q_Vector3d):
        self.origin = origin
        self.direction = direction
