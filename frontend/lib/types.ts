// Shapes of the JSON returned by Django at GET /api/sites/<account_id>/.
// `page` has exactly the shape of data/wagtail-page.sample.json.

export type Direction = "ltr" | "rtl";

export type AssetManifest = {
  asset_id: string;
  version: string;
  kind: "section" | "element";
  source: "human" | "ai";
  status: "draft" | "validated" | "approved" | "published" | "rejected";
  component_key: string;
  props_schema: Record<string, unknown>;
  supported_directions?: Direction[];
};

export type CatalogueAssetValue = {
  asset_id: string;
  version: string;
  props: Record<string, unknown> | null;
};

export type StreamBlock = { type: string; id: string; value: CatalogueAssetValue };

export type Tab = { id: string; label: string; body: StreamBlock[] };

export type CataloguePage = {
  id: number;
  meta: { type: string };
  website_id: string;
  title: string;
  tabs: Tab[];
};

export type SitePayload = {
  account: { client_id: string; account_id: string; website_id: string };
  theme: { theme_id: string; theme_version: string; design_tokens: Record<string, unknown> };
  page: CataloguePage;
  assets: AssetManifest[];
};
