import json


def to_catalogue_page(page):
    """Map a ComingSoonPage to the JSON shape of data/wagtail-page.sample.json."""
    return {
        "id": page.id,
        "meta": {"type": page._meta.label},
        "website_id": page.website.website_id,
        "title": page.title,
        "tabs": [tab_to_dict(tab) for tab in page.tabs],
    }


def tab_to_dict(tab):
    return {
        "id": tab.value["tab_id"],
        "label": tab.value["label"],
        "body": [block_to_dict(block) for block in tab.value["body"]],
    }


def block_to_dict(block):
    value = block.value
    return {
        "type": block.block_type,
        "id": block.id,
        "value": {"asset_id": value["asset_id"], "version": value["version"], "props": parse_props(value["props"])},
    }


def parse_props(text):
    # Props were validated when the editor saved them. If bad data still got in,
    # send null and let the renderer fail closed for this one block.
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None
