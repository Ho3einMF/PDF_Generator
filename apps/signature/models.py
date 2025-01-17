from django.contrib.auth.models import AbstractUser, User
from django.db import models

from apps.signature.mangers import SignatureManager
from apps.signature.utils import signature_upload_path


# Create your models here.


class Signature(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='signature')

    image = models.ImageField(upload_to=signature_upload_path)
    image_checksum = models.CharField(max_length=64)

    pdf = models.FileField(blank=True, null=True)

    objects = SignatureManager()
