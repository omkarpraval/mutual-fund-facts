# Decision Log

Running record of meaningful product, data and engineering decisions for the Mutual Fund Facts Assistant. Each entry captures the decision, the reasoning, what else was on the table, and what we gave up to get it.

Entries are append-only. If a decision is reversed later, the original stays and a new entry supersedes it, with a pointer both ways. A log that gets tidied up after the fact is worth nothing.

---

## D001. Product context and corpus scope are separate things

**Date:** August 2026
**Phase:** 1
**Decision:** Groww is the product and PM context. The corpus is one AMC plus three schemes, drawn from AMC, SEBI, AMFI and Groww's own official help documentation. These are two different scoping decisions and are documented separately.

**Why:** The milestone brief asks for a product choice from a list of distribution platforms, while the build requirements ask for an AMC and schemes. Those are not the same axis. Groww is a distributor, not a fund house, so scheme-level facts do not originate with it. Treating the platform as the user-facing context and the AMC as the knowledge scope resolves the tension without bending either requirement.

**Alternatives considered:** Treat Groww as the source of everything, which would mean sourcing scheme facts from a distributor rather than the fund house and would be less authoritative. Or ignore the product list and build a generic assistant, which would fail the brief and lose the PM framing entirely.

**Trade-off:** Adds a source tier and some explaining, in exchange for each fact coming from the organisation that actually owns it.

---

## D002. Official platform help documentation is a valid source, editorial content is not

**Date:** August 2026
**Phase:** 1
**Decision:** Groww's official Help Centre is an approved Tier 3 source for platform process questions. Groww's blog, editorial articles and educational content are not approved sources for any answer.

**Why:** The exclusion list bars third-party financial blogs and aggregator articles, which is about editorial content of uncertain authority. Official first-party process documentation is a different class of artifact. For "how do I download my capital gains statement from Groww," the platform's own help documentation is the authoritative source and nothing else is closer to the truth.

**Alternatives considered:** Exclude Groww entirely as a source, which would leave a mandated FAQ category with no correct source available. Or allow all Groww-published content, which would let editorial material in through the back door.

**Trade-off:** Requires an explicit written boundary and a source-by-source judgement during collection, rather than a simple domain-level allow or block.

---

## D003. Persistent scheme selector in the UI

**Date:** August 2026
**Phase:** 1
**Decision:** The interface carries a persistent scheme selector above the input. Every query is submitted with a scheme attached. An explicit scheme named in the question overrides the selector for that query. If neither is present, the assistant asks which scheme before retrieving.

**Why:** The mandated example questions ("What is the minimum SIP?") contain no scheme name, but retrieval needs a scheme filter to avoid pulling facts from the wrong fund. Without resolution, the system either guesses or returns a blend of schemes, and both failures look like correct answers.

**Alternatives considered:** Require the user to name the scheme every time, which is friction on every single query and will be ignored. Or infer the scheme from conversation history, which fails on the first message and drifts silently afterwards.

**Trade-off:** One extra UI element and a resolution step in the pipeline, in exchange for a large reduction in wrong-scheme retrieval, which is one of the two failure modes that produce confident wrong answers.

---

## D004. Facts are classified as static or dynamic in the data model

**Date:** August 2026
**Phase:** 1
**Decision:** Every fact in the corpus carries a type field. Static facts (investment objective, benchmark, exit load structure, ELSS lock-in) are answered normally. Dynamic facts (TER, riskometer) are answered as value plus as-of date plus source, with a staleness fallback when our stored copy is older than its refresh cycle.

**Why:** TER and riskometer are republished on a regular cycle. A number captured in August and answered confidently in October is wrong, and the citation will not catch it, because the citation is real and points at a page that now says something different. This is the worst failure this product can produce.

**Alternatives considered:** Treat all facts identically, which is simpler and quietly ships stale numbers. Or exclude dynamic facts from scope entirely, which would drop expense ratio and riskometer, two of the mandated FAQ categories.

**Trade-off:** Extra metadata, extra prompt handling, and answers that are longer and more hedged for two fact types. Worth it, because those two are the ones most likely to be acted on.

**Depends on:** Verification of the actual disclosure cadences during Workstream 2. If the cadences differ from what is currently assumed, this classification gets corrected, not abandoned.

---

## D005. KIM, scheme page and factsheet are primary; SID is extracted selectively

**Date:** August 2026
**Phase:** 1
**Decision:** The corpus is built primarily from KIM documents, official scheme pages and factsheets. SIDs are used only by extracting specific relevant sections with section metadata preserved. No whole SID is indexed.

**Why:** SIDs run to a hundred pages of dense regulatory tables. Naive PDF extraction on that material separates labels from values, and the resulting chunks produce answers that are wrong in a way that is very hard to detect. KIM is short and carries most of the target facts.

**Alternatives considered:** Index everything and rely on retrieval to sort it out, which trades a data quality problem for a retrieval problem and does not solve either.

