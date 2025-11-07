#!/usr/bin/env python3
"""
Exam Material Scraper for examinations.ie
Downloads PDFs from the State Examination Commission archive
"""

import os
import time
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests


class ExamScraper:
    def __init__(self, base_url, download_dir="downloads"):
        """
        Initialize the exam scraper

        Args:
            base_url: URL to the exam archive page
            download_dir: Directory to save downloaded PDFs
        """
        self.base_url = base_url
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)

        # Setup Selenium with Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Check for local chromedriver first
        local_driver = Path(__file__).parent / 'drivers' / 'chromedriver'
        if local_driver.exists():
            from selenium.webdriver.chrome.service import Service
            service = Service(executable_path=str(local_driver))
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            # Fall back to system chromedriver
            self.driver = webdriver.Chrome(options=options)

        self.wait = WebDriverWait(self.driver, 10)

    def get_dropdown_options(self, dropdown_element):
        """Get all options from a dropdown/select element"""
        select = Select(dropdown_element)
        return [(option.get_attribute('value'), option.text)
                for option in select.options if option.get_attribute('value')]

    def select_dropdown_option(self, dropdown_element, value):
        """Select an option from a dropdown by value"""
        select = Select(dropdown_element)
        select.select_by_value(value)
        time.sleep(0.5)  # Wait for any dynamic updates

    def find_pdf_links(self):
        """Find all PDF links on the current page"""
        pdf_links = []

        # First try: Look for links with .pdf in URL
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.lower().endswith('.pdf'):
                text = link.text.strip()
                pdf_links.append({
                    'url': href,
                    'text': text
                })

        # Second try: Look for exam material download links (with ?fp= parameter)
        # These are the actual download links on examinations.ie
        if not pdf_links:
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr')
            for row in rows:
                try:
                    # Find the description cell and download link
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 2:
                        desc = cells[0].text.strip()
                        link = cells[1].find_element(By.TAG_NAME, 'a')
                        href = link.get_attribute('href')

                        if href and '?fp=' in href and desc:
                            # Get the actual filename from hidden input if available
                            try:
                                hidden_input = row.find_element(
                                    By.CSS_SELECTOR,
                                    'input[type="hidden"][name="fileid"]'
                                )
                                filename_hint = hidden_input.get_attribute('value')
                            except:
                                filename_hint = None

                            pdf_links.append({
                                'url': href,
                                'text': desc,
                                'filename_hint': filename_hint
                            })
                except:
                    continue

        return pdf_links

    def download_pdf(self, url, filename):
        """Download a PDF file"""
        filepath = self.download_dir / filename

        # Skip if already downloaded
        if filepath.exists():
            print(f"  ✓ Already exists: {filename}")
            return True

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"  ✓ Downloaded: {filename}")
            return True
        except Exception as e:
            print(f"  ✗ Error downloading {filename}: {e}")
            return False

    def sanitize_filename(self, text):
        """Create a safe filename from text"""
        # Remove or replace invalid characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', '_', text)
        text = text.strip('._')
        return text[:200]  # Limit length

    def scrape(self, dropdown_selections=None):
        """
        Main scraping method

        Args:
            dropdown_selections: Dict mapping dropdown identifiers to values to select
                                If None, will attempt to find and list all dropdowns
        """
        try:
            print(f"Loading page: {self.base_url}")
            self.driver.get(self.base_url)

            # Wait for page to load
            time.sleep(2)

            # Check for terms and conditions checkbox
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR,
                    'input[type="checkbox"]')
                if not checkbox.is_selected():
                    checkbox.click()
                    print("✓ Accepted terms and conditions")
                    time.sleep(1)
            except NoSuchElementException:
                print("No terms checkbox found")

            # Find all dropdown elements
            dropdowns = self.driver.find_elements(By.TAG_NAME, 'select')

            if not dropdowns:
                print("No dropdown elements found on the page")
                print("\nPage source snippet:")
                print(self.driver.page_source[:1000])
            else:
                print(f"\nFound {len(dropdowns)} dropdown(s)")

                # If no selections provided, list available options
                if not dropdown_selections:
                    for i, dropdown in enumerate(dropdowns):
                        dropdown_id = dropdown.get_attribute('id') or f"dropdown_{i}"
                        dropdown_name = dropdown.get_attribute('name') or "unnamed"
                        print(f"\n--- Dropdown {i+1}: {dropdown_name} (id={dropdown_id}) ---")

                        options = self.get_dropdown_options(dropdown)
                        for value, text in options:
                            print(f"  - {text} (value={value})")

                    return

                # Apply selections
                for selector, value in dropdown_selections.items():
                    try:
                        # Re-find dropdowns after each selection (page may update)
                        time.sleep(1)
                        dropdowns = self.driver.find_elements(By.TAG_NAME, 'select')

                        if selector.isdigit():
                            # Select by index
                            idx = int(selector)
                            if idx < len(dropdowns):
                                self.select_dropdown_option(dropdowns[idx], value)
                                print(f"✓ Selected option '{value}' in dropdown {idx}")
                        else:
                            # Select by id or name
                            dropdown = self.driver.find_element(
                                By.CSS_SELECTOR,
                                f'select[id="{selector}"], select[name="{selector}"]'
                            )
                            self.select_dropdown_option(dropdown, value)
                            print(f"✓ Selected option '{value}' in '{selector}'")

                        # Wait for page to update after selection
                        time.sleep(2)
                    except Exception as e:
                        print(f"✗ Error selecting {selector}: {e}")

            # Look for PDF links
            print("\nSearching for PDF links...")
            pdf_links = self.find_pdf_links()

            if not pdf_links:
                # Check if there are more dropdowns to select
                time.sleep(1)
                dropdowns = self.driver.find_elements(By.TAG_NAME, 'select')
                unhandled_dropdowns = [d for d in dropdowns
                                      if d.get_attribute('id') not in dropdown_selections]

                if unhandled_dropdowns:
                    print(f"No PDF links found yet.")
                    print(f"Found {len(unhandled_dropdowns)} additional dropdown(s) that need selection:")
                    for dropdown in unhandled_dropdowns:
                        dropdown_id = dropdown.get_attribute('id') or "unknown"
                        dropdown_name = dropdown.get_attribute('name') or "unnamed"
                        print(f"  - {dropdown_name} (id={dropdown_id})")
                        options = self.get_dropdown_options(dropdown)
                        for value, text in options[:5]:  # Show first 5 options
                            print(f"      • {text}")
                        if len(options) > 5:
                            print(f"      ... and {len(options)-5} more")
                else:
                    print("No PDF links found. You may need to:")
                    print("  1. Select specific options from dropdowns")
                    print("  2. Submit a form")
                    print("  3. Click a button to reveal PDFs")
                return

            print(f"\nFound {len(pdf_links)} PDF link(s)")

            # Download PDFs
            print("\nDownloading PDFs...")
            for pdf in pdf_links:
                # Use filename_hint if available, otherwise sanitize the text
                if pdf.get('filename_hint'):
                    filename = pdf['filename_hint']
                else:
                    filename = self.sanitize_filename(pdf['text']) or 'document'
                    if not filename.endswith('.pdf'):
                        filename = f"{filename}.pdf"

                self.download_pdf(pdf['url'], filename)

        finally:
            self.driver.quit()

    def interactive_scrape(self):
        """
        Interactive mode - browse the page and select options step by step
        """
        try:
            print(f"Loading page: {self.base_url}")
            self.driver.get(self.base_url)
            time.sleep(2)

            # Accept terms if present
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR,
                    'input[type="checkbox"]')
                if not checkbox.is_selected():
                    checkbox.click()
                    print("✓ Accepted terms and conditions")
                    time.sleep(1)
            except NoSuchElementException:
                pass

            while True:
                # Find dropdowns
                dropdowns = self.driver.find_elements(By.TAG_NAME, 'select')

                if not dropdowns:
                    print("\nNo more dropdowns found.")
                    break

                print(f"\n{'='*60}")
                print(f"Found {len(dropdowns)} dropdown(s) on current page")

                for i, dropdown in enumerate(dropdowns):
                    dropdown_id = dropdown.get_attribute('id') or f"dropdown_{i}"
                    dropdown_name = dropdown.get_attribute('name') or "unnamed"
                    print(f"\n[{i}] {dropdown_name} (id={dropdown_id})")

                    options = self.get_dropdown_options(dropdown)
                    for j, (value, text) in enumerate(options):
                        print(f"    {j}. {text}")

                # Check for PDFs
                pdf_links = self.find_pdf_links()
                if pdf_links:
                    print(f"\n✓ Found {len(pdf_links)} PDF link(s)!")
                    choice = input("\nDownload all PDFs? (y/n): ").lower()

                    if choice == 'y':
                        print("\nDownloading PDFs...")
                        for pdf in pdf_links:
                            filename = self.sanitize_filename(pdf['text']) or 'document'
                            filename = f"{filename}.pdf"
                            self.download_pdf(pdf['url'], filename)
                    break

                # Get user input
                choice = input("\nSelect dropdown index (or 'q' to quit): ").strip()

                if choice.lower() == 'q':
                    break

                if not choice.isdigit() or int(choice) >= len(dropdowns):
                    print("Invalid selection")
                    continue

                dropdown_idx = int(choice)
                options = self.get_dropdown_options(dropdowns[dropdown_idx])

                option_choice = input(f"Select option (0-{len(options)-1}): ").strip()

                if not option_choice.isdigit() or int(option_choice) >= len(options):
                    print("Invalid option")
                    continue

                option_idx = int(option_choice)
                value = options[option_idx][0]

                self.select_dropdown_option(dropdowns[dropdown_idx], value)
                print(f"✓ Selected: {options[option_idx][1]}")
                time.sleep(1)

        finally:
            self.driver.quit()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Scrape and download PDFs from examinations.ie'
    )
    parser.add_argument(
        '--url',
        default='https://www.examinations.ie/exammaterialarchive/?i=91.97.108.95.95.104',
        help='URL to scrape'
    )
    parser.add_argument(
        '--output',
        default='downloads',
        help='Output directory for PDFs'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    args = parser.parse_args()

    scraper = ExamScraper(args.url, args.output)

    if args.interactive:
        scraper.interactive_scrape()
    else:
        # First run to discover dropdowns
        scraper.scrape()

        print("\n" + "="*60)
        print("Run with --interactive to select options interactively")
        print("Or modify the script to provide dropdown_selections dict")


if __name__ == '__main__':
    main()
