"use client";

import React, { useState } from "react";
import { CoverageResponse, CoverageCell, Scheme } from "@/lib/api";
import {
  TooltipProvider,
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "./Tooltip";
import { X } from "lucide-react";

interface CoverageLedgerProps {
  coverageData: CoverageResponse | null;
  schemes: Scheme[];
  selectedSchemeId: string | null;
  onSchemeSelect: (id: string | null) => void;
  onQueryFact: (schemeId: string, factLabel: string) => void;
}

const COLUMN_ABBREVIATIONS: Record<string, string> = {
  scheme_type: "Type",
  scheme_category: "Cat",
  investment_objective: "Objective",
  min_lumpsum: "Min inv",
  min_sip: "Min SIP",
  additional_purchase: "Addl",
  exit_load: "Exit",
  lock_in: "Lock-in",
  ter_regular: "TER (R)",
  ter_direct: "TER (D)",
  benchmark: "Bench",
  riskometer: "Risk",
};

function getCellTooltipText(
  schemeName: string,
  label: string,
  state: CoverageCell["state"]
): string {
  switch (state) {
    case "verified":
      return `${schemeName} · ${label}\nVerified from official source`;
    case "conditional":
      return `${schemeName} · ${label}\nVerified, with a condition: the KIM is a snapshot, the monthly factsheet is the authority`;
    case "gap":
      return `${schemeName} · ${label}\nNot yet verified for this scheme`;
    case "na":
      return `${schemeName} · ${label}\nNot applicable to this scheme type`;
  }
}

export function CoverageLedger({
  coverageData,
  schemes,
  selectedSchemeId,
  onSchemeSelect,
  onQueryFact,
}: CoverageLedgerProps) {
  const [showAllColumns, setShowAllColumns] = useState(false);

  const columns = coverageData?.columns || [];
  const rows = coverageData?.rows || [];

  // Default show first 7 on compact desktop panel, full 12 when expanded
  const visibleColumns = showAllColumns ? columns : columns.slice(0, 7);
  const remainingCount = columns.length - visibleColumns.length;

  const activeScheme = schemes.find((s) => s.id === selectedSchemeId);

  return (
    <TooltipProvider delayDuration={150}>
      <div className="w-full bg-card border border-rule rounded-[3px] p-5 shadow-answer">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-rule pb-3 mb-4">
          <div>
            <h2 className="mono-label text-ink font-mono text-[12px] font-semibold tracking-wider m-0">
              Certainty Ledger
            </h2>
            <p className="text-[12px] text-ink-3 m-0 mt-0.5">
              Verified knowledge boundary across schemes
            </p>
          </div>
          <span className="mono-label-sm text-verified font-mono text-[10px] bg-verified/10 px-2 py-0.5 rounded-[2px]">
            12 Facts Index
          </span>
        </div>

        {/* Scheme Context (Section P1) */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <label
              htmlFor="scheme-ledger-select"
              className="mono-label text-ink-3 block text-[10px]"
            >
              Scheme Context
            </label>
            {selectedSchemeId && (
              <button
                type="button"
                onClick={() => onSchemeSelect(null)}
                className="font-mono text-[10px] text-ink-3 hover:text-halt flex items-center gap-1 focus-visible:outline-none transition-colors"
                title="Clear scheme context to all 3 schemes"
              >
                <X className="w-3 h-3" />
                <span>clear</span>
              </button>
            )}
          </div>

          {activeScheme ? (
            <div className="p-2.5 bg-paper border border-rule rounded-[3px] text-left">
              <div className="flex items-center justify-between">
                <div className="text-[13px] font-medium text-ink font-mono">
                  Answering for: {activeScheme.name}
                </div>
                <button
                  type="button"
                  onClick={() => onSchemeSelect(null)}
                  className="font-mono text-[10px] text-ink-3 hover:text-ink px-1.5 py-0.5 border border-rule/60 rounded-[2px] bg-card focus-visible:outline-none"
                >
                  clear
                </button>
              </div>
              {activeScheme.former_name && (
                <div className="font-mono text-[11px] text-ink-3 mt-1 tracking-wide">
                  Formerly {activeScheme.former_name}
                </div>
              )}
            </div>
          ) : (
            <select
              id="scheme-ledger-select"
              value=""
              onChange={(e) => onSchemeSelect(e.target.value || null)}
              className="w-full h-10 px-3 font-body text-[14px] bg-paper text-ink border border-rule rounded-[3px] focus-visible:outline-none"
            >
              <option value="">All 3 schemes (unfiltered)</option>
              {schemes.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Desktop Certainty Matrix */}
        <div className="hidden lg:block">
          <div className="overflow-x-auto">
            <table
              className="w-full border-collapse text-left"
              aria-label="Mutual fund certainty matrix"
            >
              <thead>
                <tr className="border-b border-rule font-mono text-[11px] text-ink-2">
                  <th scope="col" className="py-2 pr-1 font-medium w-[88px] text-[11px]">
                    Scheme
                  </th>
                  {visibleColumns.map((col) => {
                    const abbr =
                      COLUMN_ABBREVIATIONS[col.topic] || col.label.slice(0, 5);
                    return (
                      <th
                        key={col.topic}
                        scope="col"
                        className="py-2 px-1 text-center font-normal"
                      >
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <button
                              type="button"
                              className="font-mono text-[11px] text-ink-2 hover:text-ink focus-visible:outline-none font-medium cursor-help"
                            >
                              {abbr}
                            </button>
                          </TooltipTrigger>
                          <TooltipContent side="top">
                            <span className="font-semibold">{col.label}</span>
                          </TooltipContent>
                        </Tooltip>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => {
                  const isRowSelected = selectedSchemeId === row.scheme_id;
                  const cellsByTopic = new Map(
                    row.cells.map((c) => [c.topic, c])
                  );

                  return (
                    <tr
                      key={row.scheme_id}
                      className={`border-b border-rule/60 transition-colors duration-120 ${
                        isRowSelected
                          ? "bg-paper font-medium"
                          : "hover:bg-paper/40"
                      }`}
                    >
                      <th
                        scope="row"
                        className="py-2.5 pr-1 font-mono text-[11px] text-ink truncate max-w-[90px]"
                        title={row.scheme_name}
                      >
                        {row.scheme_name.replace("SBI ", "")}
                      </th>

                      {visibleColumns.map((col) => {
                        const cell = cellsByTopic.get(col.topic) || {
                          topic: col.topic,
                          label: col.label,
                          state: "gap" as const,
                        };
                        const tooltipText = getCellTooltipText(
                          row.scheme_name,
                          cell.label,
                          cell.state
                        );

                        if (cell.state === "na") {
                          return (
                            <td
                              key={col.topic}
                              className="py-2 px-1 text-center"
                            >
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span
                                    tabIndex={0}
                                    className="w-4 h-4 mx-auto inline-flex items-center justify-center text-ink-3/40 font-mono text-[11px] cursor-default focus-visible:outline-none"
                                    aria-label={tooltipText.replace("\n", " — ")}
                                  >
                                    ·
                                  </span>
                                </TooltipTrigger>
                                <TooltipContent side="top">
                                  <div className="whitespace-pre-line">
                                    {tooltipText}
                                  </div>
                                </TooltipContent>
                              </Tooltip>
                            </td>
                          );
                        }

                        return (
                          <td
                            key={col.topic}
                            className="py-2 px-1 text-center"
                          >
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <button
                                  type="button"
                                  onClick={() =>
                                    onQueryFact(row.scheme_id, cell.label)
                                  }
                                  aria-label={tooltipText.replace("\n", " — ")}
                                  className="w-4 h-4 mx-auto inline-flex items-center justify-center rounded-[2px] transition-all duration-120 hover:ring-2 hover:ring-ink focus-visible:outline-none"
                                >
                                  {cell.state === "verified" && (
                                    <span className="w-3 h-3 bg-verified rounded-[1px] block" />
                                  )}
                                  {cell.state === "conditional" && (
                                    <span className="w-3 h-3 bg-conditional rounded-[1px] block" />
                                  )}
                                  {cell.state === "gap" && (
                                    <span className="w-3 h-3 border border-gap rounded-[1px] block bg-transparent" />
                                  )}
                                </button>
                              </TooltipTrigger>
                              <TooltipContent side="top">
                                <div className="whitespace-pre-line">
                                  {tooltipText}
                                </div>
                              </TooltipContent>
                            </Tooltip>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Action-Phrased Arithmetically Correct Column Toggle (Section P2) */}
          {columns.length > 7 && (
            <button
              type="button"
              onClick={() => setShowAllColumns(!showAllColumns)}
              className="mt-2.5 w-full flex items-center justify-center gap-1 font-mono text-[11px] text-ink-3 hover:text-ink py-1.5 border-t border-rule/50 focus-visible:outline-none transition-colors"
            >
              <span>
                {showAllColumns
                  ? "Show fewer ↑"
                  : `Show ${remainingCount} more facts ↓`}
              </span>
            </button>
          )}
        </div>

        {/* Mobile Horizontal Scrolling Strip (<1024px) */}
        <div className="block lg:hidden mt-3">
          <p className="mono-label-sm text-ink-3 mb-2">
            {selectedSchemeId
              ? `Facts for ${schemes.find((s) => s.id === selectedSchemeId)?.name}`
              : "Facts across all schemes"}
          </p>
          <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
            {rows
              .filter((r) => !selectedSchemeId || r.scheme_id === selectedSchemeId)
              .map((row) => (
                <div
                  key={row.scheme_id}
                  className="flex-shrink-0 flex flex-wrap gap-1.5 max-w-[300px]"
                >
                  {row.cells.map((cell) => {
                    if (cell.state === "na") return null;

                    return (
                      <button
                        key={`${row.scheme_id}-${cell.topic}`}
                        type="button"
                        onClick={() => onQueryFact(row.scheme_id, cell.label)}
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-[12px] font-mono rounded-[2px] border transition-colors duration-120 ${
                          cell.state === "verified"
                            ? "bg-verified/10 border-verified/40 text-verified hover:bg-verified/20"
                            : cell.state === "conditional"
                            ? "bg-conditional/10 border-conditional/40 text-conditional hover:bg-conditional/20"
                            : "bg-paper border-gap/50 text-ink-3 hover:border-ink-3"
                        }`}
                      >
                        <span
                          className={`w-2 h-2 rounded-[1px] ${
                            cell.state === "verified"
                              ? "bg-verified"
                              : cell.state === "conditional"
                              ? "bg-conditional"
                              : "border border-gap"
                          }`}
                        />
                        <span>{cell.label}</span>
                      </button>
                    );
                  })}
                </div>
              ))}
          </div>
        </div>

        {/* Legend in 10px mono */}
        <div className="mt-4 pt-3 border-t border-rule font-mono text-[10px] space-y-1.5 text-ink-2">
          <div className="mono-label text-ink-3 text-[10px] font-semibold mb-1">
            Coverage Legend
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 bg-verified rounded-[1px] shrink-0"
                aria-hidden="true"
              />
              <span className="truncate">Verified official</span>
            </div>
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 bg-conditional rounded-[1px] shrink-0"
                aria-hidden="true"
              />
              <span className="truncate">Conditional / cycle</span>
            </div>
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 border border-gap rounded-[1px] shrink-0"
                aria-hidden="true"
              />
              <span className="truncate">Not yet verified</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-ink-3/50 font-bold shrink-0">·</span>
              <span className="truncate">Not applicable</span>
            </div>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
