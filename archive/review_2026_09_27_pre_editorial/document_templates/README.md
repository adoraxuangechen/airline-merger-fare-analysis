# English paper sources

`writing_sample_v2.md` and `technical_supplement_v2.md` are the editable publication sources. The current builder is `build_reference_style.py`; it imports the existing numerical table loader from `build_revision.py`, and reads the saved core and extension results. It does not run or select regressions.

```sh
python documents/build_reference_style.py --out papers_recheck
```

Use the main repository requirements. The builder uses reportlab, matplotlib math typesetting, and system Times New Roman or matplotlib's DejaVu Serif fonts. It exports English-only PDFs and resolved Markdown. The layout follows the supplied academic article: letter pages, one-inch side margins, centered author/abstract block, justified paragraphs, numbered equations, unshaded three-rule tables, running headers, and centered page numbers. The first page has no running header or visible page number.

The earlier Chinese explanation is private working material outside this publication tree. Current published documents contain no Chinese text. `build_revision.py` retains the prior compact-layout implementation as a numerical loader; use the command above for the approved reference-style layout.

Rebuild the main paper and supplement together after any numerical or textual change. Render and visually inspect every page; check scientific content against the saved registries before publication.
