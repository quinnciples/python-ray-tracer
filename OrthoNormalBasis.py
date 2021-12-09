from QFunctions.Q_Functions import Q_Vector3d
import math


class OrthoNormalBasis:
    COINCIDENT = 0.9999
    EPSILON = EPSILON = 0.000000001

    def __init__(self, x: Q_Vector3d, y: Q_Vector3d, z: Q_Vector3d):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def fromXY(x: Q_Vector3d, y: Q_Vector3d):
        zz = x.cross_product(y).normalized()
        yy = Q_Vector3d.from_normal(zz.cross_product(x))
        return OrthoNormalBasis(x, yy, zz)

    @staticmethod
    def fromYX(y: Q_Vector3d, x: Q_Vector3d):
        zz = x.cross_product(y).normalized()
        xx = Q_Vector3d.from_normal(y.cross_product(zz))
        return OrthoNormalBasis(xx, y, zz)

    @staticmethod
    def fromXZ(x: Q_Vector3d, z: Q_Vector3d):
        yy = z.cross_product(x).normalized()
        zz = Q_Vector3d.from_normal(x.cross_product(yy))
        return OrthoNormalBasis(x, yy, zz)

    @staticmethod
    def fromZX(z: Q_Vector3d, x: Q_Vector3d):
        yy = z.cross_product(x).normalized()
        xx = Q_Vector3d.from_normal(yy.cross_product(z))
        return OrthoNormalBasis(xx, yy, z)

    @staticmethod
    def fromYZ(y: Q_Vector3d, z: Q_Vector3d):
        xx = y.cross_product(z).normalized()
        zz = Q_Vector3d.from_normal(xx.cross_product(y))
        return OrthoNormalBasis(xx, y, zz)

    @staticmethod
    def fromZY(z: Q_Vector3d, y: Q_Vector3d):
        xx = y.cross_product(z).normalized()
        yy = Q_Vector3d.from_normal(z.cross_product(xx))
        return OrthoNormalBasis(xx, yy, z)

    @staticmethod
    def fromZ(z_vector: Q_Vector3d):
        if math.fabs(z_vector.dot_product(Q_Vector3d.NORM_XAXIS())) > OrthoNormalBasis.COINCIDENT:
            xx = Q_Vector3d.NORM_YAXIS().cross_product(z_vector).normalized()
        else:
            xx = Q_Vector3d.NORM_XAXIS().cross_product(z_vector).normalized()
        yy = z_vector.cross_product(xx).normalized()
        return OrthoNormalBasis(xx, yy, z_vector)

    def transform(self, other_vector: Q_Vector3d):
        return self.x * other_vector.x + self.y * other_vector.y + self.z * other_vector.z

    @staticmethod
    def cone_sample(direction: Q_Vector3d, cone_theta: float, u: float, v: float) -> Q_Vector3d:
        if cone_theta < OrthoNormalBasis.EPSILON:
            return direction

        cone_theta = cone_theta * (1.0 - (2.0 * math.acos(u) / math.pi))
        radius = math.sin(cone_theta)
        z_scale = math.cos(cone_theta)
        random_theta = v * 2 * math.pi
        basis = OrthoNormalBasis.fromZ(direction)
        return basis.transform(Q_Vector3d(math.cos(random_theta) * radius, math.sin(random_theta) * radius, z_scale)).normalized()


if __name__ == '__main__':
    vector = Q_Vector3d(0, 1, 0)
    pi_div = 24.0
    print(f'Starting Vector: {vector}')
    for u_val in range(0, 101, 10):
        cone_theta = math.pi / float(pi_div)
        u = u_val / 100.0
        result_u = OrthoNormalBasis.cone_sample(direction=vector, cone_theta=cone_theta, u=u, v=0.0)
        result_v = OrthoNormalBasis.cone_sample(direction=vector, cone_theta=cone_theta, u=u, v=0.5)
        result_x = OrthoNormalBasis.cone_sample(direction=vector, cone_theta=cone_theta, u=u, v=1.0)
        print(f'v=0: {str(result_u):<70}, v=0.5: {str(result_v):<70}, v=1: {str(result_x):<70}')  #     ......... PI / {pi_div}, {u_val} / 100')
