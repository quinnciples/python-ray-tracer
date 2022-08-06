# References
# https://www.realtimerendering.com/raytracing
# https://github.com/OmarAflak/RayTracer-CPP
# https://www.realtimerendering.com/raytracing/Ray%20Tracing_%20the%20Rest%20of%20Your%20Life.pdf
# https://github.com/mattgodbolt/pt-three-ways
# https://www.youtube.com/watch?v=HbzTFCsiWcg
# TODO - Create Material
#           Static variables for colors
# import pyjion
# pyjion.config(pgc=False)
# pyjion.enable()
import argparse
import random

from Camera import Camera
from CubePrimitive import CubePrimitive
from Material import Diffuse, Glass, Material, Metal
from PlanePrimitive import PlanePrimitive
from QFunctions.Q_Functions import Q_Vector3d
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive
from PlanePrimitive import PlanePrimitive

if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("--width", help="Width", type=int)
    parser.add_argument("--height", help="Height", type=int)
    parser.add_argument("--depth", help="Maximum Depth", type=int)
    parser.add_argument("--samples", help="Number of Lighting Samples", type=int)
    # parser.add_argument(
    #     "--anti-aliasing-enabled", help="Use Anti Aliasing", action="store_true"
    # )
    parser.add_argument("--cores", help="Number of Cores to Use", type=int)

    # Read arguments from command line
    arguments = parser.parse_args()

    WIDTH = arguments.width
    HEIGHT = arguments.height
    CAMERA = Q_Vector3d(0, 0, -1)
    MAX_DEPTH = arguments.depth
    NUMBER_OF_LIGHTING_SAMPLES = int(max(arguments.samples, 1))
    CORES_TO_USE = arguments.cores

    # cam = Camera(lookfrom=Q_Vector3d(13, 2, 1), lookat=Q_Vector3d(0, 0, 4), vup=Q_Vector3d(0, -1, 0), vfov=20, aspect_ratio=float(WIDTH) / float(HEIGHT), aperture=0.1, focus_dist=10.0)
    cam = Camera(lookfrom=Q_Vector3d(12.5, 2, -0.5), lookat=Q_Vector3d(0, 0, 4), vup=Q_Vector3d(0, -1, 0), vfov=20, aspect_ratio=float(WIDTH) / float(HEIGHT), aperture=0.1, focus_dist=10.0)
    objects = list()
    scene = Scene(objects=objects)
    scene.setup_rtiaw_test_scene()
    scene.generate_bounding_boxes()
    scene.multi_render(
        camera=cam,
        width=WIDTH,
        height=HEIGHT,
        max_depth=MAX_DEPTH,
        lighting_samples=NUMBER_OF_LIGHTING_SAMPLES,
        cores_to_use=CORES_TO_USE,
    )
