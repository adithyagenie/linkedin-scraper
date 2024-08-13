from linkedin_api import Linkedin

api = Linkedin('cittest1@tutamail.com', 'password@123')

def getData(username):
    if (not username):
        raise Exception("Username not provided")
    
    try:
        res = api.get_profile(username)
        if (not res):
            raise Exception(f"Unable to fetch from api: {username}")
        # print(res["education"])
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


getData("vikram-raj-26406973")
