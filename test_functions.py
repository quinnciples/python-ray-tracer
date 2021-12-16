import math

import numpy as np

from Hit import Hit
from OrthoNormalBasis import OrthoNormalBasis
from QFunctions.Q_Functions import Q_buckets, Q_Vector3d
from Ray import Ray
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive


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
    vector2 = Q_Vector3d(3, 2, 1)
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
    assert (
        Q_Vector3d.NORM_XAXIS().cross_product(Q_Vector3d.NORM_YAXIS())
        == Q_Vector3d.NORM_ZAXIS()
    )
    assert Q_Vector3d(1, 2, 3).cross_product(Q_Vector3d(4, 5, 6)) == Q_Vector3d(
        -3, 6, -3
    )


def test_Q_Vector3d__str__():
    assert str(Q_Vector3d(1, 2, 3)) == "{1.0, 2.0, 3.0}"


def test_Q_Vector3d_axes():
    assert Q_Vector3d.NORM_XAXIS() == Q_Vector3d(1, 0, 0)
    assert Q_Vector3d.NORM_YAXIS() == Q_Vector3d(0, 1, 0)
    assert Q_Vector3d.NORM_ZAXIS() == Q_Vector3d(0, 0, 1)


def test_Q_Vector3d_reflected():
    incoming = Q_Vector3d(1, -1, 0)
    surface_normal = Q_Vector3d(0, 1, 0).normalized()
    assert incoming.reflected(surface_normal) == Q_Vector3d(1, 1, 0)


def test_Q_Vector3d_matches_numpy():
    np_origin = np.array([0, 0, 0])
    Q_origin = Q_Vector3d(x=0, y=0, z=0)
    for x in range(-5, 5):
        for y in range(-3, 6):
            for z in range(2, 8):
                np_center = np.array([-x, y, z])
                Q_center = Q_Vector3d(x=-x, y=y, z=z)
                assert (
                    np.linalg.norm(np_origin - np_center)
                    == (Q_origin - Q_center).length
                    and np.linalg.norm(np_origin - np_center) > 0
                    and (Q_origin - Q_center).length > 0
                )


def test_OrthoNormalBasis_constructor():
    onb = OrthoNormalBasis(
        x=Q_Vector3d.NORM_XAXIS(), y=Q_Vector3d.NORM_YAXIS(), z=Q_Vector3d.NORM_ZAXIS()
    )
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_fromXY():
    onb = OrthoNormalBasis.fromXY(x=Q_Vector3d.NORM_XAXIS(), y=Q_Vector3d.NORM_YAXIS())
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_fromYX():
    onb = OrthoNormalBasis.fromXY(y=Q_Vector3d.NORM_YAXIS(), x=Q_Vector3d.NORM_XAXIS())
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_fromXZ():
    onb = OrthoNormalBasis.fromXZ(x=Q_Vector3d.NORM_XAXIS(), z=Q_Vector3d.NORM_ZAXIS())
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_fromZX():
    onb = OrthoNormalBasis.fromZX(z=Q_Vector3d.NORM_ZAXIS(), x=Q_Vector3d.NORM_XAXIS())
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_fromYZ():
    onb = OrthoNormalBasis.fromYZ(y=Q_Vector3d.NORM_YAXIS(), z=Q_Vector3d.NORM_ZAXIS())
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_fromZY():
    onb = OrthoNormalBasis.fromZY(z=Q_Vector3d.NORM_ZAXIS(), y=Q_Vector3d.NORM_YAXIS())
    assert onb.x == Q_Vector3d.NORM_XAXIS()
    assert onb.y == Q_Vector3d.NORM_YAXIS()
    assert onb.z == Q_Vector3d.NORM_ZAXIS()


def test_OrthoNormalBasis_from_single_axes():
    def check_is_basis(onb: OrthoNormalBasis):
        THRESHOLD = 0.0000001
        assert math.fabs(onb.x.dot_product(onb.y)) <= THRESHOLD
        assert math.fabs(onb.x.dot_product(onb.z)) <= THRESHOLD
        assert math.fabs(onb.y.dot_product(onb.z)) <= THRESHOLD

    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.NORM_XAXIS()))  # Z100
    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.NORM_YAXIS()))  # Z010
    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.NORM_ZAXIS()))  # Z001
    check_is_basis(
        onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=0, y=0, z=2))
    )  # Z002
    check_is_basis(
        onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=-1, y=0, z=0))
    )  # Zn00
    check_is_basis(
        onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=0, y=-1, z=0))
    )  # Z0n0
    check_is_basis(
        onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=0, y=0, z=-1))
    )  # Z00n
    check_is_basis(
        onb=OrthoNormalBasis.fromZ(
            Q_Vector3d.get_normalized_vector(x=-0.211944, y=-0.495198, z=0.842530)
        )
    )  # Zrnd


