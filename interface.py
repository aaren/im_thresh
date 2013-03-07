### This script takes in a lab image and extracts the pixel
### coordinates of the interface between the upper and lower
### fluids.
###
### It is only intended for prototyping.

from sys import argv

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import imread
from scipy.ndimage import gaussian_filter
from skimage.filter import canny
from skimage.filter import sobel

# load image to array
fname = argv[1]
im = imread(fname)

# split to channels, with normalisation
r, g, b = (c.squeeze() / 255. for c in np.dsplit(im, 3))

# detect edges with canny edge detector
sigma = 4
lo = 0.1
hi = 0.3
edges = canny(b, sigma, lo, hi)

# isolate list of x and y coords of the points that form the edges
px, py = np.where(edges)

# apply heuristics to discard the points that aren't on the
# interface

# thresholding value
tval = 0.3
# plot a load of stuff to see how we're doing
# blue channel
plt.imshow(b, origin='lower')
# blue channel below threshold
plt.imshow(b < tval, origin='lower')
# gaussian filtered blue channel below threshold
plt.imshow(gaussian_filter(b < tval, sigma), origin='lower')
# sobel operator over gaussian filtered blue channel
plt.imshow(sobel(gaussian_filter(b, sigma)), origin='lower')
# canny edge detection on blue channel below threshold
plt.imshow(canny(b < tval, sigma), origin='lower')
# canny edge detection on gaussian filtered blue channel below threshold
plt.imshow(canny(gaussian_filter(b < tval, sigma), 0), origin='lower')
# canny edge detection on blue channel
plt.imshow(canny(b, sigma, lo, hi))
