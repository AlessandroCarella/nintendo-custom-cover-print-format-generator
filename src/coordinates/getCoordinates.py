from PIL import Image, ImageDraw
from os import listdir
from os.path import join, abspath, dirname, splitext, basename, exists
import cv2
import numpy as np
import pickle

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

    if exists (coverPath) and exists (frontPath) and exists (backPath) and exists (spinePath):
        templateCover = cv2.imread(coverPath) 
        templateFront = cv2.imread(frontPath)
        templateBack = cv2.imread(backPath)
        templateSpine = cv2.imread(spinePath)

        return {
            "templateCover": findSubimageCoordinates(templateCover, templateCover),
            "templateFront": findSubimageCoordinates(templateCover, templateFront),
            "templateBack": findSubimageCoordinates(templateCover, templateBack),
            "templateSpine": findSubimageCoordinates(templateCover, templateSpine)
        }
    else:
        raise Exception ("There is no template images to generate coordinates from, check the documentation to proceed.")

def getCoordinates () -> dict:
    """
    return dict object structured as such:
    {
        "templateCover": template cover coordinates,
        "templateFront": template front coordinates,
        "templateBack": template back coordinates,
        "templateSpine": template spine coordinates
    }
    """
    coordinatesFilePath = (join(dirname(abspath(__file__)), "coordinates.pickle"))

    if exists (coordinatesFilePath):
        with open (coordinatesFilePath, "rb") as f:
            coordinates = pickle.load(f)
    else:
        coordinates = generateCoordinates()    
        with open (coordinatesFilePath, "wb") as f:
            pickle.dump(coordinates, f)

    return coordinates

def getTemplateCoverSizes (coordinates:dict) -> tuple:
    coverCoordinates = coordinates ["templateCover"]
            #width              # height
    return (coverCoordinates[2], coverCoordinates[3])

def testCoordinates ():
    """
    generates image from the prelevated or present coordinates with this color scheme
    colors = {
        "templateFront": "blue",
        "templateBack": "red",
        "templateSpine": "green"
    }
    """
    coordinates = getCoordinates ()

    template_cover_x1, template_cover_y1, template_cover_x2, template_cover_y2 = coordinates["templateCover"]
    template_front_x1, template_front_y1, template_front_x2, template_front_y2 = coordinates["templateFront"]
    template_back_x1, template_back_y1, template_back_x2, template_back_y2 = coordinates["templateBack"]
    template_spine_x1, template_spine_y1, template_spine_x2, template_spine_y2 = coordinates["templateSpine"]

    # Define the image size
    template_cover_width = template_cover_x2 - template_cover_x1  # Width of the template cover
    template_cover_height = template_cover_y2 - template_cover_y1  # Height of the template cover

    # Create a new blank image
    image = Image.new('RGB', (template_cover_width, template_cover_height))

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Define the regions and colors
    regions = {
        "templateFront": (template_front_x1, template_front_y1, template_front_x2, template_front_y2),
        "templateBack": (template_back_x1, template_back_y1, template_back_x2, template_back_y2),
        "templateSpine": (template_spine_x1, template_spine_y1, template_spine_x2, template_spine_y2)
    }

    colors = {
        "templateFront": "blue",
        "templateBack": "red",
        "templateSpine": "green"
    }

    # Draw the regions with respective colors
    for region, coords in regions.items():
        x1, y1, x2, y2 = coords
        color = colors[region]
        draw.rectangle([(x1, y1), (x2, y2)], fill=color)

    # Save the generated image
    image.save((join(dirname(abspath(__file__)), "coordinatesTest.png")))
