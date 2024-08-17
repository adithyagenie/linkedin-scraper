import config as const
from database.db_operations import create_user, user_exists
from linkedin_api import Linkedin
from tqdm import tqdm

api = Linkedin(const.LINKEDIN_EMAIL, const.LINKEDIN_PASSWORD)

def searchAlumni(limit=-1):
    res = api.search_people(schools=["chennai-institute-of-technology"], limit=limit)
    for user in tqdm(res):
        if "urn_id" in user:
            if ("name" not in user or
                "location" not in user):
                raise Exception(f"Invalid return from search: {user}")
            if (user_exists(user["urn_id"])):
                print(f"User already exists {user['name']}")
            else:
                if ("name" not in user or
                    "location" not in user):
                    raise Exception(f"Invalid return from search: {user}")
                create_user(user['urn_id'], user['name'], user['location'])
                print(f"User added to db: {user['name']}")

    # with open("output.json", "w") as f:
    #     print(json.dumps(res, indent=4))
    #     f.write(json.dumps(res, indent=4))
        # exit()
    
def getData(username):
    if (not username):
        raise Exception("Username not provided")
    
    try:
        # res = api.get_profile(username)
        res = api.get_profile(urn_id="ACoAADjNw_8BDBsGSXqRjxyOkufo9s6ZOiMnxVY")
        if (not res):
            raise Exception(f"Unable to fetch from api: {username}")
        print(res["urn_id"])
        print(f"{res['firstName']} {res['lastName']}", end = ": ")
        edu = res["education"]
        exp = res["experience"]
        
        studied = staff = False
            
        for i in edu:
            if ("school" in i and i["school"]["schoolName"] == "Chennai Institute of Technology"):
                if (i['timePeriod']['endDate']['year'] < 2025):
                    print(f"Student was alumni of CIT. Graduated {i['timePeriod']['endDate']['year']} and Student's experience is {exp[0]['companyName']} from {exp[0]['timePeriod']['startDate']['month']}/{exp[0]['timePeriod']['startDate']['year']}.")
                else:
                    print(f"Student currently studying at CIT from {i['timePeriod']['startDate']['year']}.")
                studied = True
                break
            elif (exp[0]["companyName"] == "Chennai Institute of Technology"):
                print("Staff at CIT")
                staff = True
                break
        if (not studied and not staff):
            print("Student not a staff or is not studying in CIT")
    except Exception as e:
        print(f"Unable to fetch api: {e}")


# searchAlumni(10)
# res = api.search_people(keyword_school="Chennai Institute of Technology")