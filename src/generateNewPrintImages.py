from os import listdir, makedirs
from os.path import join, abspath, dirname, splitext, basename, exists, isdir
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


def createFolderIfNotExists(folderPath):
    if not exists (folderPath):
        makedirs(folderPath)


def getCoverSection (coverPath: str, sectionName: str, templateCoordinates: dict):
    newCoverResized = getResizedCover (coverPath, getTemplateCoverSizes (templateCoordinates))

    # Crop the sub-image
    x1,y1,x2,y2 = templateCoordinates["template" + sectionName.capitalize()]
    subImage = newCoverResized[y1:y2, x1:x2]

    return subImage

def splitCover (coverPath:str, templateCoordinates:dict):
    """
    takes in input the path of the cover to split in
    - back
    - front
    #- spine

    returns cv2.imread objects
    back, front#, spine

    #*spine is useless most of the time since the intended 
    use of the cover folder is to put the original covers there,
    if you have a cover with a spine you want to use in other covers
    use the defined method #TODO
    """
    back = getCoverSection (coverPath, "Back", templateCoordinates)
    front = getCoverSection (coverPath, "Front", templateCoordinates)
    #spine = getCoverSection (coverPath, "Spine")

    return back, front#, spine

def getCoverSplit (templateCoordinates:dict) -> tuple[list, list]:
    """
    returns 2 lists
    a list with all the backs extracted from the covers
    as cv2.imread objects
    and
    a list with all the fronts extracted from the covers
    as cv2.imread objects
    """
    pathCoversDir = join(dirname(abspath(__file__)), "../source images/backs")
    backs = []
    fronts = []
    for cover in listdir(pathCoversDir):
        back, front = splitCover (cover, templateCoordinates)
        backs.append(back)
        fronts.append(front)

    return backs, fronts

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

def getCv2ImReadObjFromDirPath (path:str):
    output = []

    if isdir (path):
        output.append (cv2.imread (path))

    return output

def getBacksFrontsAndSpinesFromFolders () -> tuple [list, list, list]:
    pathBacksDir = join(dirname(abspath(__file__)), "../source images/backs")
    pathFrontsDir = join(dirname(abspath(__file__)), "../source images/fronts")
    pathSpinesDir = join(dirname(abspath(__file__)), "../source images/spines")

    return (
        getCv2ImReadObjFromDirPath (pathBacksDir),
        getCv2ImReadObjFromDirPath (pathFrontsDir),
        getCv2ImReadObjFromDirPath (pathSpinesDir)
    )

def generateAllCombinations (withCoverSplit:bool):
    templateCoordinates = getCoordinates ()
    templateCoverSize = getTemplateCoverSizes (templateCoordinates)

    backs, fronts, spines = getBacksFrontsAndSpinesFromFolders ()

    if withCoverSplit:
        additionalBacks, additionalFronts = getCoverSplit (templateCoordinates)
        backs.extend (additionalBacks)
        fronts.extend (additionalFronts)

    dirPath = join(dirname(abspath(__file__)), "../generatedImages/allCombinations")
    createFolderIfNotExists (dirPath)

    imagesGeneratedCounter = 0
    for back in backs or [None]: #[None] is because
        for front in fronts or [None]: #there may be no images
            for spine in spines or [None]: #in the relative folders
                fileName = str(imagesGeneratedCounter) + ".png"
                generateNewCover (
                    templateCoordinates,
                    templateCoverSize,
                    back,
                    front,
                    spine,
                    join (dirPath, fileName)
                )
                imagesGeneratedCounter += 1

generateAllCombinations (False)

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