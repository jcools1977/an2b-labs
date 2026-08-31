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

## D15. The author-identity shortcut, closed as a control, not a limitation
Single-author slush lets the corpus-B classifier learn "is this the
author" and score beautifully while detecting nothing about polish.
Two structural fixes, frozen before the classifier exists:
1. **Epoch I's published sections join corpus B's published side**, so
   the author's voice appears in both classes and author identity
   stops being a class separator. (These documents already carry the
   D7 cutoff protection; they are excluded from author-disjoint fold
   leakage by grouping all DeVere documents into one fold group.)
2. **Author-identity control classifier**: the identical feature
   pipeline trained on DeVere-published versus Gutenberg-published
   (two classes of PUBLISHED text, differing only in author). Its AUC
   measures how much any slush-versus-published score could be style
   rather than polish. **Scoping rule, written today: if the
   author-control AUC >= 0.7, corpus B is scoped out of PASS support**
   (mirroring the D7 response ladder), its numbers reported with the
   control's, and corpus A stands alone as the experiment's evidence.
check_pass enforces the consistency: a corpus_b_valid claim beside an
author-control AUC >= 0.7 is a contradiction, not a judgment call.

## D16. Alignment yield is reportable; relay stays on estate paths
- The pairing manifest's **yield table is a finding**: how many
  published sections found draft ancestors and how much lineage went
  unpaired are counts, publishable under the D11 covenant (numbers,
  never characterization), and they measure how far the book traveled
  between December and May.
- The corpus store relays to legion by **LAN copy over the tailnet
  only** (scp, estate machine to estate machine). No cloud hop, ever,
  for manuscript text. Same rule for any future movement of the store.

## D17. Assembly operationalizations, frozen before alignment runs
- **Document units**: published Epoch I units are contiguous runs of
  sections (book order) concatenated to >= 1,500 words; the Light
  Papers text is chunked the same way at paragraph boundaries. Draft
  units are individual chapter files. Corpus-B units: Gutenberg
  mid-book spans and Epoch II chapters, all capped at 8,000 tokens of
  the Llama tokenizer of record (D9).
- **Earliest-substantial generation (D12)**: generations are the draft
  archive's version folders in lineage order (V1..V6, then the dated
  2025 folders); the gate generation is the EARLIEST whose extracted
  text totals >= 10,000 words.
- **Alignment (D12, blind)**: bge-small embeddings (the estate's
  utility embedder, never a scoring model), 400-token chunks
  mean-pooled per unit; candidate pair score = cosine; **threshold
  0.60, frozen**; greedy one-to-one matching by descending similarity
  (each published unit matched at most once). Units below threshold on
  either side are excluded per D12. Yield table reported per D16.
- **Corpus-B composition (D15)**: 20 primary Gutenberg + 5 backups;
  DeVere-published units (the corpus-A published units) join the
  published class; 20 primary slush chapters drawn by seed-31 shuffle
  of the 33, remainder as backups.
- **D7 refinement, stricter where the risk lives**: the group
  memorization gap is computed on the GUTENBERG subset versus slush
  (the confounded population); DeVere-published scores are reported
  separately and expected near zero (May 2025 post-dates both
  cutoffs). Environment note: alignment and tokenization run in the
  recorded tr020 wild environment on legion (freeze committed as
  tr020/wild-freeze.txt); scoring models and their pins are recorded
  in tr011/MANIFEST.json at first model run.

## D18. The n=4 reading, pre-registered before any delta exists
The alignment yield reshaped corpus A: thirteen of seventeen published
units have no December ancestor, so the December manuscript is a
predecessor the published book grew out of, and the paired test rests
on the four surviving lineage pairs. Frozen readings, written before
scoring:
- A paired sign-level test on n=4 has sixteen configurations; its
  smallest attainable p is 1/16. The gate stays effect-size-only as
  frozen (|Cliff's delta| >= 0.3; nobody adds a significance criterion
  now), and **the corpus-A paired result is reported as a
  demonstration on the surviving lineage, not an inference**, with n=4
  stated in the same sentence as any delta. The inferential weight of
  a PASS rests on corpus B (real n: 20 Gutenberg + 17 DeVere-published
  + 20 slush) through the sign-match clause and the AUC gate.
- The spring 2025 draft folders likely pair at higher yield against
  the published form; any later-generation pairing lives inside D13's
  exploratory fence: reportable as the lineage's second half, never
  promotable into the gate.
- Shuffle-control operationalization: sentences split on terminal
  punctuation followed by whitespace, seeded Fisher-Yates per document
  id, rejoined with single spaces (bag of words preserved exactly;
  sequence destroyed).
- Limitation, written in advance: the D7 probe measures verbatim
  recall and can underestimate SOFT memorization (lowered NLL without
  reproduced continuations). The cross-model agreement gate and the
  author-identity control are partial guards against that residual,
  and the report says so rather than discovering it in review.

## D19. Aggregation and control operationalizations, frozen before features
Committed while scoring runs and before any feature value exists:
- **Consensus thermometer**: for gate deltas, sign agreement, the
  classifier, and the KILL analysis, a document's feature value is the
  MEAN of the two scoring models' values. The D6 qualification rho is
  still computed per-feature BETWEEN models across documents;
  consensus never substitutes for agreement.
- **Corpus-B classifier**: logistic regression on the six consensus
  features, author-grouped 5-fold CV (manifest folds, seed 31), AUC
  pooled over held-out folds.
- **Author-identity control (D15)**: same features and classifier,
  DeVere-published versus Gutenberg-published, with STRATIFIED
  document-level 5-fold CV (seed 31), because author identity is the
  measurand there; author-grouped folds would delete the signal being
  measured.
- **Topic control operationalization**: topic labels are k-means (k=4,
  seed 31) clusters over bge document embeddings (semantic, computed
  blind to entropy); a logistic probe then predicts those labels from
  the entropy features under 5-fold CV. Chance = the majority-cluster
  share; the 95% bootstrap CI of probe accuracy must include chance.
- **Duplicates control**: exact array equality of the cached entropy
  series between each duplicate and its source, both models (D3).
- **Shuffle control**: paired Cliff's delta between each document and
  its shuffled twin on the consensus sequential features (acl,
  lowfreq), across all documents.
- **KILL evaluation**: consensus features residualized by the
  D5-certified residualizer against sentence-length stats (mean, SD,
  IQR of sentence token counts per document); gate re-read per D4.

