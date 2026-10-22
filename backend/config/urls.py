from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from catalogue.views import record_usage
from website.views import site_list, site_payload

admin.site.site_header = "Catalogue admin"
admin.site.site_title = "Catalogue admin"
admin.site.index_title = "Themes, assets and websites"

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    # Uploaded Wagtail documents, for example /documents/1/brochure.pdf. Served by a Django view,
    # so they work with DEBUG off too (unlike /media/).
    path("documents/", include(wagtaildocs_urls)),
    path("api/sites/", site_list),
    path("api/sites/<slug:account_id>/", site_payload),
    path("api/usage/", record_usage),
]

# Dev only: serve uploaded files (Wagtail images and their thumbnails) from MEDIA_ROOT.
# static() adds nothing when DEBUG is False; in production the web server serves /media/.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Last, because Wagtail's page URLs match every path.
urlpatterns += [path("", include(wagtail_urls))]
