# Generated by Django 5.1.6 on 2025-03-14 17:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carpetas', '0001_initial'),
        ('control_procesos', '0005_respuesta'),
    ]

    operations = [
        migrations.AddField(
            model_name='respuesta',
            name='carpeta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='carpetas.carpeta'),
        ),
        migrations.AlterField(
            model_name='respuesta',
            name='fecha_respuesta',
            field=models.DateField(),
        ),
    ]
