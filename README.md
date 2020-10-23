Warsaw, 6 thof January 2020

## Mikołaj Rajch

# Plant Segmentation and Labeling


## Contents

- 1 Introduction
   - 1.1 Project goals description
   - 1.2 Program description
- 2 Testing
- 3 Results
   - 3.1 Dice Coefficient
   - 3.2 Summary
- 4 References


## 1 Introduction

### 1.1 Project goals description

Image segmentation is a commonly used technique in digital image processing
and analysis to partition an image into multiple parts or regions, often based on the
characteristics of the pixels in the image. Image segmentation could involve separating
foreground from background, or clustering regions of pixels based on similarities in
color or shape[1].
The goal of this project is to write an algorithm that takes images from a image set
of growing plants, separates the plants from the background and colors each individual
leaf a different color.
The image set contains 900 images of different growing stages of 15 plants.
It is important for the program to recognize new leaves as they are developing.


### 1.2 Program description


The first thing that needs to be done is to separate the plant from the background.
Since the plants are all different shades of green, we can specify some range of colors
to differentiate pixels, which colors are in our range from those, which colors are not.
The range of colors (given in HSV color model) that I found to be working best overall
was from(30, 30 ,30)to(70, 128 ,110).

After loading the image and converting its color model from BGR (which is default
for OpenCV) to HSV, functioncv.inRange()is called that colors every pixel that
is in our specified range white, and all the rest (background) black.
```
# Reading image
path = " multi_plant /rgb_0"+s t r ( i )+"_0"+s t r ( j )+"_00"+s t r (k)+"_0"+
s t r ( l )+". png"
img = cv. imread ( path , cv .IMREAD_COLOR)

# Converting to HSV ( f o r inRange )
hsv = cv. cvtColor ( img , cv .COLOR_BGR2HSV)

# S e l e c t i n g c o l o r s using inRange
green = cv. inRange ( hsv , (30 , 30 , 30) , (70 , 128 , 110) )

```

Of course composing a color range so that only the plant gets separated from the
background is nearly impossible, so naturally there is a large possibility that other
objects may have gotten included too. To reduce this effect, we can remove noise from
the image by morphological opening using OpenCV functioncv.morphologyEx().
```

# noise removal
kernel = np. ones ((3 ,3) ,np. uint8 )
opening = cv. morphologyEx ( green , cv .MORPH_OPEN, kernel , i t e r a t i o n s =1)

```
Now that the image is similar to the original plant’s area, we want to differentiate
the leaves between each other. Considering that the leaves are touching, we need to
know the transform distance between the objects we want to differentiate, and after
finding it we can use thresholding to approximate the foreground of our image. We
also dilate it to approximate its background.

Those two images subtracted also give us the region we do not know whether is
background or foreground.

```
#Finding sure background area
sure_bg = cv. d i l a t e ( opening , kernel , i t e r a t i o n s =7)

# Finding sure foreground area
dist_transform = cv. distanceTransform ( opening , cv .DIST_L2, 5 )
ret , sure_fg = cv. threshold ( dist_transform , 0. 3∗dist_transform
.max() ,255 ,0)

# Finding unknown region
sure_fg = np. uint8 ( sure_fg )
unknown = cv. subtract ( sure_bg , sure_fg )


```
Now that we know the region of our leaves, background and all, we can create a
marker (an array of same size as the original image) to label the regions inside it.
This is how we will differentiate between leaves. The regions we know for sure are
labelled with any positive integers, but different integers, and the area we don’t know
for sure are just left as zero. For this we usecv.connectedComponents(). It labels
background of the image with 0, then other objects are labelled with integers starting
from 1.
```
# Marker l a b e l l i n g
ret , markers = cv. connectedComponents ( sure_fg )

# Add one to a l l l a b e l s so that sure background i s not 0 , but 1
markers = markers+

# Now, mark the region of unknown with zero
markers [ unknown==255] = 0

```
Finally, we usecv.watershed(), a function that performs a marker-based image
segmentation using the watershed algorithm. The function implements one of the
variants of watershed, a non-parametric marker-based segmentation algorithm[2]. We
made sure that the background is not marked with 0, because then the algorithm will
treat is as unknown area.
```
# Applying the Watershed algorithm
markers = cv. watershed (img , markers )
img [ markers == −1] = [255 ,0 ,0]


```
Now that the marker image was modified, and boundary region was marked with
-1, we can see the results of the program.

## 2 Testing


