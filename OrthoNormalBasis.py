from QFunctions.Q_Functions import Q_Vector3d
import math


class OrthoNormalBasis:
    COINCIDENT = 0.9999

    def __init__(self, x: Q_Vector3d, y:Q_Vector3d, z:Q_Vector3d):
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
