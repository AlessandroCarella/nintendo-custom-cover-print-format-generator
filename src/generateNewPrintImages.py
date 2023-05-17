from os import listdir
from os.path import join, abspath, dirname, splitext, basename, exists
import cv2
import numpy as np

from coordinates.getCoordinates import getCoordinates 

scaleFactorX = 1.01
scaleFactorY = 0.98

def generatePrintWithBorder(templateImage, replacement, coordinates, outPath):
    """
    saves a png file of the cover in the replacement parameter
    with the right bored to print in a4 paper format

    param:
    templateImage is a template image with boreders already in place
    taken from the coordinate object

    replacement is the new cover or front or back or spine to use

    coordinates is a coordinates subobject from the coordinate object 
    i get from getCoordinates
    to replace the front cover, for example, i would give in input
    getCoordinates["templateFront"]

    outPath is the path to save the new file to
    """
    # Extract the coordinates from the input
    x1, y1, x2, y2 = coordinates

    # Calculate the width and height of the subimage
    width = x2 - x1
    height = y2 - y1

    # Calculate the new width based on the scale factor
    newWidth = int(width * scaleFactorX)
    newHeight = int (height * scaleFactorY)

    # Resize the replacement image to the new dimensions
    replacementResized = cv2.resize(replacement, (newWidth, newHeight))

    # Calculate the difference in width between the resized replacement image and the original subimage
    widthDiff = newWidth - width
    heightDiff = newHeight - height

    # Adjust the x-coordinates of the subimage to accommodate the width difference
    x1 -= widthDiff // 2
    x2 += widthDiff - widthDiff // 2

    y1 -= heightDiff // 2
    y2 += heightDiff - heightDiff // 2

    # Replace the subimage with the replacement image
    templateImage[y1:y2, x1:x2] = replacementResized

    cv2.imwrite(outPath, templateImage)

pathCoverDir = join(dirname(abspath(__file__)), "../cover")
pathOutputDir = join(dirname(abspath(__file__)), "../outputCoversForPrint")

coordinates = getCoordinates()

templatePath = join(dirname(abspath(__file__)), "coordinates/template.png")
templatePrint = cv2.imread(templatePath)

pathOutputDir = join(dirname(abspath(__file__)), "../outputCoversForPrint")

for image in listdir(pathCoverDir):
    imageObj = cv2.imread(join (pathCoverDir, image))
    outPath = join (pathOutputDir, image)
    generatePrintWithBorder(coordinates["templatePrint"], imageObj, coordinates["templateCover"], outPath)

allPaths = []

spineCoverDir = join(dirname(abspath(__file__)), "../spines")
newCoversDir = pathOutputDir
pathOutputDir = join(dirname(abspath(__file__)), "../outputCoversSpineCombinationsForPrint")
for image in listdir(newCoversDir):
    imageObj = cv2.imread(join (newCoversDir, image)) 
    for spine in listdir(spineCoverDir):        
        if spine.split(" ")[0] in image.split(" ")[0] or spine.split(".")[0] in image.split(" ")[0]:
            spineObj = cv2.imread(join (spineCoverDir, spine))
            outPath = join(pathOutputDir, (splitext(basename(image))[0] + " + " + spine))
            allPaths.append(outPath)
            generatePrintWithBorder(imageObj, spineObj, coordinates["templateSpine"], outPath)

print (scaleFactorX)
print (scaleFactorY)