import random as rnd
from itertools import product
from ctypes import c_int64
import math


# ==================================================================================================================
# MISC.
# ==================================================================================================================

rnd.seed(5)

def easeInOut(x):
    return x * x * (3.0 - (2.0 * x))


def linearInterpolation(t, x, y):
    return x + t * (y - x)


def integerOverflow(x):
    return c_int64(x).value


# ==================================================================================================================
# FRACTAL NOISE ALGORITHMS
# ==================================================================================================================

def fBm(baseNoiseGenerator, point, octaves=4, persistence=0.5, ):
    x = point[0]
    y = point[1]

    maxAmplitude = 0
    amplitude = 1
    frequency = 1
    noiseValue = 0

    # add less-strong higher-frequency values for every octave
    for i in range(octaves):
        new_point = (x * frequency, y * frequency)
        noiseValue += baseNoiseGenerator(new_point) * amplitude
        maxAmplitude += amplitude
        amplitude *= persistence
        frequency *= 2

    noiseValue /= maxAmplitude
    return noiseValue


# ======================================================================================================================
# WHITE NOISE
# ======================================================================================================================

def whiteNoise(width: int, height: int, amplitude=1):
    return [rnd.uniform(-1.0, 1.0) * amplitude for _ in range(width * height)]


# ======================================================================================================================
# PERLIN NOISE
# ======================================================================================================================

PERLIN_GRAD_DATA = {}
PERLIN_SCALE_FACTOR = 2 / math.sqrt(2)


def basicPerlinNoise(p):
    grid_coords = []
    for coord in p:
        min_coord = math.floor(coord)
        max_coord = min_coord + 1
        grid_coords.append((min_coord, max_coord))

    def generateRandomGradient():
        vector = [rnd.gauss(0, 1), rnd.gauss(0, 1)]
        scale = 1 / math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])
        return vector[0] * scale, vector[1] * scale

    dots = []
    for grid_point in product(*grid_coords):
        if grid_point not in PERLIN_GRAD_DATA:
            PERLIN_GRAD_DATA[grid_point] = generateRandomGradient()
        gradient = PERLIN_GRAD_DATA[grid_point]

        dot = gradient[0] * (p[0] - grid_point[0]) + gradient[1] * (p[1] - grid_point[1])
        dots.append(dot)

    dim = 2
    while len(dots) > 1:
        dim -= 1
        s = easeInOut(p[dim] - grid_coords[dim][0])
        next_dots = []
        while dots:
            next_dots.append(linearInterpolation(s, dots.pop(0), dots.pop(0)))
        dots = next_dots

    return dots[0] * PERLIN_SCALE_FACTOR


def perlinNoise(width: int, height: int, amplitude=1, scale=8, octaves=4):
    noise = [0.0] * height * width
    for i in range(height):
        for j in range(width):
            p = (i / height * scale, j / width * scale)
            value = fBm(baseNoiseGenerator=basicPerlinNoise, point=p, octaves=octaves, persistence=0.5)
            noise[i * width + j] = value * amplitude
    return noise


# ======================================================================================================================
# OPEN_SIMPLEX NOISE
# ======================================================================================================================


OPEN_SIMPLEX_STRETCH = (1 / math.sqrt(2 + 1) - 1) / 2
OPEN_SIMPLEX_SQUISH = (math.sqrt(2 + 1) - 1) / 2
OPEN_SIMPLEX_NORM = 47

OPEN_SIMPLEX_GRADS = (
    5, 2, 2, 5,
    -5, 2, -2, 5,
    5, -2, 2, -5,
    -5, -2, -2, -5,
)


def generatePermutationForOpenSimplex(seed=0):
    perm = [0] * 256
    source = list(range(0, 256))
    seed = integerOverflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = integerOverflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = integerOverflow(seed * 6364136223846793005 + 1442695040888963407)
    for i in range(255, -1, -1):
        seed = integerOverflow(seed * 6364136223846793005 + 1442695040888963407)
        r = int((seed + 31) % (i + 1))
        if r < 0:
            r += i + 1
        perm[i] = source[r]
        source[r] = source[i]
    return perm


OPEN_SIMPLEX_GRAD_PERM = generatePermutationForOpenSimplex(seed=rnd.randint(0, 1024))


def openSimplex_extrapolate(xsb, ysb, dx, dy):
    index = OPEN_SIMPLEX_GRAD_PERM[(OPEN_SIMPLEX_GRAD_PERM[xsb & 0xFF] + ysb) & 0xFF] & 0x0E
    g1, g2 = OPEN_SIMPLEX_GRADS[index:index + 2]
    return g1 * dx + g2 * dy