**Trade-off:** Some facts that only appear in the SID may need manual section identification, which is slower. Extraction quality is inspected per document before embedding.

---

## D006. One primary citation, supporting citation only when necessary

**Date:** August 2026
**Phase:** 1
**Decision:** Every factual answer surfaces exactly one primary source. A second supporting source is permitted only when the question spans two distinct facts that no single authoritative source covers.

**Why:** The brief requires one clear source link. Read strictly, that fails on legitimate compound questions such as exit load plus lock-in. Read loosely, the answer card turns into a bibliography and the user stops reading any of it.

**Alternatives considered:** Hard limit of one source with compound questions split into two turns, which is cleaner to implement but worse to use. Or unlimited sources, which dilutes the thing that makes the answer trustworthy.

**Trade-off:** Slightly more complex citation validation, since both sources must be checked against the chunks actually used.

---

## D007. Ground truth fact table is built before anything is indexed

**Date:** August 2026
**Phase:** 1
**Decision:** A hand-built table of scheme, fact, value, source URL, as-of date and fact type is created from primary sources before chunking, embedding or retrieval work begins.

**Why:** It does three jobs at once. It proves the corpus can actually answer its own declared scope. It becomes the answer key for evaluation instead of eyeballing whether outputs look plausible. And it generates the coverage map for free.

**Alternatives considered:** Build the system first and write the evaluation set afterwards, which is the normal order and produces an evaluation set unconsciously shaped to what the system already does well.

**Trade-off:** Costs most of a day up front, on a six-day timeline, before anything runs. Accepted, because without it the evaluation results would be untrustworthy and the project rules forbid fabricated results.

---

## D008. Guardrail ordering: PII first, before logging or any model call

**Date:** August 2026
**Phase:** 1
**Decision:** Pipeline order is fixed as input, then PII detection, then advice and intent classification, then scheme resolution, then retrieval, then generation, then output validation, then response.

**Why:** PII detection placed anywhere after logging or after the model call means the data has already left. Detection is not the point, non-retention is. Deterministic patterns for PAN, Aadhaar, phone and email run first, and matched content is blocked before it is written anywhere or sent downstream.

**Alternatives considered:** Single LLM call handling classification and generation together, which is fewer moving parts but means the sensitive string reaches the model before anything decides it should not have.

**Trade-off:** More stages, more latency, more code. Non-negotiable regardless.

---

## D009. Advice detection is layered, not regex alone

**Date:** August 2026
**Phase:** 1
**Decision:** Deterministic rules run first as a fast path, with a lightweight classifier behind them for cases the rules miss. Ambiguous cases fall back to refusal rather than to answering.

**Why:** Rules catch "should I buy this fund" and miss "is this one worth putting money into," Hinglish phrasings, and advice questions wearing a factual costume. Rules alone will leak.

**Alternatives considered:** Regex only, which is fast, free and insufficient. Classifier only, which adds latency to every single query including obviously factual ones.

**Trade-off:** Two mechanisms to maintain and test. The fallback direction is deliberately asymmetric: a wrongly refused factual question is a minor annoyance, a wrongly answered advice question is a product failure.

---

## D010. Refusals are a designed feature with a taxonomy

**Date:** August 2026
**Phase:** 1
**Decision:** Refusals are categorised (buy or sell, fund selection, portfolio construction, return prediction, personalised financial decision) and each category maps to a specific message and a relevant official educational link. No generic flat refusal.

**Why:** The brief requires a polite refusal with a relevant educational link. Beyond compliance, a refusal that hands the user the riskometer and benchmark so they can judge for themselves is a better product than one that just says no, and it is where the difference between a working prototype and a good one actually shows.

**Alternatives considered:** Single generic refusal message, which is one line of code and reads as the system being broken.

**Trade-off:** Requires building and maintaining a small mapping table.

---

## D011. Local embeddings, API only for generation

**Date:** August 2026
**Phase:** 1
**Decision:** Embeddings run locally via sentence-transformers with Chroma persisted to disk. Only the generation step calls an external API. Retrieval quality is benchmarked against the ground truth table before anything is built on top.

**Why:** Free tier only. Indexing is the step that gets re-run most often during development, so making it quota-free removes the main source of mid-build blockage. It also makes the index reproducible offline.

**Alternatives considered:** Paid embedding API, no budget. Free-tier embedding API, which puts rate limits on the exact loop that needs to run repeatedly.

**Trade-off:** Local models are generally weaker on domain-specific financial terminology. This is why the benchmark happens before commitment rather than after, and it is why hybrid retrieval is in the plan.

---

## D012. Hybrid retrieval, dense plus keyword

**Date:** August 2026
**Phase:** 1
**Decision:** Dense semantic retrieval is combined with BM25 keyword matching.

**Why:** Most target facts are exact strings: a rupee amount, a percentage, a day count, a named index. Dense embeddings are mediocre at exact-token matching, which is precisely what this corpus is full of.

