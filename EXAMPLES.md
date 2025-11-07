# ExamScraper Usage Examples

## Recommended: Organized Downloads (download_exams_v2.py)

This creates a clean structure: `Examination/Subject/Level/YEAR_filename.pdf`

### Download All Years for a Subject

```bash
# All Junior Cert History papers (English & Bilingual only - default)
python3 download_exams_v2.py --cert jc --subject history

# All Leaving Cert Mathematics papers (English only)
python3 download_exams_v2.py --cert lc --subject mathematics --language EV

# All Leaving Cert English marking schemes (all language versions)
python3 download_exams_v2.py --cert lc --subject english --type markingschemes --language all

# All Leaving Cert Irish papers (Irish version only)
python3 download_exams_v2.py --cert lc --subject irish --language IV
```

### Download Specific Years

```bash
# Single year
python3 download_exams_v2.py --cert lc --subject mathematics --year 2024

# Year range
python3 download_exams_v2.py --cert lc --subject history --year-range 2020-2024

# Last 5 years
python3 download_exams_v2.py --cert jc --subject science --year-range 2020-2024
```

### Download Different Material Types

```bash
# Exam papers (default)
python3 download_exams_v2.py --cert lc --subject physics --year 2024

# Marking schemes
python3 download_exams_v2.py --cert lc --subject chemistry --year 2024 --type markingschemes

# Deferred exams
python3 download_exams_v2.py --cert lc --subject biology --year 2024 --type deferredexams
```

## Alternative: Bulk Download (download_all_subjects.py)

### Download all subjects for a year

```bash
# All Leaving Cert 2024 exam papers (56 subjects)
python3 download_all_subjects.py --year 2024 --level lc

# All Junior Cert 2023 marking schemes
python3 download_all_subjects.py --year 2023 --level jc --type markingschemes
```

### Download all subjects

```bash
# All Leaving Cert 2024 exam papers (56 subjects)
python3 download_all_subjects.py --year 2024 --level lc

# All Junior Cert 2023 marking schemes
python3 download_all_subjects.py --year 2023 --level jc --type markingschemes

# All Leaving Cert Applied 2024 papers
python3 download_all_subjects.py --year 2024 --level lca
```

### List available content

```bash
# See all available subjects for Leaving Cert 2024
python3 download_all_subjects.py --year 2024 --level lc --list-subjects

# See all Junior Cert subjects
python3 download_all_subjects.py --year 2024 --level jc --list-subjects
```

### Custom output directories

```bash
# Save to specific directory
python3 download_all_subjects.py --year 2024 --level lc --subject mathematics --output my_exams

# Organize by year
python3 download_all_subjects.py --year 2023 --level lc --subject english --output exams_2023
```

## Output Structure

**With download_exams_v2.py (Organized by Level):**

```
downloads/
  └── Leaving_Certificate/
      └── Mathematics/
          ├── Higher/
          │   ├── 2024_Paper_One_Higher_Level_(EV).pdf
          │   ├── 2024_Paper_One_Higher_Level_(IV).pdf
          │   ├── 2023_Paper_One_Higher_Level_(EV).pdf
          │   └── ...
          ├── Ordinary/
          │   ├── 2024_Paper_One_Ordinary_Level_(EV).pdf
          │   ├── 2023_Paper_One_Ordinary_Level_(EV).pdf
          │   └── ...
          └── Foundation/
              ├── 2024_Foundation_Level_(EV).pdf
              └── ...
```

**With download_all_subjects.py (Organized by Year):**

```
downloads/
  └── 2024_lc_exampapers/
      ├── Mathematics/
      │   ├── Paper_One_Higher_Level_(EV).pdf
      │   ├── Paper_Two_Higher_Level_(EV).pdf
      │   └── ...
      ├── English/
      │   └── ...
      └── ...
```

Note: (EV) = English Version, (IV) = Irish Version (Gaeilge)

## Material Types

| Type | Description |
|------|-------------|
| `exampapers` | Regular exam papers |
| `markingschemes` | Marking schemes for exams |
| `deferredexams` | Deferred exam papers |
| `deferredmarkingschemes` | Marking schemes for deferred exams |

## Certificate Levels

| Level | Description |
|-------|-------------|
| `lc` | Leaving Certificate |
| `jc` | Junior Certificate / Cycle |
| `lca` | Leaving Certificate Applied |

## Common Subjects (use with --subject)

Some frequently requested subjects:
- `mathematics`
- `english`
- `irish`
- `french`
- `german`
- `spanish`
- `history`
- `geography`
- `biology`
- `chemistry`
- `physics`
- `business`
- `accounting`
- `economics`

Use `--list-subjects` to see all available subjects for your chosen year and level.

## Tips

1. **Start with one subject** to test: `python3 download_all_subjects.py --year 2024 --level lc --subject mathematics`

2. **Check what's available** before downloading: Use `--list-subjects` flag

3. **Be patient with large downloads**: Downloading all subjects can take 10-20 minutes

4. **Files are skipped if already downloaded**: You can safely re-run the script

5. **Organize by year**: Use `--output` to create separate folders for different years