def basicOpenSimplexNoise(point):
    x = point[0]
    y = point[1]

    # Place input coordinates onto grid.
    stretch_offset = (x + y) * OPEN_SIMPLEX_STRETCH
    xs = x + stretch_offset
    ys = y + stretch_offset

    # Floor to get grid coordinates of rhombus (stretched square) super-cell origin.
    xsb = math.floor(xs)
    ysb = math.floor(ys)

    # Skew out to get actual coordinates of rhombus origin. We'll need these later.
    squish_offset = (xsb + ysb) * OPEN_SIMPLEX_SQUISH
    xb = xsb + squish_offset
    yb = ysb + squish_offset

    # Compute grid coordinates relative to rhombus origin.
    xins = xs - xsb
    yins = ys - ysb

    # Sum those together to get a value that determines which region we're in.
    in_sum = xins + yins

    # Positions relative to origin point.
    dx0 = x - xb
    dy0 = y - yb

    value = 0

    # Contribution (1,0)
    dx1 = dx0 - 1 - OPEN_SIMPLEX_SQUISH
    dy1 = dy0 - 0 - OPEN_SIMPLEX_SQUISH
    attn1 = 2 - dx1 * dx1 - dy1 * dy1
    if attn1 > 0:
        attn1 *= attn1
        value += attn1 * attn1 * openSimplex_extrapolate(xsb + 1, ysb + 0, dx1, dy1)

    # Contribution (0,1)
    dx2 = dx0 - 0 - OPEN_SIMPLEX_SQUISH
    dy2 = dy0 - 1 - OPEN_SIMPLEX_SQUISH
    attn2 = 2 - dx2 * dx2 - dy2 * dy2
    if attn2 > 0:
        attn2 *= attn2
        value += attn2 * attn2 * openSimplex_extrapolate(xsb + 0, ysb + 1, dx2, dy2)

    if in_sum <= 1:  # We're inside the triangle (2-Simplex) at (0,0)
        zins = 1 - in_sum
        if zins > xins or zins > yins:  # (0,0) is one of the closest two triangular vertices
            if xins > yins:
                xsv_ext = xsb + 1
                ysv_ext = ysb - 1
                dx_ext = dx0 - 1
                dy_ext = dy0 + 1
            else:
                xsv_ext = xsb - 1
                ysv_ext = ysb + 1
                dx_ext = dx0 + 1
                dy_ext = dy0 - 1
        else:  # (1,0) and (0,1) are the closest two vertices.
            xsv_ext = xsb + 1
            ysv_ext = ysb + 1
            dx_ext = dx0 - 1 - 2 * OPEN_SIMPLEX_SQUISH
            dy_ext = dy0 - 1 - 2 * OPEN_SIMPLEX_SQUISH
    else:  # We're inside the triangle (2-Simplex) at (1,1)
        zins = 2 - in_sum
        if zins < xins or zins < yins:  # (0,0) is one of the closest two triangular vertices
            if xins > yins:
                xsv_ext = xsb + 2
                ysv_ext = ysb + 0
                dx_ext = dx0 - 2 - 2 * OPEN_SIMPLEX_SQUISH
                dy_ext = dy0 + 0 - 2 * OPEN_SIMPLEX_SQUISH
            else:
                xsv_ext = xsb + 0
                ysv_ext = ysb + 2
                dx_ext = dx0 + 0 - 2 * OPEN_SIMPLEX_SQUISH
                dy_ext = dy0 - 2 - 2 * OPEN_SIMPLEX_SQUISH
        else:  # (1,0) and (0,1) are the closest two vertices.
            dx_ext = dx0
            dy_ext = dy0
            xsv_ext = xsb
            ysv_ext = ysb
        xsb += 1
        ysb += 1
        dx0 = dx0 - 1 - 2 * OPEN_SIMPLEX_SQUISH
        dy0 = dy0 - 1 - 2 * OPEN_SIMPLEX_SQUISH

    # Contribution (0,0) or (1,1)
    attn0 = 2 - dx0 * dx0 - dy0 * dy0
    if attn0 > 0:
        attn0 *= attn0
        value += attn0 * attn0 * openSimplex_extrapolate(xsb, ysb, dx0, dy0)

    # Extra Vertex
    attn_ext = 2 - dx_ext * dx_ext - dy_ext * dy_ext
    if attn_ext > 0:
        attn_ext *= attn_ext
        value += attn_ext * attn_ext * openSimplex_extrapolate(xsv_ext, ysv_ext, dx_ext, dy_ext)

    return value / OPEN_SIMPLEX_NORM


def openSimplexNoise(width: int, height: int, amplitude=1, scale=8, octaves=4):
    noise = [0.0] * height * width
    for i in range(height):
        for j in range(width):
            p = (i / height * scale, j / width * scale)
            value = fBm(baseNoiseGenerator=basicOpenSimplexNoise, point=p, octaves=octaves, persistence=0.5)
            noise[i * width + j] = value * amplitude
    return noise


# ======================================================================================================================
# WORLEY NOISE
# ======================================================================================================================


def worleyNoise(width: int, height: int, amplitude=1, seedCount=100):
    noiseValues = [0.0] * width * height
    seedsX = [rnd.randint(0, width - 1) for _ in range(seedCount)]
    seedsY = [rnd.randint(0, height - 1) for _ in range(seedCount)]

    maxDistance = 0.0
    for y in range(height):
        for x in range(width):
            distances = [math.hypot(seedsX[i] - x, seedsY[i] - y) for i in range(seedCount)]
            distances.sort()
            if distances[0] > maxDistance:
                maxDistance = distances[0]

    for y in range(height):
        for x in range(width):
            distances = [math.hypot(seedsX[i] - x, seedsY[i] - y) for i in range(seedCount)]
            distances.sort()
            noiseValues[y * height + x] = amplitude * (1 - distances[0] / maxDistance)

    return noiseValues
