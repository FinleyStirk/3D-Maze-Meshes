import numpy as np
import random as rand
from collections import defaultdict


class Maze:

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.graph = defaultdict(set)

        for y in range(height):
            for x in range(width):
                self.graph[(x, y)] 

    def neighbours(self, cell):
        x, y = cell
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.w and 0 <= ny < self.h:
                yield (nx, ny)

    def connect(self, a, b):
        self.graph[a].add(b)
        self.graph[b].add(a)
    
    def randomise(self, start=(0, 0)):
        visited = set()

        def dfs(cell):
            visited.add(cell)
            neighbours = list(self.neighbours(cell))
            rand.shuffle(neighbours)

            for neighbour in neighbours:
                if neighbour not in visited:
                    self.connect(cell, neighbour)
                    dfs(neighbour)
        
        dfs(start)


class Maze3D:
    def __init__(self, width, height, depth):
        self.w = width
        self.h = height
        self.d = depth
        self.graph = defaultdict(set)

        for z in range(depth):
            for y in range(height):
                for x in range(width):
                    cell = (x, y, z)
                    if self.is_valid_cell(cell):
                        self.graph[cell]

    def neighbours(self, cell):
        x, y, z = cell
        for dx, dy, dz in [(-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,1), (0,0,-1)]:
            nx, ny, nz= x + dx, y + dy, z + dz
            if self.is_valid_cell((nx, ny, nz)):
                yield (nx, ny, nz)

    def connect(self, a, b):
        self.graph[a].add(b)
        self.graph[b].add(a)
    
    def randomise(self, start=(0, 0, 0)):
        visited = set()

        def dfs(cell):
            visited.add(cell)
            neighbours = list(self.neighbours(cell))
            rand.shuffle(neighbours)

            for neighbour in neighbours:
                if neighbour not in visited:
                    self.connect(cell, neighbour)
                    dfs(neighbour)
        
        dfs(start)
    
    def is_valid_cell(self, cell):
        x, y, z = cell
        return 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d
    

class CubeMaze(Maze3D):
    def __init__(self, length):
        self.length = length
        super().__init__(length, length, length)
    
    def is_valid_cell(self, cell):
        return super().is_valid_cell(cell) and any(comp == 0 or comp == self.length - 1 for comp in cell)


