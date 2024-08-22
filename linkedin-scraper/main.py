import os
import sys
from time import sleep

import scraper.alumniScraper as scrape

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from scraper.alumniScraper import searchAlumni


def main():
    print("Started scraping!")
    print("Searching for Alumni!")
    searchAlumni(limit=150)
    sleep(20)
    print("Processing Users!")
    
    scrape.processStoredUsers(limit=5)
    # print(scrape.getData("ACoAAE93fzABONg3ExOQnzpqrM0elMK2O_GawJk"))

if __name__ == "__main__":
    main()
