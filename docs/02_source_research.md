# 02. Source Research and Sourcing Policy

**Project:** Mutual Fund Facts Assistant
**Phase:** Workstream 2 (Data and Knowledge)
**Status:** Research complete, collection in progress
**Date:** 26 August 2026

---

## 1. What this phase set out to settle

Four things, in order, because each one gates the next:

1. Whether Groww's help documentation is publicly readable, which decides if Tier 3 exists at all (assumption A4).
2. Whether the TER and riskometer disclosure cadences are what the plan assumed, which decides whether the static and dynamic fact model is calibrated correctly (assumption A5).
3. Which AMC to use, based on documentation quality rather than brand.
4. What the sourcing rules are when documents disagree or go stale.

All four are now answered. One answer changed a design assumption, and it is covered in section 5.

---

## 2. Verified findings

### 2.1 Groww help documentation is public (A4 resolved: yes)

`groww.in/help` loads without authentication, is indexed for search, and is organised into categories including a Mutual Funds section. Individual help articles sit at stable structured URLs under `/help/<category>/<type>/<article-slug>`.

**Consequence:** Tier 3 survives. Platform process questions, notably the capital gains statement question that the brief specifically calls out, have a legitimate first-party source.

**Important distinction, and it is not a technicality.** Searching for the capital gains statement process returns Groww's blog at `groww.in/blog/...` far more prominently than the help centre. The blog is editorial content and is excluded under decision D002. The help centre is operational documentation and is included. Same domain, different classes of artifact, opposite treatment. During collection, every Groww URL gets checked against this rule individually rather than by domain.

### 2.2 TER is disclosed daily (A5, first half: confirmed)

AMFI's own investor knowledge material states that under current SEBI regulations, <cite index="44-4">funds must publish the TER for every scheme daily, both on their own websites and on AMFI's</cite>. AMFI also notes that <cite index="44-1">the regulatory ceilings on TER sit under Regulation 52 of the SEBI Mutual Fund Regulations</cite>.

**Consequence:** TER is confirmed as a dynamic fact. Answering it from a corpus snapshot without an as-of date would produce confidently stale numbers. D004 stands as written.

### 2.3 Riskometer is evaluated monthly (A5, second half: confirmed)

AMFI's investor education material confirms that <cite index="34-1">a scheme's riskometer is reassessed every month, with the updated riskometer and portfolio published on the AMC site and the AMFI site within ten days of month end</cite>. AMFI also documents how the score is built, noting for equity that <cite index="34-4">each holding gets a risk score from market capitalisation, volatility and impact cost</cite>, and that <cite index="34-5">the market capitalisation risk values themselves refresh twice a year</cite>.

**Consequence:** Riskometer confirmed as dynamic, on a monthly cycle rather than TER's daily one. This gives us two different staleness windows rather than one, which the data model needs to hold separately.

### 2.4 Both cadences are now sourced, not assumed

Assumption A5 in the discovery document flagged that these cadences had entered the plan as stated background rather than checked facts. They are now checked, they hold, and both source URLs go into `sources.csv` as Tier 2 entries. The fact classification model needs no correction.

---

## 3. Source tiers and ownership

| Tier | Organisation | Owns | Document types |
|---|---|---|---|
| 1 | Selected AMC | Scheme-level facts | Scheme page, KIM, SID sections, factsheet, TER disclosure page |
| 2 | SEBI and AMFI | Regulatory and category facts | Master circular, TER regulation, riskometer methodology, investor education |
| 3 | Groww Help Centre | Platform processes | Help articles on reports, statements, capital gains documents |

### Priority order when more than one tier could answer

1. Latest applicable official AMC document for the specific scheme
2. Official AMC scheme page
3. AMC's dedicated disclosure page for that fact type, for example the TER page
4. AMFI
5. SEBI
6. Groww Help Centre, but only for platform processes, never for scheme facts

Tier 3 is last in priority and first in relevance for its own narrow domain. It does not compete with Tier 1, because the two never answer the same question.

### Explicitly excluded as answer sources

Aggregators and rating sites, financial news, brokerage blogs including Groww's own, forums, YouTube, tax filing services, and any site whose numbers we cannot trace to a filing. Section 4 explains why this is not merely a rule we are following.

---

## 4. Why the third-party exclusion is a real safeguard

While confirming scheme names, the same fact appeared with different values across reputable third-party sites. For one SBI equity scheme, one widely used research site listed the <cite index="51-2">minimum lumpsum as ₹1,000 and minimum SIP as ₹500</cite> while stating elsewhere on the same page that <cite index="51-1">the minimum lumpsum is ₹5,000</cite>. Another site reported the <cite index="52-2">minimum SIP as ₹1,000 with a ₹5,000 lumpsum</cite>. A third gave <cite index="54-1">₹500 SIP and ₹5,000 lumpsum</cite>.

Three sources, three different pictures of the same two numbers, all of them well known and none of them obviously wrong on the face of it.

