from django.db import models


class SignatureManager(models.Manager):

    def save_pdf(self, signature_id, pdf_name):
        signature = self.filter(id=signature_id).first()
        signature.pdf = pdf_name
        signature.save()
