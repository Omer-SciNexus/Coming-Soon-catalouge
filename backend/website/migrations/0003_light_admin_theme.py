from django.conf import settings
from django.db import migrations


def use_light_theme_for_existing_users(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    UserProfile = apps.get_model("wagtailusers", "UserProfile")
    for user in User.objects.all():
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.theme = "light"
        profile.save(update_fields=["theme"])


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0002_version_dropdown"),
        ("wagtailusers", "0015_userprofile_keyboard_shortcuts"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Reverse does nothing: users keep whatever theme they have.
        migrations.RunPython(use_light_theme_for_existing_users, migrations.RunPython.noop),
    ]