**Alternatives considered:** Dense only, which is simpler and misses on exact figures. Keyword only, which fails on paraphrased questions, and paraphrase handling is an explicit evaluation category.

**Trade-off:** Two retrievers and a merge step. Modest complexity for a meaningful accuracy gain on the fact types that matter most.

---

## D013. Scope cuts for a six-day timeline, recorded as decisions rather than gaps

**Date:** August 2026
**Phase:** 1
**Decision:** Three schemes instead of five, roughly fifteen sources instead of twenty-five, fifteen evaluation questions instead of twenty-five. Analytics becomes a metrics section inside the PRD rather than its own phase. Testing covers guardrails and citation logic rather than a full pyramid. Every cut is stated in the README limitations section.

**Why:** Six days. A complete small system beats an incomplete large one, and stated limits read as judgement while silent gaps read as failure to finish.

**Alternatives considered:** Attempt full scope and ship partial artifacts across the board.

**Trade-off:** Less breadth. Each cut sits at the minimum the brief allows, not below it.

---

## D014. Local build and recorded demo rather than deployment

**Date:** August 2026
**Phase:** 1
**Decision:** Build and run locally, submit a demo video under three minutes. Deploy only if time remains on the final day.

**Why:** The brief explicitly permits a demo video where hosting is not possible. Free-tier hosting cold-starts slowly enough to make a live demo look broken, and debugging a deployment on day six costs time that the evaluation report needs.

**Alternatives considered:** Deploy early and develop against it, which spends scarce days on infrastructure that is not being assessed.

**Trade-off:** No live link for the evaluator to click. Mitigated by a clean recorded demo and complete setup instructions in the README.

---

## D015. Documentation artifacts consolidated

**Date:** August 2026
**Phase:** 1
**Decision:** This decision log stays as its own file. The coverage map is generated from the ground truth table rather than maintained by hand. The source refresh strategy becomes a README section. The North Star and metrics tree live inside the PRD.

**Why:** Five additional standalone artifacts on top of an already long deliverable list would eat build days without adding assessed value. These four keep their substance while costing close to nothing.

**Alternatives considered:** Separate files for each, which looks thorough and spends time on formatting instead of on the system.

**Trade-off:** Slightly less discoverable individually. The README indexes all of them.

---

## D016. Default to Direct plan, name the plan in every answer

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** Where a source distinguishes Direct from Regular, answers default to Direct and state the plan explicitly in the answer text. No plan toggle in the UI.

**Why:** Groww distributes Direct plans, so a Groww user asking about expense ratio almost certainly means Direct. But a silent default is invisible, and a wrong-plan answer produced by an invisible default is indistinguishable to the user from a wrong answer. Naming the plan makes the assumption checkable, on the same principle as showing the citation.

**Alternatives considered:** A plan toggle beside the scheme selector, rejected because most users will not touch it and an untouched default is the same silent-default problem with extra UI. Showing both values, rejected because it doubles the length of the shortest answers and forces the user to do the disambiguation we were supposed to do.

**Trade-off:** Slightly longer answers on charge-related questions. Open to override.

---

## D017. The AMC is SBI Mutual Fund, deliberately not Groww Mutual Fund

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** SBI Mutual Fund is the corpus AMC. Groww Mutual Fund was considered and rejected.

**Why:** Groww runs its own AMC, which made a single-brand project tempting. Three reasons against. Its equity lineup has no flexi cap, so the required category mix would have been quietly swapped for an available one. Its documentation history is shorter than an established fund house's. Most importantly, if the AMC and the platform are the same company, the three-tier source architecture never gets exercised and becomes decorative, which throws away the thing the project is built to demonstrate.

SBI Mutual Fund was then verified to publish a dedicated TER disclosure page and a dedicated SID and KIM page in the current SEBI format, which are the two document surfaces this build depends on most.

**Alternatives considered:** Groww Mutual Fund, rejected above. HDFC, ICICI Prudential, Nippon India and Kotak, all viable and not assessed in depth on a six-day timeline. SBI is selected because its pages were verified to exist, not because the others were checked and found worse. Stated as such rather than presented as a full market scan.

**Trade-off:** We give up the neat single-brand narrative in exchange for an architecture that actually does something.

---

## D018. Every scheme carries an explicit alias list

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** Scheme metadata includes an alias list covering former names, common short forms and plan variants. Scheme resolution checks aliases before falling back to embedding similarity.

**Why:** SBI Bluechip Fund is now SBI Large Cap Fund, and the AMC's own page carries the former name in parentheses. A long-term holder will type the old name. Our corpus will mostly carry the new one. Relying on semantic similarity to bridge a rename is exactly the kind of maybe we cannot afford on scheme identity, because a scheme mismatch is a confident wrong answer rather than a visible failure.

**Alternatives considered:** Trust embedding similarity to handle it, which might work and would fail silently when it did not.

**Trade-off:** A small amount of manual metadata per scheme. Cheap, and it turns an unexplained retrieval miss into a solved case.

---

