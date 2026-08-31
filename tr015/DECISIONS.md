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
