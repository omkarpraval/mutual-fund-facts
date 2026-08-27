# Changelog

Versions track what the system can be trusted to do, not how much code exists.
A release that removes an answer is as real as one that adds a feature.

---

## 0.7.0 — 27 August 2026

Overfitting check, mixed-intent handling, and a second safety gap closed.

### The headline number changed, and that is the point

The 40-case evaluation suite reports 100%. A held-out suite of cases the
system had never seen reported **70%** on its first run. Same system, same
day. The 100% was measuring how well the system handles cases it was
tuned on, which is not the same as how well it works.

After fixing what the held-out run exposed, a second batch of freshly
written unseen cases scored **86%**, then 90% after one more fix. That
number, not the 100%, is the honest estimate of generalisation.

**Stated limitation:** I wrote both the system and the held-out cases, so
this is a weak proxy. It measures generalisation beyond exact tuned
strings; it cannot measure what I failed to imagine. The genuinely
independent evidence remains the user's own adversarial session, which
found four routing bugs a 22-case suite could not have caught.

**Protocol:** held-out cases are never tuned against. A failure is fixed,
promoted to `eval_set.csv` as a permanent regression test, and replaced
with a new unseen case. Ten cases were promoted this way (E41 to E50).

### Fixed

- **OTP was not detected as PII.** A six-digit code fell between the phone
  pattern (10 digits) and the account pattern (11 to 18), so "My OTP is
  483921" reached retrieval. The second real safety gap this project has
  found, and the held-out suite caught it, not the main one.
- **Performance claims leaked past the guard.** "Can this fund outperform
  the market?" and "Can this beat its benchmark?" were answered as
  factual, because the return-prediction pattern required "will" or
  "would". Performance framing now refuses regardless of modal.
- **Frequency now outranks lumpsum phrasing.** "Could someone start with
  Rs. 500 monthly?" matched "start with" and was treated as a lumpsum
  question. An explicit frequency makes it a SIP question.
- Synonym gaps: fund expenses, index it tracks, high risk, redeem units.

### Added

- **Mixed-intent partial answering.** "What is the TER, and should I
  invest?" answers the factual clause and declines the advisory one in the
  same response. The D009 asymmetry survives: a clause is answered only if
  it independently passes the advice guard AND resolves to a topic.
  Splitting never makes an advisory clause answerable. (D045)
- **Ambiguous scheme references offer options.** "Minimum SIP for SBI?"
  names the fund house, not a scheme, so the response lists the three
  schemes as buttons rather than dead-ending on "which scheme?". (D046)
- **Recognised scheme, unrecognised topic** now says the question falls
  outside the answerable set and lists what is available, rather than
  returning a weak retrieval match. This is what stopped "What stocks does
  this fund hold?" scraping an answer out of the corpus.
- Follow-up chips on answers, refusals and gap cards, generated from the
  coverage map so they can only offer facts that exist.
- `holdout_set.csv` and `tests/run_holdout.py`.

### Known open, deliberately

Three held-out cases still fail, all in the same direction: "Whats the
yearly cost of holding this?", "Any charge if I pull out in the first
month?", "Can I switch between plans without a charge?". All three are
wrong refusals, which under D009 are annoyances rather than failures. They
are left open because fixing them by adding synonyms would be tuning
against the held-out set, and because they are the clearest available
argument for the Groq intent classifier: measure `run_holdout.py` with and
without `GROQ_API_KEY` to see what it is worth.

---

## 0.6.0 — 27 August 2026

Adversarial testing pass. A user-run test session found four routing bugs
that my own evaluation set could not have caught.

### Fixed

- **"Can I" was treated as "Should I".** One word, `can`, sat in the same
  pattern as `should`, so every feasibility question was refused: "Can I
  invest Rs. 500 monthly?", "Can I redeem after 3 years?", "Can I invest
  less than Rs. 5,000?". A facts-only product refusing to state facts is
  the worst failure it has. The guard now splits on grammar rather than
  keywords: permission and capability are factual, recommendation is
  advice, and a permission question with no factual target still refuses.
  (D042)
