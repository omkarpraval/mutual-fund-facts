"use client";

import { ArrowRight } from "lucide-react";

interface EmptyStateProps {
  onPick: (query: string) => void;
}

const VERIFIED_EXAMPLES = [
  "What is the minimum SIP for SBI Flexicap Fund?",
  "What is the expense ratio for SBI Large Cap Fund?",
  "What is the lock-in period for SBI ELSS Tax Saver Fund?",
  "What is the riskometer rating of SBI Flexicap Fund?",
];

export function EmptyState({ onPick }: EmptyStateProps) {
  return (
    <div
      className="bg-card border border-dashed border-rule rounded-[3px] p-6 shadow-answer"
      role="region"
      aria-label="Getting started with verified facts"
    >
      <div className="border-b border-rule pb-2 mb-3">
        <span className="mono-label text-ink-3 font-mono text-[10px]">
          Factual Query Assistant
        </span>
      </div>

      <h3 className="font-display text-[22px] text-ink font-normal mb-2 leading-snug">
        Official mutual fund facts, cited at source.
      </h3>

      <p className="text-[14px] text-ink-2 mb-4 leading-relaxed">
        Select a scheme on the left or ask a question directly. All figures are verified directly from Scheme Information Documents (SID), Key Information Memorandums (KIM), AMFI, and SEBI disclosures.
      </p>

      <div className="space-y-2">
        <p className="mono-label-sm text-ink-3">
          Example queries with official verification:
        </p>
        <div className="grid grid-cols-1 gap-2">
          {VERIFIED_EXAMPLES.map((query) => (
            <button
              key={query}
              type="button"
              onClick={() => onPick(query)}
              className="group flex items-center justify-between w-full text-left px-3.5 py-2.5 bg-paper hover:bg-rule/60 border border-rule rounded-[2px] transition-colors duration-120 focus-visible:outline-none"
            >
              <span className="text-[13px] text-ink font-mono group-hover:text-ink">
                {query}
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-ink-3 group-hover:text-verified group-hover:translate-x-0.5 transition-all duration-120" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
