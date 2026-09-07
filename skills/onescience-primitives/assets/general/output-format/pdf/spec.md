# architecture_overview

PDF is a fixed-layout exchange and archival format. This primitive captures operations, inspection, and conversion boundaries without embedding a specific renderer.

# input_schema

Typical inputs are source PDF or structured content, page range, extraction target, output page size, security settings, and OCR requirements.

# output_schema

Expected outputs include PDF files, extracted text or tables, images, metadata, page-level previews, and operation logs.

# key_dependencies

- pypdf
- pdfplumber
- reportlab
- optional Poppler, qpdf, pdftk, Tesseract, or pdf2image

# common_modification_points

- page merge/split order
- page rotation and crop
- text/table extraction mode
- watermark or encryption settings
- OCR language and image resolution
- metadata and archival profile

# implementation_risks

- Text extraction can lose layout or table semantics.
- OCR output requires review and is not equivalent to source text.
- PDF rendering can hide missing fonts, clipped content, or broken embedded images.
- Encryption and permissions can block downstream review.

# provenance

Distilled from `scientific-agent-skills/skills/pdf` version `1.2`. Scripts and templates were not copied.
