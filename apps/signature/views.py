from celery.result import AsyncResult
from django.core.cache import caches
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.signature.constants import SIGNATURE_TIMEOUT
from apps.signature.models import Signature
from apps.signature.serializers import SignatureUploadSerializer
from apps.signature.tasks import generate_pdf

# Create your views here.


signature_cache = caches['signature']


class UploadSignatureView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SignatureUploadSerializer


class PDFAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, signature_id):

        # database check
        signature = Signature.objects.filter(
            id=signature_id, user_id=request.user.id, pdf__isnull=False).exclude(pdf='').first()
        if signature:
            return redirect(signature.pdf.url)

        # cache check
        task_id = signature_cache.get(f'{request.user.id}_{signature_id}')
        if task_id:
            task = AsyncResult(task_id)

            if task.status == 'PENDING':
                return Response({'detail': 'Not ready yet !!!'}, status=status.HTTP_425_TOO_EARLY)

            elif task.status == 'FAILURE':
                return Response({'detail': 'PDF generation failed'}, status=status.HTTP_408_REQUEST_TIMEOUT)

        # run celery task to generate pdf
        else:
            task = generate_pdf.delay(signature_id)
            signature_cache.set(f'{request.user.id}_{signature_id}', task.id, SIGNATURE_TIMEOUT)
            return Response({'detail': 'PDF generation task queued!'}, status=status.HTTP_202_ACCEPTED)
