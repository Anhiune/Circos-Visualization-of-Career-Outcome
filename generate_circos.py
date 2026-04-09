#!/usr/bin/env python3
import pandas as pd
import os

# Read the CSV
df = pd.read_csv('Major_Job_Cluster_Lookup_Filtered.csv')

# Aggregate data by Large Major Cluster -> Large Job Title Cluster
flow_data = df.groupby(['Large Major Cluster', 'Large Job Title Cluster']).size().reset_index(name='count')

print(f"Total flows: {len(flow_data)}")
print(f"\nUnique Major Clusters: {df['Large Major Cluster'].nunique()}")
print(f"Unique Job Clusters: {df['Large Job Title Cluster'].nunique()}")
print(f"\nMajor Clusters:")
print(df['Large Major Cluster'].unique())
print(f"\nJob Clusters:")
print(df['Large Job Title Cluster'].unique())

# Create circos directory
os.makedirs('circos', exist_ok=True)

# Create ideogram (karyotype) file
majors = df['Large Major Cluster'].unique()
jobs = df['Large Job Title Cluster'].unique()

# Build karyotype: chr - label start end color
karyotype_lines = []
colors_major = [
    'set3-12-1', 'set3-12-2', 'set3-12-3', 'set3-12-4', 'set3-12-5',
    'set3-12-6', 'set3-12-7', 'set3-12-8', 'set3-12-9', 'set3-12-10',
    'set3-12-11', 'set3-12-12'
]
colors_jobs = [
    'pastel1-9-1', 'pastel1-9-2', 'pastel1-9-3', 'pastel1-9-4', 'pastel1-9-5',
    'pastel1-9-6', 'pastel1-9-7', 'pastel1-9-8', 'pastel1-9-9'
]

pos = 0
size = 10
major_positions = {}

for i, major in enumerate(sorted(majors)):
    chr_name = f"maj_{major.replace(' ', '_').replace('&', 'and')}"
    major_positions[major] = (chr_name, pos, pos + size)
    color = colors_major[i % len(colors_major)]
    karyotype_lines.append(f"chr - {chr_name} {major} {pos} {pos+size} {color}")
    pos += size + 2

job_positions = {}
for i, job in enumerate(sorted(jobs)):
    chr_name = f"job_{job.replace(' ', '_').replace('&', 'and')}"
    job_positions[job] = (chr_name, pos, pos + size)
    color = colors_jobs[i % len(colors_jobs)]
    karyotype_lines.append(f"chr - {chr_name} {job} {pos} {pos+size} {color}")
    pos += size + 2

with open('circos/karyotype.txt', 'w') as f:
    f.write('\n'.join(karyotype_lines))

print(f"\nCreated circos/karyotype.txt with {len(karyotype_lines)} ideograms")

# Create links file for Circos
# Format: source_chr source_start source_end target_chr target_start target_end [options]
links_lines = []

for _, row in flow_data.iterrows():
    major = row['Large Major Cluster']
    job = row['Large Job Title Cluster']
    count = row['count']

    # Get chromosome names and positions
    major_chr, major_start, major_end = major_positions[major]
    job_chr, job_start, job_end = job_positions[job]

    # Scale count to line thickness (optional, for better visualization)
    thickness = max(0.1, min(3, count / 10))

    # Create link line - using the full range of each chromosome
    links_lines.append(f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color=rgba(200,200,200,0.3)")

with open('circos/links.txt', 'w') as f:
    f.write('\n'.join(links_lines))

print(f"Created circos/links.txt with {len(links_lines)} links")

print("\n[OK] Circos data files generated successfully!")
print("Next steps:")
print("1. Install Circos (if not already installed)")
print("2. Create a circos.conf configuration file")
print("3. Run: circos -conf circos.conf")
