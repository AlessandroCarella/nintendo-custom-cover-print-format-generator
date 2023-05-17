from os import listdir, makedirs
from os.path import join, abspath, dirname, splitext, basename, exists
import cv2
import numpy as np
from PIL import Image

from coordinates.getCoordinates import getCoordinates, getTemplateCoverSizes

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
    newWidth = int(width)
    newHeight = int (height)

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

def getResizedCover (coverPath, templateSizes):
    originalImage = cv2.imread (coverPath)
    return cv2.resize(originalImage, templateSizes)

def getCoverSection (coverPath: str, sectionName: str):
    templateCoordinates = getCoordinates ()
    
    newCoverResized = getResizedCover (coverPath, getTemplateCoverSizes (templateCoordinates))

    # Crop the sub-image
    x1,y1,x2,y2 = templateCoordinates["template" + sectionName.capitalize()]
    subImage = newCoverResized[y1:y2, x1:x2]

    cv2.imwrite(join(dirname(abspath(__file__)), "ciao.png"), subImage)


def createFolderIfNotExists(folderPath):
    if not exists (folderPath):
        makedirs(folderPath)


def changeSubImage (baseImage, subImage, coordinates):
    x1, y1, x2, y2 = coordinates
    
    # Resize the replacement image to the new dimensions
    subImageResized = cv2.resize(subImage, (x2 - x1, y2 - y1))
    
    baseImage [y1:y2, x1:x2] = subImageResized
    return baseImage

def generateNewCover (coordinates:dict, sizes:list, back, front, spine, outputPath):
    """
    params:
    - coordinates is the dict with all the coordinates 
    of the cover (not needed), back, front and spine
    in the template image 
    - sizes is a list of [width, height] of the template cover
    (relative to the coordinates obviously) 
    - back, front and spine are cv2.imread objects
    of the back, front and spine images
    """
    # Create a white base image
    baseImage = np.ones((sizes[1], sizes[0], 3), dtype=np.uint8) * 255

    baseImage = changeSubImage (baseImage, back, coordinates["templateBack"])
    baseImage = changeSubImage (baseImage, front, coordinates["templateFront"])
    baseImage = changeSubImage (baseImage, spine, coordinates["templateSpine"])

    cv2.imwrite (outputPath, baseImage)

def generateAllCombinations ():
    templateCoordinates = getCoordinates ()
    templateCoverSize = getTemplateCoverSizes (templateCoordinates)

    pathBacksDir = join(dirname(abspath(__file__)), "../source images/backs")
    pathFrontsDir = join(dirname(abspath(__file__)), "../source images/fronts")
    pathSpinesDir = join(dirname(abspath(__file__)), "../source images/spines")

    dirPath = join(dirname(abspath(__file__)), "../generatedImages/allCombinations")
    createFolderIfNotExists (dirPath)

    for back in listdir(pathBacksDir) or [None]:
        for front in listdir(pathFrontsDir) or [None]:
            for spine in listdir(pathSpinesDir) or [None]:
                fileName = "Back=" + splitext(back)[0] + ", Front=" + splitext(front)[0] + ", Spine=" + splitext(spine)[0] + " " + ".png"
                generateNewCover (
                    templateCoordinates,
                    templateCoverSize,
                    cv2.imread (join(pathBacksDir, back)),
                    cv2.imread (join(pathFrontsDir, front)),
                    cv2.imread (join(pathSpinesDir, spine)),
                    join (dirPath, fileName)
                )

generateAllCombinations ()

"""
pathOutputDir = join(dirname(abspath(__file__)), "../outputCoversForPrint")

coordinates = getCoordinates()

templatePath = join(dirname(abspath(__file__)), "coordinates/template.png")
templatePrint = cv2.imread(templatePath)

pathOutputDir = join(dirname(abspath(__file__)), "../outputCoversForPrint")

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

"""