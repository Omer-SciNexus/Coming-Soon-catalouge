from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404

from catalogue.models import AssetVersion

from .adapter import to_catalogue_page
from .models import ComingSoonPage, Website


def site_list(request):
    """Accounts that have a published page. The demo bar shows one button for each,
    so a website added in the admin appears there without a code change."""
    websites = Website.objects.filter(pages__live=True).distinct().order_by("id")
    return JsonResponse({"accounts": [w.account_id for w in websites]})


def site_payload(request, account_id):
    """Everything Next.js needs to render one account's website, in one response."""
    website = get_object_or_404(Website.objects.select_related("theme"), account_id=account_id)
    # live(): editors' unpublished drafts are never sent to the public site.
    page = ComingSoonPage.objects.live().filter(website=website).first()
    if page is None:
        raise Http404("No published page for this website.")

    page_data = to_catalogue_page(page)
    return JsonResponse({
        "account": {"client_id": website.client_id, "account_id": website.account_id, "website_id": website.website_id},
        "theme": {
            "theme_id": website.theme.theme_id,
            "theme_version": website.theme.version,
            "design_tokens": website.theme.design_tokens,
        },
        "page": page_data,
        "assets": manifests_for(page_data),
    })


def manifests_for(page_data):
    """Manifests of exactly the asset versions this page pins, whatever their status.
    The renderer decides what is renderable, so a drafted version shows as a placeholder."""
    pins = {(b["value"]["asset_id"], b["value"]["version"]) for tab in page_data["tabs"] for b in tab["body"]}
    versions = AssetVersion.objects.select_related("asset").filter(asset__asset_id__in={a for a, _ in pins})
    return [v.to_manifest() for v in versions if (v.asset.asset_id, v.version) in pins]
