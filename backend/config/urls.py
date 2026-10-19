from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from catalogue.views import record_usage
from website.views import site_payload

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("api/sites/<slug:account_id>/", site_payload),
    path("api/usage/", record_usage),
    path("", include(wagtail_urls)),
]
