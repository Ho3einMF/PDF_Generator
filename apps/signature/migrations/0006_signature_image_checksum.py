# Generated by Django 5.0.6 on 2024-07-05 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signature', '0005_alter_signature_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='signature',
            name='image_checksum',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
    ]