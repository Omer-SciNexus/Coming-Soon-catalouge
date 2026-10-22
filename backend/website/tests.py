import json
import tempfile
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase
from wagtail.blocks import StructBlockValidationError
from wagtail.documents import get_document_model
from wagtail.test.utils.form_data import inline_formset, nested_form_data, streamfield
from wagtail.users.models import UserProfile

from catalogue.models import Asset, AssetVersion

from .blocks import CatalogueAssetBlock, selectable_assets, selectable_versions
from .models import ComingSoonPage, Website


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

    def test_image_is_accepted_from_version_1_1_0_only(self):
        props = {"heading": "Hi", "description": "Soon", "image_url": "/media/original_images/a.jpg", "image_alt": "A"}
        self.clean(props, version="1.1.0")
        with self.assertRaises(StructBlockValidationError):
            self.clean(props)  # 1.0.0 does not declare image_url

    def test_document_is_accepted_from_version_1_2_0_only(self):
        props = {"heading": "Hi", "description": "Soon", "document_url": "/documents/1/a.pdf", "document_label": "Brochure"}
        self.clean(props, version="1.2.0")
        with self.assertRaises(StructBlockValidationError):
            self.clean(props, version="1.1.0")  # 1.1.0 does not declare document_url
        with self.assertRaises(StructBlockValidationError):
            self.clean({**props, "document_url": "javascript:alert(1)"}, version="1.2.0")

    def test_unsafe_image_url_is_rejected(self):
        for url in ["javascript:alert(1)", "//evil.example/a.jpg", "data:image/png;base64,AAAA"]:
            with self.assertRaises(StructBlockValidationError, msg=url):
                self.clean({"heading": "Hi", "description": "Soon", "image_url": url}, version="1.1.0")

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

    def test_seeded_versions_list_their_assets(self):
        self.assertEqual(selectable_versions(), [
            ("1.0.0", "1.0.0 (coming-soon-hero, updates-signup)"),
            ("1.1.0", "1.1.0 (coming-soon-hero)"),
            ("1.2.0", "1.2.0 (coming-soon-hero)"),
        ])

    def test_new_approved_version_becomes_selectable_and_draft_does_not(self):
        self.add_version("1.3.0", "approved")
        self.add_version("1.4.0", "draft")
        numbers = [number for number, _ in selectable_versions()]
        self.assertEqual(numbers, ["1.0.0", "1.1.0", "1.2.0", "1.3.0"])

    def test_versions_sort_as_numbers_not_text(self):
        self.add_version("1.10.0", "approved")
        self.add_version("1.9.0", "approved")
        numbers = [number for number, _ in selectable_versions()]
        self.assertEqual(numbers, ["1.0.0", "1.1.0", "1.2.0", "1.9.0", "1.10.0"])


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

    def test_uploaded_document_is_served_at_its_url(self):
        with tempfile.TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            document = get_document_model().objects.create(title="Brochure", file=ContentFile(b"%PDF-1.4", name="brochure.pdf"))
            response = self.client.get(document.url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(document.url.startswith("/documents/"))
            response.close()

    def test_unknown_account_returns_404(self):
        self.assertEqual(self.client.get("/api/sites/account-nope/").status_code, 404)

    def test_unpublished_draft_is_not_sent_to_the_site(self):
        page = ComingSoonPage.objects.get(website__website_id="website-01")
        page.title = "Draft title"
        page.save_revision()  # saved as a draft, not published
        payload = self.client.get("/api/sites/account-ocean/").json()
        self.assertEqual(payload["page"]["title"], "Coming Soon")


class OneLivePagePerWebsiteTests(SeededTestCase):
    def setUp(self):
        super().setUp()
        user = get_user_model().objects.create_superuser("editor", "editor@example.invalid", "pass-123-word")
        self.client.force_login(user)
        self.olive_page = ComingSoonPage.objects.get(website__website_id="website-02")

    def page_data(self, website_id, action):
        website = Website.objects.get(website_id=website_id)
        props = json.dumps({"heading": "Hi", "description": "Soon"})
        body = streamfield([("catalogue_asset", {"asset_id": "coming-soon-hero", "version": "1.0.0", "props": props})])
        data = nested_form_data({
            "title": "Test2", "slug": "test2", "website": website.pk,
            "tabs": streamfield([("tab", {"tab_id": "announcement", "label": "Announcement", "body": body})]),
            "comments": inline_formset([]),
        })
        data[action] = "1"
        return data

    def add_page(self, website_id, action):
        url = f"/cms/pages/add/website/comingsoonpage/{self.olive_page.get_parent().pk}/"
        return self.client.post(url, self.page_data(website_id, action))

    def test_second_live_page_for_a_website_is_refused(self):
        response = self.add_page("website-02", "action-publish")
        self.assertEqual(response.status_code, 200)  # the form again, with the error
        self.assertContains(response, "website-02 already has a live page")
        self.assertFalse(ComingSoonPage.objects.filter(slug="test2").exists())

    def test_draft_is_allowed_and_can_be_published_after_the_old_page_is_unpublished(self):
        self.assertEqual(self.add_page("website-02", "action-save-draft").status_code, 302)
        draft = ComingSoonPage.objects.get(slug="test2")
        self.assertFalse(draft.live)
        self.olive_page.unpublish()
        response = self.client.post(f"/cms/pages/{draft.pk}/edit/", self.page_data("website-02", "action-publish"))
        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertTrue(draft.live)

    def test_page_for_a_free_website_is_published(self):
        Website.objects.create(website_id="website-03", account_id="account-sand", client_id="client-01",
                               theme=self.olive_page.website.theme)
        self.assertEqual(self.add_page("website-03", "action-publish").status_code, 302)
        self.assertTrue(ComingSoonPage.objects.get(slug="test2").live)


class AdminThemeTests(TestCase):
    def test_new_user_gets_the_light_wagtail_admin_theme(self):
        user = get_user_model().objects.create_superuser("editor", "editor@example.invalid", "pass-123-word")
        self.assertEqual(UserProfile.get_for_user(user).theme, "light")

        self.client.force_login(user)
        response = self.client.get("/cms/")
        self.assertContains(response, '<meta name="color-scheme" content="light">', html=True)
