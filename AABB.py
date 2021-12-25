# From https://github.com/erich666/GraphicsGems/blob/master/gems/RayBox.c

from Primitive import Primitive
from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray


class AABB:
    def __init__(self, lower_left_corner: Q_Vector3d, length: float, items: list = []):
        self.min_coordinate = lower_left_corner
        self.length = length
        self.max_coordinate = Q_Vector3d(
            lower_left_corner.x + length, lower_left_corner.y + length, lower_left_corner.z + length
        )

        self.items = items

    def add_item(self, item: Primitive) -> None:
        self.items.append(item)

    def intersect(self, ray: Ray) -> bool:
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
                if coord < self.min_coordinate.__getattribute__(dim) or coord > self.max_coordinate.__getattribute__(dim):
                    return False

        return True  # ray hits box
