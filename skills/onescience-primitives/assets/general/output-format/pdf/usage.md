# typical_workflow

1. Identify whether the task is extraction, transformation, or creation.
2. Preserve page order, metadata, and source provenance.
3. Apply the smallest required operation.
4. Render or extract a preview for inspection.
5. Validate page count, text/tables, images, and security settings.

# usage_notes

- Use pypdf for basic page operations.
- Use pdfplumber for layout-sensitive text and table extraction.
- Use reportlab for structured PDF creation.
- Use OCR only when the PDF is scanned or text is unavailable.
