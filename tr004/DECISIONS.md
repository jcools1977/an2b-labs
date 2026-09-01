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
