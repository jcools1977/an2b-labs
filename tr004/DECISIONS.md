# TR-004 DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched; ambiguity resolves toward the reading
that makes H1 harder to pass. The CREDO firewall applies.

## D1. Oracle sealed at kickoff
The oracle prediction was sealed 2026-09-01 before Phase 0 closed and
before any implementation code existed: sha256
4b6776a843668d132b2d44d08c24a9ff21d8a453b65f5a2adc99aac332bd2d61,
committed at 10b718f, plaintext held out of the repository until
closeout. Zero oracle tool uses, verified. The transit limitation and
its mitigation are in oracle/sealed/TR004.SEAL.md.

## D2. Corpus and instance rules
Primary source VUAMC (MIPVU annotations); fallback TroFi, with the
choice and reason logged here at acquisition time. An instance is a
target token with a literal or metaphor-related label in context. A
lemma enters the paired set only with >= 10 instances on EACH side;
exclusions are counted in the manifest. Minimum 20 surviving lemmas
for the paired statistics to run at all; fewer stops the experiment
for PI adjudication rather than proceeding underpowered.

## D3. Embeddings, frozen before extraction
Model 1 (gated): Llama-3.1-8B-Instruct 4-bit, pinned snapshot
241a666d (the TR-011 pin), hidden state of the target token at layer
16 of 32, a single pre-registered mid-depth choice, no layer
shopping. Model 2 (the KILL comparator): bge-small-en-v1.5
final-layer token embedding of the target token, pre-pooling. Both
UNNORMALIZED: L2 normalization projects onto a sphere and alters the
very geometry under measurement. Multi-token lemmas use the first
subtoken, decided now, before any number.

## D4. Neighborhoods and estimator parameters
Per lemma: the literal cloud is all its literal instance vectors, the
metaphorical cloud all its metaphor-related instance vectors. LID per
cloud: Two-NN (Facco, standard 10% tail discard) and Levina-Bickel
MLE (k = min(10, n-2), averaged over points). Curvature proxies per
cloud: geodesic-vs-chordal distance ratio on a k-NN graph
(k = min(8, n-1)) and PCA residual spectrum decay rate. Curvature
proxies are REPORTED per protocol metrics; the frozen PASS gate
names only the LID estimators, so curvature never gates.

## D5. Estimator certification exam (red until built)
Committed at Phase 0, before the estimators exist:
- On synthetic uniform d-balls embedded in 384 dims at n = 500,
  both estimators must recover d in {2, 5, 10} within 20%.
- At n = 40 (our cloud scale), both must preserve ORDER: the d=2
  cloud must read lower than the d=10 cloud.
- The two estimators must agree in direction on a d=5 vs d=9 pair.
- The geodesic-chordal proxy must separate a 2-sphere from a flat
  2-disk of matched n, and read near-flat (ratio within 5% of 1.0)
  on the disk.
An estimator that cannot pass its exam never touches real data.

## D6. The paired statistic
Each surviving lemma contributes one paired observation per
estimator: LID(metaphorical cloud) minus LID(literal cloud). Cliff's
delta is computed over the paired per-lemma values against zero;
bootstrap over lemmas, 10,000 resamples. The PASS gate reads BOTH
estimators at delta >= 0.2 with CI excluding zero (the harder
reading of "both agree on direction, Cliff's delta >= 0.2").
Replication: the full pipeline runs at bootstrap seeds 41 and 43 and
the gate must hold at both.

## D7. Frequency and length controls
The certified-residualizer pattern with its own bite-proof exam:
per-lemma paired differences are residualized by OLS on log lemma
frequency and the fig-minus-lit mean sentence length difference.
"Survives" reads hardest: the residualized delta must itself meet
delta >= 0.2 with CI excluding zero, per estimator.

## D8. KILL operationalization
Present = gate-level effect (delta >= 0.2, CI excluding zero, either
estimator). Absent = CI includes zero OR direction reversed. KILL
fires iff model 1 is present and model 2 is absent. The middle zone
(model 2 CI excludes zero but delta < 0.2) is not absence; it
contributes to FAIL or PASS through the gates, not to KILL.

## D9. Controls operationalized
1. Label shuffle: within-lemma permutation of instance labels
   (seed 41), full recompute; the shuffled delta's CI must include
   zero.
