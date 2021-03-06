#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy
import PIL.Image

class MazeError(Exception):
    def __init__(self, msg):
        self.message = msg

class Maze:
    grey = 127

    def __init__(self, filename, factor):
        image = PIL.Image.open(filename) \
                     .convert('L')   \
                     .point(lambda p: 255 if p > 128 else 0)
        w, h = image.size
        image = image.resize((w//factor, h//factor), PIL.Image.NEAREST)
        self.array = numpy.array(image, dtype=numpy.uint8)
        self.factor = factor

    # Display the image, un-resizing it
    def show(self):
        self.image().show()

    def image(self):
        image = PIL.Image.fromarray(self.array, mode='L')
        w, h = image.size
        return image.resize((w*self.factor, h*self.factor), PIL.Image.NEAREST)

    def save(self, filename, format):
        self.image().save(filename, format)

    # Returns pixels adjacent to the given tuple
    def getadjacent(self, n):
        x, y = n
        res = []
        if x > 0:
            res.append((x-1, y))
        if x < self.array.shape[0] - 1:
            res.append((x+1, y))
        if y > 0:
            res.append((x, y-1))
        if y < self.array.shape[1] - 1:
            res.append((x, y+1))
        return res

    # This assumes the bottom row has start+end as the only white spots
    # Ignores the corners (2 pixels from each side)
    def find_start_end(self):
        skip = False
        start, end = None, None
        w = self.array.shape[0]
        for i in range(2, self.array.shape[1]-2):
            if self.array[w-1, i] == 255:
                if skip == True:
                    continue
                if start == None:
                    start = i
                    skip = True
                    continue
                if end == None:
                    end = i
                    skip  = True
                    break
            else:
                skip = False
        if start == None or end == None          \
                or self.array[w-1, start] != 255 \
                or self.array[w-1, end] != 255:
            raise MazeError('Could not find valid start/end positions')
        return (w-1, start), (w-1, end)

    # Perform a standard BFS
    def bfs(self, start, end):
        q = []
        q.append([start])

        while len(q) != 0:
            path = q.pop(0)
            pixel = path[-1]
            if pixel == end:
                return path
            for adjacent in self.getadjacent(pixel):
                x, y = adjacent
                if self.array[x, y] == 255:
                    self.array[x, y] = self.grey
                    new_path = path.copy()
                    new_path.append(adjacent)
                    q.append(new_path)
        raise MazeError('bfs() could not find an answer')

    def color_result(self, path):
        for pixel in path:
            for adjacent in self.getadjacent(pixel):
                if self.array[adjacent] == self.grey:
                    self.array[adjacent] = 254
            if self.array[adjacent] == self.grey:
                self.array[adjacent] = 254
        white_to_grey = numpy.vectorize(lambda p: self.grey if p == 255 else p)
        self.array = white_to_grey(self.array)

def main():
    assert len(sys.argv) > 1
    m = Maze(sys.argv[1], 4)

    start, end = m.find_start_end()
    path = m.bfs(start, end)
    m.color_result(path)

    if len(sys.argv) > 2:
        m.save(sys.argv[2], 'PNG')
    m.show()

if __name__ == '__main__':
    main()