def test_Q_buckets_function():
    for number_of_items in range(2, 251, 6):
        for number_of_buckets in range(2, number_of_items + 1):
            buckets = [
                _
                for _ in Q_buckets(
                    number_of_items=number_of_items, number_of_buckets=number_of_buckets
                )
            ]
            assert buckets[0][0] == 0
            assert len(buckets) == number_of_buckets
            last_end_point = buckets[0][1]
            for bucket in buckets[1:]:
                assert last_end_point == bucket[0]
                last_end_point = bucket[1]
            assert last_end_point == number_of_items


def test_Ray_constructor():
    r0 = Ray.from_two_vectors(
        first_vector=Q_Vector3d(1, 2, 3), second_vector=Q_Vector3d(2, 2, 3)
    )
    assert r0.direction == Q_Vector3d.NORM_XAXIS()
    assert r0.origin == Q_Vector3d(1, 2, 3)

    r1 = Ray.from_two_vectors(
        first_vector=Q_Vector3d(1, 2, 3), second_vector=Q_Vector3d(4, 5, 6)
    )
    assert r1.direction == (Q_Vector3d(4, 5, 6) - Q_Vector3d(1, 2, 3)).normalized()
    assert r1.origin == Q_Vector3d(1, 2, 3)

    r3 = Ray.from_two_vectors(Q_Vector3d(10, 10, 10), Q_Vector3d(10, 10, 60))
    assert r3.origin + r3.direction * 0 == Q_Vector3d(10, 10, 10)
    assert r3.origin + r3.direction * 50 == Q_Vector3d(10, 10, 60)


def test_SpherePrimitive_constructor():
    s = SpherePrimitive(
        position=Q_Vector3d(10, 20, 30),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
        radius=15,
    )
    assert s.position == Q_Vector3d(10, 20, 30)
    assert s.radius == 15


def test_SpherePrimitive_intersects():
    THRESHOLD = 0.00001
    s = SpherePrimitive(
        position=Q_Vector3d(10, 20, 30),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
        radius=15,
    )
    hit = s.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 1, 0))
    )
    assert hit is None
    hit = s.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(-10, -20, -30))
    )
    assert hit is None
    hit = s.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(10, 20, 30))
    )
    assert (
        hit is not None
        and hit.distance is not None
        and hit.normal_to_surface is not None
    )
    # 22.416738
    assert math.fabs(22.41657 - hit.distance) < THRESHOLD
    assert (
        Q_Vector3d(-0.267261, -0.534522, -0.801784) - hit.normal_to_surface
    ).length < THRESHOLD
    # CHECK(!hit.inside);


def test_SpherePrimitive_intersection():
    THRESHOLD = 0.00001
    s = SpherePrimitive(
        position=Q_Vector3d(0, 0, 30),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
        radius=10,
    )
    hit = s.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 2))
    )
    assert hit is not None and hit.normal_to_surface is not None
    assert math.fabs(hit.distance - 20.0) < THRESHOLD
    hit.normal_to_surface.x == 0
    hit.normal_to_surface.y == 0
    hit.normal_to_surface.z == -1
    ray = Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 2))
    position = ray.origin + ray.direction * hit.distance
    assert position.x == 0
    assert position.y == 0
    assert math.fabs(position.z - 20.0) < THRESHOLD
    # CHECK(!hit.inside);


def test_SpherePrimitive_intersection_inside():
    THRESHOLD = 0.00001
    s = SpherePrimitive(
        position=Q_Vector3d(0, 0, 30),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
        radius=10,
    )
    hit = s.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 30), Q_Vector3d(0, 0, 2))
    )
    assert hit is not None and hit.normal_to_surface is not None
    assert math.fabs(hit.distance - 10) < THRESHOLD
    hit.normal_to_surface.x == 0
    hit.normal_to_surface.y == 0
    hit.normal_to_surface.z == 1
    ray = Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 2))
    position = ray.origin + ray.direction * hit.distance
    assert position.x == 0
    assert position.y == 0
    assert math.fabs(position.z - 10.0) < THRESHOLD
    # CHECK(hit.inside)


def test_TrianglePrimitive_constructor():
    t = TrianglePrimitive(
        (Q_Vector3d(1, 2, 3), Q_Vector3d(2, 3, 4), Q_Vector3d(4, 5, 6)),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
    )
    assert t.vertex(0) == Q_Vector3d(1, 2, 3)
    assert t.vertex(1) == Q_Vector3d(2, 3, 4)
    assert t.vertex(2) == Q_Vector3d(4, 5, 6)


