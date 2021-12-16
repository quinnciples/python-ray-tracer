# References
# https://www.realtimerendering.com/raytracing
# https://github.com/OmarAflak/RayTracer-CPP
# https://www.realtimerendering.com/raytracing/Ray%20Tracing_%20the%20Rest%20of%20Your%20Life.pdf
# https://github.com/mattgodbolt/pt-three-ways
# https://www.youtube.com/watch?v=HbzTFCsiWcg
# TODO - Create Material
#           Static variables for colors

import argparse
import math

from CubePrimitive import CubePrimitive
from PlanePrimitive import PlanePrimitive
from QFunctions.Q_Functions import Q_Vector3d
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("--width", help="Width", type=int)
    parser.add_argument("--height", help="Height", type=int)
    parser.add_argument("--depth", help="Maximum Depth", type=int)
    parser.add_argument("--samples", help="Number of Lighting Samples", type=int)
    parser.add_argument(
        "--anti-aliasing-enabled", help="Use Anti Aliasing", action="store_true"
    )
    parser.add_argument("--cores", help="Number of Cores to Use", type=int)

    # Read arguments from command line
    arguments = parser.parse_args()

    WIDTH = arguments.width
    HEIGHT = arguments.height
    SCALE = 1
    ANTI_ALIASING = arguments.anti_aliasing_enabled
    CAMERA = Q_Vector3d(0, 0.1, -1.5)
    MAX_DEPTH = arguments.depth
    NUMBER_OF_LIGHTING_SAMPLES = (
        1 if arguments.samples <= 1 else max(int(math.sqrt(arguments.samples)), 1)
    )
    CORES_TO_USE = arguments.cores

    objects = [
        # Spheres
        SpherePrimitive(
            position=Q_Vector3d(x=5, y=-5, z=30),
            ambient=Q_Vector3d(0.1, 0, 0.1),
            diffuse=Q_Vector3d(0.7, 0, 0.7),
            specular=Q_Vector3d(1.0, 0, 1.0),
            shininess=20,
            reflection=0.1,
            radius=6.0,
        ),  # Magenta right
        SpherePrimitive(
            position=Q_Vector3d(x=-8, y=0, z=30),
            ambient=Q_Vector3d(0, 0.1, 0.1),
            diffuse=Q_Vector3d(0, 0.7, 0.7),
            specular=Q_Vector3d(0, 1.0, 1.0),
            shininess=40,
            reflection=0.2,
            radius=4.0,
        ),  # Cyan left
        SpherePrimitive(
            position=Q_Vector3d(x=16, y=12, z=50),
            ambient=Q_Vector3d(0.1, 0.1, 0),
            diffuse=Q_Vector3d(0.7, 0.7, 0),
            specular=Q_Vector3d(1.0, 1.0, 1.0),
            shininess=60,
            reflection=0.3,
            radius=8.0,
        ),  # Yellow
        SpherePrimitive(
            position=Q_Vector3d(x=-10, y=12, z=40),
            ambient=Q_Vector3d(0.1, 0.1, 0.1),
            diffuse=Q_Vector3d(0.7, 0.7, 0.7),
            specular=Q_Vector3d(1.0, 1.0, 1.0),
            shininess=80,
            reflection=0.4,
            radius=8.0,
        ),  # White
        # Bottom plane
        PlanePrimitive(
            front_bottom_left=Q_Vector3d(x=-500, y=-15, z=-10),
            rear_top_right=Q_Vector3d(500, -15, 250),
            ambient=Q_Vector3d(0, 0.45, 0),
            diffuse=Q_Vector3d(0, 0.45, 0),
            specular=Q_Vector3d(1.0, 1.0, 1.0),
            shininess=100,
            reflection=0.4,
        ),
        # Light
        PlanePrimitive(
            front_bottom_left=Q_Vector3d(x=0, y=20, z=10),
            rear_top_right=Q_Vector3d(x=10, y=30, z=10),
            ambient=Q_Vector3d(1.0, 1.0, 1.0),
            diffuse=Q_Vector3d(1.0, 1.0, 1.0),
            specular=Q_Vector3d(1.0, 1.0, 1.0),
            shininess=100,
            reflection=0,
            emission=Q_Vector3d(0.5, 0.5, 0.5),
        ),  # 0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0
        # CubePrimitive(front_bottom_left=Q_Vector3d(x=0, y=20, z=5), rear_top_right=Q_Vector3d(x=10, y=30, z=15), ambient=Q_Vector3d(1.0, 1.0, 1.0), diffuse=Q_Vector3d(1.0, 1.0, 1.0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0, emission=Q_Vector3d(0.5, 0.5, 0.5)),  # 0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0
    ]

    lights = [{"position": Q_Vector3d(5, 25, 10)}]
    scene = Scene(camera_position=CAMERA, objects=objects, lights=lights)

    scene.multi_render(
        width=WIDTH * SCALE,
        height=HEIGHT * SCALE,
        max_depth=MAX_DEPTH,
        anti_aliasing=ANTI_ALIASING,
        lighting_samples=NUMBER_OF_LIGHTING_SAMPLES,
        cores_to_use=CORES_TO_USE,
    )