To test the accuracy of the program, an auxiliary function computing the dice
coefficient was used:
```
# Function that c a l c u l a t e s the dice c o e f f i c i e n t
def dice_compare ( path_gt , path_seg ) :
img_tmp = cv. imread ( path_gt )
img_tmp = cv. cvtColor (img_tmp , cv .COLOR_BGR2GRAY)
thresh , gt = cv. threshold (img_tmp , 0 , 255 , cv .THRESH_BINARY)

img_tmp = cv. imread ( path_seg )
img_tmp = cv. cvtColor (img_tmp , cv .COLOR_BGR2GRAY)
thresh , seg = cv. threshold (img_tmp , 0 , 255 , cv .THRESH_BINARY)


x = 255
tmp = np. sum( seg [ gt==x ] )∗2.0 / (np. sum( seg [ seg==x ] ) + np. sum(
gt [ gt==x ] ) )
# Comment t h i s l i n e to NOT print r e s u l t s f o r every image
print ( "Dice c o e f f i c i e n t f o r "+s t r ( path_seg )+" : "+s t r (tmp) )


return tmp
```

However, since the pictures weren’t taken in the same time, naturally they differ
between each other (things like lighting, shadows etc.). That turned out to be some-
what problematic when choosing the color range to assess plants is all images. For
example, when a plant grew, its shadow grew with it, and considering it was also
in some dark shade of green, it heavily influenced the plant contour on the image
aftercv.inRange(). But often reducing the range for one image caused the opposite
problems for another, causing the plant to not be fully included after transformation.

Considering that there was no perfect color range for all images, I have used a sim-
ple color range calibrator program (to somewhat counter that occurrence) described
inHSVcalibrator.py, that helps to choose the best HSV color range for a singular
image. It uses the same algorithm of segmentation and labeling, but contains sliders
and thresholded image that changes in response to slider’s value changing, so that
testing the whole process would be easier for different color ranges.

Of course this process would take a really long time for all 900 images, so a fixed
range with best mean of results was used for all of them instead.


## 3 Results

### 3.1 Dice Coefficient


The accuracy of whole process was measured with dice coefficient:

```
Dice=2( |A∪B| ) / ( |A|+|B| )
```

The program measures dice coefficient for every image, as well as mean for ev-
ery plant and all images. Depending on values of variables in the code (color ranges,
iterations during noise reduction etc.), the mean overall accuracy was between ap-
proximately 90% and 92%. For color range(30, 30 ,30)to(70, 128 ,110)and variables
set as incode.py, the mean for all images was 92 .5976498523%, with mean for every
plant as follows:

```
Plant   Mean Dice Coefficient (in %)
0 : 0    91.9626871182
0 : 1    94.4733040281
0 : 2    93.4506623536
0 : 3    91.9368467918
0 : 4    92.5243005124
1 : 0    90.7399048192
1 : 1    94.2634325508
1 : 2    92.9689051991
1 : 3    93.1735053746
1 : 4    91.5260306550
2 : 0    91.8678927297
2 : 1    93.7965146802
2 : 2    93.3169345125
2 : 3    91.9036823775
2 : 4    91.0601440825
Table with mean dice coefficient for every plant
```
As we can see, the mean dice coefficient does not differ too much for each plant
and is around or above 90%. The results of course could be higher, if specific variables
were set for every individual image. It would also be easier to do that using previously
mentioned HSVcalibrator.


### 3.2 Summary

Unfortunately, due to a number of images, it was really hard to determine optimal
color range and variable values combination. The most common problem was the
changing shadow on flowerpots that often was in the set color range. This caused the
area of the plant, as well as the colored regions of each leaf, to be disrupted.

This problem usually occurred for plants in the middle stages of growth. For
bigger plants this also happened sometimes, as well as a completely opposite problem
of losing some area in the center of the plant. This happened usually when the leaves
were bigger (stalk was too small).


The program worked best for plants in the beginning stages of their growth, pre-
cisely assessing the area of the whole plant, as well as each individual leaf.

Overall, the algorithm assessed the areas of plants with satisfactory correctness.
The only more severe problem would be the estimation of region of each individual
leaf. Because of their irregular shape and size, and also elements of the background
of some images, the program sometimes creates more colored areas than needed, or
incorrectly assumes which area belongs to which leaf.

By picking specific color ranges for thresholding for individual images, most of the
previously mentioned problems occurred on much smaller scale, and the results were
overall better.


## 4 References

[1] https://www.mathworks.com/discovery/image-segmentation.html

[2] https://docs.opencv.org/master/d7/d1b/group__imgproc__misc.htmlga
243e4d3f95165d55a618c65ac6e

[3] https://docs.opencv.org/master/d3/db4/tutorial_py_watershed.html


