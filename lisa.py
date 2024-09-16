from datetime import datetime
import time
import requests

class NotLoggedInError(Exception):
    """Custom exception for when a user tries to perform an action that requires being logged in."""

    def __init__(self, message="You need to be logged in to perform this action."):
        self.message = message
        super().__init__(self.message)

class Lisa:
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic bGlzYXgtYXBpLXB1Yi11c2VyOlZWQWRMVE9GaUl5YXhHNGs3UUZCMXppaDZKR0ZEcjVk",
        "Content-Type": "application/json"
    }
    clubId = ""
    urlBase = "https://api.lisahockey.nl/api/v1"

    auth_token = None
    member_id = None
    loggedIn = False
    apiLoggedIn = True

    def __init__(self, clubId=None):
        auth_token = None
        self.clubId = clubId
        self.urlClub = f"{self.urlBase}/my/clubs/{self.clubId}"

    def set_club(self, club):
        self.clubId = club
        self.urlClub = f"{self.urlBase}/my/clubs/{self.clubId}"

    def get_clubs(self, searchString):
        total_pages = 1
        i = 0
        clubs = []

        params={"page_size":100,"current_page":i}
        if searchString != "":
            params["name_pattern"] = searchString
            params["city_pattern"] = searchString
        while i < total_pages:
            i+=1
            r = requests.get(f"{self.urlBase}/my/federations/921fe7b5-683e-4bb1-a850-784381bb1f17/clubs",
                             params = params,
                             headers = self.headers)

            # print(r.status_code)
            current = r.json()
            for t in current["clubs"]:
                clubs.append(t)
            # print(len(current["Items"]))
            total_pages = current["page"]["total_pages"]
            # print(r.url)
        return clubs

    def login(self, bondsnummer, wachtwoord):
        login = {"club_membership_number":bondsnummer,"password":wachtwoord}

        r = requests.post(self.urlClub + "/auth_tokens", data=str(login), headers=self.headers)
        if r.status_code == 403:
            print("Verkeerd wachtwoord of lidnummer.")
            return False
        if r.status_code != 201:
            print(r.status_code)
            print(r.text)
            return False
        request_json = r.json()
        self.auth_token = request_json["token"]
        self.member_id = request_json["club_member"]["id"]
        self.headers["x-lisa-auth-token"] = self.auth_token
        self.loggedIn = True
        return self.loggedIn
    
    def get_user_teams(self):
        if not self.loggedIn:
            raise NotLoggedInError()
        r = requests.get(f"{self.urlClub}/teams", headers=self.headers)
        return r.json()
    
    def get_trainingen(self, teamid):
        if not self.loggedIn:
            raise NotLoggedInError()
        total_pages = 1
        i = 0
        trainingen = []
        while i < total_pages:
            i+=1
            r = requests.get(self.urlClub + f"/season-trainings/{teamid}?show_history=false&current_page={i}&page_size=100", headers=self.headers)
            # print(r.status_code)
            current = r.json()
            for t in current["Items"]:
                trainingen.append(t)
            # print(len(current["Items"]))
            total_pages = current["page"]["total_pages"]
            # print(r.url)
        return trainingen

    def get_wedstrijden(self, teamid):
        if not self.loggedIn:
            raise NotLoggedInError()
        r = requests.get(self.urlClub + f"/teams/{teamid}/matches?show_historical_matches=false", headers=self.headers)    
        wedstrijden = r.json()

        return wedstrijden
    
    def aanwezigheidTraining(self, trainingId, teamId, memberId=None):
        if not self.loggedIn:
            raise NotLoggedInError()
        if memberId == None:
            member_id = self.member_id
        r = requests.post(f"{self.urlClub}/trainings/{trainingId}/teams/{teamId}/members/{member_id}/presences", data=str({"status": "present"}), headers=self.headers)
        return r.status_code

    def aanwezigheidWedstrijd(self, wedstrijdId, teamId, memberId=None):
        if not self.loggedIn:
            raise NotLoggedInError()
        if memberId == None:
            member_id = self.member_id
        r = requests.post(f"{self.urlClub}/matches/{wedstrijdId}/teams/{teamId}/members/{member_id}/presence", data=str({"status": "present"}), headers=self.headers)
        return r.status_code
    
    def get_schedule(self, federationId, teamId):
        pass

def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset
