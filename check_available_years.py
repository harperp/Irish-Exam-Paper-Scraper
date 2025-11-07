#!/usr/bin/env python3
"""
Check what years and levels are available for a subject
"""

import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service


def check_availability(cert_level, subject_name):
    """Check what years are available for a cert level and subject"""
    base_url = 'https://www.examinations.ie/exammaterialarchive/?i=91.97.108.95.95.104'

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
        print(f"Checking availability for {cert_level.upper()} {subject_name}...")
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
        Select(type_dropdown).select_by_value('exampapers')
        time.sleep(2)

        # Get all years
        year_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__YearSelect')
        year_select = Select(year_dropdown)
        all_years = [opt.get_attribute('value') for opt in year_select.options if opt.get_attribute('value')]

        print(f"\nTotal years available: {len(all_years)}")

        available_years = []

        for year in all_years:
            # Select year
            Select(driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__YearSelect')).select_by_value(year)
            time.sleep(1)

            # Check if cert level is available
            try:
                level_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__ExaminationSelect')
                level_select = Select(level_dropdown)
                level_values = [opt.get_attribute('value') for opt in level_select.options if opt.get_attribute('value')]

                if cert_level in level_values:
                    # Select level
                    Select(level_dropdown).select_by_value(cert_level)
                    time.sleep(1)

                    # Check if subject is available
                    try:
                        subject_dropdown = driver.find_element(By.ID, 'MaterialArchive__noTable__sbv__SubjectSelect')
                        subject_select = Select(subject_dropdown)
                        subjects = [(opt.get_attribute('value'), opt.text)
                                   for opt in subject_select.options if opt.get_attribute('value')]

                        # Check if our subject matches
                        matching = [s for s in subjects
                                   if subject_name.lower() in s[1].lower()]

                        if matching:
                            available_years.append(year)
                            print(f"  ✓ {year}: Available ({len(matching)} matching subject(s))")
                        else:
                            print(f"  ✗ {year}: Subject '{subject_name}' not found")
                    except Exception as e:
                        print(f"  ✗ {year}: Error checking subjects - {e}")
                else:
                    print(f"  ✗ {year}: {cert_level.upper()} not available (available: {level_values})")
            except Exception as e:
                print(f"  ✗ {year}: Error - {e}")

        print(f"\n{'='*60}")
        print(f"Summary: {len(available_years)} years available for {cert_level.upper()} {subject_name}")
        print(f"Years: {', '.join(available_years)}")

    finally:
        driver.quit()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Check year availability for a subject')
    parser.add_argument('--cert', required=True, help='Certificate level (lc, jc, lca)')
    parser.add_argument('--subject', required=True, help='Subject name')

    args = parser.parse_args()

    check_availability(args.cert, args.subject)
