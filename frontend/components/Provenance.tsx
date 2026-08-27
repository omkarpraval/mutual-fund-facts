"use client";

import { Citation } from "@/lib/api";
import { ExternalLink } from "lucide-react";

interface ProvenanceProps {
  citations: Citation[];
  stale?: boolean;
}

function formatDate(dateStr: string | null): string | null {
  if (!dateStr) return null;
  const parsed = new Date(dateStr + "T00:00:00");
  if (isNaN(parsed.getTime())) return dateStr;
  return parsed.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function Provenance({ citations, stale = false }: ProvenanceProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <section
      className="mt-5 pt-4 border-t border-rule"
      aria-label="Official source citations and provenance"
    >
      {stale && (
        <div className="mb-3 px-2 py-1 bg-conditional/10 border-l-2 border-conditional text-conditional font-mono text-[11px] uppercase tracking-wider">
          May not be current — verify at official source
        </div>
      )}

      {citations.map((c, idx) => {
        const factAsOfFormatted = formatDate(c.fact_as_of);
        const sourceDatedFormatted = formatDate(c.source_dated);
        const retrievedAtFormatted = formatDate(c.retrieved_at);

        return (
          <div key={`${c.url}-${idx}`} className="space-y-3">
            <div>
              <p className="mono-label text-ink-3 text-[10px] mb-1">
                Official Source
              </p>
              <h4 className="text-[14px] font-semibold text-ink leading-snug">
                {c.organization}
              </h4>
              <p className="text-[13px] text-ink-2 mt-0.5 leading-snug">
                {c.title}
              </p>
            </div>

            {/* Three distinct dates - strictly separated per Section 9 */}
            <dl className="grid grid-cols-[110px_1fr] gap-y-1 font-mono text-[12px] pt-1">
              {factAsOfFormatted && (
                <>
                  <dt className={stale ? "text-conditional font-medium" : "text-verified font-medium"}>
                    Fact as of
                  </dt>
                  <dd className={stale ? "text-conditional font-medium m-0" : "text-verified font-medium m-0"}>
                    {factAsOfFormatted}
                  </dd>
                </>
              )}

              {sourceDatedFormatted && (
                <>
                  <dt className="text-ink-3">Source dated</dt>
                  <dd className="text-ink-3 m-0">{sourceDatedFormatted}</dd>
                </>
              )}

              {retrievedAtFormatted && (
                <>
                  <dt className="text-ink-3">Retrieved</dt>
                  <dd className="text-ink-3 m-0">{retrievedAtFormatted}</dd>
                </>
              )}
            </dl>

            <div className="pt-1">
              <a
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-[13px] font-mono font-medium text-verified hover:underline focus-visible:outline-none"
              >
                <span>View official source</span>
                <ExternalLink className="w-3.5 h-3.5 stroke-[2]" aria-hidden="true" />
                <span className="sr-only">
                  (opens {c.organization} document in a new tab)
                </span>
              </a>
            </div>
          </div>
        );
      })}
    </section>
  );
}
