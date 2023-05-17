from os import listdir, makedirs
from os.path import join, abspath, dirname, splitext, basename, exists, isdir
import cv2
import numpy as np
from PIL import Image

from coordinates.getCoordinates import getCoordinates, getTemplateCoverSizes

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
    pathCoversDir = join(dirname(abspath(__file__)), "../source images/covers")
    backs = []
    fronts = []

    coversPaths = listdir(pathCoversDir)
    if (len(coversPaths) != 1):
        coversPaths = putTemplateImagesFirst (coversPaths)
        coversPaths.pop(0)
        
    for cover in coversPaths:
        back, front = splitCover (join(pathCoversDir, cover), templateCoordinates)
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

def putTemplateImagesFirst(paths:list[str]) -> list[str]:
    pos = -1
    for path in paths:
        if "AAA do not remove please" in path:
            pos = paths.index(path)
    if pos != -1:
        templateImagePath = paths.pop(pos)
        print (templateImagePath)
        paths.insert(0, templateImagePath)
    
    return paths


def getCv2ImReadObjFromDirPath (path:str):
    output = []

    if isdir (path):
        images = putTemplateImagesFirst(listdir (path))
        for image in images:
            output.append (cv2.imread (join (path, image)))

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

def cleanImages (backs:list, fronts:list, spines:list) -> tuple [list, list, list]:
    if len(backs) != 1:
        backs.pop(0)
    if len(fronts) != 1: 
        fronts.pop(0)
    if len(spines) != 1:
        spines.pop(0)
    return backs, fronts, spines 

def generateAllCombinations (withCoverSplit:bool):
    templateCoordinates = getCoordinates ()
    templateCoverSize = getTemplateCoverSizes (templateCoordinates)

    backs, fronts, spines = getBacksFrontsAndSpinesFromFolders ()

    if withCoverSplit:
        additionalBacks, additionalFronts = getCoverSplit (templateCoordinates)
        backs.extend (additionalBacks)
        fronts.extend (additionalFronts)

    backs, fronts, spines = cleanImages (backs, fronts, spines)

    dirPath = join(dirname(abspath(__file__)), "../generatedImages/allCombinations")
    createFolderIfNotExists (dirPath)

    imagesGeneratedCounter = 0
    for back in backs:
        for front in fronts:
            for spine in spines:
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

generateAllCombinations (True)
