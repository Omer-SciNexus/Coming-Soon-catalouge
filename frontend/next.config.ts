import type { NextConfig } from "next";

const djangoUrl = process.env.DJANGO_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Self-hosted: `next build` writes a standalone Node server to .next/standalone.
  output: "standalone",
  // `npm run dev` in GitHub Codespaces is opened from *.app.github.dev; allow its live reload.
  allowedDevOrigins: ["*.app.github.dev"],
  // The browser posts usage to the same origin; Next forwards it to Django (no CORS).
  // Rewrites are fixed at build time, so set DJANGO_URL before `npm run build`.
  async rewrites() {
    return [{ source: "/api/usage", destination: `${djangoUrl}/api/usage/` }];
  },
};

export default nextConfig;
