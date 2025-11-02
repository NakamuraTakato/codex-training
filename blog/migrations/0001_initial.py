# Generated manually for initial setup
from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("taggit", "0005_auto_20220424_2025"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64, unique=True)),
                ("slug", models.SlugField(max_length=64, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("excerpt", models.TextField(blank=True)),
                ("content", models.TextField()),
                ("featured_image", models.ImageField(blank=True, null=True, upload_to="posts/")),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "下書き"), ("published", "公開")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="posts",
                        to="blog.category",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(blank=True, help_text="A comma-separated list of tags.", through="taggit.TaggedItem", to="taggit.Tag", verbose_name="Tags")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["status", "created_at"], name="blog_post_status_b2a55a_idx"),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["slug"], name="blog_post_slug_013024_idx"),
        ),
    ]
