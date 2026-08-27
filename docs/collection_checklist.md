# Corpus Collection Checklist

**Status:** Manual collection required. Read section 1 before starting.
**Date:** 26 August 2026

---

## 1. Why this is a manual job, and it is not optional

Two things were tested directly today and both came back negative for automated collection.

**The PDFs are robots-disallowed.** Fetching a KIM directly from `sbimf.com/docs/...` returns a robots refusal. This applies to the whole `/docs/` path, which is where every KIM, SID, SAI and factsheet lives. That is the entire statutory document corpus.

**The HTML scheme pages are client-side rendered.** The ELSS scheme page fetches fine and returns almost nothing useful. Sitefinity serves the navigation, the footer, the contact block and a loading spinner. NAV, minimums, exit load, benchmark and riskometer all load client-side after render, so an automated fetch returns boilerplate rather than facts.

**Consequence.** Every document in Tier 1 has to be downloaded by a person in a browser. This is not a workaround for the robots rule, it is the correct reading of it: the rule governs automated agents, and a human opening a public document that the AMC publishes for investors is the intended use of that document.

This validates D020 for a much stronger reason than the one originally given. The original argument was that fifteen documents does not justify a crawler. The real argument is that a crawler would not work at all here, and had we discovered that on Day 5 with an ingestion pipeline already written against an assumed scrape, it would have cost the build.

**Add to README limitations:** the corpus is a point-in-time manual snapshot, refreshable only by repeating this checklist.

---

## 2. Download list

Save everything into `corpus/raw/` using the filename in the last column. Record the download date in `sources.csv` as you go.

### Tier 1, statutory documents (all require manual download)

| # | Document | Where to get it | Save as |
|---|---|---|---|
| 1 | KIM, SBI Large Cap Fund | `sbimf.com/offer-document-sid-kim` | `kim_large_cap.pdf` |
| 2 | KIM, SBI Flexicap Fund | direct link in `sources.csv` SRC-011 | `kim_flexicap.pdf` |
| 3 | KIM, SBI ELSS Tax Saver Fund | `sbimf.com/offer-document-sid-kim` | `kim_elss.pdf` |
| 4 | SID, SBI ELSS Tax Saver Fund | direct link in `sources.csv` SRC-014 | `sid_elss.pdf` |
| 5 | Latest monthly factsheet | `sbimf.com/factsheets` | `factsheet_YYYYMM.pdf` |

### Tier 1, live pages (screenshot the value plus the page date, do not scrape)

| # | Page | What to record | Notes |
|---|---|---|---|
| 6 | `sbimf.com/total-expense-ratio` | TER for all three schemes, Direct and Regular, plus the as-of date shown | This is the dynamic_daily fact. The as-of date matters as much as the number |
| 7 | Scheme page, each of the three | Investment objective, SEBI category, minimums | Values are client-side, so read them off the rendered page |
| 8 | `sbimf.com/notice-and-addendums` | Any addendum affecting our three schemes, especially load changes | Directly feeds the conflict policy in D021 |

### Tier 2, regulatory (already verified, no action)

Items 9 to 11 are SRC-004, SRC-005 and SRC-006 in `sources.csv`, all fetched and confirmed.

| # | Still needed | Where |
|---|---|---|
| 12 | AMFI material on ELSS lock-in at category level | amfiindia.com or mutualfundssahihai.com |

### Tier 3, platform

| # | Still needed | Where |
|---|---|---|
| 13 | Groww help article on mutual fund capital gains statement | `groww.in/help`, Mutual Funds category |
| 14 | Groww help article on mutual fund reports or statements | same |

**Reminder on Tier 3:** take these from `groww.in/help/...` only. A `groww.in/blog/...` result answering the same question is excluded under D002, and the blog ranks higher in search than the help centre for exactly this query.

---

## 3. Extraction targets

For each downloaded document, fill the matching rows in `ground_truth.csv`. Twenty-eight rows are currently PENDING.

Per scheme, extract: minimum SIP, minimum lumpsum, additional purchase amount, exit load, benchmark, riskometer, investment objective, SEBI category. Plus lock-in for the ELSS.

**Record for every value:** the document it came from, the page or section, and the document's own date. A value without its as-of date cannot be used for a dynamic fact and is weak evidence for a static one.

---

## 4. Extraction quality gate, per D005 and risk R7

Before any document is chunked, open the extracted text and confirm:

- [ ] Numbers still sit next to the labels they belong to
- [ ] Table rows have not been flattened into a single run of digits
- [ ] The minimums table survived, since this is the most commonly broken structure in a KIM
- [ ] Rupee symbols and percentages are intact rather than mangled to unicode noise
- [ ] Section headings survived, since scheme resolution keys off them

If a table breaks, extract that section by hand into a small structured file rather than fixing the parser. One table transcribed manually costs ten minutes. A parser tuned to one PDF layout costs half a day and breaks on the next document.

---

## 5. What good looks like at the end of this

- 15 or more documents in `corpus/raw/` with matching `sources.csv` rows, all dated
- 28 PENDING rows in `ground_truth.csv` filled with primary values
- Zero values sourced from anything outside Tier 1, 2 or 3
- Extraction quality gate passed per document

Only then does ingestion start.
