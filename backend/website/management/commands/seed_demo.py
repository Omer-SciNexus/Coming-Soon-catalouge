import json

from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.models import Site

from catalogue.models import Asset, AssetVersion, Theme
from website.models import ComingSoonPage, Website

PAGE_FILES = ["wagtail-page.sample.json", "wagtail-page.website-02.json"]


def read_json(name):
    return json.loads((settings.DEMO_DATA_DIR / name).read_text(encoding="utf-8"))


class Command(BaseCommand):
    help = "Load the sample JSON files from data/ into the database. Existing records are kept."

    def handle(self, *args, **options):
        for record in read_json("accounts-themes.sample.json"):
            self.load_account(record)
        for manifest in read_json("assets.sample.json"):
            self.load_manifest(manifest)
        # Under the default site home page, so Wagtail gives each page a URL ("View live").
        root = Site.objects.get(is_default_site=True).root_page
        for name in PAGE_FILES:
            self.load_page(root, read_json(name))
        self.stdout.write(self.style.SUCCESS("Demo data loaded."))

    def load_account(self, record):
        theme, _ = Theme.objects.get_or_create(
            theme_id=record["theme_id"],
            version=record["theme_version"],
            defaults={"design_tokens": record["design_tokens"]},
        )
        Website.objects.get_or_create(
            website_id=record["website_id"],
            defaults={"account_id": record["account_id"], "client_id": record["client_id"], "theme": theme},
        )

    def load_manifest(self, manifest):
        asset, _ = Asset.objects.get_or_create(asset_id=manifest["asset_id"], defaults={"kind": manifest["kind"]})
        if AssetVersion.objects.filter(asset=asset, version=manifest["version"]).exists():
            return
        version = AssetVersion(
            asset=asset,
            version=manifest["version"],
            source=manifest["source"],
            status=manifest["status"],
            component_key=manifest["component_key"],
            props_schema=manifest["props_schema"],
            supported_directions=manifest.get("supported_directions", ["ltr"]),
        )
        version.full_clean()  # the same checks the admin runs
        version.save()

    def load_page(self, root, data):
        website = Website.objects.get(website_id=data["website_id"])
        if ComingSoonPage.objects.filter(website=website).exists():
            return
        page = ComingSoonPage(
            title=data["title"],
            slug=f"coming-soon-{website.website_id}",
            website=website,
            tabs=[tab_to_stream_data(tab) for tab in data["tabs"]],
        )
        root.add_child(instance=page)
        page.save_revision().publish()


def tab_to_stream_data(tab):
    """The reverse of adapter.py: sample JSON to raw StreamField data (props stored as JSON text)."""
    body = [
        {"type": block["type"], "id": block["id"], "value": {**block["value"], "props": json.dumps(block["value"]["props"])}}
        for block in tab["body"]
    ]
    return {"type": "tab", "value": {"tab_id": tab["id"], "label": tab["label"], "body": body}}
