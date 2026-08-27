export type State =
  | "answer"
  | "refusal"
  | "pii"
  | "needs_scheme"
  | "no_evidence"
  | "known_gap"
  | "too_long"
  | "error";

export interface Citation {
  title: string;
  url: string;
  organization: string;
  last_updated: string | null;
  fact_as_of: string | null;
  source_dated: string | null;
  retrieved_at: string | null;
}

export interface ChatResponse {
  state: State;
  message: string;
  scheme?: string | null;
  citations: Citation[];
  stale: boolean;
  conflict?: string | null;
  known_gap?: boolean;
  available?: string[];
  candidates?: { id: string; name: string }[];
  partial_refusal?: string | null;
  verification?: "verified" | "conditional";
  condition?: string | null;
  fact_label?: string | null;
  fact_value?: string | null;
}

export interface Scheme {
  id: string;
  name: string;
  former_name: string | null;
}

export interface CoverageColumn {
  topic: string;
  label: string;
}

export interface CoverageCell {
  topic: string;
  label: string;
  state: "verified" | "conditional" | "gap" | "na";
}

export interface CoverageRow {
  scheme_id: string;
  scheme_name: string;
  former_name: string | null;
  cells: CoverageCell[];
}

export interface CoverageResponse {
  columns: CoverageColumn[];
  rows: CoverageRow[];
  chips: Record<string, string[]>;
}

const BASE =
  process.env.NEXT_PUBLIC_API ||
  (typeof window !== "undefined" ? "" : "http://localhost:8000");

export async function ask(
  question: string,
  schemeId: string | null
): Promise<ChatResponse> {
  try {
    const res = await fetch(`${BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, scheme_id: schemeId }),
    });
    if (!res.ok) throw new Error(String(res.status));
    return await res.json();
  } catch {
    return {
      state: "error",
      citations: [],
      stale: false,
      message:
        "The assistant is not reachable. Check that the backend is running, then ask again.",
    };
  }
}

export async function getCoverage(): Promise<CoverageResponse | null> {
  try {
    const res = await fetch(`${BASE}/api/coverage`);
    return res.ok ? await res.json() : null;
  } catch {
    return null;
  }
}

export async function getSchemes(): Promise<Scheme[]> {
  try {
    const res = await fetch(`${BASE}/api/schemes`);
    return res.ok ? await res.json() : [];
  } catch {
    return [];
  }
}
