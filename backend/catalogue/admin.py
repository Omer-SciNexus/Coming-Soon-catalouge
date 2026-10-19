from django.contrib import admin

from .models import Asset, AssetUsageEvent, AssetVersion, Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ["theme_id", "version"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["asset_id", "kind"]


@admin.register(AssetVersion)
class AssetVersionAdmin(admin.ModelAdmin):
    list_display = ["asset", "version", "status", "source", "component_key"]
    list_filter = ["status", "source"]


@admin.register(AssetUsageEvent)
class AssetUsageEventAdmin(admin.ModelAdmin):
    list_display = ["seen_at", "asset_version", "website_id", "page_id", "tab_id", "block_id", "theme_id"]
    list_filter = ["website_id", "theme_id"]
