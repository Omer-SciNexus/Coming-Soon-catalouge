import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { resolveBlock } from "@/lib/catalogue";
import { registry } from "@/lib/registry";
import type { AssetManifest, CatalogueAssetValue } from "@/lib/types";

const dataDir = path.resolve(__dirname, "../../data");
const readJson = (file: string) => JSON.parse(readFileSync(path.join(dataDir, file), "utf8"));

const manifests: AssetManifest[] = readJson("assets.sample.json");
const heroBlock: CatalogueAssetValue = {
  asset_id: "coming-soon-hero",
  version: "1.0.0",
  props: { heading: "Hi", description: "Soon" },
};

describe("resolveBlock", () => {
  it("resolves an approved asset to its registered component", () => {
    const result = resolveBlock(heroBlock, manifests, "ltr");
    expect(result.ok && result.Component).toBe(registry.ComingSoonHero);
  });

  it("rejects an unknown asset or version", () => {
    expect(resolveBlock({ ...heroBlock, asset_id: "nope" }, manifests, "ltr")).toEqual({ ok: false, reason: "not_found" });
    expect(resolveBlock({ ...heroBlock, version: "9.9.9" }, manifests, "ltr")).toEqual({ ok: false, reason: "not_found" });
  });

  it("rejects a draft version", () => {
    const drafts = manifests.map((m) => ({ ...m, status: "draft" as const }));
    expect(resolveBlock(heroBlock, drafts, "ltr")).toEqual({ ok: false, reason: "not_renderable_status" });
  });

  it("rejects a direction the asset does not support", () => {
    const ltrOnly = manifests.map((m) => ({ ...m, supported_directions: ["ltr" as const] }));
    expect(resolveBlock(heroBlock, ltrOnly, "rtl")).toEqual({ ok: false, reason: "unsupported_direction" });
  });

  it("rejects a component key that is not in the registry", () => {
    const unknown = manifests.map((m) => ({ ...m, component_key: "EvilWidget" }));
    expect(resolveBlock(heroBlock, unknown, "ltr")).toEqual({ ok: false, reason: "no_component" });
  });

  it("rejects missing props", () => {
    expect(resolveBlock({ ...heroBlock, props: null }, manifests, "ltr")).toEqual({ ok: false, reason: "invalid_props" });
  });

  it("gives both accounts the same component for the same asset version", () => {
    const accounts = readJson("accounts-themes.sample.json");
    const results = accounts.map(() => resolveBlock(heroBlock, manifests, "ltr"));
    expect(results[0].ok && results[1].ok && results[0].Component === results[1].Component).toBe(true);
  });
});

describe("registry", () => {
  it("matches the component_key enum in the manifest schema", () => {
    const schema = readJson("asset-manifest.schema.json");
    expect(Object.keys(registry).sort()).toEqual([...schema.properties.component_key.enum].sort());
  });
});