## D019. Staleness thresholds set at seven days and forty-five days

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** TER is treated as stale seven days after collection. Riskometer is treated as stale forty-five days after collection. Past threshold, the answer still gives the stored value but flags it as possibly not current and directs to the live disclosure page.

**Why:** TER is disclosed daily and riskometer monthly, both now verified against AMFI. A literal one-day threshold on TER would put every expense ratio answer permanently into the stale branch for a project built over a week, which is technically correct and useless as a demonstration. Seven days is an honest compromise that shows the normal answer path while acknowledging the value may have moved.

**Alternatives considered:** Match the thresholds exactly to the disclosure cadence, rejected as above. No threshold at all, which is the stale-number failure this whole classification exists to prevent.

**Trade-off:** A TER answer between one and seven days old is presented without a staleness flag and could be wrong. This is written into the README limitations rather than hidden.

---

## D020. Manual collection with archived local copies

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** Documents are downloaded by hand, not crawled. Each is archived locally alongside its metadata row at collection time. The archived copy is what gets indexed. The live URL is what gets cited.

**Why:** Fifteen to twenty documents does not justify a crawler, and a crawler adds robots and rate-limit questions that carry risk without adding anything the project is assessed on. Archiving protects against a page moving or changing before submission, which is risk R12.

**Alternatives considered:** Build a small crawler, rejected on cost and risk. Fetch live at query time, rejected because it makes every answer dependent on an external site being up during the demo.

**Trade-off:** Refreshing the corpus is a manual job. Documented as the refresh strategy rather than automated.

---

## D021. On genuine same-tier conflict, cite both rather than choose

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** If two sources at the same tier and same date genuinely disagree, answer from the primary document, state that sources differ, and cite both.

**Why:** Silently picking a winner is precisely the behaviour this product exists to not have. The case may never occur in a corpus this small, but discovering the policy gap during evaluation is worse than writing the rule now.

**Alternatives considered:** Always prefer the more specific document, which is a reasonable heuristic and still hides the disagreement from the user.

**Trade-off:** One answer shape that breaks the one-citation default, already permitted under D006.

---

## D022. All three schemes are renamed, so alias resolution is promoted from safeguard to core requirement

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** Alias resolution moves from a defensive measure to a first-class part of scheme resolution, backed by its own maintained file, `scheme_aliases.csv`. Every scheme in the corpus has a confirmed former name recorded before ingestion begins.

**Why:** D018 added alias lists on the strength of one observed rename. Checking the other two schemes found the same thing in both cases. SBI Bluechip Fund is now SBI Large Cap Fund. SBI Long Term Equity Fund is now SBI ELSS Tax Saver Fund. SBI Magnum Multicap Fund was recategorised to SBI Flexicap Fund. Three schemes, three renames, and the AMC's own pages and document filenames carry the former names in parentheses.

This is not an SBI quirk. It follows SEBI's scheme categorisation push, so the naming drift is industry-wide and any AMC we picked would have posed it. What makes it dangerous is the asymmetry: our corpus speaks in new names, our users speak in old ones, and the mismatch produces a wrong-scheme answer rather than a visible failure.

**Alternatives considered:** Treating the first rename as a one-off and handling it inline, which the other two cases have now disproved.

**Trade-off:** One more metadata file to keep current. Trivial next to the failure it prevents, and the evaluation set now gets a dedicated old-name paraphrase category to prove it works.

---

## D023. Ground truth values come only from primary documents, never from search snippets

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** `ground_truth.csv` ships as a skeleton with every row present and unfilled, marked PENDING, rather than pre-populated from anything found during research. Values enter only from a downloaded AMC document or an AMC page, with the document id and as-of date recorded alongside.

**Why:** Research surfaced plenty of specific-looking numbers for these exact schemes: minimum SIPs, minimum lumpsums, exit loads. They came from aggregators and distributor pages, and where two of them covered the same fact they frequently disagreed. Filling the table from those would have produced a confident, complete, wrong answer key, and every downstream evaluation metric would then have measured our agreement with bad data rather than accuracy.

An empty cell marked PENDING is honest. A filled cell from an unverifiable source is worse than useless, because it looks finished.

**Alternatives considered:** Seed from third-party values and correct during collection, rejected because seeded values that survive review by inattention are indistinguishable from verified ones once the status column gets stale.

**Trade-off:** The table looks unfinished until documents are downloaded. That is an accurate picture of where the project actually is.

---

## D024. Corpus collection is manual because automated collection does not work here

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** All Tier 1 documents are downloaded by hand in a browser. No scraping of AMC pages, no automated PDF fetching. Recorded as a permanent constraint rather than a preference.

**Why:** Both automated routes were tested and both failed. Fetching a KIM from the AMC's `/docs/` path returns a robots refusal, and that path holds every KIM, SID, SAI and factsheet. Separately, the AMC's scheme pages are client-side rendered, so an automated fetch of a scheme page returns navigation, footer and a loading spinner while every actual fact loads after render.

