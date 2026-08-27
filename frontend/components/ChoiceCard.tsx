"use client";

import { ChatResponse } from "@/lib/api";

interface ChoiceCardProps {
  response: ChatResponse;
  onPickScheme: (schemeId: string) => void;
}

export function ChoiceCard({ response, onPickScheme }: ChoiceCardProps) {
  const hasCandidates = response.candidates && response.candidates.length > 0;

  return (
    <article
      className="bg-card border border-rule border-l-4 border-l-verified rounded-[3px] p-5 shadow-answer animate-rise"
      aria-label="Scheme selection required"
    >
      <div className="pb-2 mb-2 border-b border-rule/60">
        <span className="mono-label text-verified font-mono text-[10px]">
          Scheme Specification Required
        </span>
      </div>

      <p className="text-[15px] text-ink leading-relaxed m-0 mb-3">
        {response.message}
      </p>

      {hasCandidates && (
        <div className="flex flex-wrap gap-2 pt-2">
          {response.candidates?.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => onPickScheme(c.id)}
              className="px-3 py-1.5 text-[13px] font-mono bg-paper hover:bg-rule/80 text-ink border border-rule rounded-[2px] transition-colors duration-120 text-left focus-visible:outline-none"
            >
              {c.name}
            </button>
          ))}
        </div>
      )}
    </article>
  );
}
