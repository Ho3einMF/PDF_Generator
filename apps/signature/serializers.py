from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.signature.models import Signature
from apps.signature.utils import calculate_image_checksum


class SignatureUploadSerializer(serializers.ModelSerializer):

    def validate_image(self, value):
        uploaded_checksum = calculate_image_checksum(value)
        if Signature.objects.filter(user_id=self.context['request'].user.id, image_checksum=uploaded_checksum).exists():
            raise ValidationError('This file has already been uploaded.')
        return value

    def validate(self, data):
        data = super().validate(data)
        data["user"] = self.context["request"].user
        data["image_checksum"] = calculate_image_checksum(data["image"])

        return data

    class Meta:
        model = Signature
        fields = ('image',)
