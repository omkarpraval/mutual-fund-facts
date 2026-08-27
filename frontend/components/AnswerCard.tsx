"use client";

import React from "react";
import { ChatResponse } from "@/lib/api";
import { Provenance } from "./Provenance";
import { Riskometer } from "./Riskometer";

interface AnswerCardProps {
  response: ChatResponse;
  onPick: (query: string) => void;
}

const SIP_FREQUENCIES = [
  "Daily",
  "Weekly",
  "Monthly",
  "Quarterly",
  "Semi-annual",
  "Annual",
];

export function AnswerCard({ response, onPick }: AnswerCardProps) {
  const isRiskometerTopic =
    response.message.toLowerCase().includes("riskometer") ||
    response.citations.some((c) =>
      c.title.toLowerCase().includes("riskometer")
    );

  const isMinSipTopic =
    response.message.toLowerCase().includes("sip") ||
    response.citations.some((c) => c.title.toLowerCase().includes("kim"));

  const isConditional =
    response.verification === "conditional" || isRiskometerTopic;

  const hasStructuredFact = Boolean(
    response.fact_label && response.fact_value && !isRiskometerTopic
  );

  // Compute remainder of message cleanly without regex string splitting
  let remainder = "";
  if (hasStructuredFact && response.fact_value && response.message) {
    const valIdx = response.message.indexOf(response.fact_value);
    if (valIdx !== -1) {
      const after = response.message
        .slice(valIdx + response.fact_value.length)
        .trim();
      remainder = after.replace(/^[.,\s]+/, "").trim();
    }
  }

  const isLongValue = (response.fact_value?.length ?? 0) > 24;

  return (
    <article
      className="bg-card border border-rule rounded-[3px] p-6 shadow-answer animate-rise"
      aria-label="Verified factual answer"
    >
      {/* Verification State Badge (Section P0 & P2) */}
      <div className="flex items-center justify-between border-b border-rule pb-2.5 mb-4">
        <div className="flex items-center gap-2 font-mono text-[10px] tracking-[0.08em] uppercase">
          {isConditional ? (
            <>
              <span
                className="w-2.5 h-2.5 bg-conditional rounded-[1px] inline-block shrink-0"
                aria-hidden="true"
              />
              <span className="text-conditional font-medium">
                Verified, with a condition
              </span>
            </>
          ) : (
            <>
              <span
                className="w-2.5 h-2.5 bg-verified rounded-[1px] inline-block shrink-0"
                aria-hidden="true"
              />
              <span className="text-verified font-medium">
                Verified from official source
              </span>
            </>
          )}
        </div>

        {response.scheme && (
          <span className="mono-label text-ink-3 font-mono text-[10px]">
            {response.scheme}
          </span>
        )}
      </div>

      {/* Scheme Conflict Notice */}
      {response.conflict && response.scheme && (
        <div className="font-mono text-[11px] text-ink-3 tracking-wide mb-3 pb-2 border-b border-rule">
          Selector specified {response.conflict}; question asks about {response.scheme}. Answering for {response.scheme}.
        </div>
      )}

      {/* Structured Key Fact First (Section P0) or Plain Prose Fallback */}
      <div className="my-2">
        {hasStructuredFact ? (
          <div className="space-y-1.5 my-1">
            <div className="mono-label text-ink-3 font-mono text-[10px] tracking-[0.08em]">
              {response.fact_label}
            </div>
            <div
              className={`font-display text-ink leading-tight tracking-tight ${
                isLongValue ? "text-[21px]" : "text-[40px]"
              }`}
            >
              {response.fact_value}
            </div>
            {remainder && (
              <p className="font-body text-[15px] text-ink-2 leading-normal pt-1 m-0">
                {remainder}
              </p>
            )}
          </div>
        ) : (
          <div className="font-body text-[17px] text-ink-2 leading-[1.55]">
            {response.message}
          </div>
        )}
      </div>

      {/* Authentic SEBI Riskometer Gauge if applicable */}
      {isRiskometerTopic && <Riskometer text={response.message} />}

      {/* Condition Reasoning Text (Section P0 & P2) */}
      {(response.condition || (isConditional && isRiskometerTopic)) && (
        <div
          className="mt-3.5 p-3 bg-paper/60 border-l-2 border-conditional text-[13px] text-ink-2 leading-relaxed"
          role="note"
          aria-label="Verification condition explanation"
        >
          <div className="mono-label text-conditional text-[10px] font-medium mb-0.5">
            Verification Condition
          </div>
          {response.condition ||
            "Taken from the KIM, which is a snapshot. The monthly factsheet is the authoritative source for this value."}
        </div>
      )}

      {/* Partial Refusal Notice */}
      {response.partial_refusal && (
        <div
          className="mt-4 p-3 bg-paper/60 border-l-2 border-halt text-[14px] text-ink-2 leading-relaxed"
          role="note"
          aria-label="Advisory clause refusal note"
        >
          <div className="mono-label text-halt text-[10px] font-medium mb-1">
            Advisory Clause Excluded
          </div>
          {response.partial_refusal}
        </div>
      )}

      {/* Provenance Block */}
      <Provenance citations={response.citations} stale={response.stale} />

      {/* Other Frequencies Chips for SIP */}
      {isMinSipTopic && (
        <div className="mt-4 pt-3 border-t border-rule">
          <p className="mono-label-sm text-ink-3 mb-2 font-mono text-[10px]">
            Other frequencies
          </p>
          <div className="flex flex-wrap gap-1.5">
            {SIP_FREQUENCIES.map((freq) => {
              const query = response.scheme
                ? `What is the minimum ${freq.toLowerCase()} SIP for ${response.scheme}?`
                : `What is the minimum ${freq.toLowerCase()} SIP?`;
              return (
                <button
                  key={freq}
                  type="button"
                  onClick={() => onPick(query)}
                  className="px-2.5 py-1 text-[12px] font-mono bg-paper hover:bg-rule/70 text-ink-2 border border-rule rounded-[2px] transition-colors duration-120 text-left focus-visible:outline-none"
                >
                  {freq}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Related Facts Chips */}
      {response.available && response.available.length > 0 && (
        <div className="mt-4 pt-3 border-t border-rule">
          <p className="mono-label-sm text-ink-3 mb-2 font-mono text-[10px]">
            Related facts for {response.scheme || "this scheme"}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {response.available.slice(0, 6).map((fact) => (
              <button
                key={fact}
                type="button"
                onClick={() => onPick(`What is the ${fact.toLowerCase()}?`)}
                className="px-2.5 py-1 text-[12px] font-mono bg-paper hover:bg-rule/70 text-ink-2 border border-rule rounded-[2px] transition-colors duration-120 text-left focus-visible:outline-none"
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
