#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
import subprocess

def run_scraper(year, week, output_dir="output"):
    """
    Run the NFL data scraping pipeline for specified year and week.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting NFL data scraping for {year} Week {week}")
    print("-" * 50)
    
    # Step 1: Run schedule scraper
    print("\nStep 1: Scraping schedule...")
    schedule_result = subprocess.run(
        ["python3", "scripts/scrapeSchedule.py", output_dir, str(year), str(week)],
        capture_output=True,
        text=True
    )
    
    if schedule_result.returncode != 0:
        print("Error scraping schedule:")
        print(schedule_result.stderr)
        return False
    
    print(schedule_result.stdout)
    
    # Step 2: Run data scraper
    print("\nStep 2: Scraping player stats...")
    data_result = subprocess.run(
        ["python3", "scripts/scrapeData.py", output_dir, str(year), str(week)],
        capture_output=True,
        text=True
    )
    
    if data_result.returncode != 0:
        print("Error scraping player stats:")
        print(data_result.stderr)
        return False
    
    print(data_result.stdout)
    
    print("\nScraping completed successfully!")
    print(f"Output files can be found in the '{output_dir}' directory")
    return True

def main():
    parser = argparse.ArgumentParser(description='NFL Data Scraping Pipeline')
    parser.add_argument('year', type=int, help='NFL season year')
    parser.add_argument('week', type=int, help='NFL week number')
    parser.add_argument('--output', '-o', default='output',
                       help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    success = run_scraper(args.year, args.week, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()