#!/usr/bin/env python3
"""
Enhanced exam downloader with improved organization
Structure: Examination/Subject/Level/YEAR_filename.pdf
"""

import sys
import time
import re
import argparse
from pathlib import Path
from exam_scraper import ExamScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service


def get_all_subjects(base_url, material_type, year, cert_level):
    """Get list of all available subjects for given parameters"""
    print(f"Fetching list of available subjects for {cert_level.upper()} {year}...")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    local_driver = Path(__file__).parent / 'drivers' / 'chromedriver'
    if local_driver.exists():
        service = Service(executable_path=str(local_driver))
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    try:
        driver.get(base_url)
        time.sleep(2)

        # Accept terms
        try:
            checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(1)
        except:
            pass

        # Select material type
        type_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__ViewType')
        Select(type_dropdown).select_by_value(material_type)
        time.sleep(2)

        # Select year
        year_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__YearSelect')
        Select(year_dropdown).select_by_value(str(year))
        time.sleep(2)

        # Select level
        level_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__ExaminationSelect')
        Select(level_dropdown).select_by_value(cert_level)
        time.sleep(2)

        # Get subjects
        subject_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__SubjectSelect')
        select = Select(subject_dropdown)
        subjects = [(opt.get_attribute('value'), opt.text)
                   for opt in select.options if opt.get_attribute('value')]

        return subjects

    finally:
        driver.quit()


