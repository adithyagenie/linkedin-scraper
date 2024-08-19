import os
import sys

from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.environ.get("DATABASE_URL")
LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")

if (not all({DATABASE_URI, LINKEDIN_EMAIL, LINKEDIN_PASSWORD})):
    print("ENV Variables not set.")
    sys.exit(1)