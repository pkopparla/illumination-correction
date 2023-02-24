import numpy as np
import matplotlib.pyplot as plt
import richdem as rd


def generate_elevation(image_size=20):
    """
    A function to generate elevation for a given image size, returns elevation,
    slope and azimuth of slope. Currently set to simulate 4 mountains.
    """
    oned_gradient = np.square(np.sin(np.linspace(0, 2 * np.pi, num=image_size)))
    elevation = oned_gradient[:, None] * oned_gradient[None, :]
    rdelevation = rd.rdarray(elevation, no_data=-999)
    slope = rd.TerrainAttribute(rdelevation, attrib="slope_riserun")
    aspect = rd.TerrainAttribute(rdelevation, attrib="aspect")
    return [elevation, slope, aspect]


def normalize(data):
    """
    Normalizes the maximum value in data to 1
    """
    return data / np.amax(data)


def calc_lsa(slope, aspect, sza, saa):
    """
    Calculates the cosine of the local solar irradiance angle given solar geometry,
    terrain slope and azimuth. Output has same width and height as image extent.
    """
    return np.cos(np.deg2rad(slope)) * np.cos(sza) + np.sin(np.deg2rad(slope)) * np.sin(
        sza
    ) * np.cos(np.deg2rad(aspect) - saa)


def generate_data(image_size=20, channels=10, sza=np.deg2rad(45), saa=np.deg2rad(45)):
    """
    Generates a simulated satellite image given image size, channels and solar geometry.
    The brightness values in the image have a random component on top of a terrain
    dependence.
    """
    rng = np.random.default_rng(seed=4)
    elevation, slope, aspect = generate_elevation(image_size=image_size)
    cos_gamma = calc_lsa(slope=slope, aspect=aspect, sza=sza, saa=saa)
    data_array = normalize(
        cos_gamma[:, :, None] + rng.random((image_size, image_size, channels)) * 5e-3
    )
    return [data_array, elevation, slope, aspect]
