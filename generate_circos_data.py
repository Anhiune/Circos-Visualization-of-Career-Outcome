#!/usr/bin/env python3
"""
Generate Circos karyotype and links files from major-to-career CSV data
"""

import pandas as pd
import os

# Read the CSV
df = pd.read_csv('Major_Job_Cluster_Lookup_Filtered.csv')

# Aggregate data by large clusters
flow_data = df.groupby(['Large Major Cluster', 'Large Job Title Cluster']).size().reset_index(name='count')
major_totals = df.groupby('Large Major Cluster').size().reset_index(name='total')
job_totals = df.groupby('Large Job Title Cluster').size().reset_index(name='total')

# Define ordering and colors
major_order = [
    'ARTS, LANGUAGES & THEOLOGY',
    'COMMUNICATION & MEDIA',
    'SOCIAL SCIENCES & HUMANITIES',
    'BUSINESS & MANAGEMENT',
    'EDUCATION & SOCIAL SERVICES',
    'ENGINEERING & TECHNOLOGY',
    'NATURAL & HEALTH SCIENCES',
]

job_order = [
    'Arts, Media & Legal',
    'Education & Service',
    'Business & Finance',
    'Technology & Engineering',
    'Healthcare & Science',
]

# Safe chromosome names (alphanumeric + underscore)
safe_names_major = {
    'ARTS, LANGUAGES & THEOLOGY': 'maj_arts',
    'COMMUNICATION & MEDIA': 'maj_comm',
    'SOCIAL SCIENCES & HUMANITIES': 'maj_social',
    'BUSINESS & MANAGEMENT': 'maj_business',
    'EDUCATION & SOCIAL SERVICES': 'maj_education',
    'ENGINEERING & TECHNOLOGY': 'maj_engineering',
    'NATURAL & HEALTH SCIENCES': 'maj_natural',
}

safe_names_job = {
    'Arts, Media & Legal': 'job_arts',
    'Education & Service': 'job_education',
    'Business & Finance': 'job_business',
    'Technology & Engineering': 'job_tech',
    'Healthcare & Science': 'job_health',
}

# Colors matching Williams College design
COLOR_MAP = {
    'ARTS, LANGUAGES & THEOLOGY': '#5B7FA6',
    'COMMUNICATION & MEDIA': '#4A6FA5',
    'SOCIAL SCIENCES & HUMANITIES': '#C8915F',
    'BUSINESS & MANAGEMENT': '#C17E47',
    'EDUCATION & SOCIAL SERVICES': '#C99070',
    'NATURAL & HEALTH SCIENCES': '#7CB342',
    'ENGINEERING & TECHNOLOGY': '#558B2F',
}

CAREER_COLOR = '#8B8B8B'  # Gray for careers

# Create output directory
os.makedirs('circos/data', exist_ok=True)

# ============ BUILD KARYOTYPE ============
karyotype_lines = []
major_positions = {}
job_positions = {}

pos = 0

# Process majors
for major in major_order:
    total = major_totals[major_totals['Large Major Cluster'] == major]['total'].values[0]
    size = max(total, 5)
    chr_name = safe_names_major[major]
    color = COLOR_MAP[major]

    major_positions[major] = (chr_name, pos, pos + size, color)
    karyotype_lines.append(f"chr - {chr_name} {chr_name} {pos} {pos+size} {color}")
    pos += size + 2

# Process jobs
for job in job_order:
    total = job_totals[job_totals['Large Job Title Cluster'] == job]['total'].values[0]
    size = max(total, 5)
    chr_name = safe_names_job[job]

    job_positions[job] = (chr_name, pos, pos + size, CAREER_COLOR)
    karyotype_lines.append(f"chr - {chr_name} {chr_name} {pos} {pos+size} {CAREER_COLOR}")
    pos += size + 2

# Write karyotype
with open('circos/data/karyotype.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(karyotype_lines))

print(f"[OK] Created circos/data/karyotype.txt ({len(karyotype_lines)} chromosomes)")

# ============ BUILD LINKS ============
links_lines = []
for _, row in flow_data.iterrows():
    major = row['Large Major Cluster']
    job = row['Large Job Title Cluster']
    count = row['count']

    major_chr, major_start, major_end, major_color = major_positions[major]
    job_chr, job_start, job_end, job_color = job_positions[job]

    # Ribbons colored by source (major)
    link_line = f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color={major_color}"
    links_lines.append(link_line)

with open('circos/data/links.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(links_lines))

print(f"[OK] Created circos/data/links.txt ({len(links_lines)} links)")

print("\n[DONE] All Circos data files generated!")
print("Next: Run circos with: circos -conf circos/circos.conf")
