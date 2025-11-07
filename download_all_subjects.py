#!/usr/bin/env python3
"""
Download exam materials for all subjects in a given year and level
"""

import sys
import time
import argparse
from pathlib import Path
from exam_scraper import ExamScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service


def get_all_subjects(base_url, material_type, year, level):
    """Get list of all available subjects for given parameters"""
    print("Fetching list of available subjects...")

    # Setup Selenium with Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Check for local chromedriver
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
        type_dropdown = driver.find_element(
            By.ID, 'MaterialArchive__noTable__sbv__ViewType'
        )
        Select(type_dropdown).select_by_value(material_type)
        time.sleep(2)

        # Select year
        year_dropdown = driver.find_element(
            By.ID, 'MaterialArchive__noTable__sbv__YearSelect'
        )
        Select(year_dropdown).select_by_value(year)
        time.sleep(2)

        # Select level
        level_dropdown = driver.find_element(
            By.ID, 'MaterialArchive__noTable__sbv__ExaminationSelect'
        )
        Select(level_dropdown).select_by_value(level)
        time.sleep(2)

        # Get subjects
        subject_dropdown = driver.find_element(
            By.ID, 'MaterialArchive__noTable__sbv__SubjectSelect'
        )
        select = Select(subject_dropdown)
        subjects = [(opt.get_attribute('value'), opt.text)
                   for opt in select.options if opt.get_attribute('value')]

        print(f"Found {len(subjects)} subjects")
        return subjects

    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description='Download exam materials for all subjects'
    )
    parser.add_argument(
        '--type',
        choices=['exampapers', 'markingschemes', 'deferredexams', 'deferredmarkingschemes'],
        default='exampapers',
        help='Type of material to download (default: exampapers)'
    )
    parser.add_argument(
        '--year',
        type=str,
        default='2024',
        help='Year to download (e.g., 2024, 2023)'
    )
    parser.add_argument(
        '--level',
        choices=['lca', 'lc', 'jc'],
        default='lc',
        help='Certificate level (default: lc)'
    )
    parser.add_argument(
        '--subject',
        type=str,
        help='Download specific subject only (e.g., mathematics, english). If not specified, downloads all subjects.'
    )
    parser.add_argument(
        '--output',
        default='downloads',
        help='Output directory (default: downloads)'
    )
    parser.add_argument(
        '--list-subjects',
        action='store_true',
        help='List all available subjects and exit'
    )

    args = parser.parse_args()

    base_url = 'https://www.examinations.ie/exammaterialarchive/?i=91.97.108.95.95.104'

    # Get list of subjects
    subjects = get_all_subjects(base_url, args.type, args.year, args.level)

    if args.list_subjects:
        print(f"\nAvailable subjects for {args.level.upper()} {args.year} {args.type}:")
        print("="*60)
        for value, text in subjects:
            print(f"  {value:30s} - {text}")
        return

    # Filter to specific subject if requested
    if args.subject:
        subjects = [(v, t) for v, t in subjects
                   if args.subject.lower() in v.lower() or args.subject.lower() in t.lower()]
        if not subjects:
            print(f"Error: Subject '{args.subject}' not found")
            print("Use --list-subjects to see available subjects")
            sys.exit(1)

    print(f"\nDownloading {args.type} for {len(subjects)} subject(s)")
    print(f"Year: {args.year}, Level: {args.level.upper()}")
    print(f"Output directory: {args.output}")
    print("="*60)

    # Create output directory structure
    output_base = Path(args.output) / f"{args.year}_{args.level}_{args.type}"
    output_base.mkdir(parents=True, exist_ok=True)

    # Download each subject
    for i, (subject_value, subject_text) in enumerate(subjects, 1):
        print(f"\n[{i}/{len(subjects)}] Processing: {subject_text}")
        print("-" * 60)

        # Create subject-specific output directory
        subject_dir = output_base / subject_text.replace('/', '_')
        subject_dir.mkdir(exist_ok=True)

        try:
            scraper = ExamScraper(base_url, str(subject_dir))

            selections = {
                'MaterialArchive__noTable__sbv__ViewType': args.type,
                'MaterialArchive__noTable__sbv__YearSelect': args.year,
                'MaterialArchive__noTable__sbv__ExaminationSelect': args.level,
                'MaterialArchive__noTable__sbv__SubjectSelect': subject_value
            }

            scraper.scrape(dropdown_selections=selections)

        except Exception as e:
            print(f"  ✗ Error processing {subject_text}: {e}")
            continue

        # Small delay between subjects
        time.sleep(1)

    print("\n" + "="*60)
    print(f"✓ Complete! Files saved to: {output_base}")


if __name__ == '__main__':
    main()
