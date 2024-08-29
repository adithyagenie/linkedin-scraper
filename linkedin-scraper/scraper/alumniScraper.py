import traceback
from datetime import date

import database.db_operations as db
from tqdm import tqdm, trange

from .clientManager import APIClientManager

"""
Searches people in CIT and adds them to DB.
limit=How many records to fetch, defaults to -1(all)
"""
def searchAlumni(apiManager: APIClientManager, limit=-1):
    uname, api = apiManager.get_client()
    # print(f"INFO: Req made with client {uname}")
    existNum = addedNum = 0
    added = []
    existed = []

    pbar = trange(limit)
    pbar.set_description(f"Searching people (client: {uname})...")
    res = api.search_people(schools=["chennai-institute-of-technology"], limit=limit)
    apiManager.release_client(uname, api)
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
def getData(apiManager: APIClientManager, urn_id):  
    try:
        # res = api.get_profile(username)
        uname, api = apiManager.get_client()
        res = api.get_profile(urn_id=urn_id)
        apiManager.release_client(uname, api)
        # print(f"{res['firstName']} {res['lastName']}", end = ": ")
        # print(res)
        # return
        edu = res["education"]
        exp = res["experience"]
        
        if not edu or len(edu) == 0:
            # print("Person does not have CIT in education")
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
                        print("Person studied in CIT is not in a job currently!")
                        break

                    # -------------------- DELETE EXISTING JOB RECORDS ------------------------ #
                    db.delete_user_job_experiences(urn_id)

                    # -------------------- ADD NEW JOB RECORDS ------------------- #
                    for job in exp:
                        if ("companyName" not in job or "companyUrn" not in job):
                            raise Exception("Company URN or Name is missing!")
                        
                        location = job["locationName"] if "locationName" in job else ""
                        companyName = job["companyName"]
                        jobTitle = job["title"] if "title" in job else ""
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
                        # ------------------ UPSERT JOB EXPERIENCE --------------------- #
                        db.upsert_job_experience(urn_id, companyId, jobTitle, startDate, location, endDate, is_current)

                    # ----------------- DELETE SCHOOL EXP -------------------- #
                    db.delete_user_school_experience(urn_id)
                    
                    # -------------------------- SCHOOL ---------------------- #
                    for school in edu:
                        schoolName = school["schoolName"]
                        schoolUrn = school["entityUrn"]
                        startDate = endDate = None
                        degreeName = "NOTSET"
                        fieldOfStudy = grade = None
                        is_current = False
                        if ("timePeriod" in school):
                            tp = school["timePeriod"]
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
                        degreeName = school["degreeName"] if "degreeName" in school else "NOTSET"
                        fieldOfStudy = school["fieldOfStudy"] if "fieldOfStudy" in school else None
                        grade = float(school["grade"][:-1]) if "grade" in school else None

                        # ------------------- DATABASE ADD ----------------------- #
                        if (not db.school_exists(schoolUrn)):
                            schoolId = db.create_school(schoolUrn, schoolName)
                        else:
                            existing_school = db.get_school(schoolUrn, by_urn=True)
                            schoolId = existing_school.id

                        # -------------------------- UPSERT SCHOOL EXPERIENCE -------------------------- #
                        db.upsert_school_experience(urn_id, schoolId, degreeName, fieldOfStudy, grade, startDate, endDate, is_current)

                break
        else:
            print("Not a student in CIT")
        
        # -------------- UPDATE USER LAST UPD TIMESTAMP ------------------ #
        db.update_user_last_updated(urn_id)
        return f"{res['firstName']} {res['lastName']}", uname
    except Exception as e:
        print(f"Unable to fetch api: {e}")
        print(traceback.format_exc())

"""
Process all stored users
limit=How many records to process, defaults to -1(all)
"""
def processStoredUsers(client: APIClientManager, limit=-1):
    processedCount = 0
    processedNames = []
    urn_ids = db.get_urn_ids_not_updated()
    if (limit != -1):
        urn_ids = urn_ids[:limit]
    pbar = tqdm(urn_ids)
    for urn_id in pbar:
        ret = getData(client, urn_id)
        if (ret is None):
            break
        else:
            name, uname = ret
            processedNames.append(name)
            pbar.set_description(f"Processed user: {name} with client: {uname}")
            processedCount += 1
    print(f"\n\nProcessed users: {processedNames}")
    print(f"\n\nProcessed {processedCount} users!")
    