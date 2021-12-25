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


if __name__ == '__main__':
    pass

"""

/* 
Fast Ray-Box Intersection
by Andrew Woo
from "Graphics Gems", Academic Press, 1990
*/

#include "GraphicsGems.h"

#define NUMDIM	3
#define RIGHT	0
#define LEFT	1
#define MIDDLE	2

char HitBoundingBox(minB,maxB, origin, dir,coord)
double minB[NUMDIM], maxB[NUMDIM];		/*box */
double origin[NUMDIM], dir[NUMDIM];		/*ray */
double coord[NUMDIM];				/* hit point */
{
	char inside = TRUE;
	char quadrant[NUMDIM];
	register int i;
	int whichPlane;
	double maxT[NUMDIM];
	double candidatePlane[NUMDIM];

	/* Find candidate planes; this loop can be avoided if
   	rays cast all from the eye(assume perpsective view) */
	for (i=0; i<NUMDIM; i++)
		if(origin[i] < minB[i]) {
			quadrant[i] = LEFT;
			candidatePlane[i] = minB[i];
			inside = FALSE;
		}else if (origin[i] > maxB[i]) {
			quadrant[i] = RIGHT;
			candidatePlane[i] = maxB[i];
			inside = FALSE;
		}else	{
			quadrant[i] = MIDDLE;
		}

	/* Ray origin inside bounding box */
	if(inside)	{
		coord = origin;
		return (TRUE);
	}


	/* Calculate T distances to candidate planes */
	for (i = 0; i < NUMDIM; i++)
		if (quadrant[i] != MIDDLE && dir[i] !=0.)
			maxT[i] = (candidatePlane[i]-origin[i]) / dir[i];
		else
			maxT[i] = -1.;

	/* Get largest of the maxT's for final choice of intersection */
	whichPlane = 0;
	for (i = 1; i < NUMDIM; i++)
		if (maxT[whichPlane] < maxT[i])
			whichPlane = i;

	/* Check final candidate actually inside box */
	if (maxT[whichPlane] < 0.) return (FALSE);
	for (i = 0; i < NUMDIM; i++)
		if (whichPlane != i) {
			coord[i] = origin[i] + maxT[whichPlane] *dir[i];
			if (coord[i] < minB[i] || coord[i] > maxB[i])
				return (FALSE);
		} else {
			coord[i] = candidatePlane[i];
		}
	return (TRUE);				/* ray hits box */
}	

"""
