import pandas as pd
import os

df = pd.read_csv('Major_Job_Cluster_Lookup_Filtered.csv')

flow_data = df.groupby(['Large Major Cluster', 'Large Job Title Cluster']).size().reset_index(name='count')
major_totals = df.groupby('Large Major Cluster').size().reset_index(name='total')
job_totals = df.groupby('Large Job Title Cluster').size().reset_index(name='total')

major_order = ['ARTS, LANGUAGES & THEOLOGY', 'COMMUNICATION & MEDIA', 'SOCIAL SCIENCES & HUMANITIES', 'BUSINESS & MANAGEMENT', 'EDUCATION & SOCIAL SERVICES', 'ENGINEERING & TECHNOLOGY', 'NATURAL & HEALTH SCIENCES']
job_order = ['Arts, Media & Legal', 'Education & Service', 'Business & Finance', 'Technology & Engineering', 'Healthcare & Science']

major_names = {'ARTS, LANGUAGES & THEOLOGY': 'maj_arts', 'COMMUNICATION & MEDIA': 'maj_comm', 'SOCIAL SCIENCES & HUMANITIES': 'maj_social', 'BUSINESS & MANAGEMENT': 'maj_business', 'EDUCATION & SOCIAL SERVICES': 'maj_education', 'ENGINEERING & TECHNOLOGY': 'maj_engineering', 'NATURAL & HEALTH SCIENCES': 'maj_natural'}
job_names = {'Arts, Media & Legal': 'job_arts', 'Education & Service': 'job_education', 'Business & Finance': 'job_business', 'Technology & Engineering': 'job_tech', 'Healthcare & Science': 'job_health'}

color_map = {'ARTS, LANGUAGES & THEOLOGY': '#5B7FA6', 'COMMUNICATION & MEDIA': '#4A6FA5', 'SOCIAL SCIENCES & HUMANITIES': '#C8915F', 'BUSINESS & MANAGEMENT': '#C17E47', 'EDUCATION & SOCIAL SERVICES': '#C99070', 'NATURAL & HEALTH SCIENCES': '#7CB342', 'ENGINEERING & TECHNOLOGY': '#558B2F'}
career_color = '#8B8B8B'

os.makedirs('circos/data', exist_ok=True)

karyotype_lines = []
major_positions = {}
job_positions = {}
pos = 0

for major in major_order:
    total = major_totals[major_totals['Large Major Cluster'] == major]['total'].values[0]
    size = max(total, 5)
    chr_name = major_names[major]
    color = color_map[major]
    major_positions[major] = (chr_name, pos, pos + size)
    karyotype_lines.append(f"chr - {chr_name} {chr_name} {pos} {pos+size} {color}")
    pos += size + 2

for job in job_order:
    total = job_totals[job_totals['Large Job Title Cluster'] == job]['total'].values[0]
    size = max(total, 5)
    chr_name = job_names[job]
    job_positions[job] = (chr_name, pos, pos + size)
    karyotype_lines.append(f"chr - {chr_name} {chr_name} {pos} {pos+size} {career_color}")
    pos += size + 2

with open('circos/data/karyotype.txt', 'w') as f:
    f.write('\n'.join(karyotype_lines))

print(f"Created: circos/data/karyotype.txt ({len(karyotype_lines)} chromosomes)")

links_lines = []
for _, row in flow_data.iterrows():
    major = row['Large Major Cluster']
    job = row['Large Job Title Cluster']
    major_chr, major_start, major_end = major_positions[major]
    job_chr, job_start, job_end = job_positions[job]
    color = color_map[major]
    link_line = f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color={color}"
    links_lines.append(link_line)

with open('circos/data/links.txt', 'w') as f:
    f.write('\n'.join(links_lines))

print(f"Created: circos/data/links.txt ({len(links_lines)} links)")
print("Now run: cd circos && /c/Strawberry/perl/bin/perl.exe /c/Users/hoang/circos/bin/circos -conf circos.conf")
