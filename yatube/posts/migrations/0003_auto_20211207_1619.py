# Generated by Django 2.2.9 on 2021-12-07 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20211207_0156'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='decriotion',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]