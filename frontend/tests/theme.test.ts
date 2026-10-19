import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { tokensToCssVars } from "@/lib/theme";

describe("tokensToCssVars", () => {
  it("turns snake_case keys into --kebab-case variables", () => {
    expect(tokensToCssVars({ accent: "#125f90", button_text: "#ffffff" })).toEqual({
      "--accent": "#125f90",
      "--button-text": "#ffffff",
    });
  });

  it("skips values that are not strings", () => {
    expect(tokensToCssVars({ accent: "#000", size: 12, nested: { a: "b" } })).toEqual({ "--accent": "#000" });
  });
});

describe("theming boundary", () => {
  const assetsDir = path.resolve(__dirname, "../components/assets");

  it.each(readdirSync(assetsDir))("%s has no hard-coded colours or fonts", (file) => {
    const source = readFileSync(path.join(assetsDir, file), "utf8");
    expect(source).not.toMatch(/#[0-9a-fA-F]{3,8}\b/);
    expect(source).not.toMatch(/\b(rgb|rgba|hsl|hsla)\(/);
    expect(source).not.toMatch(/font-family\s*:/);
  });
});
