import requests
import api
from lol_data import champions
import time

roles = {"Top": ("top", "Top"),
         "Jungle": ("Jungle", "jungle", "jg", "jung"),
         "Middle": ("Middle", "middle", "Mid", "mid"),
         "ADC": ("ADC", "adc", "AD", "ad" "Bot", "bot"),
         "Support": ("Support", "support", "Supp", "supp", "Sup", "sup")}


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
    r = requests.get \
        ("https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/{}?api_key={}".format(summoner, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()
    try:
        return data[summoner]["id"]
    except KeyError:
        return -1


def game_lookup(summoner):
    summoner_id = get_summoner_id(summoner.lower().replace(" ", ""))
    if int(summoner_id) < 0:
        return "Summoner not found!"

    r = requests.get \
        ("https://na.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/NA1/{}?api_key={}" \
         .format(summoner_id, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)
    elif r.status_code == 404:
        return "Summoner is not in game!"

    data = r.json()
    blue_ban_id = []
    for b in data["bannedChampions"]:
        if b["pickTurn"] % 2 != 0:
            blue_ban_id.append(b["championId"])
    red_ban_id = []
    for b in data["bannedChampions"]:
        if b["pickTurn"] % 2 == 0:
            red_ban_id.append(b["championId"])

    def champ_lookup(id):
        for champ in champions:
            if champions[champ]["id"] == str(id):
                return champions[champ]["name"]

    blue_bans = [champ_lookup(c) if champ_lookup(c) is not None else str(c) for c in blue_ban_id]
    red_bans = [champ_lookup(c) if champ_lookup(c) is not None else str(c) for c in red_ban_id]
    blue_names = []
    blue = []
    red_names = []
    red = []

    game_info = "GAME TIME: {}".format(time.strftime("%M:%S", time.gmtime(180+data["gameLength"])))
    game_info += "\n**BLUE SIDE**\n\tBans:\t"
    print(blue_bans)
    game_info += ', '.join(blue_bans)
    game_info += "\n"
    # teamId = 100
    for p in data["participants"]:
        if p["teamId"] == 100:
            blue_names.append((p["summonerName"], p["championId"]))
            blue.append(str(p["summonerId"]))

    blue_info = lookup_by_id(blue)
    for bn, b in zip(blue_names, blue_info):
        game_info += "**{}** ({} {}) on {}\n". \
                format(bn[0], b[0], b[1], champ_lookup(bn[1]))

    game_info += "\n**RED SIDE**\n\tBans:\t"
    game_info += ', '.join(red_bans)
    game_info += "\n"
    for p in data["participants"]:
        if p["teamId"] == 200:
            red_names.append((p["summonerName"], p["championId"]))
            red.append(str(p["summonerId"]))

    red_info = lookup_by_id(red)
    for rn, r in zip(red_names, red_info):
        game_info += "**{}** ({} {}) on {}\n". \
            format(rn[0], r[0], r[1], champ_lookup(rn[1]))

    return game_info


def lookup_by_id(ids: list):
    info = []

    f = ",".join(ids)
    r = requests.get \
        ("https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/{}?api_key={}" \
         .format(f, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()

    for id in ids:
        tier = "UNRANKED"
        division = ":monkey:"
        lp = 0
        try:
            for k in data[str(id)]:
                for e in k["entries"]:
                    if e["playerOrTeamId"] == str(id):
                        tier = k["tier"]
                        division = e["division"]
                        lp = e["leaguePoints"]
        except: pass
        finally:
            info.append((tier, division, lp))


    return info


def summoner_lookup(summoner):
    summoner_id = get_summoner_id(summoner.lower().replace(" ", ""))
    if int(summoner_id) < 0:
        return "Summoner not found!"

    r = requests.get \
        ("https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/{}/summary?season=SEASON2016&api_key={}" \
         .format(summoner_id, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()
    wins = None
    losses = None
    tier = "UNRANKED"
    division = ":monkey:"
    lp = 0

    for k in data["playerStatSummaries"]:
        if k["playerStatSummaryType"] == "RankedSolo5x5":
            wins = k["wins"]
            losses = k["losses"]

    time.sleep(0.5)

    r = requests.get\
        ("https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/{}?api_key={}"
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
                    lp = e["leaguePoints"]
    except KeyError:
        pass

    if tier == "CHALLENGER":
        url = "https://na.api.pvp.net/api/lol/v2.5/league/{}?typeRANKED_SOLO_5x5&api_key={}"
        time.sleep(1)
        r = requests.get \
                (url.format("challenger", api.LEAGUE_API_KEY))

    elif tier == "MASTER":
        url = "https://na.api.pvp.net/api/lol/v2.5/league/{}?typeRANKED_SOLO_5x5&api_key={}"
        time.sleep(1)
        r = requests.get \
            (url.format("challenger", api.LEAGUE_API_KEY))

    data = r.json()
    rank = ""
    try:
        for k in zip(sorted(data["entries"], key = lambda x : x["leaguePoints"]), range(len(data["entries"]))):
            if k[0]["playerOrTeamId"] == summoner_id:
                rank = k[1] + 1
    except KeyError:
        pass

    winrate = (100 * wins / (wins + losses)) if losses != 0 else (100 * wins / wins) if wins > 0 else 0

    return (tier, division if tier != "CHALLENGER" or tier != "MASTER" else rank, lp, wins, losses, winrate)
