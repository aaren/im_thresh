title: Edge detection in lab images
date: 12/03/13

I've recorded some lab runs with HD video (1920x1080, 25HZ) and am
looking at simple ways to extract data from them. 

Get a single frame at 62s out of the movie

    ffmpeg -ss 62 -i cam1.MOV -t 1 img.jpg

Split into channels:

![image-decomposition](./channels.png)

It appears that the sharpest single colour indication of the
'green' fluid that forms the lower layer is the *absence* of blue.
Similarly, the sharpest indicator of the 'red' fluid of the gravity
current is the absence of green.

We don't actually care about the bulk of the fluid, only the edges,
so we need only look at gradients of the colours in an effort to
find edges.

The projection of the original image onto the rbg colourspace is
somewhat arbitrary - in general it will be some combination of rgb
that gives the best indicator of a particular type of fluid. Just
using green and blue seems like it will work for now though.

There are a couple of ways that we can proceed now. We can detect
edges across the whole image (canny edge detection) or we can do a
simple threshold to identify the fluid type and then find the edge
of that (thresholding).

#### Canny edge detection ####

- Smooth image with a gaussian, width `sigma`. This eliminates noise
  from the image.
- apply sobel operator to get gradient strength, G = Gx + Gy, across
  the image.
- Gx and Gy also give us the edge direction, which is used to remove
  pixels that don't fall along a detected edge.
- Label all points above high threshold as edges
- recursively label all points above low threshold that are
  8-connected to a labeled point as an edge.

These last two points are the 'hysteresis thresholding', which is
used to eliminate streaking in the image. The high threshold needs
to be set so that edges that aren't strong enough are eliminated.
Along a real edge we can expect the edge strength to vary, probably
dipping below our high threshold. Using just the pixels sitting
above the high threshold would result in streaking along the real
edge. The low threshold is set low enough that it will capture these
pixels on the real edge, but with the condition that they must be
connected to a pixel captured by the high threshold.

The units of the threshold values are the gradient strength.

Here's how to apply the filter:

    :::python
    from skimage.filter import canny
    bn = b.squeeze() / 255.
    sigma = 4
    lo = 0.1
    hi = 0.3
    cb = canny(bn, sigma, lo, hi)

There is a problem here in that the gaussian smoothing reduces the
resolution of the image. We can see how much by drawing the smoothed
image with varying levels of sigma:

![gaussian-comparison](./gaussian-comp.png)


#### Thresholding ####

This is quite easy really. Look at an image and pick a reasonable
threshold value; apply gaussian filter to denoise; threshold this;
find edge of threshold region.

    :::python
    t_value = 0.3
    tbn = gaussian_filter(bn, 3) < t_value
    # have to set the sigma to 0 as we've already done gaussian
    cb = canny(tbn, 0)

![threshold](./threshold.png)

The problem with this simple thresholding is that it isn't very
clever with respect to whether things are edges or not. By using the
boolean threshold stage we remove information about the strength of
edges in the image and lose the power of the hysteresis thresholding
used in the canny algorithm.

#### Setting high / low threshold values ####

The canny algorithm takes as input two threshold values for the
hysteresis thresholding stage. The appropriate value for these
varies depending on how much smoothing we apply to the source image
and will likely vary between different input images.

The units of these threshold values are that of the magnitude of the
Sobel operator over the image. 

We need a way to automatically determine the appropriate threshold 
values to use.


#### Conversion to 1d signal ####

`cb` is a 2d boolean array whereas we desire a 1d array of the
locations of the points on the interface.

We can get a list of the indices of the true elements that define
the edges and sort them in x with

    :::python
    Y, X = np.where(cb)
    s = X.argsort()
    ix, iy = X[s], Y[s]

whether these points all sit on the true interfacial line is
another question. If our canny edge detector has been effective then
perhaps this is true. In general though we cannot expect this to
work out and we need some sort of heuristic to guide us.

What do we know about the interfacial signal? It is a one
dimensional, continuous, single valued function in x that looks
pretty smooth.

1) Use an average of all of the points to reject points far away, on
the basis that the interface is broadly flat.

2) The gradient of the interface lies within certain bounds - use
this to reject somehow.

3) Actually understand the inputs to the canny filter to reject as
much as possible.

4) Use knowledge about the image to mask regions that are clearly
not the interface.

