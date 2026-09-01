# TR-015 DECISIONS

Every judgment call, logged before the numbers it could bend toward.
Protocol thresholds untouched; ambiguity resolves toward the reading
that makes H1 harder to pass. The CREDO firewall applies.

## D1. The fresh consent, verbatim
Granted by the PI, 2026-08-31, per TR-011's D11 covenant requiring a
new word per experiment: "TR-015 may read the Epoch archive under the
same covenant terms: hashes and statistics only, drafts as seeds,
fresh consent again for whatever comes after." All TR-011 D11 terms
bind here identically: read-only input, no text or paraphrase ever
published, no qualitative characterization of draft content, and the
lab's language never implies a draft is a failure. Scope: TR-015
exactly.

## D2. Embedder
BAAI/bge-small-en-v1.5, chunks embedded as 400-token windows
mean-pooled (the TR-011 precedent). A second embedder
(intfloat/e5-small-v2) runs as a NON-GATED replication, reported and
never promotable into any gate.

## D3. Held-out read hardest: by work, never by chunk
Attribution is evaluated only on chunks from works absent from
training; every author contributes at least two works; splits are by
work, seeded. Same-work chunks in train and test would hand topic a
free ride, and the voice claim is generalization across works.

## D4. Chunking
Non-overlapping chunks at 500 and 1,500 words; both sizes gated
(accuracy and drift-direction consistency must hold at both).

## D5. Topic residualization
Seeded LDA (k=20, seed 37, scikit-learn) over content-word counts
(function words removed), one document per chunk; the topic-probability
factors are regressed out of the embeddings by OLS with intercept
(the certified-residualizer pattern).

## D6. The residualizer's bite-proof (red until built)
Synthetic exam, seeded and committed at Phase 0:
- planted topic-only class signal (injected through the topic factors):
  post-residualization attribution must fall within 5 points of chance;
- planted orthogonal voice-like signal: post-residualization
  attribution must retain at least 80% of its pre-residualization
  margin over chance.
The exam fails red until analysis/residualize exists and passes both;
verify carries it as its own leg.

## D7. Burrows Delta baseline
A frozen standard function-word list (~150 words, committed at Phase 1
before any accuracy exists), per-chunk relative frequencies, z-scored
across the corpus, Delta = mean absolute z-difference, nearest author
centroid, evaluated on the same held-out-works splits.

## D8. Paraphrase KILL, quantified
100 seeded chunks across at least 6 authors, rewritten
content-preserving by the pinned Llama-3.1-8B (snapshot 241a666d)
under TR-011's D14 bounds (length ratio [0.5, 2.0], content-word
Jaccard >= 0.3, regenerate-once-then-invalid, all bounds logged).
KILL iff paraphrased chunks' true-author attribution in the voice
subspace falls below 2x chance (chance = 1 / n_authors).

## D9. Controls operationalized
1. Shuffled authorship labels: attribution accuracy's 95% bootstrap CI
   must include chance.
2. Topic-only classifier (on the LDA factors alone): its accuracy is
   the measured leak, reported beside the residualized accuracy; if
   residualized rank<=10 accuracy misses the gate while topic-only
   approaches full-dimensional accuracy, the FAIL reads "voice was
   topic," per the protocol's own language.
3. Translation stress: reported, never gated; operationalization fixed
   at corpus assembly against what the public domain actually holds,
   and logged here then.

## D10. Drift measurement
Author-work centroids in the final voice subspace (the smallest rank
<= 10 that clears the accuracy gate; rank 10 otherwise); drift = mean
distance between consecutive works' centroids in publication order;
ratio = drift / mean pairwise between-author centroid distance.
Per-author satisfaction = ratio < 0.5 AND drift-direction cosine
between the two chunk sizes > 0. Gate: >= 80% of authors satisfy both.
Bootstrap over chunks, 10,000 resamples.

## D11. The translator confound, excluded at the door
Translated authors are excluded from the attribution set: a translated
"voice" is the translator's. Translations appear only inside control 3.

## D12. Case-study scope
The Epoch I -> Epoch II trajectory is drawn on the voice manifold as
coordinates and distances only. Draft-versus-published polish is
entangled with time along that path, so the case study makes no craft
claims, and the covenant governs every word about it.

## D13. Seeds and pins
Work-split seed 41; LDA seed 37; bootstrap seed 41 (10,000 resamples);
paraphrase sampling seed 41. Dependencies pinned as committed
(numpy 2.5.2, scipy 1.18.1, scikit-learn 1.9.0, python-docx 1.2.0,
pypdf 6.16.2); the embedding and paraphrase stacks run in the recorded
legion environments, versions already committed in this repository.

## D14. Which legs support inference, pre-registered before any embedding
TR-011's n=3 lesson applied in advance. Cross-book generalization (D3)
requires at least two works per author, so:
- **The Gutenberg attribution set carries the inferential weight**: 12+
  authors with 2-3 works each give the accuracy and drift gates real n.
- **The author's own leg is thin by construction**: one published book
  plus one book in draft. Wherever cross-book folds for that voice are
  under-powered, its numbers are reported as a DEMONSTRATION, stated in
  the same sentence as the number, never pooled into the gates. The
  longitudinal trajectory (D12) was already coordinates-only; this
  entry extends the same honesty to any attribution number touching it.
