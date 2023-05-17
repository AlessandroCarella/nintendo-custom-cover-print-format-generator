from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import os
from os.path import join, dirname, abspath
import glob
from PyPDF2 import PdfWriter, PdfReader

def createPdfWithImages(images_folder, outputFile):
    # Get the list of PNG images in the folder
    imageFiles = glob.glob(os.path.join(images_folder, '**/*.png'), recursive=True)

    # Create a new PDF file
    pdf = PdfWriter()

    # Loop through each image file
    for imageFiles in imageFiles:
        # Create a new page in the PDF
        c = canvas.Canvas('temp.pdf', pagesize=landscape(A4))

        # Calculate the centered position for the image
        imageWidth = 208 * mm
        imageHeight = 160.5 * mm
        x = (A4[1] - imageWidth) / 2
        y = (A4[0] - imageHeight) / 2

        # Draw the image on the page
        c.drawImage(imageFiles, x, y, width=imageWidth, height=imageHeight)

        # Save the modified page to the PDF
        c.showPage()
        c.save()

        # Merge the modified page into the final PDF
        with open('temp.pdf', 'rb') as f:
            modifiedPage = PdfReader (f)
            pdf.add_page(modifiedPage.pages[0])

    # Write the final PDF file
    with open(outputFile, 'wb') as f:
        pdf.write(f)

    # Remove the temporary file
    os.remove('temp.pdf')

def createPdfFromAllGeneratedImages ():
    # Usage example
    createPdfWithImages(
        join(dirname(abspath(__file__)), "../generatedImages"), 
        join(dirname(abspath(__file__)), '../print me.pdf')
    )

createPdfFromAllGeneratedImages()