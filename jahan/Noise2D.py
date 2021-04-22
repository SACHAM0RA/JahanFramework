from random import random, uniform, gauss
from itertools import product
import math


# ==================================================================================================================
# MISC.
# ==================================================================================================================

def smooth(x):
    return x * x * (3.0 - (2.0 * x))


def linearInterpolation(t, a, b):
    return a + t * (b - a)


# ==================================================================================================================
# WHITE NOISE
# ==================================================================================================================

def whiteNoise(width: int, height: int, amplitude=1):
    return [uniform(-1.0, 1.0) * amplitude for _ in range(width * height)]


# ==================================================================================================================
# PERLIN NOISE
# ==================================================================================================================


def getPerlinValueInPoint(point, gradientData, octaves=1):
    scale_factor = 2 / math.sqrt(2)

    def getBaseNoise(p, gradients):

        grid_coords = []
        for coord in p:
            min_coord = math.floor(coord)
            max_coord = min_coord + 1
            grid_coords.append((min_coord, max_coord))

        def generateRandomGradient():
            vector = [gauss(0, 1), gauss(0, 1)]
            scale = 1 / math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])
            return vector[0] * scale, vector[1] * scale

        dots = []
        for grid_point in product(*grid_coords):
            if grid_point not in gradients:
                gradients[grid_point] = generateRandomGradient()
            gradient = gradients[grid_point]

            dot = gradient[0] * (p[0] - grid_point[0]) + gradient[1] * (p[1] - grid_point[1])
            dots.append(dot)

        dim = 2
        while len(dots) > 1:
            dim -= 1
            s = smooth(p[dim] - grid_coords[dim][0])
            next_dots = []
            while dots:
                next_dots.append(linearInterpolation(s, dots.pop(0), dots.pop(0)))
            dots = next_dots

        return dots[0] * scale_factor, gradients

    returnNoiseValue = 0
    for octave in range(octaves):
        nextOctave = 2 ** octave
        new_point = []
        for i, coord in enumerate(point):
            coord *= nextOctave
            new_point.append(coord)

        noiseValue, gradientData = getBaseNoise(new_point, gradientData)
        returnNoiseValue += noiseValue / nextOctave

    returnNoiseValue = returnNoiseValue / (2 - 2 ** (1 - octaves))

    r = (returnNoiseValue + 1) / 2
    for _ in range(int(octaves / 2 + 0.5)):
        r = smooth(r)
    returnNoiseValue = r * 2 - 1

    return returnNoiseValue, gradientData


def perlinNoise(width: int, height: int, amplitude=1, octaves=4, scale=8):
    gradientData = {}
    noise = [0] * height * width
    for i in range(height):
        for j in range(width):
            p = (i / height * scale, j / width * scale)
            value, gradientData = getPerlinValueInPoint(p, gradientData, octaves=octaves)
            noise[i * width + j] = value * amplitude
    return noise


# ==================================================================================================================
# OPEN_SIMPLEX NOISE
# ==================================================================================================================

def openSimplexNoise(width: int, height: int, amplitude=1, octaves=4, scale=8):