2. Synonym control: each lemma's literal cloud paired with a
   frequency-matched DIFFERENT lemma's literal cloud (matching rule:
   nearest log-frequency neighbor, no reuse); the control delta must
   have CI including zero AND |point| < 0.1.
3. Random subspace: random orthogonal projections to ranks 32 and
   64 (seed 47); the projected delta must not exceed the original
   by more than 0.05 at any rank. The checker consumes EVERY rank
   and stratum it is given (the TR-015 D21 lesson, built in from
   birth).

## D10. Seeds and pins
Bootstrap seeds 41 and 43; shuffle seed 41; projection seed 47.
Dependencies pinned in requirements.txt (numpy 2.5.2, scipy 1.18.1,
scikit-learn 1.9.0). Extraction runs on legion in the recorded
environments; estimation runs on cockpit in the pinned venv.

## D11. Noise condition in the estimator exam (reviewer rider 1)
Added before the exam turns green. Clean synthetic manifolds certify
estimators for a world hidden states do not live in, so the exam
gains: isotropic ambient Gaussian noise at total noise variance equal
to 20% of signal variance (SNR 5:1, frozen now), under which both
estimators must remain ORDER-PRESERVING at n=40 (noisy d=2 reads
below noisy d=10), and the curvature proxy must still separate the
noisy sphere from the noisy disk with the disk within its 5%
flatness tolerance. If the estimators cannot pass the noisy exam,
the experiment learns it before its data does.

## D12. Rogue-dimension control (reviewer rider 2), pre-registered
Transformer hidden states are anisotropic: a few dimensions carry
outsized norm and can dominate unnormalized geometry. Control 4: the
key readings are recomputed with the top-k highest-variance
dimensions removed, k frozen at 3 and 10. A real effect must survive
both removals at gate level (delta >= 0.2, CI excluding zero per
D6); an effect that dies with its rogue dimensions was a
counterfeiting artifact, the geometric cousin of TR-015's topic
residualization. The checker consumes every k; absence of the block
is a violation. Registered before any hidden state is extracted.

## D13. Layer robustness, fenced (reviewer addition)
Layers 8 and 24 are pre-registered as SECONDARY reads in the
exploratory shape: extracted and reported beside the gated layer-16
numbers, never promotable into any gate, never borrowable if layer
16 misses. Purpose: pre-empt "it's a layer-16 artifact" with the
frame built in advance. Cross-depth replication or its absence is
reported either way.

## D14. The noisy exam caught two instruments; STOP surfaced
2026-09-01, logged at the moment of the red, before any real data
exists. With the proper Facco cumulative fit, both estimators pass
every clean condition (within 20% at n=500, order at n=40, direction
agreement). Under the D11 noise condition three legs fail for
measured, mechanistic reasons:
- TwoNN inverts order at n=40 under noise (d=2 reads 12.21 vs d=10
  at 10.42): it reads at the first-neighbor scale, and at SNR 5:1 in
  384 ambient dims the noise displacement (~0.32) matches the d=2
  cloud's neighbor spacing, so the tighter cloud is MORE
  noise-dominated. Levina-Bickel, integrating over k=10 neighbors,
  preserves order under the same noise (4.81 < 11.17).
- The geodesic-chordal proxy reads 1.096 on a CLEAN flat disk
  against the 5% tolerance I froze in D5: k-NN-graph geodesics carry
  a known zigzag inflation at k=8; the tolerance was set wrong for
  the instrument, not the instrument wrong for the tolerance.
- Under noise the proxy saturates (both readings ~2.5) and its
  sphere/disk order inverts, the same noise-halo mechanism.
Per BB4C rule 1 and D11's own language, this stops estimator
certification pending adjudication. No amendment is proposed from
this seat beyond stating the options; TwoNN and the proxy touch no
real data while red. MLE alone passed every leg including noise.
Corpus acquisition (which passes through no estimator) proceeds
under the standing stamp.

## D15. VUAMC acquired; instance rules frozen at acquisition
Downloaded from the Oxford Text Archive (TEI XML, 16M, 16,202
sentences), before any instance is extracted:
- METAPHORICAL instance: a word inside seg function="mrw" type="met"
  with NO subtype. The hedged categories (WIDLII, personification
  "PP", "double") are excluded from BOTH sides and counted; the
  cleanest metaphor set is the harder test.
