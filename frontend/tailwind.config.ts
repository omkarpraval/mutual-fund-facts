import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "var(--ink)",
          2: "var(--ink-2)",
          3: "var(--ink-3)",
        },
        paper: "var(--paper)",
        card: "var(--card)",
        rule: "var(--rule)",
        verified: "var(--verified)",
        conditional: "var(--conditional)",
        gap: "var(--gap)",
        halt: "var(--halt)",
        risk: {
          1: "var(--risk-1)",
          2: "var(--risk-2)",
          3: "var(--risk-3)",
          4: "var(--risk-4)",
          5: "var(--risk-5)",
        },
      },
      fontFamily: {
        display: ["var(--font-instrument)", "Instrument Serif", "Georgia", "serif"],
        body: ["var(--font-public-sans)", "Public Sans", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "IBM Plex Mono", "Menlo", "monospace"],
      },
      boxShadow: {
        answer: "0 1px 2px rgba(16, 24, 32, 0.06)",
      },
      borderRadius: {
        DEFAULT: "3px",
        sm: "2px",
        md: "3px",
        lg: "3px",
      },
    },
  },
  plugins: [],
};

export default config;
