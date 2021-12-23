from QFunctions.Q_Functions import Q_Vector3d
from Ray import Ray
from math import pi, tan


class Camera:
    def __init__(self, lookfrom: Q_Vector3d, lookat: Q_Vector3d, vup: Q_Vector3d, vfov: float, aspect_ratio: float):
        theta = vfov * pi / 180.0
        viewport_height = tan(theta / 2) * 2.0
        viewport_width = aspect_ratio * viewport_height
        self.origin = lookfrom
        w = (lookfrom - lookat).normalized()
        u = vup.cross_product(w).normalized()
        v = w.cross_product(u)

        self.horizontal = viewport_width * u
        self.vertical = viewport_height * v
        self.lower_left_corner = self.origin - (self.horizontal * 0.5) - (self.vertical * 0.5) - w

    def get_ray_from_camera(self, x: float, y: float) -> Ray:
        return Ray(
            self.origin, (self.lower_left_corner + x * self.horizontal + y * self.vertical - self.origin).normalized()
        )
