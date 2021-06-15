from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os, shutil
import requests
from django.conf import settings


class PDF2Text():

    def __init__(self, file, filename, username):
        self.pdf_file_path = file
        self.filename = filename
        self.page_counter = 1
        self.username = username
        text_file = username+'_'+str(filename)+'.txt'
        self.text_file = os.path.join(settings.MEDIA_ROOT, 'text_files/' + text_file)

    def __str__(self):
        return "Converts PDF to Txt"

    def clear_directory(self, directories: list):

        for dir in directories:
            dir = os.path.join(settings.MEDIA_ROOT, dir)
            for files in os.listdir(dir):
                path = os.path.join(dir, files)
                try:
                    if self.username in path:
                        shutil.rmtree(path)
                except OSError:
                    os.remove(path)

    def pdf2image(self):
        # Store all the pages of the PDF in a variable
        pages = convert_from_path(self.pdf_file_path, thread_count=3)

        for page in pages:
            filename = self.username+"_"+ self.filename+"_page_" + str(self.page_counter) + ".jpg"
            tmp_images = os.path.join(settings.MEDIA_ROOT, 'pdf_images/'+filename)
            page.save(tmp_images, 'JPEG')
            self.page_counter += 1

    def image2text(self):
        self.pdf2image()
        with open(self.text_file,'a') as file:
            for image_counter in range(1, self.page_counter):
                filename = self.username + "_" + self.filename + "_page_" + str(image_counter) + ".jpg"
                tmp_images = os.path.join(settings.MEDIA_ROOT, 'pdf_images/' + filename)
                text = str(pytesseract.image_to_string(Image.open(tmp_images)))
                file.write(text)

        self.clear_directory(['pdf_images', 'tmp'])

        return self.text_file
