# Generated by Django 2.2.9 on 2022-04-24 20:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20220412_2058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',)},
        ),
    ]