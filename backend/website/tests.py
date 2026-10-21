import json
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from wagtail.blocks import StructBlockValidationError
from wagtail.users.models import UserProfile

from catalogue.models import Asset, AssetVersion

from .blocks import CatalogueAssetBlock, selectable_assets, selectable_versions
from .models import ComingSoonPage


def read_json(name):
    return json.loads((settings.DEMO_DATA_DIR / name).read_text(encoding="utf-8"))


class SeededTestCase(TestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())


class CatalogueAssetBlockTests(SeededTestCase):
    block = CatalogueAssetBlock()

    def clean(self, props, version="1.0.0"):
        value = self.block.to_python({"asset_id": "coming-soon-hero", "version": version, "props": json.dumps(props)})
        return self.block.clean(value)

    def test_valid_props_are_accepted(self):
        self.clean({"heading": "Hi", "description": "Soon"})

    def test_undeclared_prop_is_rejected(self):
        with self.assertRaises(StructBlockValidationError) as caught:
            self.clean({"heading": "Hi", "description": "Soon", "colour": "red"})
        self.assertIn("props", caught.exception.block_errors)

    def test_unknown_version_is_rejected(self):
        with self.assertRaises(StructBlockValidationError) as caught:
            self.clean({"heading": "Hi", "description": "Soon"}, version="2.0.0")
        self.assertIn("version", caught.exception.block_errors)

    def test_draft_version_is_not_selectable(self):
        AssetVersion.objects.filter(asset__asset_id="coming-soon-hero").update(status="draft")
        self.assertNotIn(("coming-soon-hero", "coming-soon-hero"), selectable_assets())
        with self.assertRaises(StructBlockValidationError):
            self.clean({"heading": "Hi", "description": "Soon"})


class SelectableVersionsTests(SeededTestCase):
    def add_version(self, number, status):
        hero = AssetVersion.objects.get(asset__asset_id="coming-soon-hero", version="1.0.0")
        AssetVersion.objects.create(
            asset=Asset.objects.get(asset_id="coming-soon-hero"), version=number, source="human",
            status=status, component_key="ComingSoonHero", props_schema=hero.props_schema,
        )

    def test_seeded_version_lists_both_assets(self):
        self.assertEqual(selectable_versions(), [("1.0.0", "1.0.0 (coming-soon-hero, updates-signup)")])

    def test_new_approved_version_becomes_selectable_and_draft_does_not(self):
        self.add_version("1.1.0", "approved")
        self.add_version("1.2.0", "draft")
        numbers = [number for number, _ in selectable_versions()]
        self.assertEqual(numbers, ["1.0.0", "1.1.0"])

    def test_versions_sort_as_numbers_not_text(self):
        self.add_version("1.10.0", "approved")
        self.add_version("1.9.0", "approved")
        numbers = [number for number, _ in selectable_versions()]
        self.assertEqual(numbers, ["1.0.0", "1.9.0", "1.10.0"])


class SiteApiTests(SeededTestCase):
    def test_adapter_output_matches_the_sample_page(self):
        expected = read_json("wagtail-page.sample.json")
        payload = self.client.get("/api/sites/account-ocean/").json()
        page = ComingSoonPage.objects.get(website__website_id="website-01")
        self.assertEqual(payload["page"], {**expected, "id": page.id})

    def test_each_account_gets_its_own_theme_and_the_same_asset_versions(self):
        ocean = self.client.get("/api/sites/account-ocean/").json()
        olive = self.client.get("/api/sites/account-olive/").json()
        self.assertEqual(ocean["theme"]["theme_id"], "theme-ocean")
        self.assertEqual(olive["theme"]["theme_id"], "theme-olive")
        self.assertEqual(ocean["assets"], olive["assets"])

    def test_wagtail_page_url_redirects_to_the_nextjs_site(self):
        page = ComingSoonPage.objects.get(website__website_id="website-02")
        response = self.client.get(page.url)
        self.assertRedirects(response, f"{settings.FRONTEND_URL}/?account=account-olive", fetch_redirect_response=False)

    def test_site_list_shows_only_accounts_with_a_published_page(self):
        self.assertEqual(self.client.get("/api/sites/").json(), {"accounts": ["account-ocean", "account-olive"]})
        ComingSoonPage.objects.get(website__website_id="website-02").unpublish()
        self.assertEqual(self.client.get("/api/sites/").json(), {"accounts": ["account-ocean"]})

    def test_unknown_account_returns_404(self):
        self.assertEqual(self.client.get("/api/sites/account-nope/").status_code, 404)

    def test_unpublished_draft_is_not_sent_to_the_site(self):
        page = ComingSoonPage.objects.get(website__website_id="website-01")
        page.title = "Draft title"
        page.save_revision()  # saved as a draft, not published
        payload = self.client.get("/api/sites/account-ocean/").json()
        self.assertEqual(payload["page"]["title"], "Coming Soon")


class AdminThemeTests(TestCase):
    def test_new_user_gets_the_light_wagtail_admin_theme(self):
        user = get_user_model().objects.create_superuser("editor", "editor@example.invalid", "pass-123-word")
        self.assertEqual(UserProfile.get_for_user(user).theme, "light")

        self.client.force_login(user)
        response = self.client.get("/cms/")
        self.assertContains(response, '<meta name="color-scheme" content="light">', html=True)
