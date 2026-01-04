import pyvista as pv

from maze import Maze3D, CubeMaze
import renderer


if __name__ == "__main__":
    maze = CubeMaze(16)
    maze.randomise()
    cube_mesh = renderer.generate_maze_mesh3D(maze)
    cube_mesh.plot()


    cube_sphere = renderer.cube_sphere(maze, outer_scale=1.05, is_hollow=True)
    cube_sphere.plot()