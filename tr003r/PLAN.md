# TR-003r implementation plan (before any code; Word 3)

Restated protocol as tasks, with the control that proves each step.

1. **Phase 0 close.** Stamp lands; file moves to root; manifest
   reissued; D6 hashes logged; single-seat oracle seals; panel seals
   as pilot subject; reviewer's forecast through their channel.
2. **Store builder** (`tr003r/build_store.py`): 5,000 chunks per seed
   from TR-002r's registry with work and position; sequence edges;
   500 Q1 and 500 Q2 queries; anchor pool of at least 1,200 held-out
   chunks. Emits CORPUS_MANIFEST.json with hashes.
   Control 4 checker, red first: a fixture with one shared hash must
   fail; then the real manifest passes.
3. **Extraction** (`tr003r/extract.py`, TR-002r's extractor reused
   with its hash logged): store, queries, and anchors through all six
   spaces; float32 sidecars with sha256.
   Control 5 checker: C1 Recall@5 >= 0.90 per space on Q1, red on a
   fixture with shuffled labels.
4. **Anchor library** (`tr003r/anchors.py`): relative representations
   (cosine-to-anchor), Procrustes ceiling (TR-002r code), random
   orthogonal maps for C2 and control 3, scrambled and mismatched
   anchor generators for controls 1 and 2. Exam before duty: on a
   synthetic pair where space B is a known rotation of A, C3 and C4
   must recover retrieval near 1.0 and the two collapse controls must
   sit at chance.
5. **Retrieval grid** (`tr003r/grid.py`, resumable, one JSON line per
   configuration): 30 ordered pairs x 3 anchor counts x 2 selections
   x 2 seeds x 2 query kinds x 4 conditions, plus the three control
   arms on the primary pair. Metrics per protocol.
6. **Gate assembler** (`tr003r/checks/`): check_pass reads the three
   clauses on the primary pair only; check_kill reads C4; check
   controls read 1 to 3. Each checker has a red fixture. verify.sh
   runs every leg and exits nonzero on any violation.
7. **Figures and report**: survival table, anchor-count curves,
   class-stratified boundary map; utilization verdict drafted for
   the PI; disk line; panel reveal and score at closeout.

Budget: $0 and zero downloads. Sweep budget is the grid as written;
no configuration outside it is run.