def test_TrianglePrimitive_intersects_clockwise():
    THRESHOLD = 0.00001
    t = TrianglePrimitive(
        (Q_Vector3d(0, 0, 3), Q_Vector3d(0, 1, 3), Q_Vector3d(1, 1, 3)),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
    )
    hit = t.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 1, 0))
    )
    assert hit is None
    hit = t.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, -1))
    )
    assert hit is None
    hit = t.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 1))
    )
    assert hit is not None and hit.normal_to_surface is not None
    assert math.fabs(hit.distance - 3.0) < THRESHOLD
    ray = Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 1))
    position = ray.origin + ray.direction * hit.distance
    assert position.x == 0.0
    assert position.y == 0.0
    assert position.z == 3.0
    assert hit.normal_to_surface == Q_Vector3d(0, 0, -1)


def test_TrianglePrimitive_intersects_counter_clockwise():
    THRESHOLD = 0.00001
    t = TrianglePrimitive(
        (Q_Vector3d(0, 0, 3), Q_Vector3d(1, 1, 3), Q_Vector3d(0, 1, 3)),
        ambient=Q_Vector3d(0, 0, 0),
        diffuse=Q_Vector3d(0, 0, 0),
        specular=Q_Vector3d(0, 0, 0),
        shininess=0,
        reflection=0,
    )
    hit = t.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 1, 0))
    )
    assert hit is None
    hit = t.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, -1))
    )
    assert hit is None
    hit = t.intersect(
        ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 1))
    )
    assert hit is not None and hit.normal_to_surface is not None
    assert math.fabs(hit.distance - 3.0) < THRESHOLD
    ray = Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 1))
    position = ray.origin + ray.direction * hit.distance
    assert position.x == 0.0
    assert position.y == 0.0
    assert position.z == 3.0
    assert hit.normal_to_surface == Q_Vector3d(0, 0, -1)


def test_Scene_constructor():
    s = Scene(
        objects=[
            SpherePrimitive(
                position=Q_Vector3d(0, 0, 0),
                radius=10,
                ambient=Q_Vector3d(0, 0, 0),
                diffuse=Q_Vector3d(0, 0, 0),
                specular=Q_Vector3d(0, 0, 0),
                shininess=0,
                reflection=0,
            )
        ]
    )


def test_Scene_nearest_intersection_with_one_object():
    s = Scene(
        objects=[
            SpherePrimitive(
                position=Q_Vector3d(0, 0, 50),
                radius=10,
                ambient=Q_Vector3d(0, 0, 0),
                diffuse=Q_Vector3d(0, 0, 0),
                specular=Q_Vector3d(0, 0, 0),
                shininess=0,
                reflection=0,
            )
        ]
    )
    # Test no intersection occurs
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 1, 0))
    nearest_object, distance, normal_to_surface = s.nearest_intersection(ray=ray)
    assert nearest_object is None and normal_to_surface is None
    # Test intersection does occur
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 0, 1))
    nearest_object, distance, normal_to_surface = s.nearest_intersection(ray=ray)
    assert (
        nearest_object is not None and normal_to_surface is not None and distance == 40
    )


def test_Scene_nearest_intersection_with_two_object():
    s2 = Scene(
        objects=[
            SpherePrimitive(
                position=Q_Vector3d(0, 0, 50),
                radius=10,
                ambient=Q_Vector3d(0, 0, 0),
                diffuse=Q_Vector3d(0, 0, 0),
                specular=Q_Vector3d(0, 0, 0),
                shininess=0,
                reflection=0,
            ),
            SpherePrimitive(
                position=Q_Vector3d(0, 0, 100),
                radius=10,
                ambient=Q_Vector3d(0, 0, 0),
                diffuse=Q_Vector3d(0, 0, 0),
                specular=Q_Vector3d(0, 0, 0),
                shininess=0,
                reflection=0,
            ),
        ]
    )
    # Test no intersection occurs
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 1, 0))
    nearest_object, distance, normal_to_surface = s2.nearest_intersection(ray=ray)
    assert nearest_object is None and normal_to_surface is None
    # Test intersection does occur
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 0, 1))
    nearest_object, distance, normal_to_surface = s2.nearest_intersection(ray=ray)
    assert (
        nearest_object is not None and normal_to_surface is not None and distance == 40
    )


if __name__ == "__main__":
    list_of_tests = [x for x in dir() if "test_" in x]
    total_tests = 0
    failed_tests = 0
    for test in list_of_tests:
        try:
            print(test, "...", end="")
            total_tests += 1
            globals()[test]()
            print(" PASSED")

        except Exception as e:
            failed_tests += 1
            print(" !! FAILED !!")
            print(str(e))

    print()
    print(
        f"{total_tests} tests run, {total_tests - failed_tests} tests passed, {failed_tests} tests failed."
    )
    print()
