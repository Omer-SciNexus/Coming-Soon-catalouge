import json
from io import StringIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from .models import AssetUsageEvent, AssetVersion
from .validation import manifest_errors, props_errors


def sample_manifests():
    return json.loads((settings.DEMO_DATA_DIR / "assets.sample.json").read_text(encoding="utf-8"))


class ManifestValidationTests(TestCase):
    def test_both_sample_manifests_are_valid(self):
        for manifest in sample_manifests():
            self.assertEqual(manifest_errors(manifest), [], manifest["asset_id"])

    def test_unknown_component_key_is_rejected(self):
        manifest = {**sample_manifests()[0], "component_key": "EvilWidget"}
        self.assertTrue(manifest_errors(manifest))

    def test_broken_props_schema_is_rejected(self):
        manifest = {**sample_manifests()[0]}
        manifest["props_schema"] = {**manifest["props_schema"], "properties": {"heading": {"type": "banana"}}}
        self.assertTrue(any("props_schema" in e for e in manifest_errors(manifest)))


class PropsValidationTests(TestCase):
    schema = sample_manifests()[0]["props_schema"]

    def test_valid_props_pass(self):
        self.assertEqual(props_errors(self.schema, {"heading": "Hi", "description": "Soon"}), [])

    def test_extra_prop_is_rejected(self):
        self.assertTrue(props_errors(self.schema, {"heading": "Hi", "description": "Soon", "colour": "red"}))

    def test_missing_required_prop_is_rejected(self):
        self.assertTrue(props_errors(self.schema, {"heading": "Hi"}))


class ImmutabilityTests(TestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())
        self.version = AssetVersion.objects.get(asset__asset_id="coming-soon-hero", version="1.0.0")

    def test_approved_version_cannot_change_its_contract(self):
        self.version.props_schema = {**self.version.props_schema, "required": ["heading"]}
        with self.assertRaises(ValidationError):
            self.version.full_clean()

    def test_approved_version_can_be_withdrawn(self):
        self.version.status = "draft"
        self.version.full_clean()


class UsageEndpointTests(TestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())
        self.payload = {
            "client_id": "client-01", "account_id": "account-ocean", "website_id": "website-01",
            "page_id": 3, "tab_id": "announcement", "theme_id": "theme-ocean", "theme_version": "1.0.0",
            "blocks": [{"block_id": "block-001", "asset_id": "coming-soon-hero", "asset_version": "1.0.0"}],
        }

    def post(self, payload):
        return self.client.post("/api/usage/", json.dumps(payload), content_type="application/json")

    def test_valid_event_is_stored_with_all_identifiers(self):
        self.assertEqual(self.post(self.payload).status_code, 201)
        event = AssetUsageEvent.objects.get()
        self.assertEqual((event.website_id, event.page_id, event.block_id), ("website-01", "3", "block-001"))
        self.assertEqual(str(event.asset_version), "coming-soon-hero@1.0.0 (approved)")

    def test_missing_field_is_rejected(self):
        del self.payload["theme_id"]
        self.assertEqual(self.post(self.payload).status_code, 400)

    def test_unknown_asset_version_is_rejected(self):
        self.payload["blocks"][0]["asset_version"] = "9.9.9"
        self.assertEqual(self.post(self.payload).status_code, 400)
        self.assertFalse(AssetUsageEvent.objects.exists())
