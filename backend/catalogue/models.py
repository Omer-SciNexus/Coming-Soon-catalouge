from django.core.exceptions import ValidationError
from django.db import models

from .validation import manifest_errors

RENDERABLE_STATUSES = ["approved", "published"]


def default_directions():
    return ["ltr"]


class Theme(models.Model):
    """One version of an account theme. Websites point at an exact theme version."""

    theme_id = models.SlugField()
    version = models.CharField(max_length=20)
    design_tokens = models.JSONField(default=dict)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["theme_id", "version"], name="unique_theme_version")]

    def __str__(self):
        return f"{self.theme_id}@{self.version}"


class Asset(models.Model):
    """Stable identity of a catalogue asset. Code and contracts live in AssetVersion."""

    asset_id = models.SlugField(unique=True)
    kind = models.CharField(max_length=20, choices=[("section", "section"), ("element", "element")])

    def __str__(self):
        return self.asset_id


class AssetVersion(models.Model):
    STATUSES = ["draft", "validated", "approved", "published", "rejected"]
    # Once approved, these define what pages were reviewed against, so they never change.
    LOCKED_FIELDS = ["version", "component_key", "props_schema", "supported_directions"]

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="versions")
    version = models.CharField(max_length=20)
    source = models.CharField(max_length=10, choices=[("human", "human"), ("ai", "ai")])
    status = models.CharField(max_length=20, choices=[(s, s) for s in STATUSES], default="draft")
    component_key = models.CharField(max_length=100)
    props_schema = models.JSONField()
    supported_directions = models.JSONField(default=default_directions)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["asset", "version"], name="unique_asset_version")]
        ordering = ["asset__asset_id", "version"]

    def __str__(self):
        return f"{self.asset.asset_id}@{self.version} ({self.status})"

    def to_manifest(self):
        return {
            "asset_id": self.asset.asset_id,
            "version": self.version,
            "kind": self.asset.kind,
            "source": self.source,
            "status": self.status,
            "component_key": self.component_key,
            "supported_directions": self.supported_directions,
            "props_schema": self.props_schema,
        }

    def clean(self):
        errors = manifest_errors(self.to_manifest())
        if self.pk:
            saved = AssetVersion.objects.get(pk=self.pk)
            changed = [f for f in self.LOCKED_FIELDS if getattr(saved, f) != getattr(self, f)]
            if saved.status in RENDERABLE_STATUSES and changed:
                errors.append(f"Approved versions cannot change {', '.join(changed)}. Create a new version.")
        if errors:
            raise ValidationError(errors)


class AssetUsageEvent(models.Model):
    """One rendered block seen by a visitor. Stand-in for the backend team's asset_usage table."""

    asset_version = models.ForeignKey(AssetVersion, on_delete=models.PROTECT, related_name="usage_events")
    client_id = models.CharField(max_length=100)
    account_id = models.CharField(max_length=100)
    website_id = models.CharField(max_length=100)
    page_id = models.CharField(max_length=100)
    tab_id = models.CharField(max_length=100)
    block_id = models.CharField(max_length=100)
    theme_id = models.CharField(max_length=100)
    theme_version = models.CharField(max_length=20)
    seen_at = models.DateTimeField(auto_now_add=True)
