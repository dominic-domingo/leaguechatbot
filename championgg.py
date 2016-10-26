import requests
import api
from lol_data import champions
import time

roles = {"Top"     : ("top", "Top"),
         "Jungle"  : ("Jungle", "jungle", "jg", "jung"),
         "Middle"  : ("Middle", "middle", "Mid", "mid"),
         "ADC"     : ("ADC", "adc", "AD", "ad" "Bot", "bot"),
         "Support" : ("Support", "support", "Supp", "supp", "Sup", "sup")}

def role_lookup(role):
    corrected_role = None
    for k in roles:
        if role in roles[k]:
            corrected_role = k
            break

    if corrected_role:
        highest_winrate = "The champions with the highest win rate for {} are: ".format(corrected_role)
        r = requests.get('http://api.champion.gg/stats/role/{}/mostWinning?api_key={}&page=1&limit=5'
                         .format(corrected_role, api.CHAMPIONGG_API_KEY))
        data = r.json()
        try:
            for k in data["data"]:
                highest_winrate += "\n {}\t{}%WR\t{}%PR".format(k["name"], k["general"]["winPercent"],
                                                               k["general"]["playPercent"])
            return highest_winrate
        except KeyError:
            return "Something went wrong...Status code {}.".format(r.status_code)

    else:
        return "Could not find role {}.".format(role)

def bans_lookup():
    highest_banrate = "The champions with the highest ban rate are: "
    r = requests.get("http://api.champion.gg/stats/champs/mostBanned?api_key={}&page=1&limit=8"
                     .format(api.CHAMPIONGG_API_KEY))
    data = r.json()
    champs = []
    try:
        for k in data["data"]:
            if k["name"] not in champs:
                highest_banrate += "\n {} ({})\t{}%BR".format(k["name"], k["role"], k["general"]["banRate"])
                champs.append(k["name"])
        return highest_banrate
    except KeyError:
        return "Something went wrong...Status code {}.".format(r.status_code)

def get_summoner_id(summoner):
    id = None
    r = requests.get\
        ("https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/{}?api_key={}".format(summoner, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()
    try:
        return data[summoner]["id"]
    except KeyError:
        return -1


def summoner_lookup(summoner):
    summoner_id = get_summoner_id(summoner.lower().replace(" ", ""))
    if summoner_id < 0:
        return "Summoner not found!"

    r = requests.get\
        ("https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/{}/summary?season=SEASON2016&api_key={}"\
         .format(summoner_id, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()
    wins = None
    losses = None
    tier = "WOOD"
    division = "VI"

    for k in data["playerStatSummaries"]:
        if k["playerStatSummaryType"] == "RankedSolo5x5":
            wins = k["wins"]
            losses = k["losses"]

    time.sleep(5)

    r = requests.get\
        ("https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/{}?api_key={}"\
         .format(summoner_id, api.LEAGUE_API_KEY))


    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()
    try:
        for k in data[str(summoner_id)]:
            for e in k["entries"]:
                if e["playerOrTeamId"] == str(summoner_id):
                    tier = k["tier"]
                    division = e["division"]
    except KeyError:
        pass



    summoner_info = \
    '''
    {} is in {} {}, with a record of {}-{} ({:.3g}%).
    '''.format(summoner, tier, division, wins, losses, (100*wins/(wins+losses)) if losses != 0 else (100*wins/wins)\
        if wins > 0 else 0)

    return summoner_info




