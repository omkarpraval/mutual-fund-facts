import "./globals.css";
import { Instrument_Serif, Public_Sans, IBM_Plex_Mono } from "next/font/google";
import type { Metadata } from "next";

const instrumentSerif = Instrument_Serif({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-instrument",
  display: "swap",
});

const publicSans = Public_Sans({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-public-sans",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Mutual Fund Facts — Verified Information from Official Sources",
  description: "Factual answers about selected mutual fund schemes from official AMC, AMFI, and SEBI sources. Facts only, no investment advice.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${instrumentSerif.variable} ${publicSans.variable} ${ibmPlexMono.variable}`}
    >
      <body className="min-h-screen bg-paper text-ink font-body antialiased selection:bg-verified selection:text-white">
        {children}
      </body>
    </html>
  );
}
