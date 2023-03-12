# Generated by Django 4.2 on 2023-01-19 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.SmallIntegerField(default=1, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('annotation', models.TextField()),
                ('translate', models.TextField()),
                ('hbread', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='Riddle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.SmallIntegerField(blank=True, null=True)),
                ('riddlesum', models.SmallIntegerField(blank=True, null=True)),
                ('kind', models.SmallIntegerField(choices=[(1, '字词翻译'), (2, '句子翻译'), (3, '特殊字词'), (4, '特殊成语')], default=1)),
                ('topic', models.TextField()),
                ('answer', models.TextField()),
                ('keyword', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='riddle.article')),
            ],
            options={
                'verbose_name': '题目',
                'verbose_name_plural': '题目',
            },
        ),
    ]