D020 already specified manual collection, but for the weaker reason that fifteen documents does not justify a crawler. The real reason is that a crawler would return nothing usable. Discovering this on Day 5, with an ingestion pipeline already written against an assumed scrape, would have cost the build.

**Alternatives considered:** A headless browser to render the scheme pages, which would work technically but spends a build day on infrastructure the project is not assessed on, and still leaves the robots-blocked PDFs unsolved.

**Trade-off:** The corpus is a point-in-time manual snapshot and refreshing it means repeating the checklist. Stated in the README limitations rather than glossed.

**Note on the robots rule:** it governs automated agents. A person opening a public investor document that the AMC publishes for investors is the intended use of that document. The distinction is deliberate and worth stating in the README, because an evaluator may reasonably ask.

---

## D025. Lexical coverage gate, not a score threshold, decides no-evidence

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** A chunk becomes eligible only if a minimum share of the question's content words actually appear in it. The normalised relevance score ranks the survivors; it does not decide eligibility.

**Why:** Found by a failing test. Min-max normalisation always awards the best candidate a 1.0 no matter how irrelevant it is, so a normalised score is structurally incapable of expressing "nothing here is relevant." The out-of-corpus test returned two confident hits. Since a truthful no-evidence response is a stated product principle, the gate has to be something normalisation cannot manufacture, and lexical overlap is exactly that.

**Alternatives considered:** Raising the score threshold, which cannot work for the reason above. An absolute BM25 floor, rejected because raw BM25 is not comparable across queries of different lengths.

**Trade-off:** Purely lexical, so a heavily paraphrased question with no shared vocabulary could be wrongly refused. Acceptable under the asymmetry in D009: a wrong refusal is an annoyance, a confident wrong answer is a failure.

---

## D026. An unrecognised FAQ topic raises the evidence bar rather than lowering it

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** When query normalisation maps a question to no known topic, the coverage floor rises from 0.40 to 0.65.

**Why:** "Who is the fund manager?" scored 0.50 coverage against a regulatory chunk purely because the generic word "fund" appeared in it. That is a match on vocabulary, not on meaning, and it routed an out-of-scope question to a factual answer.

We have a defined FAQ taxonomy. A question matching none of it is, by the brief's own Class 2 definition, out of scope. So an unrecognised topic is the strongest available signal that we should not be answering, and it should tighten the gate rather than leave it unchanged.

**Alternatives considered:** IDF-weighted coverage, tested and rejected: on a corpus this small the IDF statistics are meaningless, and it broke a legitimate tier-2 retrieval. Refusing outright on unknown topic, rejected because the synonym list will never be complete and that would punish honest paraphrases.

**Trade-off:** A valid question phrased entirely outside the synonym list faces a stricter bar. The synonym list is cheap to extend when evaluation surfaces a miss.

---

## D027. The resolved scheme name is stripped from the retrieval query

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** Once scheme resolution matches an alias, that text is removed from the query before retrieval runs.

**Why:** "SBI Magnum Multicap Fund exit load" scored 0.33 coverage against the very chunk that answers it, because four of its six content words name the fund rather than the fact. The scheme is already enforced by metadata filtering, so leaving its name in the query adds no retrieval signal and actively dilutes the signal that matters.

**Alternatives considered:** Lowering the coverage floor, which would have re-admitted the false positives D026 exists to block.

**Trade-off:** None identified. The scheme constraint is strictly better expressed as a filter than as query terms.

---

## D028. Tokenisation must be punctuation-aware

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** Tokenisation extracts alphanumeric runs and preserves percentages, rather than splitting on whitespace.

**Why:** Whitespace splitting left tokens like "[expense" and "ratio]", which silently failed to match "expense ratio" and returned a BM25 score of exactly zero for a chunk that plainly contained the answer. This corpus is full of "Rs.", "(TER)", "1%" and "Nifty 500 TRI", so the failure would have been widespread and would have looked like poor retrieval rather than a tokeniser bug.

**Trade-off:** None. This was a defect.

---

## D029. Context-dependent facts are never reduced to a single value

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** Where an official source states a fact with conditions, the answer carries the conditions. For SIP minimums, the assistant gives the monthly figure with its instalment condition and states that other frequencies differ, rather than quoting one number.

**Why:** The Flexicap KIM gives six SIP minimums by frequency, each with an instalment-count condition. Monthly alone has two valid answers. Any single number is misleading, and this is exactly why three well-known third-party sites gave three different minimums during source research: each picked one branch and dropped the conditions.

This is the project's sharpest differentiator. A naive FAQ bot answers "Rs. 500" confidently and is wrong for most frequencies. The principle carries into the PRD, the system prompt, the evaluation set and the README limitations.

**Alternatives considered:** Store the most common value and footnote the rest, rejected because the footnote is what gets dropped when an answer is compressed to three sentences. Return the full table, rejected as unreadable inside a three-sentence limit.

**Trade-off:** Longer answers on conditional facts, and a follow-up turn for non-monthly frequencies.

