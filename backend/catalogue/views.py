import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import AssetUsageEvent, AssetVersion

PAGE_FIELDS = ["client_id", "account_id", "website_id", "page_id", "tab_id", "theme_id", "theme_version"]
BLOCK_FIELDS = ["block_id", "asset_id", "asset_version"]


# Public beacon endpoint: no login and no CSRF token, so it only accepts a strict shape.
@csrf_exempt
@require_POST
def record_usage(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "expected a JSON object"}, status=400)

    missing = [f for f in PAGE_FIELDS if f not in payload]
    blocks = payload.get("blocks")
    if missing or not isinstance(blocks, list) or not blocks:
        return JsonResponse({"error": "missing fields", "fields": missing or ["blocks"]}, status=400)

    page_values = {f: str(payload[f]) for f in PAGE_FIELDS}
    events = []
    for block in blocks:
        if not isinstance(block, dict) or not all(block.get(f) for f in BLOCK_FIELDS):
            return JsonResponse({"error": "block is missing fields", "block": block}, status=400)
        version = AssetVersion.objects.filter(
            asset__asset_id=block["asset_id"], version=block["asset_version"]
        ).first()
        if version is None:
            return JsonResponse({"error": "unknown asset version", "block": block}, status=400)
        events.append(AssetUsageEvent(asset_version=version, block_id=block["block_id"], **page_values))

    AssetUsageEvent.objects.bulk_create(events)
    print(f"usage: {len(events)} block(s) on {payload['website_id']} page {payload['page_id']} tab {payload['tab_id']}")
    return JsonResponse({"recorded": len(events)}, status=201)