- **Bare scheme names were not recognised.** "Flexicap" without the "SBI"
  prefix asked which scheme. Distinctive bare aliases added. "Large Cap"
  alone is deliberately excluded: it is a SEBI category, not a scheme, so
  "which large cap fund is best" must never resolve to a specific fund.
- **Quarterly SIP returned the monthly figure.** A factual error, not a
  formatting one. Answers are now frequency-aware.
- **Instalment tier picked the wrong option.** Rs. 1,000 clears the
  6-instalment tier but was quoted against the 12-instalment one,
  understating what the document allows.
- **Scheme mismatch was silent.** Selecting one scheme and asking about
  another returned a bare no-evidence. The question's scheme now wins and
  the interface says so.

### Added

- **Feasibility answering.** A stated amount turns a lookup into a check:
  "Rs. 500 is permitted for a monthly SIP with at least 12 instalments."
  The answer never opens with "Yes" — evaluating an amount against a
  published minimum is factual, but a bare "Yes" in front of a sentence
  about investing reads as endorsement. (D043)
- **Known gaps are distinguished from unknown questions.** "I don't
  understand you" and "I understand exactly and have not verified that
  fact" are different answers. The gap card names the scheme it
  recognised and lists what it does have. (D044)
- **Quick-fact chips generated from the coverage map**, so they can only
  ever offer facts that exist. Refusals carry the same chips, so a refusal
  is a redirection rather than a dead end.
- 18 adversarial regression cases (E23 to E40). Eval set is now 40.
- `.env` support with no new dependency, and `.env.example`.

### Note on the evaluation set

Every advice case in the original set used "Should I" or "Which fund". I
wrote both the classifier and its tests, so the tests covered the boundary
I already had in mind. An evaluation set written by the author of the
system measures what the author thought of, not what users do. Every bug
above is now a permanent regression test.

---

## 0.5.0 — 27 August 2026

LLM intent classification, placed where the failures actually were.

### Added

- `retrieval/intent.py`. Groq classifies a question into one topic key when
  the deterministic synonym lookup finds nothing. (D041)
- `verify_groq.py`, a live check to run locally. The build sandbox cannot
  reach api.groq.com, so the Groq path is plumbed and unit-tested but not
  verified against the real API.
- `tests/test_intent_safety.py`, which asserts no PII or advice message ever
  reaches the classifier, and that the classifier is genuinely reachable
  otherwise so the test cannot pass trivially.

### Design constraints on the classifier

- **Runs after the guards, never before.** Sending a message to a third-party
  API to work out its intent would defeat D008 if that message held a PAN.
  Asserted by test, not by convention.
- **Closed enum with an explicit `none`.** An unconstrained classifier invents
  a plausible topic for out-of-scope questions, which would quietly destroy
  refusal accuracy. The enum is enforced in code; a reply outside it is
  discarded and treated as no match.
- **Deterministic first.** The classifier runs only on unmatched queries, so
  most questions cost no latency and no quota, and free-tier rate limits stop
  being a demo risk.
- **Failure degrades to no-evidence.** A timeout or error never produces a
  guess.

### Not yet verified

Whether the classifier helps. It needs a live run against the eval set, and
in particular the three out-of-scope cases in `verify_groq.py` must come back
as `none`. Refusal accuracy is currently 100% and this is the change most
capable of breaking it.

---

## 0.4.0 — 27 August 2026

Feedback pass on the running prototype. Three defects found by using it,
plus natural-language coverage.

### Fixed

- **Three dates, never one.** `as_of_date` conflated the date a fact applies
  to, the document's publication date, and the date we downloaded it. The UI
  labelled all three "as of", claiming currency it had not established. Now
  `fact_as_of`, `source_dated` and `retrieved_at` are separate and labelled
  separately. Only `fact_as_of` means the value is current, and it exists
  today only on TER. (D038)
- **Three-sentence limit enforced in code.** The extractive path was emitting
  the full six-frequency SIP table as one block, breaching a stated
  requirement. `cap_sentences()` now runs on every generated answer.
  Conditional facts get a summary plus an explicit pointer to the rest, so
  the cap never hides the conditions. (D039)
- **Sentence splitting broke on "Rs."** Naive splitting read "Rs. 1,000" as a
  boundary and truncated answers mid-figure. Nearly every answer here contains
  "Rs.", so most conditional responses would have been mangled. Abbreviations
  are masked before splitting.
