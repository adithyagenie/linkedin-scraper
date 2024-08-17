import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from scraper.alumniScraper import searchAlumni


def main():
    print("Started scrapping!")
    searchAlumni(limit=20)

if __name__ == "__main__":
    main()
