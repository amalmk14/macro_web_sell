# Generated by Django 4.1.2 on 2023-11-06 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_delete_templates'),
    ]

    operations = [
        migrations.CreateModel(
            name='Templates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('category', models.TextField()),
                ('temp_img', models.ImageField(upload_to='temp_meadia')),
                ('temp_file', models.FileField(upload_to='templates')),
                ('price', models.IntegerField()),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.templatestype')),
            ],
        ),
    ]
