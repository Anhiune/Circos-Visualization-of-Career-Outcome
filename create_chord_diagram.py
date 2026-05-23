#!/usr/bin/env python3
"""
Generate a chord diagram matching the Williams College major-to-career visualization
using matplotlib and custom bezier curves
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, Wedge
from matplotlib.path import Path
import matplotlib.patches as patches

# Read data
df = pd.read_csv('Major_Job_Cluster_Lookup_Filtered.csv')

# Color mapping matching the website design
COLOR_MAP = {
    'ARTS, LANGUAGES & THEOLOGY': '#5B7FA6',      # Blue
    'COMMUNICATION & MEDIA': '#4A6FA5',            # Blue
    'SOCIAL SCIENCES & HUMANITIES': '#C8915F',   #Orange-brown
    'BUSINESS & MANAGEMENT': '#C17E47',            # Orange
    'EDUCATION & SOCIAL SERVICES': '#C99070',    # Peachy brown
    'NATURAL & HEALTH SCIENCES': '#7CB342',       # Green
    'ENGINEERING & TECHNOLOGY': '#558B2F',        # Dark green
}

CAREER_COLOR = '#8B8B8B'  # Neutral gray

# Aggregate data
flow_data = df.groupby(['Large Major Cluster', 'Large Job Title Cluster']).size().reset_index(name='count')
major_totals = df.groupby('Large Major Cluster').size().reset_index(name='total')
job_totals = df.groupby('Large Job Title Cluster').size().reset_index(name='total')

# Ordering
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

# Calculate positions
def calculate_positions(items, totals_df, start_angle=0, end_angle=360, inner_radius=0.5, outer_radius=1.0):
    """
    Calculate angular positions for chord diagram segments
    """
    positions = {}

    # totals_df is now indexed with major/job name, so access by index
    # Get totals and normalize to angles
    total_all = 0
    for item in items:
        if item in totals_df.index:
            total = totals_df.loc[item, 'total']
        else:
            total = 0
        total_all += total

    current_angle = start_angle
    for item in items:
        if item in totals_df.index:
            total = totals_df.loc[item, 'total']
        else:
            total = 0
        # Allocate angle proportionally
        angle_span = (total / total_all) * (end_angle - start_angle)

        positions[item] = {
            'start_angle': current_angle,
            'end_angle': current_angle + angle_span,
            'mid_angle': current_angle + angle_span / 2,
            'inner_radius': inner_radius,
            'outer_radius': outer_radius,
        }
        current_angle += angle_span

    return positions

# Get positions
major_df_idx = major_totals.set_index('Large Major Cluster')[['total']]
job_df_idx = job_totals.set_index('Large Job Title Cluster')[['total']]

major_positions = calculate_positions(major_order, major_df_idx,
                                      start_angle=-90, end_angle=180,
                                      inner_radius=0.65, outer_radius=0.95)
job_positions = calculate_positions(job_order, job_df_idx,
                                    start_angle=180, end_angle=450,
                                    inner_radius=0.65, outer_radius=0.95)

# Helper functions
def polar_to_cartesian(angle_deg, radius):
    """Convert polar to cartesian coordinates"""
    angle_rad = np.radians(angle_deg)
    return radius * np.cos(angle_rad), radius * np.sin(angle_rad)

def draw_arc_wedge(ax, inner_r, outer_r, start_angle, end_angle, color, alpha=1.0):
    """Draw a wedge/arc segment"""
    wedge = Wedge((0, 0), outer_r, start_angle, end_angle,
                  width=outer_r-inner_r, facecolor=color, edgecolor='white',
                  linewidth=2, alpha=alpha, zorder=2)
    ax.add_patch(wedge)

def draw_ribbon(ax, major_pos, job_pos, major_color, count, max_count, alpha=0.5):
    """Draw a ribbon between major and job segments"""
    # Get the angular positions
    major_start = major_pos['start_angle']
    major_end = major_pos['end_angle']
    major_mid = major_pos['mid_angle']

    job_start = job_pos['start_angle']
    job_end = job_pos['end_angle']
    job_mid = job_pos['mid_angle']

    major_inner = major_pos['inner_radius']
    major_outer = major_pos['outer_radius']
    job_inner = job_pos['inner_radius']
    job_outer = job_pos['outer_radius']

    # Ribbon starts from major arc, ends at job arc
    # Create bezier-like curves
    p1 = polar_to_cartesian(major_mid, major_inner)
    p2 = polar_to_cartesian(major_mid, major_outer)
    p3 = polar_to_cartesian(job_mid, job_inner)
    p4 = polar_to_cartesian(job_mid, job_outer)

    # Create ribbon polygon (4-point polygon that curves)
    # For simplicity, use straight lines in bezier approximation

    # More sophisticated: create a ribbon shape
    num_segments = 10
    ribbon_points_outer = []
    ribbon_points_inner = []

    t_vals = np.linspace(0, 1, num_segments)

    for t in t_vals:
        # Bezier interpolation for angles
        angle_m = major_mid + t * (job_mid - major_mid)
        # Adjust for wrapping
        if job_mid < major_mid:
            angle_m = major_mid + t * ((job_mid + 360) - major_mid)

        angle_m = angle_m % 360

        # Outer and inner arcs of ribbon
        r_outer = major_outer + t * (job_outer - major_outer)
        r_inner = major_inner + t * (job_inner - major_inner)

        ribbon_points_outer.append(polar_to_cartesian(angle_m, r_outer))
        ribbon_points_inner.append(polar_to_cartesian(angle_m, r_inner))

    # Create closed polygon
    ribbon_points = ribbon_points_outer + ribbon_points_inner[::-1]

    if len(ribbon_points) > 2:
        polygon = Polygon(ribbon_points, closed=True, facecolor=major_color,
                         alpha=alpha, edgecolor='none', zorder=1)
        ax.add_patch(polygon)

# Create figure
fig, ax = plt.subplots(figsize=(16, 16), facecolor='white')
ax.set_aspect('equal')
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.axis('off')

# Draw major arcs (colored)
for major in major_order:
    pos = major_positions[major]
    color = COLOR_MAP[major]
    draw_arc_wedge(ax, pos['inner_radius'], pos['outer_radius'],
                   pos['start_angle'], pos['end_angle'], color, alpha=0.9)

# Draw job arcs (gray)
for job in job_order:
    pos = job_positions[job]
    draw_arc_wedge(ax, pos['inner_radius'], pos['outer_radius'],
                   pos['start_angle'], pos['end_angle'], CAREER_COLOR, alpha=0.8)

# Get max count for ribbon sizing
max_count = flow_data['count'].max()

# Draw ribbons (colored by major)
for _, row in flow_data.iterrows():
    major = row['Large Major Cluster']
    job = row['Large Job Title Cluster']
    count = row['count']

    major_pos = major_positions[major]
    job_pos = job_positions[job]
    major_color = COLOR_MAP[major]

    # Ribbon thickness and transparency based on count
    alpha = 0.4 + (count / max_count) * 0.3

    draw_ribbon(ax, major_pos, job_pos, major_color, count, max_count, alpha=alpha)

# Add labels for majors
for major in major_order:
    pos = major_positions[major]
    label_radius = 1.15
    label_angle = pos['mid_angle']

    x, y = polar_to_cartesian(label_angle, label_radius)

    # Rotate text to follow circle
    rotation = label_angle + 90
    if rotation > 180:
        rotation -= 180
        ha = 'right'
    else:
        ha = 'left'

    ax.text(x, y, major, fontsize=11, ha=ha, va='center',
           rotation=rotation, fontweight='bold', color='#2C3E50')

# Add labels for jobs
for job in job_order:
    pos = job_positions[job]
    label_radius = 1.15
    label_angle = pos['mid_angle']

    x, y = polar_to_cartesian(label_angle, label_radius)

    # Rotate text
    rotation = label_angle + 90
    if rotation > 180:
        rotation -= 180
        ha = 'right'
    else:
        ha = 'left'

    ax.text(x, y, job, fontsize=11, ha=ha, va='center',
           rotation=rotation, color='#555555')

plt.title('Major-to-Career Flows', fontsize=20, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('circos_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
print("[OK] Generated circos_diagram.png (300 DPI)")
plt.close()

# Also create a higher quality version for printing
plt.figure(figsize=(20, 20), facecolor='white')
ax = plt.gca()
ax.set_aspect('equal')
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.axis('off')

# Repeat the drawing for the high-res version
for major in major_order:
    pos = major_positions[major]
    color = COLOR_MAP[major]
    draw_arc_wedge(ax, pos['inner_radius'], pos['outer_radius'],
                   pos['start_angle'], pos['end_angle'], color, alpha=0.9)

for job in job_order:
    pos = job_positions[job]
    draw_arc_wedge(ax, pos['inner_radius'], pos['outer_radius'],
                   pos['start_angle'], pos['end_angle'], CAREER_COLOR, alpha=0.8)

for _, row in flow_data.iterrows():
    major = row['Large Major Cluster']
    job = row['Large Job Title Cluster']
    count = row['count']

    major_pos = major_positions[major]
    job_pos = job_positions[job]
    major_color = COLOR_MAP[major]

    alpha = 0.4 + (count / max_count) * 0.3
    draw_ribbon(ax, major_pos, job_pos, major_color, count, max_count, alpha=alpha)

for major in major_order:
    pos = major_positions[major]
    label_radius = 1.15
    label_angle = pos['mid_angle']
    x, y = polar_to_cartesian(label_angle, label_radius)
    rotation = label_angle + 90
    if rotation > 180:
        rotation -= 180
        ha = 'right'
    else:
        ha = 'left'
    ax.text(x, y, major, fontsize=13, ha=ha, va='center',
           rotation=rotation, fontweight='bold', color='#2C3E50')

for job in job_order:
    pos = job_positions[job]
    label_radius = 1.15
    label_angle = pos['mid_angle']
    x, y = polar_to_cartesian(label_angle, label_radius)
    rotation = label_angle + 90
    if rotation > 180:
        rotation -= 180
        ha = 'right'
    else:
        ha = 'left'
    ax.text(x, y, job, fontsize=13, ha=ha, va='center',
           rotation=rotation, color='#555555')

plt.savefig('circos_diagram_hires.png', dpi=600, bbox_inches='tight', facecolor='white')
print("[OK] Generated circos_diagram_hires.png (600 DPI - High Resolution)")

print("\nDiagrams created successfully!")
