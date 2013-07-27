# generate the images for blog post
import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

from skimage import filter as skif


class LabImage(object):
    def __init__(self, fname='img.jpg', crop=(470, 700)):
        self.im = plt.imread(fname)[crop[0]:crop[1]]
        r, g, b = (c.squeeze() / 255. for c in np.dsplit(self.im, 3))
        self.r, self.g, self.b = r, g, b

    def channels(self):
        """Plot the original image and the individual
        channels in one figure
        """
        fig = plt.figure(figsize=(6, 4), dpi=100)
        fig.suptitle('Original image and colour channels')
        channels = {'red': self.r,
                    'green': self.g,
                    'blue': self.b,
                    'source': self.im}
        for i, c in enumerate(['source', 'red', 'green', 'blue']):
            ax = fig.add_subplot(4, 1, i + 1)
            ax.imshow(channels[c], origin='lower')
            ax.text(50, 170, c)
            ax.axis('off')
        fig.savefig("channels.png")

    def gaussian(self):
        """Compare gaussian smoothing across images.
        """
        fig = plt.figure(figsize=(5, 4), dpi=100)
        fig.suptitle('Gaussian smoothing of blue channel')
        for i, s in enumerate([1, 3, 5, 7, 9]):
            ax = fig.add_subplot(5, 1, i + 1)
            smooth = ndimage.gaussian_filter(self.b, s)
            ax.imshow(smooth, origin='lower')
            text = "sigma = {sigma}".format(sigma=s)
            ax.text(50, 170, text)
            ax.axis('off')
        fig.savefig('gaussian-comp.png')

    def threshold(self):
        """Make a simple thresholded image."""
        fig = plt.figure()
        fig.suptitle('Blue values less than 100')
        ax = fig.add_subplot(111)
        ax.imshow(self.b < 100 / 255., origin='lower')
        ax.axis('off')
        fig.savefig('threshold.png')

    def threshold_interface(self, thresh=100., sigma=4):
        """Canny detect the interface on a thresholded image."""
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.set_title('Interface using thresholding')
        tim = ndimage.gaussian_filter(self.b, sigma) < thresh / 255
        cb = skif.canny(tim, sigma=0)
        iy, ix = np.where(cb)
        s = ix.argsort()
        ax.imshow(self.b, origin='lower')
        ax.plot(ix[s], iy[s], 'k', linewidth=2)
        fig.savefig('threshold-interface.png')

    def sobel(self, sigma=1):
        """Plot blue channel with sobel operator to
        determine appropriate thresholds.

        NB. skimage calculates the sobel magnitude using ndimage.sobel
        rather than skimage.filter.sobel
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Sobel operator over blue channel,\n'
                     'smoothed with sigma={s}'.format(s=sigma))
        ax.axis('off')
        # apply some smoothing
        gb = ndimage.gaussian_filter(self.b, sigma=sigma)
        # apply sobel
        isob = ndimage.sobel(gb, axis=0)
        jsob = ndimage.sobel(gb, axis=1)
        sob = np.hypot(isob, jsob)
        # contour plot
        cs = ax.contourf(sob)
        fig.colorbar(cs)
        fig.savefig("sobel.png")

    def canny_interface(self, sigma=4, lo=None, hi=None):
        """Extract the interface with the canny edge detector."""
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Interface using canny edge detection')
        ax.axis('off')
        # extract the interface
        cb = skif.canny(self.b, sigma=sigma,
                        low_threshold=lo,
                        high_threshold=hi)
        iy, ix = np.where(cb)
        s = ix.argsort()
        ax.imshow(self.b, origin='lower')
        ax.plot(ix[s], iy[s], 'ko', linewidth=1)
        fig.savefig('canny-interface.png')

    def sobel_interface(self, sigma=4, lo=None, hi=None):
        """Gaussian smooth the image and apply a sobel filter.

        Then, apply canny edge detection.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(r'$\Sigma={s}$, hi={hi}, lo={lo}'.format(s=sigma, hi=hi, lo=lo))
        ax.axis('off')

        # apply some smoothing
        gb = ndimage.gaussian_filter(self.b, sigma=sigma)
        # apply sobel
        isob = ndimage.sobel(gb, axis=0)
        jsob = ndimage.sobel(gb, axis=1)
        sob = np.hypot(isob, jsob)
        # contour plot
        cs = ax.contourf(sob)
        fig.colorbar(cs)
        # get the interface and overplot
        cb = skif.canny(self.b, sigma=sigma,
                        low_threshold=lo,
                        high_threshold=hi)
        iy, ix = np.where(cb)
        s = ix.argsort()
        ax.plot(ix[s], iy[s], 'ko', linewidth=3)

        fig.savefig('sobel-interface.png')

    def display(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(self.im, origin='lower')
        plt.draw()
        plt.show()

if __name__ == '__main__':
    sigma = int(sys.argv[1])
    print "sigma = {sigma}".format(sigma=sigma)
    im = LabImage('img.jpg')
    print("channels")
    im.channels()
    print("gaussian")
    im.gaussian()
    print("threshold")
    im.threshold()
    print("canny interface")
    im.canny_interface(sigma=sigma)
    print("sobel interface")
    im.sobel_interface(sigma=sigma)
