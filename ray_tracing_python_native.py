# TODO - Create Material
#           Static variables for colors

from CubePrimitive import CubePrimitive
from QFunctions.Q_Functions import Q_Vector3d
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive


WIDTH = 64
HEIGHT = 48
SCALE = 5
CAMERA = Q_Vector3d(0, 0, -1.75)
MAX_DEPTH = 10

objects = [
    # Spheres
    SpherePrimitive(position=Q_Vector3d(x=3.5, y=0, z=10), ambient=Q_Vector3d(0.1, 0, 0.1), diffuse=Q_Vector3d(0.7, 0, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0, radius=3.0),  # Magenta right
    SpherePrimitive(position=Q_Vector3d(x=-3.5, y=0, z=10), ambient=Q_Vector3d(0, 0.1, 0.1), diffuse=Q_Vector3d(0, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=1.0, radius=3.0),  # Cyan left
    SpherePrimitive(position=Q_Vector3d(x=16, y=12, z=40), ambient=Q_Vector3d(0.1, 0.1, 0), diffuse=Q_Vector3d(0.7, 0.7, 0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.75, radius=8.0),  # Yellow
    SpherePrimitive(position=Q_Vector3d(x=-16, y=12, z=40), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.75, radius=8.0),  # White

    # TrianglePrimitive(vertices=(Q_Vector3d(x=-13, y=0, z=10), Q_Vector3d(x=-3, y=0, z=10), Q_Vector3d(x=-8, y=5, z=10)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-13, y=0, z=10), Q_Vector3d(x=-3, y=0, z=10), Q_Vector3d(x=-8, y=-5, z=10)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-10, y=15, z=10), Q_Vector3d(x=10, y=15, z=10), Q_Vector3d(x=0, y=15, z=5)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),  # Overhead plane
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-10, y=15, z=10), Q_Vector3d(x=10, y=15, z=10), Q_Vector3d(x=0, y=15, z=25)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),  # Overhead plane
    # SpherePrimitive(position=Q_Vector3d(x=0, y=0, z=0), ambient=Q_Vector3d(0, 0, 0), diffuse=Q_Vector3d(0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0), specular=Q_Vector3d(0, 0, 0), shininess=0, reflection=0, radius=600),  # Testing camera INSIDE SPHERE
    # SpherePrimitive(position=Q_Vector3d(x=0, y=-1000, z=15), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=990.0),  # Bottom plane

    # TrianglePrimitive(vertices=(Q_Vector3d(x=-100, y=50, z=100), Q_Vector3d(x=100, y=50, z=100), Q_Vector3d(x=100, y=-50, z=100)), ambient=Q_Vector3d(0, 0, 0), diffuse=Q_Vector3d(0xad / 255.0 / 2.0, 0xd8 / 255.0 / 2.0, 0xe6 / 255.0 / 2.0), specular=Q_Vector3d(0, 0, 0), shininess=0, reflection=0),  # Back wall
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-100, y=50, z=100), Q_Vector3d(x=100, y=-50, z=100), Q_Vector3d(x=-100, y=-50, z=100)), ambient=Q_Vector3d(0, 0, 0), diffuse=Q_Vector3d(0xad / 255.0 / 2.0, 0xd8 / 255.0 / 2.0, 0xe6 / 255.0 / 2.0), specular=Q_Vector3d(0, 0, 0), shininess=0, reflection=0),  # Back wall

    # # Bottom plane
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-100, y=-10, z=-100), Q_Vector3d(x=-100, y=-10, z=1000), Q_Vector3d(x=100, y=-10, z=1000)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),  # Bottom plane
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-100, y=-10, z=-100), Q_Vector3d(x=100, y=-10, z=-100), Q_Vector3d(x=100, y=-10, z=1000)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),  # Bottom plane

    # Bottom cube
    CubePrimitive(front_bottom_left=Q_Vector3d(x=-25, y=-55, z=-10), rear_top_right=Q_Vector3d(25, -5, 40), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=1.0),
]

lights = [
    {'position': Q_Vector3d(0, 5, 0), 'color': Q_Vector3d(0xad / 255.0, 0xd8 / 255.0, 0xe6 / 255.0)}
]

scene = Scene(objects=objects, lights=lights)

print()

scene.render(camera_position=CAMERA, width=WIDTH * SCALE, height=HEIGHT * SCALE, max_depth=MAX_DEPTH, anti_aliasing=False)

# Test
# ray_origin = np.array([0, 0, 0])
# vOrigin = Q_Vector3D(x=0, y=0, z=0)
# radius = 1.0
# for x in range(5):
#     for y in range(-3, 6):
#         for z in range(2, 8):
#             center = np.array([x, y, z])
#             vCenter = Q_Vector3D(x=x, y=y, z=z)
#             if np.linalg.norm(ray_origin - center) != (vOrigin - vCenter).length:
#                 print(np.linalg.norm(ray_origin - center), (vOrigin - vCenter).length, np.linalg.norm(ray_origin - center) == (vOrigin - vCenter).length)
