from celery.result import AsyncResult
from django.core.cache import caches
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.signature.constants import SIGNATURE_TIMEOUT
from apps.signature.models import Signature
from apps.signature.serializers import SignatureUploadSerializer
from apps.signature.tasks import pdf_generate, pdf_task_manger

# Create your views here.


signature_cache = caches['signature']


class UploadSignatureView(CreateAPIView, UpdateAPIView):
    queryset = Signature.objects.all()
    serializer_class = SignatureUploadSerializer
    http_method_names = ('post', 'put')

    def get_object(self):
        return Signature.objects.filter(user_id=self.request.user.id).first()


class PDFAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        # database check
        signature = Signature.objects.filter(
            user_id=request.user.id, pdf__isnull=False).exclude(pdf='').first()
        if signature:
            return redirect(signature.pdf.url)

        # cache check
        task_id = signature_cache.get(f'{request.user.id}')
        if task_id:
            task = AsyncResult(task_id)

            if task.status == 'PENDING':
                return Response({'detail': 'Not ready yet !!!'}, status=status.HTTP_425_TOO_EARLY)

            elif task.status == 'FAILURE':
                return Response({'detail': 'PDF generation failed'}, status=status.HTTP_408_REQUEST_TIMEOUT)

        # run celery task to generate pdf
        else:
            task = pdf_task_manger.delay(user_id=request.user.id)
            signature_cache.set(f'{request.user.id}', task.id, SIGNATURE_TIMEOUT)
            return Response({'detail': 'PDF generation task queued!'}, status=status.HTTP_202_ACCEPTED)