This is exactly the failure our product exists to prevent, and it is worth stating plainly in the README: none of these numbers enter our ground truth table. Every minimum in our corpus comes from the AMC's own KIM or scheme page, and is recorded with the document it came from and the date we read it. The divergence above is evidence, not data.

It also sharpens the value proposition from section 5 of the discovery document. The problem is not that facts are unavailable. It is that the fast sources disagree and the user cannot tell which one is right.

---

## 5. What changed: scheme names are not stable

SBI's large cap scheme is now **SBI Large Cap Fund**, and the AMC's own scheme page carries the parenthetical <cite index="55-1">"(Formerly known as SBI Bluechip Fund)"</cite>. Third-party sites are inconsistent about this: several still use the old name in URLs and page titles while displaying the new one.

**This is a retrieval problem, not a trivia problem.** A user who has held the fund for years will type "SBI Bluechip." Our corpus will mostly say "SBI Large Cap Fund." Pure semantic similarity may or may not bridge that, and we cannot afford may or may not on scheme identity, because a scheme mismatch is failure mode R3.

**Design consequence, added to the plan:** every scheme in the corpus carries an explicit alias list in its metadata, covering former names, common short forms and plan variants. Scheme resolution checks aliases before falling back to embedding similarity. This is cheap to build and closes a gap that would otherwise show up as unexplained retrieval misses during evaluation.

A second instance needs checking during collection: SBI's ELSS appears in AMC material as SBI Long Term Equity Fund, while at least one third-party listing refers to an SBI ELSS Tax Saver Fund. We do not treat that as resolved. The AMC's own scheme list settles it, and the alias list records whatever we find.

---

## 6. Freshness policy

Every source carries this metadata:

```
document_id, title, url, source_organization, tier, scheme,
document_type, publication_date, last_updated_date, date_collected,
topic, fact_type, priority, access_status
```

`fact_type` is the field that does the work. It takes one of three values:

| fact_type | Refresh cycle | Answer treatment |
|---|---|---|
| `static` | Changes only by addendum | Answer normally with source |
| `dynamic_daily` | TER | Value, as-of date, source, plus a line noting daily disclosure |
| `dynamic_monthly` | Riskometer | Value, as-of month, source |

### Staleness thresholds

| fact_type | Considered stale after | Behaviour when stale |
|---|---|---|
| `dynamic_daily` | 7 days from collection | Give the stored value, flag it as possibly not current, direct to the live disclosure page |
| `dynamic_monthly` | 45 days from collection | Same pattern, monthly wording |
| `static` | No automatic threshold | Refreshed only if an addendum is found |

The daily threshold is set at seven days rather than one deliberately. A one-day threshold would put every TER answer permanently in the stale branch for a project built over a week, which would be technically correct and completely useless as a demonstration. Seven days is honest about the tradeoff: it acknowledges the value may have moved while still showing the normal answer path. This is written into the README limitations rather than hidden.

---

## 7. Conflict policy

When two official sources disagree:

1. **Different tiers.** Higher tier wins for its own domain. A scheme fact from the AMC beats a general statement from AMFI. A regulatory limit from SEBI beats an AMC's summary of it.
2. **Same tier, different dates.** Latest applicable document wins. Applicable matters: a KIM superseded by an addendum loses to the addendum even though the KIM is a bigger document.
3. **Same tier, same date, genuine disagreement.** Do not pick a winner. Return the answer from the primary document, state that sources differ, and cite both. A silent choice here is exactly the behaviour this product is supposed to not have.
4. **Third party disagrees with an official source.** Not a conflict. The third party is not a source.

Case 3 is rare and may not appear in our corpus at all. It is specified anyway, because discovering the policy gap mid-evaluation is worse than writing three sentences now.

---

## 8. Collection method

Manual download, not crawling. Fifteen to twenty documents does not justify a crawler, and a crawler introduces robots and rate-limit questions that add risk without adding anything the project is assessed on.

Each document is saved locally alongside its metadata row at collection time, so that a page moving or changing before submission does not invalidate the corpus (risk R12). The archived copy is what we index. The live URL is what we cite.

---

## 9. Acceptance check

| Criterion | Status |
|---|---|
| Sources are public | Met, A4 verified directly |
| Sources are authoritative | Met, three tiers with documented ownership |
| No third-party blogs as answer sources | Met, with the Groww blog and help centre distinction written down |
| Every source has metadata | Met, schema defined in section 6 |
| Source conflict policy documented | Met, section 7 |
| Freshness strategy documented | Met, section 6 |
| 15 to 25 sources collected | In progress, 9 verified, remainder pending scheme lock |

---

## 10. Open items carried into collection

1. Confirm SBI's ELSS scheme name from the AMC's own scheme list, and record aliases.
2. Confirm the flexi cap scheme name and that a current KIM is downloadable.
3. Build the alias list for all three schemes, including plan variants.
4. Inspect PDF extraction quality per document before embedding, per D005 and risk R7.
