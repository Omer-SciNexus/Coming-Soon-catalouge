"use client";

import { useEffect } from "react";

export type UsageContext = {
  client_id: string;
  account_id: string;
  website_id: string;
  page_id: number;
  tab_id: string;
  theme_id: string;
  theme_version: string;
};

// After the page is shown, read the analytics identifiers from the rendered blocks
// and send one batched event. /api/usage is forwarded to Django (see next.config.ts).
export function UsageBeacon({ context }: { context: UsageContext }) {
  useEffect(() => {
    const elements = document.querySelectorAll<HTMLElement>("[data-asset-id]");
    const blocks = Array.from(elements).map((el) => ({
      block_id: el.dataset.blockId,
      asset_id: el.dataset.assetId,
      asset_version: el.dataset.assetVersion,
    }));
    if (blocks.length === 0) return;

    fetch("/api/usage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...context, blocks }),
    }).catch((error) => console.warn("Usage event not sent", error));
  }, [context]);

  return null;
}
