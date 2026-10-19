import type { ComponentType } from "react";
import { ComingSoonHero } from "@/components/assets/ComingSoonHero";
import { UpdatesSignup } from "@/components/assets/UpdatesSignup";

// This is the allowlist. A manifest can only point at code that exists here,
// which matches the component_key enum in asset-manifest.schema.json.
// Data (themes, pages, versions) changes at runtime; adding code here needs a build.
export const registry: Record<string, ComponentType<any>> = {
  ComingSoonHero,
  UpdatesSignup,
};
