# 03. Scope: AMC and Scheme Selection

**Project:** Mutual Fund Facts Assistant
**Phase:** Workstream 2 (Data and Knowledge)
**Status:** Recommendation, pending confirmation
**Date:** 26 August 2026

---

## 1. The decision that had to be made first

Groww runs its own AMC. Groww Mutual Fund exists, with a full scheme lineup including Groww Large Cap Fund, Groww ELSS Tax Saver Fund, Groww Multicap Fund, Groww Value Fund and others.

That is worth stopping on, because it offers a genuinely tempting shortcut: pick Groww Mutual Fund as the AMC and the entire project collapses into one organisation. Product context and corpus become the same brand. The narrative gets very tidy.

**We are not doing that, and the reasons are worth recording.**

**Reason 1, the mandated mix breaks.** The brief asks for a spread such as one large cap, one flexi cap, one ELSS. Groww Mutual Fund's equity lineup has a large cap and an ELSS but no flexi cap. The nearest substitutes are a multicap and a value fund, which are different SEBI categories with different mandates. We would be quietly swapping the required mix for an available one.

**Reason 2, and this is the real one: it would destroy what the architecture demonstrates.** The whole point of the three-tier source model is that a single user question can span three organisations that each own a different piece of the answer. If the AMC and the platform are the same company, that architecture still runs but it never gets exercised. The source hierarchy becomes decorative. An evaluator reading the design would reasonably ask why we built tiers at all.

**Reason 3, documentation depth.** Groww Mutual Fund is a comparatively recent AMC. Established fund houses have longer document histories, more addenda, and more mature disclosure pages. For a project whose difficulty lives in document extraction, that matters.

So: **the AMC is deliberately not Groww.** The separation between product and corpus that we set up in D001 is not an accident of the brief, it is the thing the project is built to show, and choosing Groww Mutual Fund would have thrown it away in exchange for a neater logo story.

---

## 2. AMC selection

### Criteria and weights

Documentation quality only. Fund performance, popularity and AUM are irrelevant here and were not considered, since we make no performance claims anywhere in this product.

| Criterion | Weight | What it measures |
|---|---|---|
| Dedicated TER disclosure page | 25% | Can we cite the dynamic fact properly, or only a PDF |
| Dedicated SID and KIM download page | 25% | Can we get statutory documents without hunting |
| Category coverage for the required mix | 20% | Large cap, flexi cap, ELSS all present |
| Scheme page quality | 15% | Are facts on the page or only in PDFs |
| Factsheet availability | 10% | Monthly factsheet published and reachable |
| Naming stability and alias clarity | 5% | Does the AMC document its own renames |

### Scoring

| AMC | TER page | SID/KIM page | Category mix | Scheme pages | Factsheet | Naming | Verdict |
|---|---|---|---|---|---|---|---|
| **SBI Mutual Fund** | Verified, dedicated page with current and historical TER | Verified, dedicated page in current SEBI format | All three present | Verified, structured per scheme | Expected, to confirm | Documents former names on its own pages | **Selected** |
| Groww Mutual Fund | Not assessed | Not assessed | No flexi cap | Not assessed | Not assessed | Not assessed | Rejected, see section 1 |
| HDFC, ICICI Prudential, Nippon India, Kotak | Not individually verified | Not individually verified | All believed to have the mix | Not verified | Not verified | Not verified | Viable alternates, not assessed in depth |

### Why SBI Mutual Fund

Two things were verified directly rather than assumed, and both are load-bearing.

