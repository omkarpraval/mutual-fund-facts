# 01. Product Discovery and Problem Definition

**Project:** Mutual Fund Facts Assistant (facts-only FAQ)
**Product context:** Groww
**Milestone:** PM Milestone 4
**Phase:** 1 of 5 workstreams (Product and Research)
**Status:** Draft for review
**Author:** Omkar Raval
**Date:** August 2026

---

## A note on evidence before we begin

This milestone runs on a short timeline and does not include primary user research. Nothing in this document is presented as a validated finding. Where a claim is directional rather than proven, it is written as an assumption and listed in Section 8 with a note on how it would be tested. No survey numbers, ticket volumes, user counts or market sizes appear anywhere in this document, because we have not measured them and inventing them would undermine the whole point of a facts-only product.

That constraint is deliberate. A product whose central promise is "we do not make things up" should not be introduced by a document that does.

---

## 1. Problem statement

### Who has the problem

Retail mutual fund investors who already hold or are considering schemes through a distribution platform, in our case Groww. Secondarily, the support and content teams inside that platform who answer the same factual questions over and over.

### What problem they face

When a retail investor needs a specific factual detail about a scheme, the minimum SIP amount, the exit load, the current expense ratio, the benchmark, the riskometer category, whether an ELSS has a lock-in, or how to pull a capital gains statement, that detail exists and is public. It is just scattered.

The minimum SIP might sit in the KIM. The exit load might be in the scheme page and restated in the SID. The expense ratio lives on a daily disclosure page. The riskometer is republished on a monthly cycle. The lock-in is a regulatory fact rather than a scheme-specific one. The statement download process belongs to the platform, not to the fund house at all.

So a single user question can span three different organisations and four document types. The user does not know that, and should not have to.

### Why it matters

Two reasons, and they pull in different directions.

The first is friction. Finding one number can take several minutes of scrolling through a long PDF, and the user often gives up before finding it.

The second is worse, and it is the reason this product has to be built carefully. When official sources are hard to search, users route around them. They ask a search engine, a forum, a finance influencer, or a general purpose chatbot. Those answers arrive faster and they are frequently outdated, sometimes about a different plan of the same scheme, and occasionally just wrong. The user has no way to tell. In a domain where the number in question affects real money, a confident wrong answer is materially worse than no answer.

### How it is currently solved

Roughly four ways, in descending order of reliability and ascending order of convenience:

1. Read the official document directly. Accurate, slow, and requires knowing which document to open.
2. Use the platform's help centre or search. Good for platform processes, thinner on scheme-level specifics.
3. Contact support. Reliable but slow, and expensive on the platform's side for questions that are already answered in public documents.
4. Ask a search engine, an aggregator site, a forum, or a general chatbot. Fast, unsourced, frequently stale.

The convenience gradient runs exactly opposite to the accuracy gradient. That inversion is the actual problem.

### Why the current experience is inefficient

- The user has to know which document type holds which fact before they can start looking.
- Official documents are written for regulatory completeness, not for lookup.
- Direct and Regular plans carry different expense ratios, and the distinction is easy to miss.
- Some facts are dynamic. A number that was correct last month may not be correct today, and static content rarely says when it was last true.
- Nothing in the fast options tells the user where the answer came from, so verification is impossible.

### The opportunity

Not "build an AI chatbot." The opportunity is narrower and more defensible:

> **Reduce the effort required to find and verify a factual mutual fund detail, without becoming another unsourced opinion.**

The distinguishing feature is not the answer. Plenty of things will give you an answer. It is the answer arriving with its source attached, its as-of date visible, and a clear refusal when the source does not support a reply.

---

## 2. Target user

### Primary persona: the verifier

**Who:** A retail investor with an existing Groww account, holding or evaluating a small number of schemes.

**Context:** Usually on mobile. Usually mid-task, comparing two schemes, setting up a SIP, filing taxes, or reacting to something they read. The question is specific and they want it closed quickly.

**Goals**

- Get one specific fact, correctly, in under a minute.
- Confirm a number they think they already know.
- Understand a scheme's stated terms before committing money.
- Complete a process task such as downloading a statement for tax filing.

**Pain points**

- Does not know which document holds which fact.
- Finds official PDFs long and hostile to skimming.
- Encounters unfamiliar terminology such as TER, riskometer, benchmark, exit load.
- Cannot tell whether a number found online is current.
- Cannot tell whether an answer applies to Direct or Regular plan.

**Behaviour**

- Asks short, telegraphic questions rather than full sentences.
- Often omits the scheme name, assuming context.
- Abandons the search if the first two attempts fail.
- Will sometimes ask an advice question while framing it as a factual one.

