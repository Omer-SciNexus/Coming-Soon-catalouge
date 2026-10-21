import type { SitePayload } from "./types";

const DJANGO_URL = process.env.DJANGO_URL ?? "http://127.0.0.1:8000";

// Accounts that have a published page, in the order the demo bar shows them.
export async function getAccounts(): Promise<string[]> {
  const url = `${DJANGO_URL}/api/sites/`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`Django returned ${response.status} for ${url}`);
  const data: { accounts: string[] } = await response.json();
  return data.accounts;
}

// Returns null when Django does not know the account (the page then shows 404).
// `no-store`: every request reads the current database records, so a change in
// the admin is visible on the next refresh.
export async function getSite(accountId: string): Promise<SitePayload | null> {
  const url = `${DJANGO_URL}/api/sites/${encodeURIComponent(accountId)}/`;
  const response = await fetch(url, { cache: "no-store" });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`Django returned ${response.status} for ${url}`);
  return response.json();
}
