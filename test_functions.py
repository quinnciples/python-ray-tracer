import math
import random

import numpy as np

from Hit import Hit
from OrthoNormalBasis import OrthoNormalBasis
from QFunctions.Q_Functions import Q_buckets, Q_Vector3d
from Ray import Ray
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive
from AABB import AABB

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
    assert Q_Vector3d.NORM_XAXIS().cross_product(Q_Vector3d.NORM_YAXIS()) == Q_Vector3d.NORM_ZAXIS()
    assert Q_Vector3d(1, 2, 3).cross_product(Q_Vector3d(4, 5, 6)) == Q_Vector3d(-3, 6, -3)


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
                    np.linalg.norm(np_origin - np_center) == (Q_origin - Q_center).length
                    and np.linalg.norm(np_origin - np_center) > 0
                    and (Q_origin - Q_center).length > 0
                )


def test_OrthoNormalBasis_constructor():
    onb = OrthoNormalBasis(x=Q_Vector3d.NORM_XAXIS(), y=Q_Vector3d.NORM_YAXIS(), z=Q_Vector3d.NORM_ZAXIS())
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
    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=0, y=0, z=2)))  # Z002
    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=-1, y=0, z=0)))  # Zn00
    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=0, y=-1, z=0)))  # Z0n0
    check_is_basis(onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=0, y=0, z=-1)))  # Z00n
    check_is_basis(
        onb=OrthoNormalBasis.fromZ(Q_Vector3d.get_normalized_vector(x=-0.211944, y=-0.495198, z=0.842530))
    )  # Zrnd


def test_OrthoNormalBasis_random_vectors():
    THRESHOLD = 0.02

    def random_in_unit_sphere() -> Q_Vector3d:
        p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
        while p.length_squared >= 1.0:
            p = ((Q_Vector3d(random.random(), random.random(), random.random()) * 2.0) - Q_Vector3d(1, 1, 1))
        return p

    source_direction = Q_Vector3d(0, 1, 0).normalized()
    random_unit_vectors = [(source_direction + random_in_unit_sphere()).normalized() for _ in range(100_000)]
    v_min_x = min(x.x for x in random_unit_vectors)
    v_max_x = max(x.x for x in random_unit_vectors)
    # v_min_y = min(x.y for x in random_unit_vectors)
    # v_max_y = max(x.y for x in random_unit_vectors)
    v_min_z = min(x.z for x in random_unit_vectors)
    v_max_z = max(x.z for x in random_unit_vectors)
    # print()
    # print(min_x, max_x, min_y, max_y, min_z, max_z)

    CONE_THETA = math.pi / 2.0
    ortho_random_vectors = []
    source_direction = Q_Vector3d(0, 1, 0).normalized()
    for u_ in range(333):
        for v_ in range(333):
            ortho_random_vectors.append(OrthoNormalBasis.cone_sample(direction=source_direction, cone_theta=CONE_THETA, u=u_ / 333, v=v_ / 333))
    o_min_x = min(x.x for x in ortho_random_vectors)
    o_max_x = max(x.x for x in ortho_random_vectors)
    # o_min_y = min(x.y for x in ortho_random_vectors)
    # o_max_y = max(x.y for x in ortho_random_vectors)
    o_min_z = min(x.z for x in ortho_random_vectors)
    o_max_z = max(x.z for x in ortho_random_vectors)
    # print(min_x, max_x, min_y, max_y, min_z, max_z)
    assert math.fabs(o_min_x - v_min_x) <= THRESHOLD
    assert math.fabs(o_max_x - v_max_x) <= THRESHOLD
    # assert math.fabs(o_min_y - v_min_y) <= THRESHOLD
    assert math.fabs(o_min_z - v_min_z) <= THRESHOLD
    assert math.fabs(o_max_z - v_max_z) <= THRESHOLD


def test_Q_buckets_function():
    for number_of_items in range(2, 251, 6):
        for number_of_buckets in range(2, number_of_items + 1):
            buckets = [_ for _ in Q_buckets(number_of_items=number_of_items, number_of_buckets=number_of_buckets)]
            assert buckets[0][0] == 0
            assert len(buckets) == number_of_buckets
            last_end_point = buckets[0][1]
            for bucket in buckets[1:]:
                assert last_end_point == bucket[0]
                last_end_point = bucket[1]
            assert last_end_point == number_of_items


def test_Ray_constructor():
    r0 = Ray.from_two_vectors(first_vector=Q_Vector3d(1, 2, 3), second_vector=Q_Vector3d(2, 2, 3))
    assert r0.direction == Q_Vector3d.NORM_XAXIS()
    assert r0.origin == Q_Vector3d(1, 2, 3)

    r1 = Ray.from_two_vectors(first_vector=Q_Vector3d(1, 2, 3), second_vector=Q_Vector3d(4, 5, 6))
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
    hit = s.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 1, 0)))
    assert hit is None
    hit = s.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(-10, -20, -30)))
    assert hit is None
    hit = s.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(10, 20, 30)))
    assert hit is not None and hit.distance is not None and hit.normal_to_surface is not None
    # 22.416738
    assert math.fabs(22.41657 - hit.distance) < THRESHOLD
    assert (Q_Vector3d(-0.267261, -0.534522, -0.801784) - hit.normal_to_surface).length < THRESHOLD
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
    hit = s.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 2)))
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
    hit = s.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 30), Q_Vector3d(0, 0, 2)))
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
    hit = t.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 1, 0)))
    assert hit is None
    hit = t.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, -1)))
    assert hit is None
    hit = t.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 1)))
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
    hit = t.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 1, 0)))
    assert hit is None
    hit = t.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, -1)))
    assert hit is None
    hit = t.intersect(ray=Ray.from_two_vectors(Q_Vector3d(0, 0, 0), Q_Vector3d(0, 0, 1)))
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
        camera_position=Q_Vector3d(0, 0, 0),
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
        ],
    )
    assert s is not None and len(s.objects) > 0


