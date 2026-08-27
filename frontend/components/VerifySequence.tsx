"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";

interface Step {
  id: number;
  label: string;
}

const STEPS: Step[] = [
  { id: 0, label: "Checking for personal information" },
  { id: 1, label: "Resolving scheme" },
  { id: 2, label: "Locating official source" },
  { id: 3, label: "Validating citation" },
];

export function VerifySequence() {
  const [activeStep, setActiveStep] = useState<number>(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 150);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="p-5 bg-card border border-rule rounded-[3px] shadow-answer"
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="flex items-center justify-between border-b border-rule pb-2 mb-3">
        <span className="mono-label text-ink-3 font-mono text-[10px]">
          Pipeline Verification
        </span>
        <span className="mono-label font-mono text-[10px] text-verified">
          Step {Math.min(activeStep + 1, 4)} of 4
        </span>
      </div>

      <ul className="space-y-2.5 my-1" aria-label="Verification progress">
        {STEPS.map((step) => {
          const isDone = activeStep > step.id;
          const isCurrent = activeStep === step.id;

          return (
            <li
              key={step.id}
              className={`flex items-center gap-2.5 font-mono text-[13px] transition-colors duration-150 ${
                isDone
                  ? "text-verified font-medium"
                  : isCurrent
                  ? "text-ink font-medium"
                  : "text-ink-3 opacity-40"
              }`}
            >
              <div
                className={`w-4 h-4 rounded-[2px] flex items-center justify-center border text-[10px] ${
                  isDone
                    ? "bg-verified border-verified text-white"
                    : isCurrent
                    ? "border-ink text-ink animate-pulse"
                    : "border-rule text-transparent"
                }`}
                aria-hidden="true"
              >
                {isDone ? <Check className="w-3 h-3 stroke-[2.5]" /> : "·"}
              </div>
              <span>{step.label}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
