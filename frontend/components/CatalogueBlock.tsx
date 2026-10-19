import { resolveBlock } from "@/lib/catalogue";
import type { AssetManifest, Direction, StreamBlock } from "@/lib/types";

export type PageIds = {
  websiteId: string;
  pageId: number;
  tabId: string;
  themeId: string;
  themeVersion: string;
};

type Props = {
  block: StreamBlock;
  manifests: AssetManifest[];
  direction: Direction;
  ids: PageIds;
};

// Renders one StreamField block of type "catalogue_asset".
// On any problem it fails closed: a small visible placeholder, never a crash.
export function CatalogueBlock({ block, manifests, direction, ids }: Props) {
  if (block.type !== "catalogue_asset") {
    return <Placeholder blockId={block.id} reason="unknown_block_type" />;
  }

  const result = resolveBlock(block.value, manifests, direction);
  if (!result.ok) {
    console.warn("Catalogue block not rendered", { blockId: block.id, ...block.value, reason: result.reason });
    return <Placeholder blockId={block.id} reason={result.reason} />;
  }

  const { Component, manifest } = result;
  return (
    <div
      data-block-id={block.id}
      data-asset-id={manifest.asset_id}
      data-asset-version={manifest.version}
      data-website-id={ids.websiteId}
      data-page-id={ids.pageId}
      data-tab-id={ids.tabId}
      data-theme-id={ids.themeId}
      data-theme-version={ids.themeVersion}
    >
      <Component {...block.value.props} />
    </div>
  );
}

function Placeholder({ blockId, reason }: { blockId: string; reason: string }) {
  return (
    <p className="block-placeholder">
      Block {blockId} is not available ({reason}).
    </p>
  );
}
