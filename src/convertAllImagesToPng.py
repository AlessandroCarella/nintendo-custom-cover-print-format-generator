from os import listdir
from os.path import join, abspath, dirname, splitext, basename
from PIL import Image


def convertImageToPng(inputPath, outputPath):
    # Open the image file
    image = Image.open(inputPath)

    # Convert the image to RGB if it has an alpha channel
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        image = image.convert('RGBA')
    else:
        image = image.convert('RGB')

    # Save the image as PNG
    image.save(outputPath, format='PNG')

    # Close the image
    image.close()

    print(f"Image converted to PNG: {outputPath}")

pathCoverDir = join(dirname(abspath(__file__)), "../cover")
for image in listdir(pathCoverDir):
    if not "png" in splitext(basename(image))[1]:
        convertImageToPng (
            join (pathCoverDir, image),
            join(pathCoverDir, splitext(basename(image))[0] + ".png")
        )