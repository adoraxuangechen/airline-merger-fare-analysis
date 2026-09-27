# Revision history and archival record

This record distinguishes dates printed in documents, dates recorded by Git, and the actual date on which archival copies were created. It preserves the sequence that can be established from the available files without inventing intermediate commit dates. The historical source files and existing Git commits were not altered.

| Stage | Available evidence | Preserved location |
|---|---|---|
| Original course paper, dated December 2025 | The 27-page paper's title page says *December 2025*. Its PDF creation and modification metadata both contain `D:20251204185230Z`. These are document attributes, not independent proof of completion or submission. | [Original PDF](../archive/original_2025_12/Econ_449_final_paper_Adora.pdf) and [historical-status note](../archive/original_2025_12/README.md). |
| Existing public-repository version, September 21, 2026 recorded Git dates | The cloned repository contains 12 existing commits. Its base commit is `de38cd0e173d786c3d5c1edf9f463bb0dd4049f5`, with author and committer timestamps recorded as `2026-09-21T16:57:56-04:00`. Earlier commit records remain intact. | [Existing v1 files](../archive/v1/), [commit/ref record](git_history_at_revision_start.json), and [Git-history record](../archive/git_history_2026_09_27/README.md). The duplicate backup bundle remains private. |
| September 27, 2026 analytical revision | The current working revision added market-composition adjustments, expanded-comparison and carrier-composition diagnostics, carrier-group fare comparisons, sensitivity analysis, and cross-language regression checks. This row describes the working revision; it does not imply separate historical Git timestamps for each analytical step. | Current `analysis/`, `extensions/`, `results/`, and their method records. |
| September 27, 2026 review snapshot before the next editorial rewrite | At `2026-09-27T19:48:51+00:00`, the available 8-page review paper, 12-page supplement, resolved Markdown, value map, source templates, and builders were copied. Both PDFs carry creation metadata `D:20260927154658-04'00'`. All copied bytes matched their sources. | [Review snapshot](../archive/review_2026_09_27_pre_editorial/) and [capture receipt](revision_archive_capture.json). |
| September 27, 2026 snapshot before the raw-fare and breakdown additions | At `2026-09-27T20:12:49.670944+00:00`, the delivered 8-page paper, 12-page supplement, resolved text, source templates, and reference-style builder were copied byte-for-byte before these additions. | [Review snapshot](../archive/review_2026_09_27_before_trend_plot/) and [capture receipt](../archive/review_2026_09_27_before_trend_plot/capture.json). |
| Subsequent editorial revision | The current manuscripts may subsequently change wording, structure, presentation, and documentation. This record does not preassign a completion date or claim publication of changes that have not been committed and published. | Maintained `papers/` and `documents/`; later Git history when actually committed. |

## Integrity checks

- The original December paper was copied byte-for-byte from the supplied local file; the source remained untouched.
- During the complete private capture, all **55 tracked files** at base commit `de38cd0e173d786c3d5c1edf9f463bb0dd4049f5` were compared with their `archive/v1/` counterparts. Every file in that private capture was byte-identical to its historical Git blob. The public tree omits one historical document builder; see the explicit public archive scope. The [verification record](v1_preservation_verification.json) gives original paths, archived paths, and SHA-256 values.
- The pre-editorial snapshot records source and destination SHA-256 equality for every copied item. Exact source paths appear in [the capture receipt](revision_archive_capture.json).
- The [public archive manifest](archive_sha256_manifest.json) records hashes and sizes of included archived files. The [earlier complete private-capture manifest](private_capture_archive_manifest.json) also records files intentionally omitted from this public tree. It is a fingerprint of the captured contents, not a claim that every file was independently timestamped at its historical document date.
- The Git bundle was checked with `git bundle verify`, which reported a valid bundle with complete history. It preserves the existing 12 commits and the existing tag; it does not include uncommitted changes.

## How to interpret changes

Archived papers and results are historical materials. Numerical claims may be superseded by later data handling, sample definitions, estimation choices, or interpretation. Read the current analysis with its matching code and results; do not combine favorable numbers from incompatible versions.

Document dates, filesystem attributes, Git dates, and archive timestamps have different meanings. None alone establishes authorship or independently proves the chronology of every piece of work. No commits were created, rewritten, backdated, or pushed by this archival step. Subsequent publication should preserve the actual history rather than manufacture a separate historical commit for each recovered draft.

## Raw-fare and unadjusted-breakdown follow-up

The working revision now adds raw nominal fare paths for the unchanged primary route panel, an unadjusted HonestDiD breakdown with exact pooled projection weights, and a plain definition of the other-code comparison. The breakdown was refined numerically and checked by full confidence-set inversion. An effective internal simulation-seed audit clarifies software defaults without changing the prior adjusted outputs. These additions were prepared on September 27, 2026 and are included in the current release tree. The snapshot above preserves the review copies delivered before these additions.

The [next local snapshot](../archive/review_2026_09_27_before_title_footnote/) preserves the version with the three analytical additions before the author requested a title-page acknowledgment footnote, JEL codes, month-only date, author-date reference cleanup, and typography standardization. Its capture receipt records the actual archival time. These editorial changes do not alter estimates.
