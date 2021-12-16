from QFunctions.Q_Functions import Q_Vector3d


class Ray:
    def __init__(self, origin: Q_Vector3d, direction: Q_Vector3d):
        self.origin = origin
        self.direction = direction

    @staticmethod
    def from_two_vectors(first_vector: Q_Vector3d, second_vector: Q_Vector3d):
        return Ray(origin=first_vector, direction=(second_vector - first_vector).normalized())

    @staticmethod
    def from_origin_and_direction(origin: Q_Vector3d, direction: Q_Vector3d):
        return Ray(origin=origin, direction=direction)

    def position_at_distance(self, distance: float) -> Q_Vector3d:
        return self.origin + self.direction * distance
