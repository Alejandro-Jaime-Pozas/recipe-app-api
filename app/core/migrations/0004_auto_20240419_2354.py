# Generated by Django 3.2.25 on 2024-04-19 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20240419_2342'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='core.Tag'),
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='link',
        ),
        migrations.AddField(
            model_name='recipe',
            name='link',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