---

## D030. Four verification states, not two

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** `ground_truth.csv` uses VERIFIED, CONDITIONAL, PENDING and CONFLICT rather than a verified/unverified binary. Only VERIFIED and CONDITIONAL are answerable, and CONDITIONAL answers must carry their condition.

**Why:** Collection produced facts that were none of verified-or-not. A partial exit-load structure read from a factsheet was real evidence and unusable. A KIM riskometer is genuine official evidence but is not the monthly disclosure that governs freshness. A binary forces both into "verified" or discards them, and both choices lose information the pipeline needs.

**Trade-off:** More states for the ingestion layer to respect. Cheap, and it directly prevents the two failure modes that produce confident wrong answers.

---

## D031. Version conflicts resolve by document specificity first, recency second

**Date:** August 2026
**Phase:** Workstream 2
**Decision:** When two official documents disagree, prefer the scheme-specific statutory document over a composite or generic one. Recency decides only when both documents carry actual publication dates and the specificity is equal.

**Why:** A real conflict surfaced. The generic common application form gave the Flexicap exit load as 0.50% within 30 days; the scheme-specific SID gave 0.10%. The SID wins, but not for the reason first proposed: the argument offered was that a search engine indexed it as published roughly nine months ago, and index recency is not a publication date. Neither document's own date was captured during collection.

The defensible ground is specificity. A composite application form covers many schemes and lags scheme-level changes; the SID is the statutory scheme-specific disclosure. That reasoning holds without knowing either date.

**Consequence:** `publication_date` is now mandatory in `sources.csv` for any document used to resolve a conflict. Leaving it blank is what made this call rest on the wrong evidence.

**Trade-off:** One more field to capture per document at collection time.

---

## D032. Verification state, not the prompt, controls answerability

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** The corpus builder reads `ground_truth.csv` and indexes only VERIFIED and CONDITIONAL rows. PENDING and CONFLICT rows are never indexed; they are registered as known gaps.

**Why:** A quarantined fact must be unreachable, not merely discouraged. If a partial exit-load structure reaches the model as context, no prompt instruction reliably stops it being used. Enforcing at index time means the failure is impossible rather than unlikely.

The distinction between a known gap and an unknown question is also worth keeping: both produce a no-evidence response, but a gap is deliberate, listed, and reportable.

**Trade-off:** The corpus shrinks as facts are quarantined. That is the intended direction: the system should be willing to answer less as research reveals more uncertainty.

---

## D033. Index-time vocabulary expansion

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** Each chunk is indexed with its topic's synonym list appended. The expansion is searchable but never sent to the model.

**Why:** Evaluation caught it. The corpus speaks in document language ("TER Regular plan: 2.06%", "Riskometer: Very High") while users speak plainly ("expense ratio", "how risky is it"). A lexical coverage gate cannot bridge that on its own, and three evaluation questions failed purely because the corpus used the official word. Expansion gives the gate the user's vocabulary without polluting the generation context.

**Trade-off:** The synonym list is now load-bearing for retrieval, not just classification, so a gap in it costs recall. Evaluation misses are the mechanism for finding those gaps.

---

## D034. Source hierarchy is a categorical sort key, not a score bonus

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** When a scheme is resolved, chunks carrying that scheme's own fact rank above general regulatory chunks sharing the topic, regardless of similarity. Implemented as a two-level sort key.

**Why:** "What is the expense ratio of SBI Flexicap Fund?" cited AMFI's definition of TER instead of SBI's actual figure. The answer text would have read plausibly while the citation pointed at a definition rather than the number, which is a citation-accuracy failure that a reader is unlikely to catch.

An additive boost was tried first and was the wrong shape: AMFI's longer chunk out-scored the terse SBI fact on raw BM25 even after the bonus. The documented hierarchy says tier 1 owns scheme facts, and that is a categorical claim, so the code should express it categorically.

**Trade-off:** A genuinely regulatory question asked while a scheme is selected demotes tier 2. Harmless in practice, because no scheme-specific chunk exists for those topics, so tier 2 still surfaces.

---

## D035. Eligibility is decided in exactly one place

**Date:** August 2026
**Phase:** Workstream 3
**Decision:** The numeric relevance floor is removed. The coverage gate is the sole eligibility test; the normalised score only orders the survivors.

**Why:** D025 already established this split, but a leftover score floor stayed in the code and quietly contradicted it. The correct TER chunk normalised to 0.11 against a floor of 0.12 and was discarded, so the system fell back to a weaker source. Two independent gates meant neither was fully responsible and the interaction between them was invisible.

**Trade-off:** None. Removing it took retrieval accuracy from 92% to 100% on the evaluation set with no regression in the no-evidence cases, since coverage was doing that work all along.

---

## D036. Retrieval happens in exactly one place

**Date:** August 2026
**Phase:** Workstream 4
**Decision:** The pipeline returns the evidence it used. The API never re-runs retrieval.

