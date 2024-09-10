import os
import sys

import scraper.alumniScraper as scrape

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.clientManager import createClients


def main():
    apiManager = createClients()
    print("Started scraping!")
    print("Searching for alumni!")
    # searchAlumni(apiManager, limit=-1)
    # sleep(20)
    print("Processing users!")
    scrape.processStoredUsers(apiManager, limit=500)
    print("Exiting...")

if __name__ == "__main__":
    main()