def test_Scene_nearest_intersection_with_one_object():
    s = Scene(
        camera_position=Q_Vector3d(0, 0, 0),
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
        ],
    )
    # Test no intersection occurs
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 1, 0))
    nearest_object, hit = s.nearest_intersection(ray=ray)
    assert nearest_object is None and hit is None
    # Test intersection does occur
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 0, 1))
    nearest_object, hit = s.nearest_intersection(ray=ray)
    assert nearest_object is not None and hit is not None and hit.distance == 40


def test_Scene_nearest_intersection_with_two_object():
    s2 = Scene(
        camera_position=Q_Vector3d(0, 0, 0),
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
        ],
    )
    # Test no intersection occurs
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 1, 0))
    nearest_object, hit = s2.nearest_intersection(ray=ray)
    assert nearest_object is None and hit is None
    # Test intersection does occur
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 0, 1))
    nearest_object, hit = s2.nearest_intersection(ray=ray)
    assert nearest_object is not None and hit is not None and hit.distance == 40


def test_Scene_anti_aliasing_offsets_do_not_overlap():
    """
    Assume a 3x3 grid
    -------------------------
    (1, 3) - (2, 3) - (3, 3)
    |                       |
    (1, 2) - (2, 2) - (3, 2)
    |                       |
    (1, 1) - (2, 1) - (3, 1)
    -------------------------
    When calculating the potential subpixels for the center pixel (2, 2),
    valid x coordinates should be between the midpoint of this pixel
    and its left neighbor (1.5) and right neighbor (2.5) and
    valid y coordinates should be between the midpoint of this pixel
    and its lower neighbor (1.5) and upper neighbor (2.5)
    """
    width, height = 3, 3
    x_offset = 1
    y_offset = 1
    x, y = 2, 2
    x_total, x_count, y_total, y_count = 0, 0, 0, 0
    for _ in range(500):
        x_coord = x + ((random.random() - 0.5) * x_offset)
        if x_coord < x:
            x_total += x_coord
            x_count += 1
        y_coord = y + ((random.random() - 0.5) * y_offset)
        if y_coord < y:
            y_total += y_coord
            y_count += 1
        assert x >= 1.5 and x <= 2.5
        assert y >= 1.5 and y <= 2.5


def test_front_vectors():
    origin = Q_Vector3d(0, 0, 0)
    towards = Q_Vector3d(0, 0, 5)
    hit_object = Q_Vector3d(0, 0, 10)
    hitable_object = Q_Vector3d(3, 10, 10)
    behind_object = Q_Vector3d(0, 0, -2)
    missable_object = Q_Vector3d(-1, 5, -6)

    assert ((towards - origin).dot_product(hit_object - origin)) > 0
    assert ((towards - origin).dot_product(hitable_object - origin)) > 0
    assert ((towards - origin).dot_product(behind_object - origin)) < 0
    assert ((towards - origin).dot_product(missable_object - origin)) < 0


def test_AABB_constructor():
    bounding_box = AABB(Q_Vector3d(-5, -5, -5), length=10)
    assert bounding_box.min_coordinate == Q_Vector3d(-5, -5, -5)
    assert bounding_box.length == 10
    assert bounding_box.max_coordinate == Q_Vector3d(5, 5, 5)


def test_AABB_intersection_with_ray_originating_from_within_AABB():
    bounding_box = AABB(Q_Vector3d(-5, -5, -5), length=10)
    ray = Ray(origin=Q_Vector3d(0, 0, 0), direction=Q_Vector3d(0, 0, 2).normalized())
    result = bounding_box.intersect(ray=ray)
    assert result is True
    ray = Ray(origin=Q_Vector3d(50, 30, 80), direction=Q_Vector3d(0, 0, 2).normalized())
    result = bounding_box.intersect(ray=ray)
    assert result is False
    # Testing ray originating from box perimiter
    ray = Ray(origin=Q_Vector3d(-5, -5, -5), direction=Q_Vector3d(3, 4, 5).normalized())
    result = bounding_box.intersect(ray=ray)
    assert result is True


def test_AABB_intersection_with_ray_originating_from_outside_AABB():
    bounding_box = AABB(Q_Vector3d(-5, -5, -5), length=10)
    # Ray starts on the right side of the box and moves right = miss
    ray = Ray(origin=Q_Vector3d(20, 0, 0), direction=Q_Vector3d(1, 0, 0).normalized())
    result = bounding_box.intersect(ray=ray)
    assert result is False
    # Ray starts on the right side of the box and moves left = hit
    ray = Ray(origin=Q_Vector3d(20, 0, 0), direction=Q_Vector3d(-1, 0, 0).normalized())
    result = bounding_box.intersect(ray=ray)
    assert result is True
    # Ray starts above and on the right side of the box and moves left = miss
    ray = Ray(origin=Q_Vector3d(20, 500, 0), direction=Q_Vector3d(-1, 0, 0).normalized())
    result = bounding_box.intersect(ray=ray)
    assert result is False


if __name__ == "__main__":
    list_of_tests = [x for x in dir() if "test_AABB" in x]
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
            print(e)

    print()
    print(f"{total_tests} tests run, {total_tests - failed_tests} tests passed, {failed_tests} tests failed.")
    print()
