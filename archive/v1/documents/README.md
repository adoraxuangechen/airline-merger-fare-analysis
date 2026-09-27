# Rebuild the editable documents

From the repository root, after obtaining the committed saved results:

```sh
python -m pip install -r documents/requirements.txt
python documents/build_documents.py --only writing_sample
python documents/build_documents.py --only technical_supplement
```

The builder reads the Markdown templates and `results/`, inserts estimates and tables, and writes editable DOCX and filled Markdown to `delivery/`. Open the DOCX in Word or LibreOffice to export PDF. The published PDFs were rendered and checked page by page; PDF pagination can vary with the local fonts and renderer. No proprietary software is required to create DOCX.