**Why:** Caught by the first API smoke test. The endpoint was re-searching with the raw request `scheme_id`, discarding the pipeline's alias resolution, topic detection and scheme-name stripping. "SBI Bluechip Fund exit load?" resolved correctly to Large Cap inside the pipeline, was then re-searched with no scheme, and came back with the ELSS fund's exit load and a genuine citation attached.

This is the R3 wrong-scheme failure in its most dangerous form: the answer is fluent, the citation is real, and nothing about the response looks wrong. The evaluation suite did not catch it because the harness calls the pipeline directly, so the bug lived only on the path a user would actually take.

**Alternatives considered:** Pass the resolved scheme into a second retrieval call, rejected because duplicated retrieval logic was the defect itself, not the parameters given to it.

**Trade-off:** The response object carries its evidence. Worth it, and it also removes a redundant search per request.

---

## D037. Amber means one thing

**Date:** August 2026
**Phase:** Workstream 4
**Decision:** The interface uses a single regulatory amber, reserved exclusively for a value past its staleness window. It appears nowhere else.

**Why:** Staleness is invisible by nature: a stale TER looks exactly like a current one, and its citation is real. If amber also signalled warnings, errors or emphasis, its meaning would dilute and the one case where it must be unmissable would stop registering. Refusals and PII warnings use a separate halt colour, so the two never compete.

**Trade-off:** A narrower palette. That is the point.

---

## D038. Three dates, never one

**Date:** August 2026
**Phase:** Workstream 4
**Decision:** Every fact carries `fact_as_of`, `source_dated` and `retrieved_at` as separate fields. The interface labels each distinctly and never calls a retrieval date "as of".

**Why:** The single `as_of_date` column conflated three different things, and the UI displayed all of them as "as of". For most facts that date was simply when we downloaded the document, so the interface was claiming currency it had not established. For a product whose entire proposition is that you can check whether a number is still true, that is the most damaging kind of quiet overstatement.

Only `fact_as_of` means the value itself is current, and it exists only where the source states it, which today is the TER page.

**Trade-off:** Most facts now show only a retrieval date, which looks weaker. It is weaker, and it is accurate.

---

## D039. The three-sentence limit is enforced in code

**Date:** August 2026
**Phase:** Workstream 4
**Decision:** Generated output passes through `cap_sentences()` before it reaches the response. Facts with many official conditions get a summary plus an explicit pointer to the rest.

**Why:** The limit is a stated requirement and the extractive path was emitting the full six-frequency SIP table as one block. Trusting a prompt instruction to hold a hard constraint is not enforcement, and the extractive path has no prompt at all.

The condition pointer matters as much as the cap. Truncating the SIP answer to fit would hide exactly the conditions D029 exists to preserve, so the summary names the monthly case and invites the rest.

**Bug found while building it:** naive sentence splitting treated "Rs. 1,000" as a boundary and truncated answers mid-figure. Nearly every answer in this corpus contains "Rs.", so this would have mangled most conditional responses. Abbreviations are now masked before splitting.

---

## D040. Citations show document titles, not internal ids

**Date:** August 2026
**Phase:** Workstream 4
**Decision:** The interface shows the organisation, a human document title and a labelled link. Internal ids such as `kim_flexicap` stay in the data layer.

**Why:** A citation exists so a person can decide whether to trust an answer and go check it. `kim_flexicap` communicates nothing to a retail user and reads like a leaked database key, which undermines trust rather than building it.

**Trade-off:** A title map to maintain per document. Small, and it is the field most visible to a reviewer.

---

## D041. LLM intent classification, after the guards and behind a closed enum

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** Groq classifies a question into one topic key, but only when the deterministic lookup finds nothing, only after the PII and advice guards have run, and only into a fixed enum that includes an explicit `none`.

**Why here rather than at generation:** the observed failures ("Flexicap se paisa jaldi nikalne pe charges lagenge?", "Can I put 500 rupees every month") were retrieval misses. The query never reached a chunk, so a better generator would have had nothing to write from. Improving the writing layer would not have fixed a single one of them.

**Why after the guards:** sending a message to a third-party API to determine its intent would defeat D008 entirely if that message contained a PAN. `tests/test_intent_safety.py` uses a spy classifier to assert that no blocked message ever reaches it, and separately that the classifier is reachable for safe queries so the assertion cannot pass by accident.

**Why a closed enum:** an unconstrained classifier will produce a confident, plausible topic for "who manages this fund", and that would quietly convert a correct refusal into a wrong answer. Refusal accuracy is at 100% and this change is the one most capable of breaking it. The enum is enforced in code rather than trusted to the prompt, and any reply outside it is discarded.

**Alternatives considered:** extending the synonym list indefinitely, which does not generalise across languages and grows unboundedly. Embedding similarity on the query, rejected because it cannot express "none" for the same structural reason a score threshold could not, per D025.

**Trade-off:** a network call on unmatched queries, and a dependency that can fail. Failure degrades to no-evidence rather than to a guess.

