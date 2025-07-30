import os
import sys

from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.environ.get("DATABASE_URL")

LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL").split()
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD").split()
COOLDOWN = os.environ.get("COOLDOWN")
if (COOLDOWN is not None):
    COOLDOWN = int(COOLDOWN)
UPDATE_HOURS = os.environ.get("UPDATE_HOURS")
if (UPDATE_HOURS is not None):
    UPDATE_HOURS = int(UPDATE_HOURS)

if (not all([DATABASE_URI, LINKEDIN_EMAIL, LINKEDIN_PASSWORD, UPDATE_HOURS])):
    print("ENV Variables not set.")
    sys.exit(1)