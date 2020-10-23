import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import copy
import random


# Function that colors the leaves and background and saves image
def save_colors(img, markers, path):
    img_tmp = copy.deepcopy(img)
    img_tmp[markers < 2] = (0,0,0)
    for i in range(2, markers.max() + 1):
        img_tmp[markers == i] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    cv.imwrite(path, img_tmp)


# Function that calculates the dice coefficient
def dice_compare(path_gt, path_seg):
    img_tmp = cv.imread(path_gt)
    img_tmp = cv.cvtColor(img_tmp, cv.COLOR_BGR2GRAY)
    thresh, gt = cv.threshold(img_tmp, 0, 255, cv.THRESH_BINARY)
                    
    img_tmp = cv.imread(path_seg)
    img_tmp = cv.cvtColor(img_tmp, cv.COLOR_BGR2GRAY)
    thresh, seg = cv.threshold(img_tmp, 0, 255, cv.THRESH_BINARY)
                
    x = 255
    tmp = np.sum(seg[gt==x])*2.0 / (np.sum(seg[seg==x]) + np.sum(gt[gt==x]))
    # Comment this line to NOT print results for every image
    print("Dice coefficient for "+str(path_seg)+":   "+str(tmp))
    
    return tmp


def main():
    allres = []
    
    for i in range(0, 3):
        for j in range(0, 5):
            dice = []
            for k in range(0, 10):
                for l in range(0, 6):
        
                    # Reading image
                    path = "multi_plant/rgb_0"+str(i)+"_0"+str(j)+"_00"+str(k)+"_0"+str(l)+".png"
                    img = cv.imread(path, cv.IMREAD_COLOR)

                    # Converting to HSV (for inRange)
                    hsv = cv.cvtColor(img , cv.COLOR_BGR2HSV)

                    # Selecting colors using inRange
                    green = cv.inRange(hsv, (30, 30, 30), (70, 128, 110))

                    # noise removal
                    kernel = np.ones((3,3),np.uint8)
                    opening = cv.morphologyEx(green,cv.MORPH_OPEN,kernel, iterations = 1)

                    #Finding sure background area
                    sure_bg = cv.dilate(opening,kernel,iterations=7)
    
                    # Finding sure foreground area
                    dist_transform = cv.distanceTransform(opening,cv.DIST_L2,5)
                    ret, sure_fg = cv.threshold(dist_transform,0.3*dist_transform.max(),255,0)

                    # Finding unknown region
                    sure_fg = np.uint8(sure_fg)
                    unknown = cv.subtract(sure_bg,sure_fg)

                    # Marker labelling
                    ret, markers = cv.connectedComponents(sure_fg)
                    
                    # Add one to all labels so that sure background is not 0, but 1
                    markers = markers+1
                    
                    # Now, mark the region of unknown with zero
                    markers[unknown==255] = 0

                    # Applying the Watershed algorithm
                    markers = cv.watershed(img,markers)
                    img[markers == -1] = [255,0,0]

                    path_gt = "multi_label/label_0"+str(i)+"_0"+str(j)+"_00"+str(k)+"_0"+str(l)+".png"
                    path_seg = "results/rgb_0"+str(i)+"_0"+str(j)+"_00"+str(k)+"_0"+str(l)+".png"
                    
                    save_colors(img, markers, path_seg)

                    dice.append(dice_compare(path_gt, path_seg))

                    l+=1
                    #end of l loop
                l=0    
                k+=1
                #end of k loop
            print("Plant "+str(i)+":"+str(j)+" - Dice: "+str(np.mean(dice)))
            allres.append(np.mean(dice))
            k=0
            j+=1
            #end of j loop
        j=0
        i+=1
        #end of i loop
    print("Done!")
    print("-------------------------------------------")
    print("Mean of all: "+ str(np.mean(allres)))

if __name__=="__main__":
    main()