- LITERAL instance: a word inside no mrw segment at all.
- POS restriction: lexical verbs (VV*), nouns (NN*), adjectives
  (AJ*) only, matching the protocol's per-POS breakdown; be/have/
  modals are function words and never instances.
- Lemma survival: >= 10 instances per side (D2). Cloud balancing:
  each side subsampled (seed 41) to n = min(n_lit, n_met, 60), so
  the paired clouds always have EQUAL n; LID estimators are
  n-sensitive and unequal clouds would bias the paired difference.
- Per instance: sentence text, target token index, sentence length;
  per lemma: corpus frequency. Dedup on (sentence, position).

## D16. Extraction operationalization, before any hidden state exists
- Target-token alignment, Llama: the sentence is the whitespace join
  of its VUAMC tokens; the target's first subtoken index is the
  length of the tokenization of the preceding prefix (BPE space
  boundary alignment). For bge: fast-tokenizer character offsets
  against the target's character start.
- Layers captured in ONE pass: 8, 16, 24 (gated: 16; fenced: 8 and
  24 per D13), post-block residual stream, no norm applied.
- Storage float16 (geometry unaffected at this precision), cast up
  to float64 in analysis; hashes in committed sidecars.
- Runs on legion: Llama via mlx (pinned snapshot 241a666d), bge via
  the recorded tr020 wild environment.

## D17. The residualizer's identifiability commitment, logged mid-red
The D7 bite-proof caught the intercept trap as designed (a full-OLS
subtraction eats the effect), then its confound leg exposed a second,
real question: which part of the MEAN paired difference is removable
is a modeling commitment, not a discoverable fact. Committed now:
- Covariates with a meaningful zero (the fig-minus-lit sentence
  length difference, where zero means no length asymmetry) enter
  UNCENTERED: their slope times their full value, mean included, is
  confound and is removed.
- Covariates with no meaningful zero (log lemma frequency, a
  lemma-level moderator shared by both sides of the pair) enter
  CENTERED: only their covariation is removable; extrapolating to
  frequency zero would eat true effect through the back door.
The exam is corrected to encode this commitment (confound routed
through the meaningful-zero covariate must collapse; a residual
correlation bound applies to the centered covariate; a true constant
effect must survive). This is an exam change after a red, stated
plainly, surfaced with D14 for the reviewer.
D17 addendum: the exam's confound leg first read delta -0.090 at
N=200 against the 0.05 tolerance; Cliff's delta of pure noise at
N=200 has sampling SD ~0.07, so the exam demanded more precision
than its sample could carry. N raised to 2000 (tolerance UNCHANGED);
a systematic bias would stay red, sampling noise shrinks.

## D18. The D14 ruling, witnessed and ratified; operationalized here
Relayed by the PI 2026-09-02: TwoNN decertified for this regime with
substitution-by-exam; the proxy's delta leg added; the D11 noise
operationalization untouched. Logged per the PI's word, with this
seat's operationalizations stated for correction if misread:
- Substitute candidate: the participation ratio (PR, spectral linear
  dimension, (sum lambda)^2 / sum lambda^2 of the cloud covariance),
  mechanistically independent of Levina-Bickel's kNN likelihood. It
  enters ONLY by passing the frozen D5+D11 exam in TwoNN's slot,
  every leg including noise. TwoNN remains in the codebase,
  decertified, touching no real data.
- Proxy delta leg: certification by SEPARATION, sphere ratio minus
  disk ratio >= 0.05, clean and noisy; the absolute 5%-of-1.0
  flatness leg is dropped as mis-set (D14). Disclosed: the clean
  observed values (1.201 vs 1.096) were known when the 0.05 margin
  was chosen; the proxy is reported-only (D4) and never gates, so
  the margin certifies an instrument, not a verdict. If the noisy
  delta leg fails, the proxy is scoped CLEAN-ONLY: the exam prints
  the scope, the report carries it, and only a clean-leg failure
  reds the exam's exit.
- Strictness carried into the frozen controls checker's single-value
  slots: random-subspace uses orig_delta = the WEAKER estimator's
  delta with every estimator-rank projection reported against it;
  rogue-dimension entries carry, per k, the weaker estimator's delta
  and CI. Both choices only make violations easier to trigger.
