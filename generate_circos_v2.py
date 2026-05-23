#!/usr/bin/env python3
import pandas as pd
import os

# Read the CSV
df = pd.read_csv('Major_Job_Cluster_Lookup_Filtered.csv')

# Color mapping: Group majors by academic discipline
# Blues: Language/Arts/Communication
# Oranges/Browns: Social Sciences/Business/Humanities
# Greens: STEM/Science/Engineering
COLOR_MAP = {
    'ARTS, LANGUAGES & THEOLOGY': '#6B9BD1',      # Medium blue
    'COMMUNICATION & MEDIA': '#5B8AC5',            # Slightly darker blue
    'SOCIAL SCIENCES & HUMANITIES': '#D4944E',   # Warm tan/brown
    'BUSINESS & MANAGEMENT': '#CA8844',            # Orange-brown
    'EDUCATION & SOCIAL SERVICES': '#C9956F',    # Peachy brown
    'NATURAL & HEALTH SCIENCES': '#7CB342',       # Muted green
    'ENGINEERING & TECHNOLOGY': '#558B2F',        # Darker green
}

# All careers get the same neutral gray
CAREER_COLOR = '#A9A9A9'  # Neutral gray

# Aggregate data
flow_data = df.groupby(['Large Major Cluster', 'Large Job Title Cluster']).size().reset_index(name='count')
major_totals = df.groupby('Large Major Cluster').size().reset_index(name='total')
job_totals = df.groupby('Large Job Title Cluster').size().reset_index(name='total')

# Print summary
print("=== Major-to-Career Flow Analysis ===")
print(f"Total records: {len(df)}")
print(f"Total unique flows: {len(flow_data)}")
print(f"\nMajor clusters and totals:")
for _, row in major_totals.sort_values('total', ascending=False).iterrows():
    print(f"  {row['Large Major Cluster']}: {row['total']}")
print(f"\nJob clusters and totals:")
for _, row in job_totals.sort_values('total', ascending=False).iterrows():
    print(f"  {row['Large Job Title Cluster']}: {row['total']}")

os.makedirs('circos', exist_ok=True)

# === BUILD KARYOTYPE ===
# Order majors with related ones grouped together
major_order = [
    'ARTS, LANGUAGES & THEOLOGY',
    'COMMUNICATION & MEDIA',
    'SOCIAL SCIENCES & HUMANITIES',
    'BUSINESS & MANAGEMENT',
    'EDUCATION & SOCIAL SERVICES',
    'ENGINEERING & TECHNOLOGY',
    'NATURAL & HEALTH SCIENCES',
]

# Order careers
job_order = [
    'Arts, Media & Legal',
    'Education & Service',
    'Business & Finance',
    'Technology & Engineering',
    'Healthcare & Science',
]

karyotype_lines = []
major_positions = {}
job_positions = {}

# Assign positions based on aggregated counts
# Major size = total count of people from that major
# Job size = total count of connections to that job

pos = 0

# Place majors (left side of circle)
for major in major_order:
    total = major_totals[major_totals['Large Major Cluster'] == major]['total'].values[0]
    # Scale to arc size: use count directly as size
    size = max(total, 5)  # minimum 5 units

    chr_name = f"maj_{major.replace(' ', '_').replace('&', 'and')}"
    color = COLOR_MAP[major]
    major_positions[major] = (chr_name, pos, pos + size, color)

    # Format: chr - [label] [start] [end] [color]
    karyotype_lines.append(f"chr - {chr_name} {major} {pos} {pos+size} {color}")
    pos += size + 2

# Place jobs (right side of circle) - all gray
for job in job_order:
    total = job_totals[job_totals['Large Job Title Cluster'] == job]['total'].values[0]
    size = max(total, 5)

    chr_name = f"job_{job.replace(' ', '_').replace('&', 'and')}"
    job_positions[job] = (chr_name, pos, pos + size, CAREER_COLOR)

    karyotype_lines.append(f"chr - {chr_name} {job} {pos} {pos+size} {CAREER_COLOR}")
    pos += size + 2

# Write karyotype
with open('circos/karyotype.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(karyotype_lines))

print(f"\nCreated circos/karyotype.txt with {len(karyotype_lines)} ideograms")

# === BUILD LINKS FILE ===
# Format: source_chr source_start source_end target_chr target_start target_end [options]
# Ribbons are colored by SOURCE (major), not destination

links_lines = []
for _, row in flow_data.iterrows():
    major = row['Large Major Cluster']
    job = row['Large Job Title Cluster']
    count = row['count']

    major_chr, major_start, major_end, major_color = major_positions[major]
    job_chr, job_start, job_end, job_color = job_positions[job]

    # Ribbon gets the major's color with transparency
    # Use rgba format: source_color with alpha=0.4
    color_rgba = major_color.lstrip('#')
    r = int(color_rgba[0:2], 16)
    g = int(color_rgba[2:4], 16)
    b = int(color_rgba[4:6], 16)

    # Create link with major's color and transparency
    link_line = f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color=rgba({r},{g},{b},0.5)"
    links_lines.append(link_line)

with open('circos/links.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(links_lines))

print(f"Created circos/links.txt with {len(links_lines)} links")
print("\n[OK] Circos data files generated successfully!")
