# TR-011 DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched; entries resolve ambiguity toward the
interpretation that makes H1 harder to pass. The CREDO firewall applies:
nothing in this file cites product value.

## D1. The six series features, frozen with their numbers
Computed on each document's per-token entropy series (nats, full-vocab
softmax), per scoring model:
1. **mean**: mean entropy.
2. **variance**: entropy variance.
3. **acl**: autocorrelation length, the first lag where the entropy
   series' autocorrelation drops below 1/e.
4. **lowfreq**: fraction of periodogram power below 0.1 cycles/token.
5. **spike_rate**: fraction of tokens with entropy above the document's
   mean + 2 SD.
6. **boundary_delta**: mean entropy over the first 10 tokens after each
   paragraph break minus mean entropy of interior tokens.

Sequential features (the shuffle control's targets): acl and lowfreq.

## D2. Statistics, frozen
- **Paired Cliff's delta (corpus A)**: over pairs (published, draft) of
  the same work, delta = (#pairs published > draft minus #pairs
  published < draft) / n, per feature.
- **Sign agreement (corpus B)**: the same feature's group difference
  (published minus slush medians) must have the same sign as its
  corpus-A delta.
- **Classifier**: logistic regression on the six features (per scoring
  model), author-disjoint grouped CV, AUC pooled over held-out folds.
- All resampling and CV folds seeded; seeds recorded with results.

## D3. Determinism control read hardest
Duplicate documents under different filenames must produce
**byte-identical** entropy series and therefore exactly equal features.
Tolerance zero; scoring is deterministic, so "near" would only hide a
pipeline leak.

## D4. KILL operationalization
Sentence-length control: features are residualized against a frozen
length-statistics vector (mean, SD, and IQR of sentence token-lengths
per document) by ordinary least squares across documents; a length-only
baseline classifier is reported alongside. **KILL fires iff the PASS
conditions no longer hold after residualization** (fewer than two
qualifying features at |delta| >= 0.3 with corpus-B sign agreement, or
residualized AUC < 0.7). The entanglement result is then published per
the protocol.

## D5. The KILL machinery gets its own bite-proof (red-then-green)
The residualizer can fake either verdict: over-residualize and a real
signal disappears (false KILL); under-residualize and a length artifact
survives (false pass). Before any real data is analyzed, the
residualizer must pass two synthetic fixtures, seeded and committed:
- **planted pure-length corpus**: group difference injected only through
  sentence-length distribution; post-residualization |delta| must
  collapse below 0.1 on every feature.
- **planted orthogonal-entropy corpus**: a feature signal injected
  independently of length; post-residualization deltas must retain at
  least 80% of their pre-residualization magnitude.
The test exists from Phase 0 and fails red until the residualizer
exists and passes both; verify carries it as its own leg.

## D6. Cross-model agreement formula, frozen
Per-feature **Spearman rho across all scored documents (both corpora
pooled), between the two scoring models' feature values.** A feature
QUALIFIES for the PASS claim only if its rho >= 0.7; the protocol's
"cross-model agreement holds" means both PASS-claiming features
qualify. If qualification leaves fewer than two features meeting the
delta gates, the verdict is FAIL. This is the harder reading: agreement
is per-feature and gates eligibility, not a pooled average.

## D7. Memorization audit: measurement, threshold, and response, all frozen
Public-domain published text may sit in the scoring models' training
data; memorized text scores artificially low entropy and never-seen
slush scores high, a gradient that mimics H1's direction on corpus B
exactly. Frozen before any probe runs:
- **Probe**: per corpus-B document, 20 seeded 50-token prefixes;
  greedy-continue 20 tokens with each scoring model; per-prefix score =
  exact-token-match rate against the true continuation; document score
  = max over models of mean prefix score.
- **Individual threshold**: any document scoring > 0.5 is excluded and
  replaced from the committed backup list before analysis.
- **Group threshold**: if (published median minus slush median) > 0.05
  after exclusions, **corpus B is scoped out entirely**: its results
  are reported but cannot support a PASS (the B leg is invalid by this
  pre-registered rule), and corpus A is reported alone as the
  experiment's evidence, verdict stated accordingly. At or below 0.05,
  the audit table ships as a limitation paragraph.
- **Ordering, structural**: the analysis runner refuses to run unless
  results/memorization_audit.json already exists; the audit can never
  be run after a feature delta has been seen.
Corpus A is protected separately by publication-date check against the
scoring models' training cutoffs (recorded at corpus assembly).

## D8. Scoring configuration
Scoring models: the pinned, cached cross-family builds
mlx-community/Qwen3-1.7B-4bit and Meta-Llama-3.1-8B-Instruct-4bit
(snapshot commits recorded in MANIFEST at first legion run). Sliding
window 2048, stride 1024; entropy recorded only for tokens with at
least 1024 tokens of context; full-vocabulary softmax entropy in nats
plus per-token NLL. Cache keyed by config hash, invalidated wholesale
on any change (TR-001 D6 pattern). Sequential model residency; the
Clutch headroom rule carries over verbatim (85% line or any swap:
co-tenant pauses for the window).

## D9. Corpus assembly rules
Normalized-hash dedup within and across corpora; per-document scored
span capped at 8,000 tokens (Model B tokenizer of record: the Llama
build), spans committed; author-disjoint fold lists committed before
any scoring; corpus-B backup list (for D7 exclusions) committed at
assembly time; split seed 31. Corpus A pairing manifest (which draft
maps to which published span) committed with provenance.

## D10. Dependency pins
numpy==2.5.2, scipy==1.18.1, scikit-learn==1.9.0 now; the model stack
at the legion phase with versions recorded here. No unpinned installs
on the experiment path.

## D11. The data covenant
Committed 2026-08-31, BEFORE any draft file is read. The Epoch I draft
archive (private repo, archive/epoch1-draftwork/, provenance-sealed) is
one iteration of a living authorial process, not a dataset. Binding
terms:
- The archive is **read-only input, never a lab artifact**. Nothing in
  it is copied into the lab repo; the lab holds derived numbers only.
- The lab publishes **hashes and statistics only**: never text, never
  excerpts, never paraphrase.
- The report never characterizes draft content qualitatively. No "the
  early version was weaker," no describing what changed between
  versions, nothing a reader could turn into commentary on unfinished
  work. Numbers about entropy series, full stop.
- Scope is **TR-011 exactly**. Any future experiment that wants these
  files obtains a fresh word from the author, per experiment.
- The drafts are **seeds, not failures**. The December material is a
  book that may still become a book, and the lab's language never
  implies otherwise.
This covenant has the same standing as a frozen threshold: written
first, on the record, before anything can be tempted.

## D12. Draft-to-published pairing, constructed blind to the signal
The six-generation transformation makes "same text at two stages" only
loosely true, so the pairing rule is frozen before any alignment runs:
- **The frozen gate pairing**: earliest-substantial draft generation
  versus published text, at matched spans, per D9.
- **Blindness, structural**: whatever aligns draft spans to published
  sections (embedding similarity with a fixed threshold, or a
  documented manual mapping) must never touch the scoring models or
  any entropy feature. The alignment code lives outside the feature
  pipeline, in its own module, and runs before any scoring exists to
  leak. Pairs selected by the signal would make the gate measure its
  own selection.
- **No-ancestor exclusion**: published sections with no identifiable
  draft ancestor stay out of the paired test entirely, whatever that
  costs in n. The pairing manifest records every inclusion, exclusion,
  and the alignment scores behind them.

## D13. The generational trend is exploratory, fenced off from the gate
V1 through V6 permit a within-author monotonicity check (do features
trend across successive versions of the same work?). Pre-registered as
**exploratory only**: reported in its own section, never promotable
into evidence for a PASS, never borrowed to rescue a miss. The frozen
gate reads only the D12 pairing.

## D14. Corpus B composition realities, logged before assembly
- **Slush is single-author** (the author's Epoch II drafts): the only
  $0, license-clean, topic-controllable unpublished prose available.
  Consequence, named now: the corpus-B classifier's author-disjoint
  splits are one-sided (published side spans ~20 authors; slush side
  one), so corpus-B AUC could partly reflect author identity rather
  than published-ness. The paired corpus A (same author on both sides)
  carries the design's main protection; corpus B serves the
  sign-agreement check and its AUC ships with this limitation stated.
- **Published side is canonical public-domain fiction** (25 distinct
  authors, 20 primary + 5 backup, Gutenberg IDs committed in the
  manifest). Canonical works maximize the memorization risk the D7
  audit exists to arbitrate; the audit's pre-registered response
  ladder, not selection cleverness, decides whether corpus B survives.
  Mid-book spans, headers stripped, 8,000-token cap per D9.
- **Slush documents** are drawn from Epoch II manuscript chapters
  (distinct book from corpus A, so cross-corpus disjointness is
  structural), covered by the D11 covenant identically: hashes and
  statistics only, no text, no qualitative characterization.

