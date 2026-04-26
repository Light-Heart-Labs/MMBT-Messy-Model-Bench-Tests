# ADR-005: Chart Design and Visualization Strategy

**Date:** 2025-06-18  
**Status:** Accepted

## Context
Need to create charts for the board presentation that are:
1. Colorful and distinctive but earn it
2. Charts should be the visual centerpiece
3. No clip-art, no generic stock imagery, no AI-generated faces
4. Charts should reinforce the data (sector colors consistent, scenario colors consistent)
5. Every chart must have a reproducible script

## Requirements

### Visual Design
1. **Color palette** - Distinctive but data-driven
2. **Typography** - Clean, readable, professional
3. **Chart conventions** - Consistent across slides
4. **Data density** - More data per slide, less text

### Chart Types
1. **Financial trajectory** - Line chart with historical + projected
2. **Competitive landscape** - Scatter plot or bar chart
3. **Scenario analysis** - Probability-weighted visualization
4. **Reasoning trail** - Dependency graph or flowchart
5. **Dead ends** - Decision tree or flowchart

### Reproducibility
1. Every chart must have a script in `/assets/charts/`
2. Charts must be generated from data in `/input/repo/`
3. Scripts must be runnable to regenerate exact charts

## Alternatives Considered

### Alternative 1: Default Matplotlib Style
- **Pros:** Easy to use, well-documented
- **Cons:** Looks generic, not distinctive enough
- **Why Rejected:** Doesn't meet "colorful and distinctive" requirement

### Alternative 2: Seaborn Default Style
- **Pros:** More visually appealing than matplotlib
- **Cons:** Still generic, not distinctive enough
- **Why Rejected:** Doesn't meet "colorful and distinctive" requirement

### Alternative 3: Plotly Interactive Charts
- **Pros:** Interactive, zoomable, hover tooltips
- **Cons:** May not work well in PowerPoint; requires JavaScript
- **Why Rejected:** PowerPoint is static; interactive charts don't translate well

### Alternative 4: Custom Color Palette (Selected)
- **Pros:** Distinctive, data-driven, professional
- **Cons:** Requires more setup
- **Why Selected:** Meets "colorful and distinctive" requirement

## Decision

**Selected: Custom Color Palette with Data-Driven Design**

### Color Palette

| Purpose | Color | Hex | Rationale |
|---------|-------|-----|-----------|
| **Primary (GitLab)** | Blue | #1E88E5 | GitLab brand color (from logo) |
| **Secondary (Revenue)** | Green | #43A047 | Positive, growth-oriented |
| **Tertiary (Loss)** | Red | #E53935 | Negative, cautionary |
| **Bear Scenario** | Red | #D32F2F | Downside risk |
| **Base Scenario** | Green | #388E3C | Base case, most likely |
| **Bull Scenario** | Blue | #1976D2 | Upside potential |
| **Text (Dark)** | Black | #212121 | Readable, professional |
| **Text (Light)** | White | #FFFFFF | High contrast |
| **Background** | Off-white | #FAFAFA | Clean, professional |
| **Grid Lines** | Light gray | #E0E0E0 | Subtle, not distracting |

### Typography

| Purpose | Font | Size | Rationale |
|---------|------|------|-----------|
| **Title** | Arial Bold | 28-32pt | Clear, readable, professional |
| **Subtitle** | Arial | 20-24pt | Distinct from title |
| **Body Text** | Arial | 14-16pt | Readable, not too small |
| **Chart Labels** | Arial | 10-12pt | Readable, not too small |
| **Chart Title** | Arial Bold | 14-16pt | Clear, readable |
| **Chart Legend** | Arial | 10-12pt | Readable, not too small |

### Chart Conventions

| Element | Convention | Rationale |
|---------|------------|-----------|
| **Bar Width** | 60-80% of category width | Not too wide, not too narrow |
| **Line Width** | 2-3pt | Clear, not too thick |
| **Marker Size** | 6-8pt | Clear, not too big |
| **Grid Lines** | Light gray, dashed | Subtle, not distracting |
| **Axis Labels** | 10-12pt Arial | Readable, not too small |
| **Chart Title** | 14-16pt Arial Bold | Clear, readable |
| **Data Labels** | On bars/points, 10-12pt | Clear, not cluttered |

## Rationale

### Why This Design Works

1. **Color palette is distinctive** - Uses GitLab brand colors, but adjusted for professional presentation
2. **Data-driven** - Colors reinforce the data (green for positive, red for negative)
3. **Consistent** - Same colors used across all charts
4. **Professional** - Clean, modern, not flashy
5. **Accessible** - High contrast, readable fonts

### Key Design Decisions

1. **GitLab brand color (blue)** - Used for primary elements to establish brand identity
2. **Green for positive, red for negative** - Intuitive, universal color coding
3. **Scenario colors (bear=red, base=green, bull=blue)** - Consistent with data direction
4. **Arial font** - Clean, readable, professional, widely available
5. **Off-white background** - Clean, modern, not stark white

## Implementation

### Tools
- Python with `matplotlib` for charts
- `python-pptx` for PowerPoint generation
- `pandas` for data manipulation

### Chart Scripts
Each chart will have a script in `/assets/charts/`:
1. `financial_trajectory.py` - Historical + projected revenue, margins, FCF
2. `competitive_landscape.py` - EV/Revenue vs. revenue growth scatter plot
3. `scenario_analysis.py` - Probability-weighted scenario visualization
4. `reasoning_trail.py` - Dependency graph showing agent's decision process
5. `dead_ends.py` - Decision tree showing what didn't work

### Reproducibility
Each script will:
1. Read data from `/input/repo/` (or `/workspace/extracted/`)
2. Generate chart with custom color palette
3. Save to `/assets/charts/` as PNG
4. Include metadata (date, script version, data source)

## Limitations

1. **PowerPoint charts are static** - Can't use interactive Plotly charts
2. **Colorblind accessibility** - May need to add patterns or shapes
3. **Font licensing** - Arial is widely available but not open source
4. **Chart complexity** - Some charts (reasoning trail) may be complex to create

## Next Steps

1. Create financial trajectory chart script
2. Create competitive landscape chart script
3. Create scenario analysis chart script
4. Create reasoning trail diagram
5. Create dead ends diagram
6. Integrate charts into PowerPoint deck

## Approval

**Approved by:** Board Presentation Agent  
**Date:** 2025-06-18  
**Status:** Accepted
