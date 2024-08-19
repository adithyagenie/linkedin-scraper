import os
import sys

import scraper.alumniScraper as scrape

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from scraper.alumniScraper import searchAlumni


def main():
    print("Started scraping!")
    searchAlumni(limit=20)
    scrape.processStoredUsers(limit=5)

if __name__ == "__main__":
    main()
