# Circos Configuration Guide

## File: circos/circos.conf

This configuration file controls how your diagram looks. Here's what each section does:

### 1. IMAGE SETTINGS
```
<image>
dir = .                      # Output directory
file = circos.png           # Output filename
png = yes                   # Generate PNG (yes/no)
svg = no                    # Generate SVG (yes/no)
radius = 1500p              # Canvas size (pixels)
background = white          # Background color
</image>
```

**To change:**
- `radius`: Make diagram bigger (increase value) or smaller (decrease)
- `svg = yes`: Also generate SVG vector format

### 2. IDEOGRAM SETTINGS (colored circles/arcs)
```
<ideogram>
radius = 1.8r               # Position from center (relative radius)
thickness = 45p             # Width of colored band in pixels
fill = yes                  # Fill with color
stroke_thickness = 3p       # Border thickness
stroke_color = white        # Border color
label_radius = 2.4r         # Where labels appear
label_size = 18p            # Font size
label_font = condensed      # Font style (condensed, default, bold)
show_label = yes            # Show labels (yes/no)
</ideogram>
```

**To change:**
- `label_size = 18p`: Larger labels = higher number
- `thickness = 45p`: Thicker bands = higher number
- `stroke_color = white`: Change border color

### 3. COLOR RULES (for ideograms)
```
<rules>
<rule>
condition = /^maj_business$/  # Matches chromosome name
fill_color = #C17E47          # Color in hex format
</rule>
</rules>
```

**To change colors:**
1. Find the major cluster you want to change
2. Edit the `fill_color` value
3. Use hex color codes: #RRGGBB
   - Red: #FF0000
   - Blue: #0000FF
   - Green: #00FF00

### 4. LINKS SETTINGS (ribbons between majors and careers)
```
<links>
<link>
file = data/links.txt       # Data file
radius = 1.7r               # Position of ribbons
ribbon = yes                # Use ribbon style (curves)
bezier_radius = 0.3r        # Curvature amount (0 = straight, >1 = tight)
thickness = 2p              # Ribbon width
stroke = no                 # Draw border (yes/no)
</link>
</links>
```

**To change:**
- `thickness = 2p`: Thicker ribbons = higher number
- `bezier_radius = 0.3r`: More curved = lower number, straighter = higher number
- `stroke = yes`: Add outline to ribbons

### 5. INCLUDES (external config files)
```
<<include etc/colors_fonts_patterns.conf>>
<<include etc/housekeeping.conf>>
```

These load standard Circos settings. Keep these lines at the bottom.

---

## Common Customizations

### Make diagram bigger
```
<image>
radius = 2000p   # Instead of 1500p
</image>
```

### Change label position
```
<ideogram>
label_radius = 2.6r   # Further from center
</ideogram>
```

### Make ribbons more transparent
In `generate_circos_data.py`, find this line:
```python
link_line = f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color={color}"
```

Change to:
```python
link_line = f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color={color}:alpha=0.3"
```

(Alpha ranges from 0=invisible to 1=opaque)

### Change all major colors
Edit `COLOR_MAP` in `generate_circos_data.py`:
```python
COLOR_MAP = {
    'ARTS, LANGUAGES & THEOLOGY': '#NEW_COLOR_HEX',
    'COMMUNICATION & MEDIA': '#NEW_COLOR_HEX',
    # ... etc
}
```

### Change career color (gray)
Edit in `generate_circos_data.py`:
```python
CAREER_COLOR = '#NEW_GRAY_HEX'  # Instead of '#8B8B8B'
```

---

## Units Explained

- `p` = pixels (fixed size on screen)
- `r` = relative radius (1r = full circle radius)
- `u` = chromosomal units (based on your data)

---

## After making changes:

1. Edit the config file
2. Run: `python generate_circos_data.py`
3. Run: `circos -conf circos/circos.conf`
4. Check output: `circos/circos.png`

If something breaks, the error message will tell you what's wrong!
