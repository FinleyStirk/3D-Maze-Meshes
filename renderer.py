import pyvista as pv
import numpy as np

from maze import Maze, Maze3D


def quad(p0, p1, p2, p3):
    points = np.array([p0, p1, p2, p3], dtype=float)
    faces = np.array([4, 0, 1, 2, 3])
    return pv.PolyData(points, faces)


def generate_maze_mesh3D(maze: Maze3D):
    meshes = []

    FACE_DEFS = {
        # X faces
        ( 1, 0, 0): [(1,0,0), (1,1,0), (1,1,1), (1,0,1)],
        (-1, 0, 0): [(0,0,0), (0,0,1), (0,1,1), (0,1,0)],

        # Y faces
        (0,  1, 0): [(0,1,0), (0,1,1), (1,1,1), (1,1,0)],
        (0, -1, 0): [(0,0,0), (1,0,0), (1,0,1), (0,0,1)],

        # Z faces
        (0, 0,  1): [(0,0,1), (1,0,1), (1,1,1), (0,1,1)],
        (0, 0, -1): [(0,1,0), (0,0,0), (1,0,0), (1,1,0)],
    }

    for (x, y, z), links in maze.graph.items():
        cell = np.array([x, y, z], dtype=float)

        for direction, offsets in FACE_DEFS.items():
            neighbour = (x + direction[0],
                         y + direction[1],
                         z + direction[2])
            
            if neighbour not in links and maze.is_valid_cell(neighbour):
                p = [cell + np.array(o) for o in offsets]
                wall = quad(
                    p[0], 
                    p[1], 
                    p[2], 
                    p[3]
                )
                meshes.append(wall)

    return pv.merge(meshes, merge_points=True)


def project_to_sphere(x, y, z):
    project = lambda i, j, k: i * np.sqrt(1 - (j * j)/2 - (k * k)/2 + (j * j * k * k)/3)
    nx = project(x, y, z)
    ny = project(y, x, z)
    nz = project(z, x, y)
    return nx, ny, nz


def cube_sphere(maze: Maze3D, outer_scale: float = 0.9, is_hollow: bool = False):
    num_vertices = maze.w
    coords = np.linspace(-1.0, 1.0, num_vertices)

    points = [] 
    faces = []   

    def add_face(const_axis, const_value, u_axis, v_axis):
        start_index = len(points)

        for u in coords:
            for v in coords:
                p = [0.0, 0.0, 0.0]
                p[const_axis] = const_value
                p[u_axis] = u
                p[v_axis] = v
                points.append(project_to_sphere(*p))

        n = num_vertices
        if not is_hollow:
            for i in range(n - 1):
                for j in range(n - 1):
                    a = start_index + i*n + j
                    b = a + 1
                    c = a + n
                    d = c + 1

                    faces.append([3, a, b, d])
                    faces.append([3, a, d, c])

        for i in range(n - 1):
            for j in range(n - 1):
                a = start_index + i*n + j
                b = a + 1
                c = a + n
                d = c + 1

                edges = [
                    (a, b, (i-1, j)),  # top
                    (b, d, (i, j+1)),  # right
                    (c, d, (i+1, j)),  # bottom
                    (a, c, (i, j-1)),  # left
                ]

                for base0_idx, base1_idx, neigh in edges:
                    ni, nj = neigh
                    
                    cell_xyz = face_cell_to_xyz(
                        i, j,
                        const_axis, const_value,
                        n
                    )
                    links = maze.graph[cell_xyz]

                    neigh_xyz = face_cell_to_xyz(
                        ni, nj,
                        const_axis, const_value,
                        n
                    )
                    
                    if neigh_xyz in links or not maze.is_valid_cell(neigh_xyz):
                        continue

                    base_v0 = np.array(points[base0_idx], dtype=float)
                    base_v1 = np.array(points[base1_idx], dtype=float)

                    top_v0 = base_v0 * outer_scale
                    top_v1 = base_v1 * outer_scale

                    top_v0_idx = len(points)
                    points.append(top_v0)
                    top_v1_idx = len(points)
                    points.append(top_v1)

                    faces.append([3, base0_idx, base1_idx, top_v1_idx])
                    faces.append([3, base0_idx, top_v1_idx, top_v0_idx])

    add_face(0,  1, 1, 2)  # +X
    add_face(0, -1, 1, 2)  # -X
    add_face(1,  1, 0, 2)  # +Y
    add_face(1, -1, 0, 2)  # -Y
    add_face(2,  1, 0, 1)  # +Z
    add_face(2, -1, 0, 1)  # -Z

    pts_np = np.array(points, dtype=float)
    faces_flat = np.array(faces, dtype=np.int64).flatten()
    mesh = pv.PolyData(pts_np, faces_flat)

    return mesh


def face_cell_to_xyz(i, j, const_axis, const_value, size):
    cell = [0, 0, 0]

    cell[const_axis] = size - 1 if const_value > 0 else 0

    axes = [0, 1, 2]
    axes.remove(const_axis)

    cell[axes[0]] = i
    cell[axes[1]] = j

    return tuple(cell)