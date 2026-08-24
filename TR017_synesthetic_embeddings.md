# TR-017: Synesthetic Embeddings
**Track D: Art, Voice, and Perception** | Status: Protocol draft v0.1

## Question
If text embeddings are mapped deterministically to sound, can human listeners distinguish semantically coherent documents from incoherent ones by ear alone, without reading a word?

## Hypothesis
**H1:** Listeners discriminate coherent vs incoherent documents from sonified embedding trajectories at >= 70% accuracy (chance 50%), above-chance within the first 15 seconds, with the effect holding for listeners given no training beyond two labeled examples.
**H0:** Sonified semantic structure is not perceptually accessible; discrimination sits at chance and the instrument is decoration.

## Background
Embedding trajectories of coherent text move through semantic space with characteristic continuity: small steps within topics, occasional larger transitions. Incoherent text (shuffled sentences, interleaved documents) produces jagged trajectories. Human audition is exquisitely tuned to continuity, rhythm, and anomaly in streams. If the mapping preserves trajectory structure in audible dimensions, the ear becomes a semantic instrument, and every document gains a sound. This is the program's purest art-science hybrid, and the demo is itself the disclosure.

## Design
- **Sonification mapping (fixed before listening tests):** per-sentence embedding reduced to 4 dims (PCA fit on a reference corpus); dims map to pitch (pentatonic quantized), timbre brightness, stereo pan, and note density; inter-sentence cosine distance maps to loudness of a transition marker; rendered via Tone.js, ~1.5 sec per sentence
- **Stimuli:** 40 document pairs; coherent member = intact 25-sentence passage; incoherent member = same sentences shuffled, or two documents interleaved (both incoherence types, balanced)
- **Listeners:** n >= 20 (online panel plus local volunteers), two labeled training examples, then 2AFC: "which of these two clips is the intact document"
- **Timing arm:** response allowed at any point; log decision time
- **Machine ceiling:** a simple classifier on the same 4-dim trajectories establishes how much signal the mapping preserves

## Metrics
- 2AFC accuracy overall, by incoherence type, and by decision-time bucket
- Machine-ceiling accuracy (if the classifier fails, the mapping, not the ear, is the bottleneck)
- Per-listener distribution (is it a general ability or a few golden ears)

## Pass/Fail (frozen before data)
- **PASS:** group 2AFC accuracy >= 70% with CI excluding 50%, at least one incoherence type >= 75%, and machine ceiling >= 85% (mapping verified to carry signal).
- **FAIL:** accuracy CI includes chance, or only golden ears (median listener at chance).
- **KILL:** machine ceiling < 85%: the mapping loses the structure, so no claim about human perception is licensed; redesign mapping before any listener claim.

## Negative Controls
1. **Sonified white noise pairs:** listeners judging two random-trajectory clips must sit at chance (no response-bias artifact).
2. **Loudness-stripped variant:** removing the transition-marker channel must reduce accuracy (identifies which channel carries the effect, and guards against a single trivial cue masquerading as "semantic hearing", reported either way).
3. **Deterministic render check:** identical documents must produce byte-identical audio (pipeline determinism).

## Cost and Time
Small panel cost (~$100-200) is the program's only cash expense. Est. 3 sessions.

## Deliverables
- `tr017/` repo plus a public web demo (paste text, hear it); listener results; 5-7 page report. The demo doubles as AN2B Labs' most shareable artifact.

## Dependencies
None.
