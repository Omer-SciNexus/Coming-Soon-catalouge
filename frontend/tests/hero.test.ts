import { describe, expect, it } from "vitest";
import { isSafeUrl } from "@/components/assets/ComingSoonHero";

describe("isSafeUrl", () => {
  it("accepts http(s) addresses and same-site paths", () => {
    expect(isSafeUrl("https://example.com/a.jpg")).toBe(true);
    expect(isSafeUrl("http://127.0.0.1:8000/media/original_images/a.jpg")).toBe(true);
    expect(isSafeUrl("/media/original_images/a.jpg")).toBe(true);
    expect(isSafeUrl("/documents/1/brochure.pdf")).toBe(true);
  });

  it("rejects other schemes, protocol-relative addresses and non-strings", () => {
    expect(isSafeUrl("javascript:alert(1)")).toBe(false);
    expect(isSafeUrl("data:image/svg+xml,<svg/>")).toBe(false);
    expect(isSafeUrl("//evil.example/a.jpg")).toBe(false);
    expect(isSafeUrl("")).toBe(false);
    expect(isSafeUrl(42)).toBe(false);
  });
});
