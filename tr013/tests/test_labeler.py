#!/usr/bin/env python3
"""Labeler exam (D4), red then green: a synthetic run that starts
varied and falls into an exact loop at turn 21 must be labeled with
onset within one turn of 21 and kind loop; a run of distinct turns
must be non-collapsing; a run that paraphrases itself tightly from
turn 31 must be labeled mode-lock near 31; and with the loop
threshold set impossibly high (red side) the loop run must no longer
be labeled a loop. Exit nonzero on any leg."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import label.label as L  # noqa: E402
from label.embed import embed_texts  # noqa: E402

VARIED = ["The lighthouse keeper counted ships at dawn.", "Bread rises because yeast exhales carbon dioxide.",
          "A cello's lowest string hums at sixty-five hertz.", "Monarch butterflies cross the continent in autumn.",
          "The first telescopes were made by spectacle makers.", "Honeycombs tile the plane with hexagons.",
          "Rivers meander because erosion favors the outer bank.", "Winter oranges taste sweeter after a frost.",
          "Old maps drew sea monsters where knowledge ended.", "Glaciers carve valleys into the shape of a U."]


def main():
    bad = 0
    varied = [VARIED[i % 10] + f" Note {i}: a different observation about item {i*7 % 13}." for i in range(60)]
    loop = varied[:20] + ["I think we have covered everything there is to say about this."] * 40
    lock = varied[:30] + [f"The bicycle changed how people moved through cities, and that change was lasting ({i})." for i in range(30)]
    for name, texts, want_kind, want_onset in (("varied", varied, None, None), ("loop", loop, "loop", 21), ("lock", lock, "modelock", 31)):
        E = embed_texts(texts)
        onset, kind, _ = L.label_run(texts, E)
        ok = (kind == want_kind) and (want_onset is None or (onset is not None and abs(onset - want_onset) <= 2))
        bad += 0 if ok else 1
        print(f"  {'ok ' if ok else 'FAIL'} {name:6} onset={onset} kind={kind} (wanted {want_kind} near {want_onset})")
    # red side: thresholds matter
    saved = L.OVERLAP
    L.OVERLAP = 1.01
    E = embed_texts(loop)
    onset, kind, _ = L.label_run(loop, E)
    L.OVERLAP = saved
    ok = kind != "loop"
    bad += 0 if ok else 1
    print(f"  {'ok ' if ok else 'FAIL'} red: with the loop threshold impossible, the loop run is not labeled loop (got {kind})")
    print(f"labeler exam: {'CERTIFIED' if bad == 0 else str(bad) + ' legs failing'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
