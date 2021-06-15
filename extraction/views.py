from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import requests
import os
import glob
import json
import uuid

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .conf import *
from .ocr_extraction.pdf_data_extraction import PDF2Text

from authentication.forms import LoginForm

import logging

logger = logging.getLogger("pdf_extractor_log")

# Create your views here.


class ExtractionFileView(View):

    template_name = 'fileview/pdfview.html'

    @staticmethod
    def pdf_files():
        directory = FILE_DIR
        os.chdir(directory)
        pdf_files = list()
        extensions = ['*.pdf', '*.PDF']
        for ext in extensions:
            for pdf_file in glob.glob(ext):
                file_size = '{0:.2f}'.format(os.path.getsize(pdf_file)/1024)
                data = {'file_name': pdf_file, 'file_size':file_size, 'file': directory+'/'+pdf_file}
                pdf_files.append(data)
        return pdf_files

    def get(self, request):
        if request.session.get('access_token'):

            # getting all the files
            pdf_files = self.pdf_files()

            return render(request, self.template_name,
                          {'files': pdf_files, 'username': request.session.get('username')})

        return HttpResponseRedirect(reverse('authentication:user_login'))


class PdfToTextView(View):

    def get(self, request):
        if request.session.get('username'):
            return HttpResponseRedirect(reverse('extraction:extraction_file_view'))

        return HttpResponseRedirect(reverse('authentication:user_login'))

    def post(self, request):
        file = request.POST
        file = file['filename']
        upload_file = open(file, 'rb')
        url = request.get_host()
        headers = {"Authorization": "Bearer " + request.session.get('access_token')}
        pdftotext_response = requests.post(url='http://' + url + '/extract/api/pdftotext',
                                           files={"upload_file": upload_file},
                                           data={'username': request.session.get('username')},
                                           headers=headers)
        data = json.loads(pdftotext_response.content)
        if pdftotext_response.status_code == status.HTTP_200_OK:
            return render(request, 'textview/pdftotext.html',
                          {'extracted_text': data['extracted_data'], 'textfile': data['textfile'],
                           'username': request.session.get('username')})

        return HttpResponseRedirect('/extract/info?error='+data['detail'])


class PdfToTextAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request_file = request.FILES
            file_data = request_file['upload_file']
            filename = str(request.data['upload_file'])+'_'+request.data.get('username')
            logger.info(f'Performing the pdf to text extraction for file :{str(filename)}')
            path = default_storage.save('tmp/' + filename, ContentFile(file_data.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            pdf2text = PDF2Text(tmp_file, filename, request.data.get('username'))
            # pdf2text.pdf2image()
            text_file = pdf2text.image2text()
            logger.info(f'Text file generated')
            with open(text_file, 'r') as text_file:
                file_content = text_file.read()

        except Exception as exception:
            logger.error(f'Unable to perform Pdf to Text extraction :{str(exception)}')
            return Response({'detail':'Unable to perform Pdf to Text extraction'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'extracted_data': file_content, 'textfile': str(text_file.name)},status=status.HTTP_200_OK)


# class PdfToTextDownloadView(View):
#     template_name = 'textview/pdftotext.html'
#     def post(self,request):
#         data = request.POST
#         download_file_path = data['download_file_path']
#         url = request.get_host()
#         data = {'download_file_path': download_file_path}
#         download_response = requests.post(url='http://' + url + '/extract/api/pdftotext/download',
#                                         data=json.dumps(data),
#                                         headers={"Content-Type": "application/json"})
#         response = json.loads(download_response.content)
#
#         return render(request, self.template_name, {'msg': response['msg']})


class PdfToTextAPIDownloadView(APIView):

    def post(self, request):
        logger.info('Starting the Download Process')
        data = request.POST
        download_file_path = data['download_file_path']
        try:
            with open(download_file_path, "r") as file:
                response = HttpResponse(file, content_type='application/text')
                filename = str(uuid.uuid4()) + '.txt'
                response['Content-Disposition'] = 'attachment; filename=' + filename
            return response

        except Exception as exception:
            logger.error(f'Download Failed :{str(exception)}')
            return Response({'detail': 'Download Failed, please try again!'}, status=status.HTTP_412_PRECONDITION_FAILED)


class PdfToTextUploadView(View):

    template_name = 'textview/pdftotext.html'

    def post(self, request):
        data = request.POST
        upload_file_path = data['upload_file_path']
        url = request.get_host()
        data = {'upload_file_path': upload_file_path}
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + request.session.get('access_token')}
        upload_response = requests.post(url='http://' + url + '/extract/api/pdftotext/upload',
                                        data=json.dumps(data),
                                        headers=headers)
        response = json.loads(upload_response.content)

        if upload_response.status_code == status.HTTP_200_OK:
            return HttpResponseRedirect('/extract/info?message=' + response['detail'])

        return HttpResponseRedirect('/extract/info?error=' + response['detail'])


class PdfToTextAPIUploadView(APIView):

    permission_classes = [IsAuthenticated]
    # s3 = boto3.resource('s3', aws_access_key_id=KEY_ID, aws_secret_access_key=ACCESS_KEY,
    #                     config=Config(signature_version='s3v4'), region_name= REGION_NAME)

    def post(self,request):
        data = request.data
        upload_file_path = data['upload_file_path']
        logger.info(f'Starting the file upload process : {str(upload_file_path)}')
        # with open(upload_file_path, 'rb') as file:
        #
        #     destination = str(uuid.uuid4())+'_'+os.path.basename(upload_file_path)
        #     try:
        #         self.s3.Bucket(BUCKET_NAME).put_object(Key=destination, Body=file)
        #     except ClientError as exception:
        #         # raise Exception(e)
        #         return Response({'detail': 'Failed to Upload to AWS S3'}, status=status.HTTP_412_PRECONDITION_FAILED)

        return Response({'detail': 'Uploaded Successfully to AWS S3'}, status=status.HTTP_200_OK)


class ErrorView(View):

    template_name = 'info/info.html'

    def get(self, request):
        detail = request.GET
        if detail.get('error'):
            if 'Given token not valid for any token type' in detail.get('error'):
                request.session.flush()
                form = LoginForm()
                return render(request, 'login/login.html',
                              {"form": form, "error": {'msg': 'Session Expired. Login Again'}})
            return render(request, self.template_name, {'error':detail['error']})
        elif detail.get('message'):
            return render(request, self.template_name, {'message': detail['message']})

        return render(request, self.template_name, {'error': 'Something went wrong'})