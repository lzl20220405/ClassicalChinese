# Generated by Django 4.2 on 2023-01-19 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('riddle', '0003_alter_comment_parent_comment_alter_comment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='article',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='riddle.article'),
        ),
    ]
