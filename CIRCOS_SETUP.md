# Circos Installation Guide

Circos is a Perl-based command-line tool that renders chord diagrams. It is required for Steps 4, 7, and 9 of the pipeline (the steps that actually render SVG images from configuration files).

**If you only want to view the existing dashboards, you do not need to install Circos.**

---

## What Version Is Needed

Circos v0.69-9 (the current stable release as of 2026). The pipeline was developed and tested on this version.

---

## Installation: Windows

Windows requires a Perl distribution. The recommended option is Strawberry Perl, which includes the package manager (`cpan`) needed to install Circos's dependencies.

### Step 1 — Install Strawberry Perl

1. Download from [https://strawberryperl.com](https://strawberryperl.com)
2. Run the installer. Accept the default location (`C:\Strawberry`).
3. Verify: open a new PowerShell window and run:
   ```
   perl --version
   ```
   You should see `v5.32` or newer.

### Step 2 — Install Circos Perl dependencies

Open PowerShell (not Command Prompt) and run:

```powershell
cpan Config::General
cpan Math::Bezier
cpan Math::Round
cpan Math::VecStat
cpan Readonly
cpan Regexp::Common
cpan Set::IntSpan
cpan Statistics::Basic
cpan Text::Format
cpan List::MoreUtils
cpan GD
```

> The `GD` module may take several minutes to compile. If it fails, install the pre-compiled binary:
> ```
> cpan GD::SVG
> ```
> The pipeline uses SVG output only (not PNG), so `GD::SVG` is sufficient.

### Step 3 — Download and install Circos

1. Download the Circos distribution from [https://circos.ca/software/download/circos/](https://circos.ca/software/download/circos/)
2. Extract it to `C:\Users\<yourname>\circos`
3. Verify the structure:
   ```
   C:\Users\<yourname>\circos\
   ├── bin\
   │   └── circos          ← the main executable (no .pl extension on some versions)
   ├── etc\
   └── lib\
   ```

### Step 4 — Set the CIRCOS_ROOT environment variable

The pipeline scripts read `CIRCOS_ROOT` to find the Circos executable.

**Temporary (for this session only):**
```powershell
$env:CIRCOS_ROOT = "C:\Users\<yourname>\circos"
```

**Permanent (for all sessions):**
```powershell
[System.Environment]::SetEnvironmentVariable("CIRCOS_ROOT", "C:\Users\<yourname>\circos", "User")
```

Then close and reopen your terminal.

### Step 5 — Verify

```powershell
$env:CIRCOS_ROOT\bin\circos --version
```

Expected output: `circos | v 0.69-9` (or similar).

---

## Installation: macOS

### Step 1 — Install Perl dependencies

macOS comes with Perl pre-installed, but you need to install Circos modules. The easiest way is with `cpan` or `cpanm`:

```bash
# If you don't have cpanm:
curl -L https://cpanmin.us | perl - --sudo App::cpanminus

# Install Circos dependencies:
cpanm Config::General Math::Bezier Math::Round Math::VecStat Readonly \
       Regexp::Common Set::IntSpan Statistics::Basic Text::Format \
       List::MoreUtils GD
```

If `GD` fails to compile, install it via Homebrew first:

```bash
brew install gd
cpanm GD
```

### Step 2 — Download and install Circos

```bash
# Download (check circos.ca for the current version URL)
curl -O https://circos.ca/distribution/circos-0.69-9.tgz
tar xzf circos-0.69-9.tgz
mv circos-0.69-9 ~/circos
```

### Step 3 — Set CIRCOS_ROOT

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
export CIRCOS_ROOT="$HOME/circos"
export PATH="$CIRCOS_ROOT/bin:$PATH"
```

Reload: `source ~/.zshrc`

### Step 4 — Verify

```bash
circos --version
```

---

## Installation: Linux (Ubuntu/Debian)

### Step 1 — System dependencies

```bash
sudo apt-get update
sudo apt-get install -y perl libgd-dev cpanminus
```

### Step 2 — Perl modules

```bash
sudo cpanm Config::General Math::Bezier Math::Round Math::VecStat Readonly \
            Regexp::Common Set::IntSpan Statistics::Basic Text::Format \
            List::MoreUtils GD
```

### Step 3 — Download and install Circos

```bash
wget https://circos.ca/distribution/circos-0.69-9.tgz
tar xzf circos-0.69-9.tgz
mv circos-0.69-9 ~/circos
```

### Step 4 — Set CIRCOS_ROOT

Add to `~/.bashrc`:

```bash
export CIRCOS_ROOT="$HOME/circos"
export PATH="$CIRCOS_ROOT/bin:$PATH"
```

Reload: `source ~/.bashrc`

### Step 5 — Verify

```bash
circos --version
```

---

## Testing Your Circos Installation

After setting `CIRCOS_ROOT`, run the included test to confirm Circos is working before running the pipeline:

```bash
cd $CIRCOS_ROOT
circos -conf example/etc/circos.conf -outputdir /tmp/circos_test
```

If this produces `circos.svg` in `/tmp/circos_test/`, your installation is working.

---

## Troubleshooting

### "Can't locate Config/General.pm in @INC"

A Perl module is missing. Re-run the `cpanm` or `cpan` install command for `Config::General`.

### "GD module not available"

The GD image library is not installed. On Windows with Strawberry Perl, try:
```
cpan GD::SVG
```
The pipeline generates SVG output only, so `GD::SVG` is sufficient even if full `GD` fails.

### "circos: command not found" (macOS/Linux)

Check that `$CIRCOS_ROOT/bin` is in your `$PATH`, or call Circos with the full path:
```bash
$CIRCOS_ROOT/bin/circos -conf circos.conf
```

### Circos runs but produces an empty SVG

Open the generated `circos.conf` in a text editor and look for path errors (absolute paths from the development machine that don't exist on your machine). The most common cause is that `CIRCOS_ROOT` points to a different version than was used to generate the config.
