"use client";

import { ChatResponse } from "@/lib/api";

interface GapCardProps {
  response: ChatResponse;
  onPick: (query: string) => void;
}

export function GapCard({ response, onPick }: GapCardProps) {
  const isKnownGap = response.state === "known_gap" || response.known_gap;

  return (
    <article
      className="bg-card border border-rule border-l-4 border-l-gap rounded-[3px] p-5 shadow-answer animate-rise"
      aria-label={isKnownGap ? "Known fact gap notice" : "No evidence notice"}
    >
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-rule/60">
        <span className="mono-label text-ink-3 font-mono text-[10px]">
          {isKnownGap
            ? "Fact Boundary · Not Yet Verified"
            : "Outside Verified Knowledge Boundary"}
        </span>
        {response.scheme && (
          <span className="mono-label text-ink-2 font-mono text-[10px]">
            {response.scheme}
          </span>
        )}
      </div>

      <p className="text-[15px] text-ink leading-relaxed m-0">
        {response.message}
      </p>

      {/* Related facts chips row (Section P1) */}
      {response.available && response.available.length > 0 && (
        <div className="mt-4 pt-3 border-t border-rule">
          <p className="mono-label-sm text-ink-3 mb-2 font-mono text-[10px]">
            Related facts for {response.scheme || "selection"}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {response.available.map((fact) => (
              <button
                key={fact}
                type="button"
                onClick={() => onPick(`What is the ${fact.toLowerCase()}?`)}
                className="px-2.5 py-1 text-[12px] font-mono bg-paper hover:bg-rule/70 text-ink border border-rule rounded-[2px] transition-colors duration-120 focus-visible:outline-none"
              >
                {fact}
              </button>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
