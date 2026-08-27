"use client";

import React, { forwardRef } from "react";
import { Search } from "lucide-react";

interface AskBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  selectedSchemeName?: string | null;
}

export const AskBar = forwardRef<HTMLInputElement, AskBarProps>(function AskBar(
  { value, onChange, onSubmit, disabled = false, selectedSchemeName },
  ref
) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSubmit();
  };

  return (
    <div className="w-full space-y-2">
      <form
        onSubmit={handleSubmit}
        className="w-full flex gap-2"
        aria-label="Factual question form"
      >
        <div className="relative flex-1">
          <label htmlFor="question-input" className="sr-only">
            Ask a factual question
          </label>
          <input
            id="question-input"
            ref={ref}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            maxLength={400}
            disabled={disabled}
            placeholder={
              selectedSchemeName
                ? `Ask a fact about ${selectedSchemeName}…`
                : "Ask a factual question about a selected scheme…"
            }
            className="w-full h-12 px-4 font-body text-[15px] bg-card text-ink border border-rule rounded-[3px] placeholder:text-ink-3 focus-visible:outline-none disabled:opacity-60 transition-colors"
          />
        </div>

        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="h-12 min-h-[44px] px-6 bg-ink text-white font-mono text-[14px] font-medium tracking-wide rounded-[3px] hover:bg-ink/90 active:bg-ink disabled:bg-rule disabled:text-ink-3 disabled:cursor-not-allowed transition-colors duration-120 flex items-center gap-2 focus-visible:outline-none"
        >
          <Search className="w-4 h-4 stroke-[2]" aria-hidden="true" />
          <span>Ask</span>
        </button>
      </form>

      {/* Input helper text (Section P2) */}
      <p className="font-mono text-[11px] text-ink-3 m-0 pl-1">
        Ask about minimum SIP, expense ratio, exit load, benchmark, riskometer or lock-in.
      </p>
    </div>
  );
});
