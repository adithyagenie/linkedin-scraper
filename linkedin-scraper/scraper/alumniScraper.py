from datetime import date
from random import randint
from time import sleep

import config as const
import database.db_operations as db
from linkedin_api import Linkedin
from tqdm import tqdm, trange

api = Linkedin(const.LINKEDIN_EMAIL, const.LINKEDIN_PASSWORD)
api2 = Linkedin
"""
Searches people in CIT and adds them to DB.
limit=How many records to fetch, defaults to -1(all)
"""
def searchAlumni(limit=-1):
    existNum = addedNum = 0
    added = []
    existed = []

    pbar = trange(limit)
    pbar.set_description("Searching people...")
    res = api.search_people(schools=["chennai-institute-of-technology"], limit=limit)
    pbar = tqdm(res)
    pbar.set_description("Storing people...")
    for user in pbar:
        if ("name" not in user or
            "location" not in user):
            raise Exception(f"Invalid return from search: {user}")
        if "urn_id" in user:
            if (db.user_exists(user["urn_id"])):
                existNum += 1
                existed.append(user["name"])
                # print(f"User already exists {user['name']}")
            else:
                db.create_user(user['urn_id'], user['name'], user['location'])
                addedNum += 1
                added.append(user["name"])
                # print(f"User added to db: {user['name']}")
    print(f"Scrape successful!\nNew users: {addedNum}\nExisting users: {existNum}\n\nUsers added: {added}\n\nExisting users: {existed}")

"""
Fetches profile of user
urn_id = User's urn_id
"""
def getData(urn_id):  
    try:
        # res = api.get_profile(username)
        res = api.get_profile(urn_id=urn_id)
        # print(f"{res['firstName']} {res['lastName']}", end = ": ")
        # print(res)
        # return
        edu = res["education"]
        exp = res["experience"]
        
        if not edu or len(edu) == 0:
            print("Person does not have CIT in education")
            return 
        for i in edu:
            if ("school" in i and 
                (
                    ("schoolName" in i["school"] and i["school"]["schoolName"] == "Chennai Institute of Technology") 
                    or 
                    ("entityUrn" in i["school"] and i["school"]["entityUrn"] == "urn:li:fs_miniSchool:195969")
                )
            ):
                if ("timePeriod" in i and "endDate" in i['timePeriod'] and i["timePeriod"]['endDate']['year'] < 2025):
                    # ---------------- ALUMNI FOUND ------------------ #

                    db.update_user(urn_id, alumni=True)

                    if (not exp or len(exp) == 0):
                        print("Person studied in CIT is jobless")
                        break

                    for job in exp:
                        if ("companyName" not in job or "companyUrn" not in job):
                            raise Exception("Company URN or Name is missing!")
                        
                        location = job["locationName"] if "locationName" in job else ""
                        companyName = job["companyName"]
                        title = job["title"] if "title" in job else ""
                        companyUrn = job["companyUrn"]
                        startDate = endDate = None
                        is_current = False
                        if ("timePeriod" in job):
                            tp = job["timePeriod"]
                            if ("startDate" in tp):
                                start = tp["startDate"]
                                if ("year" in start):
                                    startDate = date(start["year"], start["month"] if "month" in start else 1, 1)
                            if ("endDate" in tp):
                                end = tp["endDate"]
                                if ("year" in start):
                                    endDate = date(end["year"], end["month"] if "month" in end else 1, 1)
                            else:
                                is_current = True if "startDate" in tp else False

                        # ------------------- DATABASE ADD ----------------------- #
                        if (not db.company_exists(companyUrn)):
                            companyId = db.create_company(companyUrn, companyName)
                        else:
                            company = db.get_company(companyUrn, by_urn=True)
                            companyId = company.id
                        existing_job_exp = db.job_experience_exists(urn_id, companyId, title)
                        if (existing_job_exp == None):
                            # ----------------- ADD JOB EXPERIENCE --------------------- #
                            db.create_job_experience(urn_id, companyId, title, location, startDate, endDate, is_current)
                        else:
                            # ----------------- UPDATE JOB EXPERIENCE --------------------- #
                            db.update_job_experience(existing_job_exp, person_id=urn_id, company_id=companyId, job_title=title, location=location, start_date=startDate, end_date=endDate, is_current=is_current)

                break
        else:
            print("Not a student in CIT")
        return f"{res['firstName']} {res['lastName']}"
    except Exception as e:
        print(f"Unable to fetch api: {e}")

"""
Process all stored users
limit=How many records to process, defaults to -1(all)
"""
def processStoredUsers(limit=-1):
    processedCount = 0
    processedNames = []
    urn_ids = db.get_urn_ids()
    if (limit != -1):
        urn_ids = urn_ids[:limit]
    pbar = tqdm(urn_ids)
    for urn_id in pbar:
        name = getData(urn_id)
        processedNames.append(name)
        pbar.set_description(f"Processing user: {urn_id}")
        processedCount += 1
        sleep(randint(10, 15))
    print(f"\n\nProcessed users: {processedNames}")
    print(f"\n\nProcessed {processedCount} users!")
    