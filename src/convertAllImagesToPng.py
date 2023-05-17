from os import listdir, remove
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

def convertAllImagesToPng ():
    imagesDirsPath = [
        join(dirname(abspath(__file__)), "../backs"),
        join(dirname(abspath(__file__)), "../cover"),
        join(dirname(abspath(__file__)), "../fronts"),
        join(dirname(abspath(__file__)), "../spines")
    ]
    
    toRemovePaths = []

    for imagesDirPath in imagesDirsPath:
        for image in listdir(imagesDirPath):
            if not "png" in splitext(basename(image))[1]:
                oldImagePath = join(imagesDirPath, image)
                toRemovePaths.append(oldImagePath)
                convertImageToPng (
                    oldImagePath,
                    join(imagesDirPath, splitext(basename(image))[0] + ".png")
                )

    for path in toRemovePaths:
        remove(path)