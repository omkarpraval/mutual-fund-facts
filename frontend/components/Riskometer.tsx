"use client";

import React, { useEffect, useState } from "react";

interface RiskometerProps {
  text: string;
}

interface RiskLevel {
  key: string;
  label: string;
  shortLabel: string;
  angle: number; // Centered angle in degrees on semicircle (0 = leftmost, 180 = rightmost)
  color: string;
}

// Exactly centered in each of the 5 equal 36° bands (0-36 => 18, 36-72 => 54, 72-108 => 90, 108-144 => 126, 144-180 => 162)
const SEBI_LEVELS: RiskLevel[] = [
  { key: "low", label: "Low", shortLabel: "Low", angle: 18, color: "var(--risk-1)" },
  { key: "low to moderate", label: "Low to Moderate", shortLabel: "Low-Mod", angle: 54, color: "var(--risk-2)" },
  { key: "moderate", label: "Moderate", shortLabel: "Moderate", angle: 90, color: "var(--risk-3)" },
  { key: "moderately high", label: "Moderately High", shortLabel: "Mod-High", angle: 126, color: "var(--risk-4)" },
  { key: "high", label: "High", shortLabel: "High", angle: 162, color: "var(--risk-5)" },
  { key: "very high", label: "Very High", shortLabel: "Very High", angle: 162, color: "var(--risk-5)" },
];

const ARC_BANDS = [
  { color: "var(--risk-1)", startAngle: 0, endAngle: 36, label: "Low" },
  { color: "var(--risk-2)", startAngle: 36, endAngle: 72, label: "Low to Mod" },
  { color: "var(--risk-3)", startAngle: 72, endAngle: 108, label: "Moderate" },
  { color: "var(--risk-4)", startAngle: 108, endAngle: 144, label: "Mod-High" },
  { color: "var(--risk-5)", startAngle: 144, endAngle: 180, label: "Very High" },
];

function parseRiskLevel(text: string): RiskLevel | null {
  const lower = text.toLowerCase();
  if (lower.includes("very high")) {
    return SEBI_LEVELS.find((l) => l.key === "very high") || null;
  }
  if (lower.includes("moderately high") || lower.includes("mod-high")) {
    return SEBI_LEVELS.find((l) => l.key === "moderately high") || null;
  }
  if (lower.includes("low to moderate") || lower.includes("low-moderate")) {
    return SEBI_LEVELS.find((l) => l.key === "low to moderate") || null;
  }
  if (lower.includes("moderate")) {
    return SEBI_LEVELS.find((l) => l.key === "moderate") || null;
  }
  if (lower.includes("high")) {
    return SEBI_LEVELS.find((l) => l.key === "high") || null;
  }
  if (lower.includes("low")) {
    return SEBI_LEVELS.find((l) => l.key === "low") || null;
  }
  return null;
}

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = (180 - angleDeg) * (Math.PI / 180);
  return {
    x: cx + r * Math.cos(rad),
    y: cy - r * Math.sin(rad),
  };
}

function describeArc(
  cx: number,
  cy: number,
  rInner: number,
  rOuter: number,
  startAngle: number,
  endAngle: number
) {
  const startOuter = polarToCartesian(cx, cy, rOuter, startAngle);
  const endOuter = polarToCartesian(cx, cy, rOuter, endAngle);
  const startInner = polarToCartesian(cx, cy, rInner, endAngle);
  const endInner = polarToCartesian(cx, cy, rInner, startAngle);

  return [
    `M ${startOuter.x} ${startOuter.y}`,
    `A ${rOuter} ${rOuter} 0 0 1 ${endOuter.x} ${endOuter.y}`,
    `L ${startInner.x} ${startInner.y}`,
    `A ${rInner} ${rInner} 0 0 0 ${endInner.x} ${endInner.y}`,
    "Z",
  ].join(" ");
}

export function Riskometer({ text }: RiskometerProps) {
  const matchedLevel = parseRiskLevel(text);
  const [needleAngle, setNeedleAngle] = useState(0);

  useEffect(() => {
    if (matchedLevel) {
      const timer = setTimeout(() => {
        setNeedleAngle(matchedLevel.angle);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [matchedLevel]);

  if (!matchedLevel) {
    return null;
  }

  const cx = 140;
  const cy = 130;
  const rOuter = 110;
  const rInner = 82;
  const rotationDeg = needleAngle - 90;

  return (
    <div
      className="my-4 p-4 border border-rule bg-paper/50 rounded-[3px] flex flex-col items-center"
      role="figure"
      aria-label={`SEBI Riskometer gauge indicating ${matchedLevel.label} risk`}
    >
      {/* Risk Level prominently raised ABOVE the gauge (Section P2) */}
      <div className="w-full text-center pb-2 mb-2 border-b border-rule">
        <div className="mono-label text-ink-3 font-mono text-[10px] mb-0.5">
          SEBI Statutory Riskometer
        </div>
        <div
          className="font-mono text-[14px] font-semibold uppercase tracking-wider"
          style={{ color: matchedLevel.color }}
        >
          Level: {matchedLevel.label}
        </div>
      </div>

      <div className="relative w-[280px] h-[155px] overflow-hidden flex justify-center">
        <svg viewBox="0 0 280 145" className="w-full h-full" aria-hidden="true">
          {/* Five Semicircular Bands */}
          {ARC_BANDS.map((band, idx) => (
            <path
              key={idx}
              d={describeArc(
                cx,
                cy,
                rInner,
                rOuter,
                band.startAngle + 0.8,
                band.endAngle - 0.8
              )}
              fill={band.color}
              className="opacity-95"
            />
          ))}

          {/* Inner Rail */}
          <path
            d={`M ${cx - rInner + 4} ${cy} A ${rInner - 4} ${rInner - 4} 0 0 1 ${
              cx + rInner - 4
            } ${cy}`}
            fill="none"
            stroke="var(--rule)"
            strokeWidth="1"
          />

          {/* Needle Base Hub */}
          <circle cx={cx} cy={cy} r="8" fill="var(--ink)" />
          <circle cx={cx} cy={cy} r="3" fill="#FFFFFF" />

          {/* Centred Animated Needle (Section P2) */}
          <g
            style={{
              transformOrigin: `${cx}px ${cy}px`,
              transform: `rotate(${rotationDeg}deg)`,
              transition: "transform 500ms cubic-bezier(0.22, 1, 0.36, 1)",
            }}
          >
            <polygon
              points={`${cx - 3},${cy} ${cx},${cy - rOuter + 8} ${cx + 3},${cy}`}
              fill="var(--ink)"
            />
          </g>
        </svg>
      </div>

      {/* Band Labels */}
      <div className="w-full grid grid-cols-5 text-center mt-1 pt-2 border-t border-rule font-mono text-[10px] uppercase text-ink-3">
        <div className="text-left text-risk-1 font-medium">Low</div>
        <div>Low-Mod</div>
        <div>Moderate</div>
        <div>Mod-High</div>
        <div className="text-right text-risk-5 font-medium">Very High</div>
      </div>
    </div>
  );
}
