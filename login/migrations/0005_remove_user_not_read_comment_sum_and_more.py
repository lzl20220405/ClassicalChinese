# Generated by Django 4.2 on 2023-01-30 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_remove_user_not_read_comment_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='not_read_comment_sum',
        ),
        migrations.AddField(
            model_name='user',
            name='not_read_comment_articleid',
            field=models.TextField(blank=True, null=True),
        ),
    ]
