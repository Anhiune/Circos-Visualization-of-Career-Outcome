#!/usr/bin/env python3
"""
Complete Circos generator - data preparation + execution
Run this to generate the full diagram in one command
"""

import pandas as pd
import os
import subprocess
import sys

# ============ CONFIGURATION ============
CSV_FILE = 'Major_Job_Cluster_Lookup_Filtered.csv'
CIRCOS_CONF = 'circos.conf'
CIRCOS_OUTPUT_DIR = 'circos'

# ============ COLOR CONFIGURATION ============
COLOR_MAP = {
    'ARTS, LANGUAGES & THEOLOGY': '#5B7FA6',
    'COMMUNICATION & MEDIA': '#4A6FA5',
    'SOCIAL SCIENCES & HUMANITIES': '#C8915F',
    'BUSINESS & MANAGEMENT': '#C17E47',
    'EDUCATION & SOCIAL SERVICES': '#C99070',
    'NATURAL & HEALTH SCIENCES': '#7CB342',
    'ENGINEERING & TECHNOLOGY': '#558B2F',
}
CAREER_COLOR = '#8B8B8B'

# ============ CHROMOSOME NAME MAPPING ============
MAJOR_NAMES = {
    'ARTS, LANGUAGES & THEOLOGY': 'maj_arts',
    'COMMUNICATION & MEDIA': 'maj_comm',
    'SOCIAL SCIENCES & HUMANITIES': 'maj_social',
    'BUSINESS & MANAGEMENT': 'maj_business',
    'EDUCATION & SOCIAL SERVICES': 'maj_education',
    'ENGINEERING & TECHNOLOGY': 'maj_engineering',
    'NATURAL & HEALTH SCIENCES': 'maj_natural',
}

JOB_NAMES = {
    'Arts, Media & Legal': 'job_arts',
    'Education & Service': 'job_education',
    'Business & Finance': 'job_business',
    'Technology & Engineering': 'job_tech',
    'Healthcare & Science': 'job_health',
}

MAJOR_ORDER = list(MAJOR_NAMES.keys())
JOB_ORDER = list(JOB_NAMES.keys())

# ============ FUNCTIONS ============

def generate_circos_files():
    """Generate karyotype.txt and links.txt from CSV"""
    print("[1/3] Reading CSV data...")
    df = pd.read_csv(CSV_FILE)

    flow_data = df.groupby(['Large Major Cluster', 'Large Job Title Cluster']).size().reset_index(name='count')
    major_totals = df.groupby('Large Major Cluster').size().reset_index(name='total')
    job_totals = df.groupby('Large Job Title Cluster').size().reset_index(name='total')

    os.makedirs('circos/data', exist_ok=True)

    # Build karyotype
    print("[2/3] Generating karyotype.txt...")
    karyotype_lines = []
    major_positions = {}
    job_positions = {}
    pos = 0

    for major in MAJOR_ORDER:
        total = major_totals[major_totals['Large Major Cluster'] == major]['total'].values[0]
        size = max(total, 5)
        chr_name = MAJOR_NAMES[major]
        color = COLOR_MAP[major]

        major_positions[major] = (chr_name, pos, pos + size)
        karyotype_lines.append(f"chr - {chr_name} {chr_name} {pos} {pos+size} {color}")
        pos += size + 2

    for job in JOB_ORDER:
        total = job_totals[job_totals['Large Job Title Cluster'] == job]['total'].values[0]
        size = max(total, 5)
        chr_name = JOB_NAMES[job]

        job_positions[job] = (chr_name, pos, pos + size)
        karyotype_lines.append(f"chr - {chr_name} {chr_name} {pos} {pos+size} {CAREER_COLOR}")
        pos += size + 2

    with open('circos/data/karyotype.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(karyotype_lines))
    print(f"   -> Created: circos/data/karyotype.txt ({len(karyotype_lines)} chromosomes)")

    # Build links
    print("[2/3] Generating links.txt...")
    links_lines = []
    for _, row in flow_data.iterrows():
        major = row['Large Major Cluster']
        job = row['Large Job Title Cluster']

        major_chr, major_start, major_end = major_positions[major]
        job_chr, job_start, job_end = job_positions[job]
        color = COLOR_MAP[major]

        link_line = f"{major_chr} {major_start} {major_end} {job_chr} {job_start} {job_end} color={color}"
        links_lines.append(link_line)

    with open('circos/data/links.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(links_lines))
    print(f"   -> Created: circos/data/links.txt ({len(links_lines)} links)")

def run_circos():
    """Execute circos command"""
    print("[3/3] Running Circos...")

    try:
        # Use bash to run the command
        cmd = [
            'bash',
            '-c',
            'cd circos && /c/Strawberry/perl/bin/perl.exe /c/Users/hoang/circos/bin/circos -conf circos.conf'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"   -> SUCCESS! Generated: circos/circos.png")
            return True
        else:
            print(f"   -> ERROR running Circos:")
            if result.stderr:
                print(result.stderr[-500:])
            return False
    except subprocess.TimeoutExpired:
        print(f"   -> ERROR: Circos timed out")
        return False
    except Exception as e:
        print(f"   -> ERROR: {e}")
        return False

def main():
    print("====================================")
    print("Circos Major-to-Career Diagram")
    print("====================================\n")

    if not os.path.exists(CSV_FILE):
        print(f"ERROR: {CSV_FILE} not found!")
        sys.exit(1)

    generate_circos_files()
    success = run_circos()

    if success:
        print("\n" + "="*40)
        print("DONE! Your diagram is ready.")
        print("="*40)
    else:
        print("\nFailed to generate diagram. Check errors above.")

if __name__ == "__main__":
    main()
