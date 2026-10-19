import type { ComponentType } from "react";
import { registry } from "./registry";
import type { AssetManifest, CatalogueAssetValue, Direction } from "./types";

export const RENDERABLE_STATUSES = ["approved", "published"];

export type FailureReason =
  | "not_found"
  | "not_renderable_status"
  | "unsupported_direction"
  | "no_component"
  | "invalid_props";

export type Resolution =
  | { ok: true; manifest: AssetManifest; Component: ComponentType<Record<string, unknown>> }
  | { ok: false; reason: FailureReason };

// Django already validated the block when the editor saved it. The renderer still
// checks again and fails closed, so one bad record can never break a live page.
// The version is matched exactly: a page always gets the version it pinned, never "latest".
export function resolveBlock(
  value: CatalogueAssetValue,
  manifests: AssetManifest[],
  direction: Direction,
): Resolution {
  const manifest = manifests.find(
    (m) => m.asset_id === value.asset_id && m.version === value.version,
  );
  if (!manifest) return { ok: false, reason: "not_found" };
  if (!RENDERABLE_STATUSES.includes(manifest.status)) {
    return { ok: false, reason: "not_renderable_status" };
  }
  const directions = manifest.supported_directions ?? ["ltr"];
  if (!directions.includes(direction)) return { ok: false, reason: "unsupported_direction" };
  const Component = registry[manifest.component_key];
  if (!Component) return { ok: false, reason: "no_component" };
  if (typeof value.props !== "object" || value.props === null || Array.isArray(value.props)) {
    return { ok: false, reason: "invalid_props" };
  }
  return { ok: true, manifest, Component };
}
