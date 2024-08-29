# Linkedin Alumni Scraper

## Setting up:

Modify .env file to add env variables:

- `LINKEDIN_EMAIL` -> Space seperated linkedin login emails
- `LINKEDIN_PASSWORD` -> Space seperated linkedin login passwords corresponding to email, in order
- `DATABASE_URL` -> Postgres DB url
- `COOLDOWN` -> Cooldown between consecutive requests, defaults to 5
- `UPDATE_HOURS` -> Number of hours before a user's record is processed again

> [!CAUTION]
> We are not responsible if your network or your account gets banned. Scraping is against Linkedin's TOS.