- The gate population is the Gutenberg set exactly; the Epoch material
  appears in the manifold and the case study, not in the PASS
  arithmetic. Written today, while no embedding exists.


## D15. The frozen word list is high-frequency, not purely functional
The D7 list (150 words, committed in `data/function_words.txt` and in
the builder before any accuracy existed) draws from a standard
high-frequency English list and therefore contains common content
nouns (house, world, mother, school) alongside true function words.
Noticed AFTER the baseline accuracies ran. The list stays frozen: D7
forbids editing it once accuracies exist, and the imperfection points
the conservative way, because content words leak topic into the
baseline, making Burrows stronger, and Burrows-wins is a FAIL clause
for the latent instrument. The label "function-word list" in prose is
hereby corrected to "frozen high-frequency word list" wherever the
report describes it.

## D16. e5 replication prefix
intfloat/e5-small-v2 requires an instruction prefix per its model
card; chunks are embedded with "passage: " uniformly. bge-small runs
bare, per the TR-011 precedent. Decided before any embedding exists.
Both models embed 400-token windows mean-pooled and L2-normalized per
D2; the pooling asymmetry with each model's native protocol (bge
prefers CLS) is accepted because D2 froze mean pooling and both arms
use the identical procedure.

## D17. One split to rule every instrument
`analysis/split.py` computes the held-out-by-works assignment once
(seed 41, gate population only, per-author choice of held-out work)
and every instrument (Burrows baseline, raw embeddings, residualized
embeddings, subspace projections) consumes the same assignment, so no
instrument can shop for a friendlier split. The chunk registry stamps
`gate_population` per chunk; devere and translation-control works are
structurally excluded from train and test at the registry level, not
by convention.

## D18. KILL-path operationalization, before any paraphrase exists
Three calls, each read hardest:
- Chunk size 500 for the paraphrase sample: the size where attribution
  is weakest, so the KILL is most likely to fire.
- The 100 chunks are drawn (seed 41) from held-out TEST works only;
  paraphrases of training text would flatter the subspace.
- Paraphrase residualization: paraphrase rows are concatenated with
  the corpus matrix and passed through the one certified residualize()
  so no uncertified code touches the KILL path; the 100 rows' effect
  on the fitted coefficients is negligible against 1,920 and applies
  identically to every author.
Also fixed here: the gate files (analysis.json, controls.json) are
written by the bge arm only; e5 writes its own detail file and can
never overwrite a gate input (D2's non-promotable clause, enforced in
code).

## D19. Control 1 feeds the checker its strictest size
Logged AFTER the first cold read, stated plainly: the analysis runner
initially handed the label-shuffle gate the CI from the worst-PASS-
margin size (1500), which on the real data was the friendlier control;
the 500-word CI [0.077, 0.125] excludes chance 0.071. The read-hardest
rule cuts against the instrument here, so the gate now consumes
whichever size's CI sits farthest from chance, and both CIs are
reported beside it. No threshold, formula, or seed changed; only which
pre-computed number reaches the frozen checker. The permutation itself
is a single seed-41 shuffle of training labels with a 10,000-resample
bootstrap over test chunks (the D9 letter); chunks cluster by work, so
this CI understates permutation variance, which is reported as a
limitation rather than repaired post hoc. The mid-run choice is
surfaced to the PI and reviewer per BB4C rule 1.

## D20. Closeout disk line (standing estate-hygiene rule)
TR-015 leaves: cockpit tr015/corpus_store 79M (raw Gutenberg cache,
chunks, embeddings 12M, paraphrases); legion tr015/corpus_store 40M
(chunks, embeddings, paraphrases); embedder snapshots in legion's HF
cache measured at ~1M each as cached (bge-small, e5-small-v2); the
8B paraphraser reused TR-011's pinned snapshot already on legion.
Sweepable on the PI's word: both corpus_store trees are rebuildable
from the committed builder plus TR-011's covenant store; nothing here
is unique. Transient logs (embed.log, paraphrase.log, topics.log)
are sweepable without ceremony.

## D21. D19 ratified by the reviewer, with the asymmetry written in
Adjudicated 2026-09-01: the control-1 red stands as a disclosed
caveat and cannot rescue or threaten the verdict, by direction of
mechanism. A label-shuffle reading above chance in a chunk-level
design means structure survived label destruction (near-neighbor
chunks of the same work); leakage of that kind can only INFLATE
true-label accuracy, never deflate it. The measured accuracies
(0.648, 0.422, 0.054) are therefore, if anything, slight
overestimates, and the FAIL is more secure than the numbers say. Same
structural move as TR-020's placebo asymmetry: a one-directional
control failure cannot manufacture the opposite verdict.
Two conditions attached and executed in this session:
1. Structural closure: the control checker now consumes every chunk
   size and passes only if all pass, so "which size" is never a
   choice again. Hardened red-then-green with a violating fixture.
2. Supplementary diagnostic, replacing nothing: the shuffle rerun at
   the WORK level (labels permuted per work, chunks riding with
   their work). If the excess vanishes, the clustering mechanism is
   confirmed with evidence instead of "likely."
