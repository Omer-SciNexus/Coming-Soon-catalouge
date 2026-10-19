import json
from functools import cache

from django.conf import settings
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


@cache
def manifest_validator():
    path = settings.DEMO_DATA_DIR / "asset-manifest.schema.json"
    return Draft202012Validator(json.loads(path.read_text(encoding="utf-8")))


def manifest_errors(manifest):
    """Check a manifest (from a human or the AI agent) before it enters the catalogue."""
    errors = [error.message for error in manifest_validator().iter_errors(manifest)]
    try:
        # The props_schema must itself be a valid JSON Schema, or props can never be checked.
        Draft202012Validator.check_schema(manifest.get("props_schema", {}))
    except SchemaError as error:
        errors.append(f"props_schema is not a valid JSON Schema: {error.message}")
    return errors


def props_errors(props_schema, props):
    """Check one block's props against the props_schema of the version it pins."""
    return [error.message for error in Draft202012Validator(props_schema).iter_errors(props)]
