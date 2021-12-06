from QFunctions.Q_Functions import Q_Vector3d
import os
from Scene import Scene
from SpherePrimitive import SpherePrimitive
from TrianglePrimitive import TrianglePrimitive


WIDTH = 64
HEIGHT = 48
SCALE = 10
CAMERA = Q_Vector3d(0, 0, -1.75)
MAX_DEPTH = 10

objects = [
    SpherePrimitive(position=Q_Vector3d(x=3.5, y=0, z=15), ambient=Q_Vector3d(0.1, 0, 0.1), diffuse=Q_Vector3d(0.7, 0, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=3.0),  # Magenta right
    SpherePrimitive(position=Q_Vector3d(x=-3.5, y=0, z=15), ambient=Q_Vector3d(0, 0.1, 0.1), diffuse=Q_Vector3d(0, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=3.0),  # Cyan left
    SpherePrimitive(position=Q_Vector3d(x=0, y=8, z=40), ambient=Q_Vector3d(0.1, 0.1, 0), diffuse=Q_Vector3d(0.7, 0.7, 0), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=8.0),  # Yellow
    SpherePrimitive(position=Q_Vector3d(x=0, y=-1000, z=15), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5, radius=990.0),  # Bottom plane
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-13, y=0, z=10), Q_Vector3d(x=-3, y=0, z=10), Q_Vector3d(x=-8, y=5, z=10)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),
    # TrianglePrimitive(vertices=(Q_Vector3d(x=-13, y=0, z=10), Q_Vector3d(x=-3, y=0, z=10), Q_Vector3d(x=-8, y=-5, z=10)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),
    TrianglePrimitive(vertices=(Q_Vector3d(x=-10, y=15, z=10), Q_Vector3d(x=10, y=15, z=10), Q_Vector3d(x=0, y=15, z=5)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),
    TrianglePrimitive(vertices=(Q_Vector3d(x=-10, y=15, z=10), Q_Vector3d(x=10, y=15, z=10), Q_Vector3d(x=0, y=15, z=25)), ambient=Q_Vector3d(0.1, 0.1, 0.1), diffuse=Q_Vector3d(0.7, 0.7, 0.7), specular=Q_Vector3d(1.0, 1.0, 1.0), shininess=100, reflection=0.5),
]

lights = [
    {'position': Q_Vector3d(-5, 5, 5), 'color': Q_Vector3d(1, 1, 1)}
]

scene = Scene(objects=objects, lights=lights)

os.system('cls')
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
