import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.environ.get("DATABASE_URL")
LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
