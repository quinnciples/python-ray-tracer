from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from math import pi, tan


class Camera:
    def __init__(self, lookfrom: Q_Vector3d, lookat: Q_Vector3d, vup: Q_Vector3d, vfov: float, aspect_ratio: float, aperture: float = 0.1, focus_dist: float = 0.0):
        theta = vfov * pi / 180.0
        viewport_height = tan(theta / 2) * 2.0
        viewport_width = aspect_ratio * viewport_height
        self.origin = lookfrom
        self.w = (lookfrom - lookat).normalized()
        self.u = vup.cross_product(self.w).normalized()
        self.v = self.w.cross_product(self.u)
        self.aperture = aperture
        self.lens_radius = aperture / 2.0
        self.focus_dist = (lookfrom - lookat).length if focus_dist == 0 else focus_dist
        self.horizontal = self.focus_dist * viewport_width * self.u
        self.vertical = self.focus_dist * viewport_height * self.v
        self.lower_left_corner = self.origin - (self.horizontal * 0.5) - (self.vertical * 0.5) - (self.w * self.focus_dist)

    def get_ray_from_camera(self, x: float, y: float) -> Ray:
        rd = self.lens_radius * Q_Vector3d.random_in_unit_disk()
        offset = self.u * rd.x + self.v * rd.y
        return Ray(
            self.origin + offset, (self.lower_left_corner + x * self.horizontal + y * self.vertical - self.origin - offset).normalized()
        )