**Information needs**

Scheme basics, investment minimums, charges, risk classification, benchmark, lock-in where applicable, and platform document processes.

**Trust concerns**

This is the part that matters most for design.

- "Is this number current?"
- "Where did this come from?"
- "Is this AI making it up?"
- "Is it quietly trying to sell me something?"

Every one of those maps to a UI decision later: the source link, the as-of date, the no-evidence response, and the refusal.

### Secondary persona: the support and content team

Internal users at the platform who field repetitive factual questions. Their goal is deflection of already-public information so human time goes to genuinely account-specific issues. They are not the MVP's design target, but they are the reason a business would fund this, and they matter for the metrics story in the PRD.

---

## 3. Jobs to be done

**JTBD 1**
When I need a specific fact about a scheme I am considering or already hold, I want to get that fact quickly from an official source, so that I do not have to search through several long documents.

**JTBD 2**
When I receive an answer about my money, I want to see exactly where it came from, so that I can verify it myself and decide whether to trust it.

**JTBD 3**
When the assistant does not actually know something, I want it to tell me plainly, so that I do not act on a guess that looks like a fact.

**JTBD 4**
When I ask something the assistant should not answer, such as whether to buy a fund, I want to be told clearly and pointed toward information I can use to decide for myself, so that I do not feel dismissed.

**JTBD 5**
When I need to complete a document task such as downloading a capital gains statement, I want the current official process, so that I can finish my tax filing.

Note that JTBD 3 and 4 are jobs about the system's limits. Most chatbot projects treat those as constraints. For this product they are features, and the quality of how we deliver them is a large part of what is actually being assessed.

---

## 4. Pain points

Ranked by how much they influence what we build.

| # | Pain point | Consequence | Addressed in MVP |
|---|---|---|---|
| P1 | Facts scattered across scheme pages, KIM, SID, factsheets and regulatory sites | User does not know where to look | Yes, unified retrieval over one curated corpus |
| P2 | No way to verify an answer found online | User cannot distinguish reliable from unreliable | Yes, one citation on every factual answer |
| P3 | Some facts change on a regular cycle, notably TER and riskometer | Stale numbers presented as current | Yes, static and dynamic fact classification with as-of dates |
| P4 | Official PDFs are long and not built for lookup | Search is slow, users give up | Yes, chunked retrieval over targeted sections |
| P5 | Ambiguity between Direct and Regular plans | Wrong number retrieved for the user's actual holding | Partly, plan stated explicitly in the answer where the source distinguishes it |
| P6 | Ambiguity about which scheme is being asked about | Retrieval pulls from the wrong fund | Yes, persistent scheme selector plus in-query override |
| P7 | Unfamiliar terminology | User cannot phrase the question | Partly, query normalisation over common synonyms |
| P8 | Fear that an AI answer is fabricated | User does not trust the tool at all | Yes, explicit no-evidence response and visible sourcing |
| P9 | Repetitive public questions consuming support time | Cost to the platform | Indirectly, this is the business case rather than an MVP feature |

---

## 5. Opportunity and positioning

### What we are building

A facts-only mutual fund assistant, positioned inside a large retail investing platform, that answers a bounded set of factual questions about a small set of schemes using only official sources, and that cites every answer.

### What makes it different from the alternatives

| Alternative | Fast | Accurate | Sourced | Current |
|---|---|---|---|---|
| Reading the official document | No | Yes | Yes | Yes |
| Platform help search | Partly | Yes for platform topics | Partly | Yes |
| Contacting support | No | Yes | No | Yes |
| Search engine or aggregator | Yes | Sometimes | No | Often not |
| General purpose chatbot | Yes | Unreliable | Rarely | Often not |
| **This assistant** | **Yes** | **Yes within scope** | **Always** | **Stated explicitly** |

The empty cell everyone else has is the sourced column. That is the wedge.

### Where we deliberately do not compete

We are not trying to be comprehensive. A product that covers every scheme in the Indian mutual fund industry and gets nine out of ten answers right is less useful here than one that covers three schemes and gets ten out of ten right with a link. Coverage is a later problem. Trust is the first one, and trust does not survive being right most of the time.

---

## 6. Product hypothesis

> **If** we give retail investors a single conversational surface that answers a bounded set of factual mutual fund questions from official sources, always shows one relevant citation and an as-of date, and clearly refuses advice and unsupported questions rather than guessing,
> **then** users will resolve factual scheme questions faster than by searching official documents themselves, and will trust the answers enough to act on them,
> **because** the friction they currently face is locating and verifying facts rather than the facts being unavailable.

### What would falsify it

