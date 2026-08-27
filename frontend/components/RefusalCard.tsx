"use client";

import { ChatResponse } from "@/lib/api";

interface RefusalCardProps {
  response: ChatResponse;
  onPick: (query: string) => void;
}

const FACTUAL_REDIRECTIONS = [
  "Riskometer",
  "Benchmark",
  "Expense ratio (Direct)",
  "Exit load",
  "Lock-in",
];

export function RefusalCard({ response, onPick }: RefusalCardProps) {
  return (
    <article
      className="bg-card border border-rule border-l-4 border-l-halt rounded-[3px] p-5 shadow-answer animate-rise"
      aria-label="Investment advice refusal notice"
    >
      <div className="pb-2 mb-2 border-b border-rule/60 flex items-center justify-between">
        <span className="mono-label text-halt font-mono text-[10px]">
          Statutory Constraint · Advice Refusal
        </span>
      </div>

      <p className="text-[15px] text-ink leading-relaxed m-0 font-normal">
        {response.message}
      </p>

      <div className="mt-4 pt-3 border-t border-rule">
        <p className="mono-label-sm text-ink-3 mb-2">
          Factual baseline to evaluate independently
        </p>
        <div className="flex flex-wrap gap-1.5">
          {FACTUAL_REDIRECTIONS.map((fact) => (
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
    </article>
  );
}
