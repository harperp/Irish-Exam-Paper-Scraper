# ExamScraper Quick Start Guide

## Installation (One-time setup)

```bash
# 1. Install Python packages
pip3 install --user -r requirements.txt

# 2. Install ChromeDriver locally
./setup_chromedriver_local.sh
```

## Common Commands

### Download all years for a subject

```bash
# Junior Cert History (all years, English & Bilingual only - default)
python3 download_exams_v2.py --cert jc --subject history

# Leaving Cert Mathematics (all years, English only)
python3 download_exams_v2.py --cert lc --subject mathematics --language EV

# Leaving Cert English (all years, all language versions)
python3 download_exams_v2.py --cert lc --subject english --language all
```

### Download specific year

```bash
# 2024 only
python3 download_exams_v2.py --cert lc --subject mathematics --year 2024
```

### Download year range

```bash
# Last 5 years (2020-2024)
python3 download_exams_v2.py --cert lc --subject physics --year-range 2020-2024
```

### Download marking schemes

```bash
# Add --type markingschemes
python3 download_exams_v2.py --cert lc --subject chemistry --year 2024 --type markingschemes
```

## Quick Reference

| Option | Values |
|--------|--------|
| `--cert` | `lc` `jc` `lca` |
| `--subject` | `mathematics` `english` `history` `physics` etc. |
| `--year` | `2024` `2023` etc. (or omit for all years) |
| `--year-range` | `2020-2024` |
| `--type` | `exampapers` `markingschemes` `deferredexams` `deferredmarkingschemes` |
| `--language` | `EV,BV` (default), `EV` (English), `IV` (Irish), `BV` (Bilingual), `all` |

## Language Versions

PDF files have language codes in their names:
- **(EV)** = English Version
- **(IV)** = Irish Version (Gaeilge)
- **(BV)** = Bilingual Version

**By default**, only English (EV) and Bilingual (BV) versions are downloaded. Use `--language all` to download all versions including Irish.

## Output Structure

Files are saved as: `Examination/Subject/Level/YEAR_filename.pdf`

Example:
```
downloads/
  └── Leaving_Certificate/
      └── History/
          ├── Higher/
          │   ├── 2024_Higher_Level_(EV).pdf
          │   ├── 2024_Higher_Level_(BV).pdf
          │   ├── 2023_Higher_Level_(EV).pdf
          │   └── ...
          └── Ordinary/
              ├── 2024_Ordinary_Level_(EV).pdf
              └── ...
```

## Subject Names

Common subjects (use with `--subject`):
- Core: `mathematics`, `english`, `irish`
- Sciences: `physics`, `chemistry`, `biology`, `agricultural science`
- Languages: `french`, `german`, `spanish`, `italian`
- Humanities: `history`, `geography`, `business`, `economics`
- Other: `art`, `music`, `accounting`, `computer science`

Tip: Subject names are fuzzy-matched, so `math` will match `mathematics`.

## Tips

1. **Start small**: Test with one year first before downloading all years
2. **Be patient**: Downloading all years can take 10-15 minutes per subject
3. **Already downloaded**: Files are automatically skipped if they exist
4. **Multiple subjects**: Run the command multiple times for different subjects
