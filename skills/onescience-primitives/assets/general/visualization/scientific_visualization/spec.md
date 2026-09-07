# architecture_overview

Scientific visualization is a figure-planning and review primitive. It emphasizes honest encoding, accessibility, reproducibility, and delivery validation.

# input_schema

Typical inputs are source data paths, variable semantics, units, missingness, estimator choice, uncertainty definition, target medium, and export constraints.

# output_schema

Expected outputs include figure specifications, plotting implementation notes, export requirements, inspection checklist, alt text or data-alternative notes, and provenance metadata.

# key_dependencies

- matplotlib
- seaborn
- plotly
- pillow or pypdf for metadata inspection
- optional kaleido for static Plotly export

# common_modification_points

- figure size and target medium
- estimator and uncertainty interval
- color palette and redundant encodings
- static vs interactive output
- raster/vector export formats
- journal or publisher constraints

# implementation_risks

- Automated export checks do not certify scientific correctness or journal acceptance.
- Color alone is not a sufficient accessibility channel.
- Binning, smoothing, axis limits, and image adjustments can distort evidence.
- Interactive output needs static and accessible fallbacks when used for publication.

# provenance

Distilled from `scientific-agent-skills/skills/scientific-visualization` version `1.1`. Scripts and style assets were not copied.