class EnhancedExamScraper(ExamScraper):
    """Extended scraper with better file organization"""

    def __init__(self, base_url, download_dir, year, exam_level, subject_name, language_filter=None):
        # Don't call parent __init__ yet, we need to set up directory first
        self.base_url = base_url
        self.year = year
        self.exam_level = exam_level  # LC, JC, LCA
        self.subject_name = subject_name
        self.language_filter = language_filter or ['EV', 'BV']  # Default: English and Bilingual only

        # Create directory structure: Examination/Subject/Level/
        base_path = Path(download_dir)

        # Map exam level to full name
        exam_names = {
            'lc': 'Leaving_Certificate',
            'jc': 'Junior_Certificate',
            'lca': 'Leaving_Certificate_Applied'
        }
        exam_dir = exam_names.get(exam_level.lower(), exam_level)

        self.base_download_dir = base_path / exam_dir / subject_name
        self.base_download_dir.mkdir(parents=True, exist_ok=True)

        # We'll set download_dir per level when we find PDFs
        self.download_dir = self.base_download_dir
        self.download_dir.mkdir(exist_ok=True)

        # Now initialize the rest from parent
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        local_driver = Path(__file__).parent / 'drivers' / 'chromedriver'
        if local_driver.exists():
            from selenium.webdriver.chrome.service import Service
            service = Service(executable_path=str(local_driver))
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)

        self.wait = WebDriverWait(self.driver, 10)

    def organize_file(self, pdf_info):
        """Determine the level subdirectory and filename with year prefix"""
        text = pdf_info['text'].lower()

        # Determine level from text
        if 'higher' in text or 'higher level' in text:
            level_dir = 'Higher'
        elif 'ordinary' in text or 'ordinary level' in text:
            level_dir = 'Ordinary'
        elif 'foundation' in text:
            level_dir = 'Foundation'
        else:
            level_dir = 'Other'

        # Create level directory
        level_path = self.base_download_dir / level_dir
        level_path.mkdir(exist_ok=True)

        # Create filename with year prefix
        if pdf_info.get('filename_hint'):
            filename = pdf_info['filename_hint']
        else:
            filename = self.sanitize_filename(pdf_info['text'])
            if not filename.endswith('.pdf'):
                filename = f"{filename}.pdf"

        # Add year prefix if not already there
        if not filename.startswith(str(self.year)):
            filename = f"{self.year}_{filename}"

        return level_path / filename

    def scrape(self, dropdown_selections=None):
        """Override scrape to use new organization"""
        try:
            print(f"Loading page: {self.base_url}")
            self.driver.get(self.base_url)
            time.sleep(2)

            # Accept terms
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                if not checkbox.is_selected():
                    checkbox.click()
                    time.sleep(1)
            except:
                pass

            # Apply selections
            if dropdown_selections:
                for selector, value in dropdown_selections.items():
                    try:
                        time.sleep(1)
                        dropdown = self.driver.find_element(
                            By.CSS_SELECTOR,
                            f'select[id="{selector}"], select[name="{selector}"]'
                        )
                        from selenium.webdriver.support.ui import Select
                        Select(dropdown).select_by_value(value)
                        time.sleep(2)
                    except Exception as e:
                        print(f"✗ Error selecting {selector}: {e}")

            # Find PDF links
            pdf_links = self.find_pdf_links()

            if not pdf_links:
                print("No PDF links found")
                return

            print(f"Found {len(pdf_links)} PDF link(s)")

            # Filter by language
            if self.language_filter:
                original_count = len(pdf_links)
                pdf_links = [
                    pdf for pdf in pdf_links
                    if any(f"({lang})" in pdf['text'] or f"({lang.lower()})" in pdf['text'].lower()
                           for lang in self.language_filter)
                ]
                if original_count != len(pdf_links):
                    print(f"Filtered to {len(pdf_links)} PDF(s) based on language: {', '.join(self.language_filter)}")

            if not pdf_links:
                print("No PDFs match the language filter")
                return

            # Download PDFs with new organization
            for pdf in pdf_links:
                filepath = self.organize_file(pdf)

                # Skip if already downloaded
                if filepath.exists():
                    print(f"  ✓ Already exists: {filepath.name}")
                    continue

                # Download with retry logic
                import requests
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Create session with retry strategy
                        session = requests.Session()
                        retry_strategy = Retry(
                            total=3,
                            backoff_factor=2,
                            status_forcelist=[429, 500, 502, 503, 504],
                        )
                        adapter = HTTPAdapter(max_retries=retry_strategy)
                        session.mount("http://", adapter)
                        session.mount("https://", adapter)

                        # Add delay between downloads to avoid rate limiting
                        if attempt > 0:
                            wait_time = 5 * (attempt + 1)
                            print(f"  ⏳ Retry {attempt + 1}/{max_retries}, waiting {wait_time}s...")
                            time.sleep(wait_time)

                        response = session.get(pdf['url'], stream=True, timeout=30)
                        response.raise_for_status()

                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        print(f"  ✓ Downloaded: {filepath.parent.name}/{filepath.name}")

                        # Configurable delay between successful downloads
                        time.sleep(2)  # Default 2 seconds between files
                        break

                    except requests.exceptions.ConnectionError as e:
                        if attempt == max_retries - 1:
                            print(f"  ✗ Connection failed after {max_retries} attempts: {filepath.name}")
                        continue
                    except Exception as e:
                        print(f"  ✗ Error downloading {filepath.name}: {e}")
                        break

        finally:
            self.driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description='Download Irish exam materials with organized structure'
    )
    parser.add_argument(
        '--cert',
        choices=['lc', 'jc', 'lca'],
        required=True,
        help='Certificate: lc (Leaving Cert), jc (Junior Cert), lca (Leaving Cert Applied)'
    )
    parser.add_argument(
        '--subject',
        type=str,
        required=True,
        help='Subject name (e.g., mathematics, history, english)'
    )
    parser.add_argument(
        '--paper-level',
        choices=['higher', 'ordinary', 'foundation', 'all'],
        default='all',
        help='Paper level (note: this filters results, not the scraping)'
    )
    parser.add_argument(
        '--year',
        type=str,
        help='Specific year (e.g., 2024) or leave blank for all years'
    )
    parser.add_argument(
        '--year-range',
        type=str,
        help='Year range (e.g., 2020-2024)'
    )
    parser.add_argument(
        '--type',
        choices=['exampapers', 'markingschemes', 'deferredexams', 'deferredmarkingschemes'],
        default='exampapers',
        help='Material type (default: exampapers)'
    )
    parser.add_argument(
        '--output',
        default='downloads',
        help='Output base directory (default: downloads)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay in seconds between downloads (default: 2.0, increase if getting connection errors)'
    )
    parser.add_argument(
        '--language',
        type=str,
        default='EV,BV',
        help='Language versions to download: EV (English), IV (Irish), BV (Bilingual), or "all". Comma-separated. Default: EV,BV'
    )

    args = parser.parse_args()

    # Determine years to download
    years = []
    if args.year:
        years = [args.year]
    elif args.year_range:
        start, end = args.year_range.split('-')
        years = [str(y) for y in range(int(start), int(end) + 1)]
    else:
        # All available years
        years = [str(y) for y in range(1995, 2026)]

    base_url = 'https://www.examinations.ie/exammaterialarchive/?i=91.97.108.95.95.104'

    # Parse language filter
    if args.language.lower() == 'all':
        language_filter = None  # Download all languages
    else:
        language_filter = [lang.strip().upper() for lang in args.language.split(',')]

    print(f"Downloading {args.type} for {args.cert.upper()} {args.subject}")
    print(f"Years: {years[0]}-{years[-1]} ({len(years)} years)")
    print(f"Languages: {', '.join(language_filter) if language_filter else 'All'}")
    print(f"Output: {args.output}")
    print("="*60)

    total_downloaded = 0

    for year in years:
        print(f"\n{'='*60}")
        print(f"Processing year: {year}")
        print('='*60)

        # Get subjects for this year
        try:
            subjects = get_all_subjects(base_url, args.type, year, args.cert)
        except Exception as e:
            print(f"✗ Error fetching subjects for {year}: {e}")
            continue

        # Find matching subject
        matching_subjects = [(v, t) for v, t in subjects
                            if args.subject.lower() in t.lower() or args.subject.lower() in v.lower()]

        if not matching_subjects:
            print(f"✗ Subject '{args.subject}' not found for {year}")
            continue

        # Download for each matching subject
        for subject_value, subject_text in matching_subjects:
            print(f"\nDownloading: {subject_text}")

            try:
                scraper = EnhancedExamScraper(
                    base_url,
                    args.output,
                    year,
                    args.cert,
                    subject_text.replace('/', '_'),
                    language_filter=language_filter
                )

                selections = {
                    'MaterialArchive__noTable__sbv__ViewType': args.type,
                    'MaterialArchive__noTable__sbv__YearSelect': year,
                    'MaterialArchive__noTable__sbv__ExaminationSelect': args.cert,
                    'MaterialArchive__noTable__sbv__SubjectSelect': subject_value
                }

                scraper.scrape(dropdown_selections=selections)
                total_downloaded += 1

            except Exception as e:
                print(f"✗ Error processing {subject_text} for {year}: {e}")

        # Longer delay between years to avoid rate limiting
        if len(years) > 1:
            print(f"⏳ Waiting 5 seconds before next year...")
            time.sleep(5)

    print("\n" + "="*60)
    print(f"✓ Complete! Processed {total_downloaded} year/subject combinations")

    # Show directory structure
    exam_names = {
        'lc': 'Leaving_Certificate',
        'jc': 'Junior_Certificate',
        'lca': 'Leaving_Certificate_Applied'
    }
    final_path = Path(args.output) / exam_names[args.cert]
    print(f"✓ Files saved to: {final_path}")


if __name__ == '__main__':
    main()
