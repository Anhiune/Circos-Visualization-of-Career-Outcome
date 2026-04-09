# Circos Major-to-Career Diagram Generator

## Files Included

1. **generate_circos_data.py** - Python script to convert your CSV to Circos format
2. **circos/circos.conf** - Circos configuration file
3. **This README**

## Prerequisites

1. **Python 3** (with pandas)
2. **Circos** software installed

### Install Circos

**Option A: Download from circos.ca**
```bash
# Download
curl -L http://circos.ca/distribution/circos-0.69-9.tgz -o circos.tgz
tar -xzf circos.tgz
mv circos-0.69-9 /path/to/circos

# Add to PATH (Windows/Bash)
export PATH="/path/to/circos/bin:$PATH"
```

**Option B: Using conda (if available)**
```bash
conda install -c bioconda circos
```

## How to Use

### Step 1: Prepare your data
Place your CSV file in the same directory:
```
Major_Job_Cluster_Lookup_Filtered.csv
```

### Step 2: Generate Circos data files
```bash
python generate_circos_data.py
```

This creates:
- `circos/data/karyotype.txt` - Chromosome definitions
- `circos/data/links.txt` - Connection data

### Step 3: Run Circos
```bash
cd circos
circos -conf circos.conf
```

This generates: **circos.png**

## Configuration Details

### Colors (in circos.conf)
- **Blues** (#5B7FA6, #4A6FA5): Arts, Languages, Communication
- **Oranges/Browns** (#C8915F, #C17E47, #C99070): Social Sciences, Business, Education
- **Greens** (#7CB342, #558B2F): Natural Sciences, Engineering
- **Gray** (#8B8B8B): Careers (neutral background)

### Customization

**To change colors:** Edit `circos.conf` in the `<rules>` section:
```
<rule>
condition = /^maj_business$/
fill_color = #NEW_COLOR
</rule>
```

**To change diagram size:** Edit `circos.conf`:
```
<image>
radius = 1500p  # Change this value
</image>
```

**To change label size:** Edit in `<ideogram>`:
```
label_size = 18p  # Change font size
```

**To change ribbon transparency:** Edit in `<links>`:
```
thickness = 2p  # Change ribbon thickness
```

## Troubleshooting

**Error: "No such child element 'include'"**
- Make sure Circos `etc/` directory is in the same parent directory as `circos.conf`

**Error: "Perl modules not found"**
- Use Strawberry Perl (Windows) or ensure Perl core modules are installed
- Path: https://strawberryperl.com/

**Black/empty diagram**
- Check that `data/karyotype.txt` and `data/links.txt` exist
- Verify file paths in `circos.conf` are correct

**Missing labels**
- Ensure `label_font = condensed` and `show_label = yes` in ideogram block

## Tips

1. Keep chromosome names alphanumeric + underscore only
2. Colors should be in hex format (#RRGGBB)
3. Always run `circos` command from the circos directory (where circos.conf is)
4. The links file format must be: `chr_src start_src end_src chr_tgt start_tgt end_tgt [options]`

## Output

The PNG file will be created in the same directory as `circos.conf`:
```
circos/circos.png
```

## For more help

Official Circos documentation: http://circos.ca/documentation/
