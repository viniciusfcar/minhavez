# Generated by Django 2.2.7 on 2020-04-18 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('especialista', '0017_auto_20200417_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='especialista',
            name='descricao',
        ),
        migrations.RemoveField(
            model_name='especialista',
            name='email',
        ),
        migrations.RemoveField(
            model_name='especialista',
            name='telefone',
        ),
    ]
