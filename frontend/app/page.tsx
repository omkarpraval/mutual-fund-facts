"use client";

import { useEffect, useRef, useState } from "react";
import {
  ask,
  getSchemes,
  getCoverage,
  ChatResponse,
  Scheme,
  CoverageResponse,
} from "@/lib/api";
import { CoverageLedger } from "@/components/CoverageLedger";
import { AskBar } from "@/components/AskBar";
import { VerifySequence } from "@/components/VerifySequence";
import { ResponseState } from "@/components/ResponseState";

export default function Page() {
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [coverageData, setCoverageData] = useState<CoverageResponse | null>(null);
  const [selectedSchemeId, setSelectedSchemeId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [lastAskedQuestion, setLastAskedQuestion] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [response, setResponse] = useState<ChatResponse | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const responseAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initial fetch of schemes and full coverage matrix
    Promise.all([getSchemes(), getCoverage()]).then(([sData, cData]) => {
      setSchemes(sData);
      setCoverageData(cData);
    });
  }, []);

  const handleQuery = async (
    queryText: string,
    schemeOverride?: string | null
  ) => {
    const trimmed = queryText.trim();
    if (!trimmed || isBusy) return;

    setLastAskedQuestion(trimmed);
    const targetSchemeId =
      schemeOverride !== undefined ? schemeOverride : selectedSchemeId;

    setIsBusy(true);
    setResponse(null);

    const res = await ask(trimmed, targetSchemeId);
    setResponse(res);

    // If answer resolved a specific scheme, reflect it in Scheme Context
    if (res.scheme) {
      const matched = schemes.find((s) => s.name === res.scheme);
      if (matched) {
        setSelectedSchemeId(matched.id);
      }
    }

    setIsBusy(false);

    setTimeout(() => {
      responseAreaRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }, 50);
  };

  const handleFactClick = (schemeId: string, factLabel: string) => {
    const scheme = schemes.find((s) => s.id === schemeId);
    setSelectedSchemeId(schemeId);
    const query = scheme
      ? `What is the ${factLabel.toLowerCase()} of ${scheme.name}?`
      : `What is the ${factLabel.toLowerCase()}?`;
    setQuestion(query);
    handleQuery(query, schemeId);
  };

  const handleSchemeDisambiguation = (chosenSchemeId: string) => {
    setSelectedSchemeId(chosenSchemeId);
    // Re-run the user's original question against the chosen scheme (Section P1)
    const queryToRun = lastAskedQuestion || question.trim();
    if (queryToRun) {
      handleQuery(queryToRun, chosenSchemeId);
    }
  };

  const activeScheme = schemes.find((s) => s.id === selectedSchemeId);

  return (
    <div className="min-h-screen bg-paper flex flex-col justify-between">
      {/* Sticky Compliance-Adjacent Header (Section P2) */}
      <header className="sticky top-0 z-40 w-full bg-paper/95 backdrop-blur-sm border-b border-rule shadow-sm">
        <div className="max-w-[1120px] mx-auto px-4 sm:px-6 py-3.5 flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1">
          <div>
            <h1 className="font-display text-[26px] sm:text-[30px] text-ink font-normal tracking-tight m-0 leading-none">
              Mutual Fund Facts
            </h1>
            <p className="text-[12px] sm:text-[13px] text-ink-2 mt-0.5 font-body m-0">
              Verified information from official AMC, AMFI, and SEBI disclosures
            </p>
          </div>
          <div className="mono-label text-verified font-mono text-[10px] sm:text-[11px] font-semibold tracking-wider pt-0.5 sm:pt-0">
            Facts Only · No Investment Advice
          </div>
        </div>
      </header>

      <main className="w-full max-w-[1120px] mx-auto px-4 sm:px-6 py-6 sm:py-8 flex-1">
        {/* Two-Column Desktop Layout (1024px+), Single-Column Mobile */}
        <div className="flex flex-col lg:flex-row items-start gap-8">
          {/* Left Column: 380px Desktop — The Certainty Ledger & Scheme Context */}
          <aside className="w-full lg:w-[380px] lg:shrink-0">
            <CoverageLedger
              coverageData={coverageData}
              schemes={schemes}
              selectedSchemeId={selectedSchemeId}
              onSchemeSelect={setSelectedSchemeId}
              onQueryFact={handleFactClick}
            />
          </aside>

          {/* Right Column: 720px Max Desktop — Ask Bar & Answer State */}
          <section className="w-full lg:flex-1 lg:min-w-0 lg:max-w-[720px] space-y-6">
            {/* Ask Input Bar with Quiet Helper Line */}
            <div className="w-full">
              <AskBar
                ref={inputRef}
                value={question}
                onChange={setQuestion}
                onSubmit={() => handleQuery(question)}
                disabled={isBusy}
                selectedSchemeName={activeScheme?.name}
              />
            </div>

            {/* Response Display Region */}
            <div
              ref={responseAreaRef}
              aria-live="polite"
              aria-atomic="true"
              className="w-full min-h-[160px]"
            >
              {isBusy ? (
                <VerifySequence />
              ) : (
                <ResponseState
                  response={response}
                  onPick={(q) => {
                    setQuestion(q);
                    handleQuery(q);
                  }}
                  onPickScheme={handleSchemeDisambiguation}
                  onRetry={() => handleQuery(question)}
                />
              )}
            </div>
          </section>
        </div>
      </main>

      {/* Statutory Disclaimer Footer */}
      <footer className="w-full border-t border-rule bg-card/60 py-6 px-4 sm:px-6 mt-12">
        <div className="max-w-[1120px] mx-auto text-[13px] text-ink-2/80 font-body leading-relaxed">
          <p className="m-0">
            <strong>Statutory Disclosure:</strong> This assistant provides factual information compiled exclusively from selected official Scheme Information Documents (SID), Key Information Memorandums (KIM), AMFI, and SEBI regulatory filings. It does not provide investment, financial, taxation, or portfolio allocation advice. Do not submit personal identifiable information (PAN, Aadhaar, account credentials, OTPs, or contact numbers).
          </p>
        </div>
      </footer>
    </div>
  );
}
