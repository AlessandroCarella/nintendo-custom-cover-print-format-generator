from os import listdir
from os.path import join, abspath, dirname, splitext, basename, exists
import cv2
import numpy as np
import pickle

def createBlankImageLike(image):
    # Get the size of the image
    height, width, _ = image.shape

    # Create a blank image with the same size
    blankImage = np.full((height, width, 3), (255, 255, 255), dtype=np.uint8)

    return blankImage

def findSubimageCoordinates(image, subimage) -> list:
    # Convert the images to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    subimageGray = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(imageGray, subimageGray, cv2.TM_CCOEFF_NORMED)

    # Define a threshold to determine the matching areas
    threshold = 0.9 
    locations = np.where(result >= threshold)

    coordinates = []
    for pt in zip(*locations[::-1]):
        x1, y1 = pt
        x2, y2 = x1 + subimage.shape[1], y1 + subimage.shape[0]
        coordinates.append([x1, y1, x2, y2])

    return coordinates [0]

def generateCoordinates () -> dict:
    templatePath = join(dirname(abspath(__file__)), "template.png")
    coverPath = join(dirname(abspath(__file__)), "templateCover.png")
    frontPath = join(dirname(abspath(__file__)), "templateFront.png")
    backPath = join(dirname(abspath(__file__)), "templateBack.png")
    spinePath = join(dirname(abspath(__file__)), "templateSpine.png")

    if exists (templatePath) and exists (coverPath) and exists (frontPath) and exists (backPath) and exists (spinePath):
        # Open the template image
        templatePrint = cv2.imread(templatePath)

        templateCover = cv2.imread(coverPath) 
        coverCoordinates = findSubimageCoordinates(templatePrint, templateCover)

        templateFront = cv2.imread(frontPath)
        frontCoordinates = findSubimageCoordinates(templatePrint, templateFront)

        templateBack = cv2.imread(backPath)
        backCoordinates = findSubimageCoordinates(templatePrint, templateBack)

        templateSpine = cv2.imread(spinePath)
        spineCoordinates = findSubimageCoordinates(templatePrint, templateSpine)

        return {
            "templatePrint": createBlankImageLike(templatePrint),
            "templateCover": coverCoordinates,
            "templateFront": frontCoordinates,
            "templateBack": backCoordinates,
            "templateSpine": spineCoordinates,
        }
    else:
        raise Exception ("There is no template images to generate coordinates from, check the documentation to proceed.")
    
def getCoordinates () -> dict:
    """
    return dict object structured as such:
    {
        "templatePrint": templatePrintBlank,
        "templateCover": templateCover,
        "templateFront": templateFront,
        "templateBack": templateBack,
        "templateSpine": templateSpine,
    }
    """
    coordinatesFilePath = (join(dirname(abspath(__file__)), "coordinates.pickle"))

    if exists (coordinatesFilePath):
        with open (coordinatesFilePath, "rb") as f:
            coordinates = pickle.load(f)
    else:
        coordinates = generateCoordinates()    
        #with open (coordinatesFilePath, "wb") as f:
        #    pickle.dump(coordinates, f)

    return coordinates