import Link from "next/link";
import { notFound } from "next/navigation";
import { CatalogueBlock } from "@/components/CatalogueBlock";
import { UsageBeacon } from "@/components/UsageBeacon";
import { getSite } from "@/lib/api";
import { tokensToCssVars } from "@/lib/theme";
import type { Direction } from "@/lib/types";

// Always render on request, so the page reflects the current database records.
export const dynamic = "force-dynamic";

const DEMO_ACCOUNTS = ["account-ocean", "account-olive"];

type Query = { account?: string; tab?: string; dir?: string };

export default async function Page({ searchParams }: { searchParams: Promise<Query> }) {
  const query = await searchParams;
  const accountId = query.account ?? DEMO_ACCOUNTS[0];
  const site = await getSite(accountId);
  if (!site) notFound();

  const { account, theme, page, assets } = site;
  const direction: Direction = query.dir === "rtl" ? "rtl" : "ltr";
  const activeTab = page.tabs.find((tab) => tab.id === query.tab) ?? page.tabs[0];
  if (!activeTab) notFound();

  const hrefWith = (changes: Query) => {
    const params = new URLSearchParams({ account: accountId, tab: activeTab.id, dir: direction, ...changes });
    return `/?${params}`;
  };

  return (
    <main className="site" dir={direction} style={tokensToCssVars(theme.design_tokens)}>
      <div className="site-inner">
        <nav className="demo-controls" aria-label="Demo controls">
          {DEMO_ACCOUNTS.map((id) => (
            <Link key={id} href={hrefWith({ account: id })} aria-current={id === accountId}>
              {id}
            </Link>
          ))}
          <Link href={hrefWith({ dir: "ltr" })} aria-current={direction === "ltr"}>LTR</Link>
          <Link href={hrefWith({ dir: "rtl" })} aria-current={direction === "rtl"}>RTL</Link>
          <span>
            theme: {theme.theme_id}@{theme.theme_version}
          </span>
        </nav>

        <h1>{page.title}</h1>

        <div role="tablist" className="tablist">
          {page.tabs.map((tab) => (
            <Link
              key={tab.id}
              id={`tab-${tab.id}`}
              role="tab"
              className="tab"
              aria-selected={tab.id === activeTab.id}
              aria-controls={`panel-${tab.id}`}
              href={hrefWith({ tab: tab.id })}
            >
              {tab.label}
            </Link>
          ))}
        </div>

        <section role="tabpanel" id={`panel-${activeTab.id}`} aria-labelledby={`tab-${activeTab.id}`}>
          {activeTab.body.map((block) => (
            <CatalogueBlock
              key={block.id}
              block={block}
              manifests={assets}
              direction={direction}
              ids={{
                websiteId: page.website_id,
                pageId: page.id,
                tabId: activeTab.id,
                themeId: theme.theme_id,
                themeVersion: theme.theme_version,
              }}
            />
          ))}
        </section>
      </div>

      <UsageBeacon
        context={{
          ...account,
          page_id: page.id,
          tab_id: activeTab.id,
          theme_id: theme.theme_id,
          theme_version: theme.theme_version,
        }}
      />
    </main>
  );
}
