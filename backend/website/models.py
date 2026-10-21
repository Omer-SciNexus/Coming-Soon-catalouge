from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.users.models import UserProfile

from catalogue.models import Theme

from .blocks import TabBlock


class Website(models.Model):
    """One account owns one website. The theme is chosen here, so changing it needs no code."""

    website_id = models.SlugField(unique=True)
    account_id = models.SlugField(unique=True)
    client_id = models.SlugField()
    theme = models.ForeignKey(Theme, on_delete=models.PROTECT, related_name="websites")

    def __str__(self):
        return f"{self.website_id} ({self.account_id})"


class ComingSoonPage(Page):
    website = models.ForeignKey(Website, on_delete=models.PROTECT, related_name="pages")
    tabs = StreamField([("tab", TabBlock())])

    content_panels = Page.content_panels + [FieldPanel("website"), FieldPanel("tabs")]

    # Headless: Next.js renders the page, so Wagtail has no template and no preview here.
    preview_modes = []

    def serve(self, request, *args, **kwargs):
        return redirect(f"{settings.FRONTEND_URL}/?account={self.website.account_id}")


# Wagtail's admin theme defaults to "System default", which turns dark on a dark-mode OS.
# New CMS users start with the light theme instead; each user can still change it in
# Account > Preferences. Existing users were switched by migration 0003_light_admin_theme.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def use_light_admin_theme(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={"theme": UserProfile.AdminColorThemes.LIGHT})
