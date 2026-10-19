import json

from django.core.exceptions import ValidationError
from wagtail import blocks

from catalogue.models import RENDERABLE_STATUSES, Asset, AssetVersion
from catalogue.validation import props_errors


def selectable_assets():
    """Choices for the editor: only assets with at least one approved or published version."""
    assets = Asset.objects.filter(versions__status__in=RENDERABLE_STATUSES).distinct().order_by("asset_id")
    return [(asset.asset_id, asset.asset_id) for asset in assets]


def field_error(name, message):
    return blocks.StructBlockValidationError(block_errors={name: ValidationError(message)})


class CatalogueAssetBlock(blocks.StructBlock):
    asset_id = blocks.ChoiceBlock(choices=selectable_assets)
    # Exact version. A page keeps the version it was approved with; it never follows "latest".
    version = blocks.CharBlock(help_text="Exact version, for example 1.0.0")
    # Wagtail has no built-in JSON block, so props are stored as JSON text and checked in clean().
    props = blocks.TextBlock(default="{}", help_text="JSON object matching the version's props_schema")

    def clean(self, value):
        value = super().clean(value)
        version = AssetVersion.objects.filter(
            asset__asset_id=value["asset_id"], version=value["version"], status__in=RENDERABLE_STATUSES
        ).first()
        if version is None:
            raise field_error("version", "No approved or published version with this number.")
        try:
            props = json.loads(value["props"])
        except json.JSONDecodeError as error:
            raise field_error("props", f"Not valid JSON: {error}")
        errors = props_errors(version.props_schema, props)
        if errors:
            raise field_error("props", "; ".join(errors))
        return value


class TabBlock(blocks.StructBlock):
    tab_id = blocks.CharBlock(help_text="Used in the URL, for example announcement")
    label = blocks.CharBlock()
    body = blocks.StreamBlock([("catalogue_asset", CatalogueAssetBlock())])
