from django.urls import path
from .views import ExtractionFileView, PdfToTextAPIView, PdfToTextView, PdfToTextAPIDownloadView, \
    PdfToTextAPIUploadView, PdfToTextUploadView, ErrorView

app_name = 'extraction'

urlpatterns = [

    path('', ExtractionFileView.as_view(), name='extraction_file_view'),
    path('pdftotext', PdfToTextView.as_view(), name='extraction_file'),
    # path('pdftotext/download', PdfToTextDownloadView.as_view(), name='pdf_to_text_download'),
    path('pdftotext/upload', PdfToTextUploadView.as_view(), name='pdf_to_text_upload'),

    # Info page
    path('info', ErrorView.as_view(), name='info'),


    # API for Extraction
    path('api/pdftotext', PdfToTextAPIView.as_view(), name='pdf_to_text_api'),

    # API for Download
    path('api/pdftotext/download', PdfToTextAPIDownloadView.as_view(), name='pdf_to_text_download_api'),

    # API for Upload to S3
    path('api/pdftotext/upload', PdfToTextAPIUploadView.as_view(), name='pdf_to_text_upload_api'),

]