**A dedicated TER page exists.** SBI Mutual Fund publishes a page for (cite index="41-1">the latest TER across all schemes, with both current year and historical TER available to download</cite>. This matters more than it sounds. TER is our hardest fact because it is dynamic, and an AMC that publishes it on a purpose-built page gives us a citation that points at the fact itself rather than at a homepage or a hundred-page PDF. That is the difference between satisfying the citation requirement and satisfying its intent.

**A dedicated SID and KIM page exists**, and it is (cite index="42-1">maintained in the current SID and KIM format required under the SEBI circular of November 2023</cite>. Current format matters because our extraction logic keys off document structure, and a page maintained to the current standard is less likely to hand us a mix of old and new layouts.

The honest caveat: the other large AMCs very likely have comparable pages. SBI is selected because its pages were verified to exist, not because the alternatives were checked and found worse. That is the correct standard on a six-day timeline, and it is stated as such rather than dressed up as a comprehensive market scan.

---

## 3. Scheme selection

Three schemes, per D013.

| # | Scheme | Category | Why it is here |
|---|---|---|---|
| 1 | SBI Large Cap Fund (formerly SBI Bluechip Fund) | Large Cap | Verified on the AMC's own scheme page. Carries a documented former name, which makes it our test case for alias resolution |
| 2 | SBI Flexicap Fund | Flexi Cap | Required for category diversity. Name and current KIM to be confirmed at collection |
| 3 | SBI Long Term Equity Fund | ELSS | Mandatory. Lock-in is a required FAQ category and only an ELSS demonstrates it. Name to be confirmed, see below |

### Why these three and not others

**Category diversity is the point, not fund quality.** Each scheme is here to make a different retrieval case work:

- The **large cap** is the baseline. Standard facts, standard documents, and an alias problem built in.
- The **flexi cap** tests scheme disambiguation. Two SBI equity funds with overlapping vocabulary is exactly the case where retrieval pulls from the wrong fund, and having both in the corpus means our evaluation actually tests R3 rather than assuming it away.
- The **ELSS** unlocks an entire FAQ category. Lock-in is regulatory rather than scheme-specific, so it also exercises the Tier 1 to Tier 2 handoff: the scheme document states the lock-in, and SEBI or AMFI material explains it.

**Three, not five.** Five schemes would add roughly ten more documents and eight more ground truth rows without demonstrating a single new retrieval case. On a six-day build, breadth here buys nothing that depth does not buy more of.

### Names still to confirm

Two of the three scheme names are not yet verified against the AMC's own scheme list. The ELSS in particular appears as SBI Long Term Equity Fund in AMC material and as an ELSS Tax Saver Fund in at least one third-party listing. Given section 5 of the source research document, third-party naming is not evidence. Both names get confirmed from the AMC directly at collection, and whatever is found goes into the alias list rather than replacing what is written here.

---

## 4. Supported topics

Derived from the FAQ taxonomy, restricted to what the corpus can actually source.

| Category | Questions in scope | Tier | fact_type |
|---|---|---|---|
| A. Scheme basics | What is the scheme, investment objective, SEBI category | 1 | static |
| B. Investment details | Minimum SIP, minimum lumpsum, additional purchase, SIP frequency | 1 | static |
| C. Charges | Expense ratio, exit load | 1 | TER dynamic_daily, exit load static |
| D. Risk | Riskometer level, risk classification | 1, 2 | dynamic_monthly |
| E. Benchmark | Benchmark index, additional benchmark | 1 | static |
| F. ELSS | Lock-in period, ELSS factual information | 1, 2 | static |
| G. Documents and statements | Capital gains statement download, reports access | 3 | static |
| H. Regulatory context | TER limits, riskometer methodology, what lock-in means | 2 | static |

## 5. Out of scope

Beyond the non-goals already in the discovery document, these are specifically out of corpus scope:

- Any scheme outside the three selected, including other SBI schemes
- Any AMC other than SBI Mutual Fund
- NAV, AUM, returns, portfolio holdings, fund manager details
- Historical values of any fact, including past TER and past riskometer
- Platform processes other than statements and reports
- Anything requiring a user's own account data

The second one is worth a note. A user asking about SBI Small Cap Fund gets a no-evidence response, not an answer, even though it is the same AMC and the document probably exists. Scope is scope. The coverage map in the README makes this visible so it reads as a boundary rather than a bug.

---

## 6. Plan handling, carried forward from the open question

Groww distributes Direct plans, and our AMC publishes both Direct and Regular. Same scheme, different expense ratio.

**Proposed rule:** default to Direct, and name the plan explicitly in every answer where the source distinguishes it. "The TER for the Direct plan is X% as of DD MMM YYYY." No silent defaults, no plan toggle.

The toggle was rejected because it is a second control most users will not touch, and a wrong-plan answer produced by an untouched default is indistinguishable from a wrong answer. Naming the plan in the answer text means a user on the wrong plan can see it immediately, which is the same principle as showing the citation.

This is recorded as D016 and is open to override.

---

## 7. Acceptance check

| Criterion | Status |
|---|---|
| One AMC selected | Met, SBI Mutual Fund |
| 3 to 5 schemes selected | Met, three |
| Selection justified | Met, sections 2 and 3 |
| Corpus small enough to maintain manually | Met, roughly 15 documents |
| Corpus rich enough to demonstrate RAG | Met, three retrieval cases plus three source tiers |
| Supported topics documented | Met |
| Out-of-scope topics documented | Met |
| Scheme names verified | Partial, one of three confirmed, two pending collection |
