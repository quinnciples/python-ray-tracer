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
    NUMBER_OF_LIGHTING_SAMPLES = (
        int(max(arguments.samples, 1))
    )
    CORES_TO_USE = arguments.cores

    objects = list()
    for a in range(-11, 11):
        for b in range(-11, 11):
            choose_mat = random.random()
            # Check for collissions
            fail = True
            while fail:
                fail = False
                center = Q_Vector3d(a + 0.9 * random.random(), 0.2, b + 0.9 * random.random())
                for sphere in objects:
                    if (sphere.position - center).length < 0.41 or (center - Q_Vector3d(4, 0.2, 0)).length <= 0.9:
                        fail = True
                        break

            if (center - Q_Vector3d(4, 0.2, 0)).length > 0.9:
                if choose_mat < 0.65:
                    # Diffuse material
                    # Random color
                    color_value = Q_Vector3d(random.random(), random.random(), random.random())
                    objects.append(SpherePrimitive(position=center, material=Diffuse(attenuation=color_value), radius=0.2))
                elif choose_mat < 0.90:
                    # Metal
                    color_value = Q_Vector3d(random.random() / 2.0 + 0.5, random.random() / 2.0 + 0.5, random.random() / 2.0 + 0.5)
                    fuzz = random.random() / 2.0
                    fuzz = 0 if fuzz < 0.15 else fuzz
                    objects.append(SpherePrimitive(position=center, material=Metal(attenuation=color_value, fuzziness=float(fuzz)), radius=0.2))
                else:
                    # Glass
                    objects.append(SpherePrimitive(position=center, material=Glass(refraction_index=1.5), radius=0.2))

    objects.append(SpherePrimitive(position=Q_Vector3d(0, -1000.0001, 0), material=Diffuse(attenuation=Q_Vector3d(0.5, 0.5, 0.5)), radius=1000))
    objects.append(SpherePrimitive(position=Q_Vector3d(0, 1, 0), material=Glass(refraction_index=1.5), radius=1.0))
    objects.append(SpherePrimitive(position=Q_Vector3d(-4, 1, 0), material=Diffuse(attenuation=Q_Vector3d(0.4, 0.2, 0.1)), radius=1.0))
    objects.append(SpherePrimitive(position=Q_Vector3d(4, 1, 0), material=Metal(attenuation=Q_Vector3d(0.7, 0.6, 0.5), fuzziness=0.0), radius=1.0))

    print(f'{len(objects)} added to scene...')
    print('*' * 40)
    print()
    with open('render_settings.txt', 'w') as f_out:
        for o in objects:
            f_out.write(repr(o) + '\n')

    cam = Camera(lookfrom=Q_Vector3d(13, 2, -3), lookat=Q_Vector3d(0, 0, 0), vup=Q_Vector3d(0, -1, 0), vfov=20, aspect_ratio=float(WIDTH) / float(HEIGHT), aperture=0.1, focus_dist=10.0)
    scene = Scene(camera_position=CAMERA, objects=objects)
    scene.generate_bounding_boxes()

    scene.multi_render(
        camera=cam,
        width=WIDTH,
        height=HEIGHT,
        max_depth=MAX_DEPTH,
        lighting_samples=NUMBER_OF_LIGHTING_SAMPLES,
        cores_to_use=CORES_TO_USE,
    )
