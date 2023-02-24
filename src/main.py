from utils import generate_data, calc_lsa
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression


def apply_c_correction(data_array, channels, cos_gamma):
    """
    A function that takes an input image with the local solar
    incidence angles and returns the terrain corrected image
    and correction factors
    """
    corr_factors = np.zeros(channels)
    correlations = np.zeros(channels)
    for i in range(channels):
        linear_model = LinearRegression().fit(
            cos_gamma.reshape(-1, 1), data_array[:, :, i].reshape(-1)
        )
        corr_factors[i] = float(linear_model.intercept_ / linear_model.coef_)
        correlations[i] = np.corrcoef(
            np.ravel(cos_gamma), np.ravel(data_array[:, :, i])
        )[0, 1]
        correctable_channels = np.squeeze(np.where(correlations > 0.5))
    corr_da = np.copy(data_array)
    corr_da[:, :, correctable_channels] = (
        data_array[:, :, correctable_channels]
        * (np.cos(sza) + corr_factors[None, None, correctable_channels])
        / (cos_gamma[:, :, None] + corr_factors[None, None, correctable_channels])
    )
    return [corr_da, corr_factors, correlations]


sza = np.deg2rad(30)  # solar zenith angle
saa = np.deg2rad(45)  # solar azimuth angle
channels = 10  # no of wavelengths in the image
image_size = 20  # no of pixels

# generate the synthetic image with elevation data
# aspect is the azimuth correspoding to the terrain slope
data_array, elevation, slope, aspect = generate_data(
    image_size=image_size, channels=channels, sza=sza, saa=saa
)

# calculate the local solar irradiance geometry based on terrain
cos_gamma = calc_lsa(slope=slope, aspect=aspect, sza=sza, saa=saa)
cos_beta = np.cos(sza)

# apply correction to the data array
corr_da, corr_factors, correlations = apply_c_correction(
    data_array=data_array, channels=channels, cos_gamma=cos_gamma
)
print(correlations)
# plotting code
fig, ax = plt.subplots(ncols=2, nrows=2)
sample = 5

cax = ax[0, 0].contourf(data_array[:, :, sample], cmap="Spectral")
ax[0, 0].set_title("Original Image")
fig.colorbar(cax, ax=ax[0, 0])

cax = ax[1, 0].contourf(corr_da[:, :, sample], cmap="Spectral")
ax[1, 0].set_title("Terrain Corrected Image")
fig.colorbar(cax, ax=ax[1, 0])

cax = ax[0, 1].contourf(elevation, cmap="gray")
ax[0, 1].set_title("Elevation")
fig.colorbar(cax, ax=ax[0, 1])

this_corr_fac = (np.cos(sza) + corr_factors[sample]) / (
    cos_gamma + corr_factors[sample]
)
cax = ax[1, 1].contourf(this_corr_fac, cmap="bwr")
ax[1, 1].set_title("Correction Factors")
fig.colorbar(cax, ax=ax[1, 1])
plt.tight_layout()
plt.savefig("results_summary.png")