- **Citations showed internal ids.** `kim_flexicap` told a retail user
  nothing and read like a leaked database key. Now organisation, document
  title, dated provenance and a labelled link. (D040)

### Added

- Natural and Hinglish phrasings in query normalisation: "500 every month",
  "paisa nikalne pe charges", "fund fee", "withdrawal charges", "har mahine".
  Deterministic, no model call.
- `backend/app/corpus/titles.py`, document id to human title.

### Known limits unchanged

Four facts remain quarantined and unanswerable by design. Latest factsheet
located is March 2026, so riskometer values stay conditional.

---

## 0.3.0 — 27 August 2026

API and interface.

### Added

- FastAPI: `/api/chat`, `/api/health`, `/api/schemes`.
- Generation adapter with Gemini and Groq implementations, and an extractive
  fallback that composes the answer from the retrieved fact. The fallback
  cannot hallucinate because it never generates, so the system is demoable
  with no key.
- Next.js frontend, all nine required UI states.
- Provenance strip as the signature element: source and date as a filing
  block rather than a footnote.

### Fixed

- **Wrong-scheme answers through the API.** The endpoint re-ran retrieval with
  the raw request `scheme_id`, discarding alias resolution and scheme-name
  stripping. "SBI Bluechip Fund exit load?" resolved correctly inside the
  pipeline, was re-searched with no scheme, and returned the ELSS fund's exit
  load with a real citation attached. Fluent, cited, wrong fund. The
  evaluation suite missed it because the harness calls the pipeline directly,
  so the bug lived only on the path a user takes. Retrieval now happens in
  exactly one place. (D036)

---

## 0.2.0 — 27 August 2026

Real corpus and evaluation. Routing 68% to 100%, retrieval 58% to 100%.

### Added

- Corpus built from `ground_truth.csv`, with verification state gating
  indexing. Quarantined facts are unreachable rather than discouraged. (D032)
- Evaluation harness, 22 questions across seven categories, scored against
  ground truth rather than by inspection.

### Fixed

- **Tokenisation ignored punctuation**, leaving "[expense" and "ratio]" as
  tokens and scoring exactly zero on chunks that plainly held the answer.
- **No-evidence was structurally impossible.** Min-max normalisation always
  awards the top candidate 1.0, so a score threshold cannot express "nothing
  fits". Eligibility moved to a lexical coverage gate. (D025)
- **Unrecognised topics got answered** on generic vocabulary overlap. An
  unknown topic now raises the evidence bar rather than leaving it. (D026)
- **Scheme names diluted their own queries.** Four of six content words in
  "SBI Magnum Multicap Fund exit load" named the fund, not the fact. The
  resolved alias is now stripped before retrieval. (D027)
- **Citations pointed at definitions instead of values.** "Expense ratio of
  SBI Flexicap Fund" cited AMFI's definition of TER rather than SBI's figure.
  Source hierarchy is now a categorical sort key, not a score bonus. (D034)
- **Two eligibility gates contradicted each other.** A leftover relevance
  floor discarded the correct TER chunk at 0.11 against a 0.12 threshold.
  Eligibility is decided in one place. (D035)

---

## 0.1.0 — 26 August 2026

Product definition, corpus research, retrieval and safety core.

### Added

- Discovery, source research and scope documents.
- PII and advice guards, five-branch refusal taxonomy, fixed guard ordering
  with PII before any logging or model call. (D008)
- Alias-first scheme resolution. All three schemes were renamed under SEBI
  categorisation, so users type names the corpus does not hold. (D022)
- Section-aware chunking with a label/value audit.
- Static and dynamic fact classification with staleness windows. (D004)

### Findings that shaped the product

- Minimum SIP has six values by frequency, each with an instalment condition.
  Three research sites gave three different answers because each picked one
  branch and dropped the conditions. This became the product principle: do
  not oversimplify a fact whose official source carries conditions. (D029)
- Automated collection does not work here. The AMC's document path disallows
  it and scheme pages render client-side. (D024)
- A genuine version conflict on Flexicap exit load, 0.50% against 0.10%,
  resolved on document specificity rather than index recency. (D031)
