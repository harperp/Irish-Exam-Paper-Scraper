#!/usr/bin/env python3
"""
Automated exam downloader
Downloads all PDFs for specified material type and year
"""

import sys
import argparse
from exam_scraper import ExamScraper


def main():
    parser = argparse.ArgumentParser(
        description='Download exam materials from examinations.ie'
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
        choices=['lca', 'lc', 'jc', 'all'],
        default='lc',
        help='Certificate level: lca (Leaving Cert Applied), lc (Leaving Cert), jc (Junior Cert), all (default: lc)'
    )
    parser.add_argument(
        '--output',
        default='downloads',
        help='Output directory (default: downloads)'
    )
    parser.add_argument(
        '--show-dropdowns',
        action='store_true',
        help='Show all available dropdowns and options'
    )

    args = parser.parse_args()

    scraper = ExamScraper(
        'https://www.examinations.ie/exammaterialarchive/?i=91.97.108.95.95.104',
        args.output
    )

    if args.show_dropdowns:
        # Just discover and display dropdowns
        scraper.scrape()
    else:
        # Map level argument to actual values
        level_map = {
            'lca': 'lca',  # Leaving Certificate Applied
            'lc': 'lc',    # Leaving Certificate
            'jc': 'jc',    # Junior Certificate / Cycle
        }

        # Download with specified selections
        print(f"Downloading {args.type} for year {args.year}")
        print(f"Level: {args.level}")
        print(f"Output directory: {args.output}")
        print("="*60)

        if args.level == 'all':
            # Download for all levels
            for level_key, level_val in level_map.items():
                print(f"\n--- Processing {level_key} ---")
                selections = {
                    'MaterialArchive__noTable__sbv__ViewType': args.type,
                    'MaterialArchive__noTable__sbv__YearSelect': args.year,
                    'MaterialArchive__noTable__sbv__ExaminationSelect': level_val
                }
                scraper.scrape(dropdown_selections=selections)
        else:
            # Download for single level
            selections = {
                'MaterialArchive__noTable__sbv__ViewType': args.type,
                'MaterialArchive__noTable__sbv__YearSelect': args.year,
                'MaterialArchive__noTable__sbv__ExaminationSelect': level_map[args.level]
            }
            scraper.scrape(dropdown_selections=selections)

    print("\nDone!")


if __name__ == '__main__':
    main()
