from django.urls import path

from apps.signature.views import UploadSignatureView, PDFAPIView

app_name = 'signature'
urlpatterns = [
    path('', UploadSignatureView.as_view(), name='signature'),
    path('pdf/', PDFAPIView.as_view(), name='pdf'),
]
