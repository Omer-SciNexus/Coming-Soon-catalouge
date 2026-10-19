import type { CSSProperties } from "react";

// { button_text: "#fff" } becomes { "--button-text": "#fff" }.
// Only string values are accepted; anything else is skipped.
export function tokensToCssVars(tokens: Record<string, unknown>): CSSProperties {
  const vars: Record<string, string> = {};
  for (const [key, value] of Object.entries(tokens)) {
    if (typeof value !== "string") continue;
    vars[`--${key.replaceAll("_", "-")}`] = value;
  }
  return vars as CSSProperties;
}
