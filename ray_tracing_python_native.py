# References
# https://github.com/OmarAflak/RayTracer-CPP
# https://www.realtimerendering.com/raytracing/Ray%20Tracing_%20the%20Rest%20of%20Your%20Life.pdf
# https://github.com/mattgodbolt/pt-three-ways
# https://www.youtube.com/watch?v=HbzTFCsiWcg
# TODO - Create Material
#           Static variables for colors

from QFunctions.Q_Functions import Q_Vector3d
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive
from PlanePrimitive import PlanePrimitive
from CubePrimitive import CubePrimitive

if __name__ == '__main__':
    WIDTH = 64 # 64
    HEIGHT = 48 # 48
    SCALE = 10
    ANTI_ALIASING = False
    CAMERA = Q_Vector3d(0, 0.1, -1.5)
    MAX_DEPTH = 10
    NUMBER_OF_LIGHTING_SAMPLES = 1

    objects = [
        # Spheres
        SpherePrimitive(position=Q_Vector3d(x=5, y=-5, z=30), ambient=Q_Vector3d(0.1, 0, 0.1), diffuse=Q_Vector3d(0.7, 0, 0.7), specular=Q_Vector3d(1.0, 0, 1.0), shininess=100, reflection=0.1, radius=6.0),  # Magenta right
        SpherePrimitive(position=Q_Vector3d(x=-8, y=0, z=30), ambient=Q_Vector3d(0, 0.1, 0.1), diffuse=Q_Vector3d(0, 0.7, 0.7), specular=Q_Vector3d(0, 1.0, 1.0), shininess=100, reflection=0.2, radius=4.0),  # Cyan left
        SpherePrimitive(position=Q_Vector3d(x=16, y=12, z=50), ambient=Q_Vector3d(0.1, 0.1, 0), diffuse=Q_Vector3d(0.7, 0.7, 0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.3, radius=8.0),  # Yellow
        SpherePrimitive(position=Q_Vector3d(x=-10, y=12, z=40), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.4, radius=8.0),  # White

        # Bottom plane - plane
        PlanePrimitive(front_bottom_left=Q_Vector3d(x=-500, y=-15, z=-10), rear_top_right=Q_Vector3d(500, -15, 250), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.1, 0.1, 0.1), specular=Q_Vector3d(0.3, 0.3, 0.3), shininess=0, reflection=0),

        # Light
        PlanePrimitive(front_bottom_left=Q_Vector3d(x=0, y=20, z=10), rear_top_right=Q_Vector3d(x=10, y=30, z=10), ambient=Q_Vector3d(1.0, 1.0, 1.0), diffuse=Q_Vector3d(1.0, 1.0, 1.0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0, emission=Q_Vector3d(0.5, 0.5, 0.5)),  # 0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0
        # CubePrimitive(front_bottom_left=Q_Vector3d(x=0, y=20, z=5), rear_top_right=Q_Vector3d(x=10, y=30, z=15), ambient=Q_Vector3d(1.0, 1.0, 1.0), diffuse=Q_Vector3d(1.0, 1.0, 1.0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0, emission=Q_Vector3d(0.5, 0.5, 0.5)),  # 0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0
    ]

    lights = [
        {'position': Q_Vector3d(5, 25, 10)}  # 'color': Q_Vector3d(0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0)}
    ]

    scene = Scene(objects=objects, lights=lights)

    print()

    scene.multi_render(camera_position=CAMERA, width=WIDTH * SCALE, height=HEIGHT * SCALE, max_depth=MAX_DEPTH, anti_aliasing=ANTI_ALIASING, lighting_samples=NUMBER_OF_LIGHTING_SAMPLES)
