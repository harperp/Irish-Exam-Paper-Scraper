# Exam Material Scraper

A Python script to download PDF examination materials from the State Examinations Commission archive at examinations.ie.

## Features

- Automated dropdown navigation
- PDF discovery and download
- Logical file naming based on exam material descriptions
- Interactive mode for manual selection
- Automatic handling of terms and conditions
- Skip already downloaded files

## Installation

1. Install Python dependencies:
```bash
pip3 install --user -r requirements.txt
```

2. Install ChromeDriver locally (no sudo required):
```bash
./setup_chromedriver_local.sh
```

This will download ChromeDriver to a local `drivers/` directory.

## Usage

### Quick Start - Organized Downloads (Recommended)

Use `download_exams_v2.py` for organized downloads with the structure: `Examination/Subject/Level/YEAR_filename.pdf`

```bash
# Download all Junior Cert History papers (all years, English & Bilingual only - default)
python3 download_exams_v2.py --cert jc --subject history

# Download Leaving Cert Mathematics for a specific year (English only)
python3 download_exams_v2.py --cert lc --subject mathematics --year 2024 --language EV

# Download multiple years with range (all language versions)
python3 download_exams_v2.py --cert lc --subject english --year-range 2020-2024 --language all

# Download marking schemes instead of papers (Irish version only)
python3 download_exams_v2.py --cert lc --subject physics --year 2024 --type markingschemes --language IV
```

**Directory structure created:**
```
downloads/
  └── Leaving_Certificate/
      └── Mathematics/
          ├── Higher/
          │   ├── 2024_Paper_One_Higher_Level_(EV).pdf
          │   ├── 2024_Paper_One_Higher_Level_(IV).pdf
          │   └── ...
          ├── Ordinary/
          │   ├── 2024_Paper_One_Ordinary_Level_(EV).pdf
          │   └── ...
          └── Foundation/
              └── 2024_Foundation_Level_(EV).pdf
```

**Available options:**
- **Certificates**: `lc` (Leaving Cert), `jc` (Junior Cert), `lca` (Leaving Cert Applied)
- **Material types**: `exampapers`, `markingschemes`, `deferredexams`, `deferredmarkingschemes`
- **Years**: Single year (`--year 2024`), range (`--year-range 2020-2024`), or all years (omit both)
- **Languages**: Default is EV,BV (English & Bilingual only)
  - `--language EV` - English only
  - `--language IV` - Irish only
  - `--language BV` - Bilingual only
  - `--language EV,BV` - English and Bilingual (default)
  - `--language all` - All language versions

### Alternative: Download All Subjects

Use `download_all_subjects.py` to download all subjects for a specific year:

```bash
# Download ALL Leaving Cert 2024 exam papers (56 subjects)
python3 download_all_subjects.py --year 2024 --level lc

# List available subjects
python3 download_all_subjects.py --year 2024 --level lc --list-subjects
```

### Interactive Mode (Recommended for exploration)

Run the script in interactive mode to explore dropdowns and select options:

```bash
python3 exam_scraper.py --interactive
```

This will:
1. Load the webpage
2. Display all available dropdowns and their options
3. Let you select options step-by-step
4. Download PDFs when they become available

### Advanced Usage

Discover what dropdowns are available:

```bash
python3 exam_scraper.py
```

Custom options:

```bash
# Specify custom URL
python3 exam_scraper.py --url "https://www.examinations.ie/exammaterialarchive/?i=..."

# Specify output directory
python3 exam_scraper.py --output "my_exams"

# Combine options
python3 exam_scraper.py --interactive --output "leaving_cert_2023"
```

## Programmatic Usage

You can also use the scraper in your own Python code:

```python
from exam_scraper import ExamScraper

# Initialize scraper
scraper = ExamScraper(
    base_url='https://www.examinations.ie/exammaterialarchive/?i=91.97.108.95.95.104',
    download_dir='my_downloads'
)

# Run with specific dropdown selections
# Note: You need to discover the dropdown IDs/names first
scraper.scrape(dropdown_selections={
    'year': '2023',
    'subject': 'mathematics',
    'level': 'higher'
})
```

## File Organization

Downloaded PDFs are automatically named based on their description on the website and saved to the `downloads/` directory (or your specified output directory).

For example:
- `Leaving_Certificate_Mathematics_Higher_Level_2023.pdf`
- `Junior_Certificate_English_Ordinary_Level_Marking_Scheme_2022.pdf`

## Troubleshooting

### ChromeDriver Issues

If you get a ChromeDriver error, ensure:
1. Chrome browser is installed
2. ChromeDriver is installed and in your PATH
3. ChromeDriver version matches your Chrome version

### Headless Mode

The script runs in headless mode by default. To see the browser in action (useful for debugging), edit [exam_scraper.py](exam_scraper.py) and remove this line:
```python
options.add_argument('--headless')
```

### No Dropdowns Found

If no dropdowns are found, the page structure may have changed or the specific URL may not contain dropdown elements. Try:
1. Verifying the URL in a browser
2. Running in non-headless mode to see what's happening
3. Checking if the page requires JavaScript to load dropdowns

## Notes

- The script respects the terms and conditions checkbox automatically
- Downloads are skipped if the file already exists
- The script includes delays to allow dynamic content to load
- PDF URLs and page structure may change over time

### Handling Connection Errors

If you see "Connection refused" or "Max retries exceeded" errors:

✅ **The script automatically retries** - Each file is retried 3 times with delays
✅ **Just re-run the command** - Already downloaded files are skipped automatically
✅ **Download in batches** - Use `--year-range` to download smaller chunks

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

## License

MIT License - Feel free to modify and use as needed.
