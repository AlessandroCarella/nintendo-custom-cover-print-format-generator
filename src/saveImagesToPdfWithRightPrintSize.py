from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import os
import glob
from PyPDF2 import PdfWriter, PdfReader

def create_pdf_with_images(images_folder, output_file):
    # Get the list of PNG images in the folder
    image_files = glob.glob(os.path.join(images_folder, '*.png'))

    # Create a new PDF file
    pdf = PdfWriter()

    # Loop through each image file
    for image_file in image_files:
        # Create a new page in the PDF
        c = canvas.Canvas('temp.pdf', pagesize=landscape(A4))

        # Calculate the centered position for the image
        image_width = 208 * mm
        image_height = 160.5 * mm
        x = (A4[1] - image_width) / 2
        y = (A4[0] - image_height) / 2

        # Draw the image on the page
        c.drawImage(image_file, x, y, width=image_width, height=image_height)

        # Save the modified page to the PDF
        c.showPage()
        c.save()

        # Merge the modified page into the final PDF
        with open('temp.pdf', 'rb') as f:
            modified_page = PdfReader (f)
            pdf.add_page(modified_page.pages[0])

    # Write the final PDF file
    with open(output_file, 'wb') as f:
        pdf.write(f)

    # Remove the temporary file
    os.remove('temp.pdf')

# Usage example
create_pdf_with_images(
    r'C:\Users\Alessandro\Desktop\nintendo-custom-cover-print-format-generator\cover', 
    r'C:\Users\Alessandro\Desktop\nintendo-custom-cover-print-format-generator\src\output.pdf'
)
