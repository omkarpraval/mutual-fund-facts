"use client";

import { ShieldAlert, AlertTriangle, WifiOff } from "lucide-react";

interface NoticeCardProps {
  type: "pii" | "too_long" | "error";
  message: string;
  onRetry?: () => void;
}

export function NoticeCard({ type, message, onRetry }: NoticeCardProps) {
  if (type === "pii") {
    return (
      <article
        className="bg-card border border-rule border-l-4 border-l-halt rounded-[3px] p-5 shadow-answer animate-rise"
        aria-label="Personal information security notice"
      >
        <div className="flex items-center gap-2 pb-2 mb-2 border-b border-rule/60 text-halt">
          <ShieldAlert className="w-4 h-4 stroke-[2]" aria-hidden="true" />
          <span className="mono-label font-mono text-[10px]">
            Privacy Guard · Data Redacted
          </span>
        </div>
        <p className="text-[15px] text-ink leading-relaxed m-0">
          {message}
        </p>
        <p className="text-[12px] font-mono text-ink-3 mt-3 pt-2 border-t border-rule">
          Personal identification numbers (PAN, Aadhaar), account numbers, and contact details are rejected before processing.
        </p>
      </article>
    );
  }

  if (type === "too_long") {
    return (
      <article
        className="bg-card border border-rule border-l-4 border-l-ink-3 rounded-[3px] p-5 shadow-answer animate-rise"
        aria-label="Query length limit notice"
      >
        <div className="flex items-center gap-2 pb-2 mb-2 border-b border-rule/60 text-ink-2">
          <AlertTriangle className="w-4 h-4 stroke-[2]" aria-hidden="true" />
          <span className="mono-label font-mono text-[10px]">
            Scope Notice · Query Length
          </span>
        </div>
        <p className="text-[15px] text-ink leading-relaxed m-0">
          {message}
        </p>
      </article>
    );
  }

  return (
    <article
      className="bg-card border border-rule border-l-4 border-l-halt rounded-[3px] p-5 shadow-answer animate-rise"
      aria-label="Connection error notice"
    >
      <div className="flex items-center gap-2 pb-2 mb-2 border-b border-rule/60 text-halt">
        <WifiOff className="w-4 h-4 stroke-[2]" aria-hidden="true" />
        <span className="mono-label font-mono text-[10px]">
          Service Unavailable
        </span>
      </div>
      <p className="text-[15px] text-ink leading-relaxed m-0">
        {message || "The assistant backend could not be reached. Check that the API service is active, then submit again."}
      </p>
      {onRetry && (
        <div className="mt-4 pt-2">
          <button
            type="button"
            onClick={onRetry}
            className="px-3 py-1.5 text-[13px] font-mono font-medium bg-ink text-white rounded-[2px] hover:opacity-90 focus-visible:outline-none"
          >
            Retry Request
          </button>
        </div>
      )}
    </article>
  );
}
