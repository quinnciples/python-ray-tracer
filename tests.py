import sys
from QFunctions.Q_Functions import Q_Vector3d


def test_Q_Vector3d_constructor():
    vector = Q_Vector3d(0, 1, 2)
    assert vector.x == 0
    assert vector.y == 1
    assert vector.z == 2


def test_Q_Vector3d_eq_operator():
    vector1 = Q_Vector3d(1, 2, 3)
    vector2 = Q_Vector3d(1, 2, 3)
    assert vector1 == vector2


def test_Q_Vector3d_neq_operator():
    vector1 = Q_Vector3d(1, 2, 3)
    vector2 = Q_Vector3d(3, 4, 5)
    assert vector1 != vector2


def test_Q_Vector3d_negation():
    vector1 = Q_Vector3d(1, 2, 3)
    assert vector1 * -1 == Q_Vector3d(-1, -2, -3)
    assert Q_Vector3d.NORM_YAXIS() * -1 == Q_Vector3d(0, -1, 0)
    assert -vector1 == Q_Vector3d(-1, -2, -3)


def test_Q_Vector3d_dot_product():
    vector = Q_Vector3d(0, 1, 0)
    assert vector.dot_product(Q_Vector3d(4, 5, 6)) == 5
    assert Q_Vector3d(1, 2, 3).dot_product(Q_Vector3d(4, 5, 6)) == 1 * 4 + 2 * 5 + 3 * 6


def test_Q_Vector3d_cross_product():
    assert Q_Vector3d.NORM_XAXIS().cross_product(Q_Vector3d.NORM_YAXIS()) == Q_Vector3d.NORM_ZAXIS()
    assert Q_Vector3d(1, 2, 3).cross_product(Q_Vector3d(4, 5, 6)) == Q_Vector3d(-3, 6, -3)


def test_Q_Vector3d__str__():
    assert str(Q_Vector3d(1, 2, 3)) == '{1.0, 2.0, 3.0}'


def test_Q_Vector3d_axes():
    assert Q_Vector3d.NORM_XAXIS() == Q_Vector3d(1, 0, 0)
    assert Q_Vector3d.NORM_YAXIS() == Q_Vector3d(0, 1, 0)
    assert Q_Vector3d.NORM_ZAXIS() == Q_Vector3d(0, 0, 1)


def test_Q_Vector3d_reflected():
    incoming = Q_Vector3d(1, -1, 0)
    surface_normal = Q_Vector3d(0, 1, 0).normalized()
    assert incoming.reflected(surface_normal) == Q_Vector3d(1, 1, 0)


if __name__ == '__main__':
    list_of_tests = [x for x in dir() if 'test_' in x]
    total_tests = 0
    failed_tests = 0
    for test in list_of_tests:
        try:
            print(test, '...', end='')
            total_tests += 1
            globals()[test]()
            print(' PASSED')
            

        except Exception as e:
            failed_tests += 1
            print(' !! FAILED !!')
            print(str(e))

    print()
    print(f'{total_tests} tests run, {total_tests - failed_tests} tests passed, {failed_tests} tests failed.')
