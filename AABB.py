# From https://github.com/erich666/GraphicsGems/blob/master/gems/RayBox.c

# from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
import math


class AABB:
    BOX_POSITIONS = {
        "left_bottom_rear": (0, 0, 0),
        "right_bottom_rear": (1, 0, 0),
        "left_bottom_front": (0, 0, 1),
        "right_bottom_front": (1, 0, 1),
        "left_top_front": (0, 1, 1),
        "right_top_front": (1, 1, 1),
        "left_top_rear": (0, 1, 0),
        "right_top_rear": (1, 1, 0),
    }

    def __init__(self, lower_left_corner: Q_Vector3d, length: float, name: str = ''):
        self.min_coordinate = lower_left_corner
        self.length = length
        self.max_coordinate = Q_Vector3d(
            lower_left_corner.x + length, lower_left_corner.y + length, lower_left_corner.z + length
        )

        self.items = list()
        self.name = name

    def add_item(self, item) -> None:
        self.items.append(item)

    def get_corners(self) -> list:
        corners = list()
        # Left Bottom Front
        corners.append(self.min_coordinate)
        # Right Bottom Front
        corners.append(Q_Vector3d(self.min_coordinate.x + self.length, self.min_coordinate.y, self.min_coordinate.z))
        # Left Top Front
        corners.append(Q_Vector3d(self.min_coordinate.x, self.min_coordinate.y + self.length, self.min_coordinate.z))
        # Right Top Front
        corners.append(Q_Vector3d(self.min_coordinate.x + self.length, self.min_coordinate.y + self.length, self.min_coordinate.z))

        # Left Bottom Rear
        corners.append(Q_Vector3d(self.min_coordinate.x, self.min_coordinate.y, self.min_coordinate.z + self.length))
        # Right Bottom Rear
        corners.append(Q_Vector3d(self.min_coordinate.x + self.length, self.min_coordinate.y, self.min_coordinate.z + self.length))
        # Left Top Rear
        corners.append(Q_Vector3d(self.min_coordinate.x, self.min_coordinate.y + self.length, self.min_coordinate.z + self.length))
        # Right Top Rear
        corners.append(Q_Vector3d(self.min_coordinate.x + self.length, self.min_coordinate.y + self.length, self.min_coordinate.z + self.length))

        return corners

    def split(self, split_level: int = 1) -> list:
        if split_level == 0:
            return [self]
        boxes_to_add = list()
        starting_position = self.min_coordinate
        new_box_length = self.length / 2.0
        for label, dim_adjustments in AABB.BOX_POSITIONS.items():
            dim_mod_x, dim_mod_y, dim_mod_z = dim_adjustments
            box_position = Q_Vector3d(
                starting_position.x + dim_mod_x * new_box_length,
                starting_position.y + dim_mod_y * new_box_length,
                starting_position.z + dim_mod_z * new_box_length,
            )
            bounding_box = AABB(
                lower_left_corner=box_position,
                length=new_box_length,
                name=self.name + " " + label,
            )
            boxes_to_add.append(bounding_box)
        split_boxes = list()
        for box_to_add in boxes_to_add:
            for box in box_to_add.split(split_level=split_level - 1):
                split_boxes.append(box)
        return split_boxes

    def intersect(self, ray: Ray, t: float = math.inf) -> bool:
        # https://tavianator.com/cgit/dimension.git/tree/libdimension/bvh/bvh.c#n194
        # This is actually correct, even though it appears not to handle edge cases
        # (ray.n.{x,y,z} == 0).  It works because the infinities that result from
        # dividing by zero will still behave correctly in the comparisons.  Rays
        # which are parallel to an axis and outside the box will have tmin == inf
        # or tmax == -inf, while rays inside the box will have tmin and tmax
        # unchanged.
        # .n_inv = dmnsn_new_vector(1.0/ray.n.X, 1.0/ray.n.Y, 1.0/ray.n.Z)

        # ray.direction = ray.direction.normalized()
        tx1 = (self.min_coordinate.x - ray.origin.x) * (math.inf if ray.direction.x == 0 else (1.0 / ray.direction.x))
        tx2 = (self.max_coordinate.x - ray.origin.x) * (math.inf if ray.direction.x == 0 else (1.0 / ray.direction.x))  # ray.n_inv.x

        tmin = min(tx1, tx2)
        tmax = max(tx1, tx2)

        ty1 = (self.min_coordinate.y - ray.origin.y) * (math.inf if ray.direction.y == 0 else (1.0 / ray.direction.y))
        ty2 = (self.max_coordinate.y - ray.origin.y) * (math.inf if ray.direction.y == 0 else (1.0 / ray.direction.y))

        tmin = max(tmin, min(ty1, ty2))
        tmax = min(tmax, max(ty1, ty2))

        tz1 = (self.min_coordinate.z - ray.origin.z) * (math.inf if ray.direction.z == 0 else (1.0 / ray.direction.z))  # ray.n_inv.z
        tz2 = (self.max_coordinate.z - ray.origin.z) * (math.inf if ray.direction.z == 0 else (1.0 / ray.direction.z))  # ray.n_inv.z

        tmin = max(tmin, min(tz1, tz2))
        tmax = min(tmax, max(tz1, tz2))

        return tmax >= max(0.0, tmin) and tmin <= t

    def intersection(self, ray: Ray) -> bool:
        # Check if ray is originating within this AABB
        # if (
        #     ray.origin.x >= self.min_coordinate.x
        #     and ray.origin.x <= self.max_coordinate.x
        #     and ray.origin.y >= self.min_coordinate.y
        #     and ray.origin.y <= self.max_coordinate.y
        #     and ray.origin.z >= self.min_coordinate.z
        #     and ray.origin.z <= self.max_coordinate.z
        # ):
        #     return True
        quadrant = {}
        candidate_plane = {}
        inside = True
        LEFT = -1
        MIDDLE = 0
        RIGHT = 1
        intersection_point = Q_Vector3d(0, 0, 0)

        for dim in ('x', 'y', 'z'):
            if ray.origin.__getattribute__(dim) < self.min_coordinate.__getattribute__(dim):
                quadrant[dim] = LEFT
                candidate_plane[dim] = self.min_coordinate.__getattribute__(dim)
                inside = False
            elif ray.origin.__getattribute__(dim) > self.max_coordinate.__getattribute__(dim):
                quadrant[dim] = RIGHT
                candidate_plane[dim] = self.max_coordinate.__getattribute__(dim)
                inside = False
            else:
                quadrant[dim] = MIDDLE

        if inside:
            intersection_point = ray.origin
            return True

        # Calculate T distances to candidate planes
        maxT = Q_Vector3d(0, 0, 0)
        for dim in ('x', 'y', 'z'):
            if (quadrant[dim] != MIDDLE and ray.direction.__getattribute__(dim) != 0.0):
                maxT.__setattr__(dim, (candidate_plane[dim] - ray.origin.__getattribute__(dim)) / ray.direction.__getattribute__(dim))
            else:
                maxT.__setattr__(dim, -1.0)

        # Get largest of the maxT's for final choice of intersection
        which_plane = 'x'
        for dim in ('y', 'z'):
            if (maxT.__getattribute__(which_plane) < maxT.__getattribute__(dim)):
                which_plane = dim

        # /* Check final candidate actually inside box */
        if maxT.__getattribute__(which_plane) < 0.0:
            return False

        for dim in ('x', 'y', 'z'):
            if which_plane != dim:
                coord = ray.origin.__getattribute__(dim) + maxT.__getattribute__(which_plane) * ray.direction.__getattribute__(dim)
                intersection_point.__setattr__(dim, coord)
                if coord < self.min_coordinate.__getattribute__(dim) or coord > self.max_coordinate.__getattribute__(dim):
                    return False
            else:
                coord = candidate_plane[dim]
                intersection_point.__setattr__(dim, coord)

        return True  # ray hits box
