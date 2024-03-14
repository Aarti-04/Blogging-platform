# Generated by Django 5.0.3 on 2024-03-14 04:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_alter_comments_parent_comment_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="comments",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="comments",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