**Status:** unverified. Plumbed and unit-tested, not yet run against the live API or scored on the evaluation set.

---

## D042. Permission and recommendation are different questions

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** The advice guard splits grammatically. Permission and capability framing ("can I", "am I allowed", "is it possible", "does the scheme permit") is factual. Recommendation framing ("should I", "is it wise", "a good idea", "better", "suitable for me") is advice. A permission question with no detectable factual topic still refuses.

**Why:** The original pattern put `can` in the same alternation as `should`, so every feasibility question was refused. "Can I invest Rs. 500 monthly?", "Can I redeem after 3 years?", "Can I invest less than Rs. 5,000?" all returned an advice refusal while the answer sat verified in the ground truth. A facts-only product refusing to state facts is its worst possible failure and the one most likely to surface in a demo.

The proposed alternative was entity-based: look for an amount or frequency and route factual if present. That fixes the SIP cases and misses "Can I redeem after 3 years?", which carries no amount. The grammatical cut covers both, because it targets what the question is actually asking for rather than what it happens to mention.

**Consequence for ordering:** deterministic topic detection moved ahead of the advice guard so the guard can tell a permission question with a factual target from one without. It is local and makes no network call, so nothing leaves the process before the guards run. The LLM classifier still sits after both.

**Trade-off:** ambiguity still resolves to refusal, per D009. "Can I invest in this fund?" has no factual target and is refused.

---

## D043. Feasibility answering, without saying yes

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** When a question states an amount, the answer compares it against the documented minimum for that frequency. The response never opens with "Yes".

**Why:** Comparing a stated amount against a published minimum is a factual determination, and answering "Rs. 500 is permitted for a monthly SIP with at least 12 instalments" is disclosure. But a bare "Yes" at the front of a sentence about investing does work the sentence does not: it reads as approval of the decision rather than confirmation of the rule. Same information, no accidental endorsement.

**Trade-off:** Slightly stiffer phrasing in exchange for a boundary that survives being probed.

---

## D044. A known gap is not an unknown question

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** Facts quarantined in `ground_truth.csv` produce a distinct response naming the recognised scheme and listing what is available, rather than the generic no-evidence message.

**Why:** Asking for the Large Cap minimum SIP returned "I couldn't find this information in the official sources available to me." The system was behaving exactly as designed, since that fact is deliberately quarantined, and it communicated that as though it had failed. We already store four verification states per fact and the interface was discarding all of it.

This is the highest-leverage change in the release because it costs nothing in data and turns the corpus's smallness from a weakness into visible integrity: the system shows exactly where its knowledge ends.

**Trade-off:** One more response state. The coverage map that drives it is derived, not maintained separately.

---

## D045. Mixed questions get partial answers, not blanket refusal

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** A question containing both a factual and an advisory clause is split. Factual clauses are answered with citations; advisory clauses are declined in the same response.

**Why:** "What is the TER, and should I invest?" has a verified, cited answer sitting in the corpus and a question we must not answer. Refusing both withholds a fact we have. Answering both gives advice. Neither is right, and the blanket refusal is the more common failure because it is the safer-looking one.

**How the safety property survives:** a clause is answered only if it independently passes the advice guard AND resolves to a factual topic. The D009 asymmetry is untouched: splitting can never promote an advisory clause to answerable, it only stops an advisory clause from suppressing a separable factual one.

**Trade-off:** clause splitting is heuristic and will occasionally over-split. The failure mode is a narrower answer, not a wrong one.

---

## D046. Ambiguous scheme references offer options

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** A question naming only the fund house ("minimum SIP for SBI?") returns the schemes in scope as selectable options. A question naming no scheme at all still asks plainly.

**Why:** "Which scheme are you asking about?" is a dead end when we know the three candidates and could just show them. Distinguishing "you named something too broad, here are the options" from "you named nothing" costs one branch and removes a step.

**Trade-off:** one more response state.

---

## D047. Held-out cases are never tuned against

**Date:** August 2026
**Phase:** Workstream 5
**Decision:** `holdout_set.csv` is scored but never used to tune. A failure is fixed, promoted to `eval_set.csv` as a permanent regression test, and replaced with a new unseen case.

**Why:** The main suite reported 100% while a held-out run of the same system reported 70%. The gap is the measurement being wrong, not the system being good: 40 cases at 100% measures how well it handles cases it was built against. Without a set it has never seen, that number only ever goes up and stops meaning anything.

**Stated limitation, and it matters:** I wrote both the system and the held-out cases, so this is a weak proxy. It measures generalisation past exact tuned strings; it cannot measure what I failed to imagine. The genuinely independent evidence is the user's own adversarial session.

**Consequence:** three held-out failures are left open rather than fixed, because fixing them by adding the exact missing synonyms would be tuning against the set and would restore a fake 100%. They are all wrong refusals, which D009 classifies as annoyances rather than failures.

**Trade-off:** the project's headline accuracy number goes down. It is now worth something.
