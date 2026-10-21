from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from catalogue.views import record_usage
from website.views import site_list, site_payload

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("api/sites/", site_list),
    path("api/sites/<slug:account_id>/", site_payload),
    path("api/usage/", record_usage),
]

# Dev only: serve uploaded files (Wagtail images and their thumbnails) from MEDIA_ROOT.
# static() adds nothing when DEBUG is False; in production the web server serves /media/.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Last, because Wagtail's page URLs match every path.
urlpatterns += [path("", include(wagtail_urls))]