- Users ignore the citation entirely, which would suggest verification is not actually a felt need.
- Users abandon after a refusal instead of rephrasing, which would suggest the refusal reads as failure rather than as a boundary.
- Users mostly ask questions outside our corpus, which would mean we scoped the FAQ taxonomy against the wrong set of needs.
- Users get answers but still open the source document to check, which would mean we bought them nothing.

### How we would know it worked

Not measurable on a student MVP without real users, so these are stated as the instrumentation the PRD will define rather than as results:

- Share of factual questions answered with a valid citation.
- Share of advice questions correctly refused.
- Share of out-of-corpus questions correctly declined instead of answered.
- Citation click rate, as a proxy for whether sourcing is doing any work.
- Rephrase rate after a refusal, as a proxy for whether refusals are usable.

---

## 7. Scope hypothesis

Not final. Locked in Workstream 2. Recorded here so the assumptions below have something concrete to attach to.

**Product context:** Groww, as the surface and the PM framing.

**Corpus:** One AMC, three schemes, chosen for documentation quality rather than brand size. Intended mix is one large cap, one flexi cap, and one ELSS. The ELSS is required, because lock-in is a mandated FAQ category and only an ELSS demonstrates it.

**Source tiers:**

| Tier | Source | Owns |
|---|---|---|
| 1 | Selected AMC | Scheme-level facts: objective, minimums, exit load, TER, benchmark, riskometer |
| 2 | SEBI and AMFI | Regulatory and category-level facts: ELSS lock-in, TER limits, riskometer methodology, terminology |
| 3 | Groww official Help Centre | Platform processes: statement downloads, capital gains documents |

Tier 3 needs a clarification on the record. The project rules exclude third-party financial blogs and editorial articles, and that exclusion covers platform-published editorial content. It does not cover a platform's own official help documentation about its own processes. When the question is "how do I download my capital gains statement from Groww," the only correct source is Groww's official help documentation. Using anything else would be less accurate, not more. This distinction is a deliberate decision, recorded in the decision log, not an exception being quietly taken.

---

## 8. Assumptions

Every one of these is unvalidated. The validation column says what would settle it.

| # | Assumption | Risk if wrong | How we validate |
|---|---|---|---|
| A1 | The facts in our FAQ taxonomy are actually present in public AMC documents for the chosen schemes | Corpus cannot answer its own scope | Build the ground truth table by hand in Workstream 2 before any indexing |
| A2 | Users want the source link and will use it | Core differentiator is dead weight | Citation click rate once instrumented; cannot test pre-launch |
| A3 | A short bounded FAQ set covers most real factual questions | Users hit out-of-corpus responses constantly | Compare our taxonomy against publicly visible help centre FAQ categories |
| A4 | Groww's help documentation on statements is publicly readable without login | Tier 3 collapses, statement questions must reroute to RTA sources | Direct check, first task in Workstream 2 |
| A5 | TER is disclosed on a daily cycle and riskometer on a monthly one | Our freshness model is calibrated wrong | Read the SEBI master circular and AMFI disclosure page directly, treat both as corpus sources rather than assumed background |
| A6 | Local embeddings retrieve well enough on Indian financial terminology | Retrieval quality floor too low, need paid embeddings we do not have budget for | Benchmark retrieval against the ground truth table before building anything on top |
| A7 | Table-bearing PDFs survive extraction well enough to preserve label and value pairs | Numbers get separated from their labels, answers become wrong in a hard-to-detect way | Inspect extraction output manually before embedding, per document |
| A8 | Users will phrase questions in ways our normalisation handles | Retrieval misses on paraphrases | Paraphrase set inside the evaluation dataset |
| A9 | A visible scheme selector removes most scheme ambiguity | Wrong-scheme retrieval persists | Scheme-specific questions in the evaluation dataset |

A5 deserves a specific note. Both cadences were carried into this plan as stated background rather than as checked facts. They are load-bearing for the freshness design, so they get verified against the primary regulatory documents during source collection, and the fact classification table gets corrected if they turn out to differ.

---

## 9. Risks

| # | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R1 | Hallucinated fact presented with a real-looking citation | Critical | Medium | Grounded prompt, retrieval score threshold, citation validated against the chunk actually used |
| R2 | Stale dynamic fact, especially TER, answered as current | Critical | High | Static and dynamic classification, as-of date on every dynamic answer, staleness fallback message |
| R3 | Wrong scheme retrieved, answer plausible but about a different fund | Critical | Medium | Scheme selector, metadata filtering, scheme stated back in the answer |
| R4 | Direct and Regular plan confusion | High | High | State the plan explicitly wherever the source distinguishes it |
| R5 | Advice leaks through a factual-looking question | High | Medium | Layered detection, deterministic rules plus classifier, output validation |
| R6 | User submits PAN, Aadhaar or account number | High | Low | Deterministic pattern check as the very first pipeline step, before logging or any model call |
| R7 | PDF table extraction silently separates labels from values | High | Medium | Manual inspection per document, ground truth table as the check |
| R8 | Scope creep against a six-day timeline | High | High | Three schemes, fifteen sources, fifteen eval questions, documented as cuts rather than gaps |
| R9 | Conflicting values between two official sources | Medium | Medium | Documented source hierarchy, latest applicable document wins, conflict noted |
| R10 | Refusal reads as product failure rather than as a boundary | Medium | Medium | Refusal taxonomy with useful educational redirects instead of a flat no |
| R11 | Free-tier generation model rate limits during the demo | Medium | Medium | Local embeddings so indexing never depends on quota, cached demo responses as fallback |
| R12 | Source page changes or moves before submission | Low | Medium | Archive the fetched copy alongside the URL and the date collected |

R2 and R4 are the two that will actually bite. Both produce answers that look completely correct and are not, which is the failure mode a citation does not catch, because the citation is real.

---

## 10. Non-goals

Explicitly out of scope for this MVP. Listed so that nothing here is mistaken for an oversight.

**Advice and recommendations**

- Whether to buy, sell, hold or switch
- Which fund is better
- Portfolio construction or asset allocation
- Personalised financial or tax planning
- Return or performance prediction
- Any "best fund" framing

**Performance**

- Computing returns
- Comparing returns between schemes
- Interpreting past performance
- Performance questions are redirected to the official factsheet without commentary

**Personal data**

- PAN, Aadhaar, account numbers, OTPs, phone numbers, email addresses
- User accounts or authentication
- Any personalised holding data

**Transactions**

- Buying, redeeming, switching
- Creating or modifying SIPs
- Anything that moves money

**Coverage**

- More than one AMC
- More than three schemes in this milestone
- Full industry coverage
- Live NAV or market data

**Engineering**

- Multi-agent architecture
- Fine-tuning
- Automated crawling and refresh, the refresh strategy is documented rather than built
- Microservices, queues, or infrastructure beyond one frontend and one backend

---

## 11. Phase decision framework

The project rule requires each phase to answer six questions. For Phase 1:

**What are we building?**
A facts-only mutual fund FAQ assistant inside a retail investing platform, scoped to one AMC and three schemes, where every factual answer carries one official citation and an as-of date.

**Why does the user need it?**
Because official facts are public but scattered, and the fast alternatives are unsourced. The gap is verification, not availability.

**How will we implement it?**
Curated corpus, hybrid retrieval with scheme-level metadata filtering, grounded generation, layered guardrails, citation validation, and a deliberately small UI.

**What alternatives did we consider?**
A static searchable FAQ page, which is cheaper and more reliable but does not handle paraphrased natural language and does not demonstrate RAG. A multi-AMC corpus, rejected because breadth at the cost of accuracy inverts the product's own value proposition. A general chatbot with web search, rejected because it cannot guarantee source authority, which is the entire point.

**How will we know it works?**
Every factual answer carries a valid citation to an approved source, every advice question in the evaluation set is refused, every out-of-corpus question is declined rather than answered, and answers match the hand-built ground truth table.

**What could go wrong?**
Section 9. The two that matter most are stale dynamic facts and wrong-scheme retrieval, because both fail while looking correct.

---

## 12. Phase 1 acceptance check

| Criterion | Status |
|---|---|
| Problem is specific | Met |
| Target user is clear | Met |
| MVP opportunity is realistic | Met |
| Non-goals explicitly documented | Met |
| Jobs to be done identified | Met |
| Assumptions recorded with validation method | Met |
| Risks recorded with mitigations | Met |
| No implementation begun | Met |
| AMC and schemes selected | Deliberately deferred to Workstream 2 |

---

## 13. What happens next

Workstream 2 opens with four tasks, in this order:

1. Verify that Groww's official help documentation on statements and capital gains is publicly readable. This settles assumption A4 and determines whether Tier 3 survives.
2. Verify the TER and riskometer disclosure cadences against the SEBI master circular and AMFI disclosure material. This settles A5 and either confirms or corrects the fact classification model.
3. Shortlist candidate AMCs on documentation quality, score them, and select one. Then select three schemes under it, one large cap, one flexi cap, one ELSS.
4. Begin the ground truth fact table, filled by hand from primary sources, before a single document is chunked or embedded.

Nothing gets indexed until step 4 is underway, because the ground truth table is what tells us whether the corpus can answer its own scope.
