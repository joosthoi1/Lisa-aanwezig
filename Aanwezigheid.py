import time
import lisa
from datetime import datetime
import getpass

def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset

LisaApi = lisa.Lisa()
loggedin, clubFound = False, False

while (not clubFound):
    clubSearchString = input("Zoek club op stad of naam: ")
    clubs = LisaApi.get_clubs(clubSearchString)
    if len(clubs) == 0:
        print("Geen clubs gevonden")
        continue
    
    club = None
    while not club:
        for c, i in enumerate(clubs, 1):
            print(f"{c}) {i['club']['name']}")

        clubNrStr = input("Kies met een getal het gewenste team: ")

        if str.isdigit(clubNrStr):
            clubNr = int(clubNrStr)
            if clubNr >= 0 and clubNr <= len(clubs):
                club = clubs[clubNr-1]["club"]
                clubFound = True
            else:
                print(f"Vul een nummer van 1 tot en met {len(clubs)} in")
        else:
            print("vul een nummer in.")

print(club["name"])
LisaApi.set_club(club["id"])

while (not loggedin):
    lidnummer = input("Voer uw lidnummer in: ")
    wachtwoord = getpass.getpass("Voer uw wachtwoord in: ")

    loggedin = LisaApi.login(lidnummer, wachtwoord)

teams = LisaApi.get_user_teams()

teamId = None
while not teamId:
    print("Uw persoonlijke teams zijn:")
    for c, i in enumerate(teams["personal_teams"]):
        print(f"{c+1}) {i['name']}")

    teamNrStr = input("Kies met een getal het gewenste team: ")
    
    if str.isdigit(teamNrStr):
        teamNr = int(teamNrStr) - 1
        if teamNr >= 0 and teamNr <= len(teams["personal_teams"]):
            teamId = teams["personal_teams"][teamNr]["id"]
        else:
            print(f"Vul een nummer van 1 tot en met {len(teams)+1} in")
    else:
        print("vul een nummer in.")

print(f'{teams["personal_teams"][teamNr]["name"]} geselecteerd')

trainingen = LisaApi.get_trainingen(teamId)

for i in trainingen:
    datetime_object = datetime.strptime(i["start_utc"], "%Y-%m-%dT%H:%M:%SZ")
    code = LisaApi.aanwezigheidTraining(i["id"], teamId)
    if code != 200:
        print(f"mislukt met code {code}")
    print(f"training van {utc2local(datetime_object)} op aanwezig gezet")

wedstrijden = LisaApi.get_wedstrijden(teamId)

for i in wedstrijden:
    datetime_object = datetime.strptime(i["date"], "%d-%m-%Y")
    code = LisaApi.aanwezigheidWedstrijd(i["id"], teamId)
    if code != 201:
        print(f"mislukt met code {code}")
    print(f"wedstrijd van {datetime_object} op aanwezig gezet")

input("Druk op enter om te sluiten.")