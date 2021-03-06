import requests
import api
from lol_data import champions
import time

roles = {"TOP": ("top", "Top"),
         "JUNGLE": ("Jungle", "jungle", "jg", "jung"),
         "MIDDLE": ("Middle", "middle", "Mid", "mid"),
         "DUO_CARRY": ("ADC", "adc", "AD", "ad" "Bot", "bot"),
         "DUO_SUPPORT": ("Support", "support", "Supp", "supp", "Sup", "sup")}


def champ_lookup(id):
    r = requests.get("http://ddragon.leagueoflegends.com/cdn/8.12.1/data/en_US/champion.json")
    data = r.json()
    for champ in data["data"].keys():
        if data["data"][champ]["key"] == str(id):
            return data["data"][champ]["name"]


def role_lookup(role):
    corrected_role = None
    for k in roles:
        if role in roles[k]:
            corrected_role = k
            break

    if corrected_role:
        highest_winrate = "The champions with the highest win rate for {} are: ".format(corrected_role)
        r = requests.get('http://api.champion.gg/v2/champions?sort=winRate-desc&limit=130&api_key={}'
                         .format(api.CHAMPIONGG_API_KEY))
        data = r.json()
        try:
            count = 0
            for champ in data:
                if champ["playRate"] >= 0.1:
                    if champ["role"] == corrected_role:
                        champ_name = champ_lookup(champ["championId"])
                        highest_winrate += "\n {}\t{:.2f}%WR\t{:.2f}%PR".format(champ_name, champ["winRate"] * 100,
                                                                       champ["playRate"] * 100)
                        count += 1
                        if count == 5:
                            return highest_winrate
            return highest_winrate
        except KeyError:
            return "Something went wrong...Status code {}.".format(r.status_code)

    else:
        return "Could not find role {}.".format(role)


def bans_lookup():
    highest_banrate = "The champions with the highest ban rate are: "
    r = requests.get("http://api.champion.gg/v2/champions?sort=banRate-desc&limit=130&api_key={}"
                     .format(api.CHAMPIONGG_API_KEY))
    data = r.json()
    champs = []
    try:
        count = 1
        for k in data:
            champ_name = champ_lookup(k["championId"])
            if champ_name not in champs:
                highest_banrate += "\n{}. {}\t{:.2f}%BR".format(count, champ_name, k["banRate"] * 100)
                champs.append(champ_name)
                count += 1
                if len(champs) >= 10:
                    break
        return highest_banrate
    except KeyError:
        return "Something went wrong...Status code {}.".format(r.status_code)


def get_summoner_id_and_level(summoner):
    id = None
    r = requests.get \
        ("https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{}?api_key={}".format(summoner, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)

    data = r.json()
    print(data)
    try:
        return data["id"], data["summonerLevel"]
    except KeyError:
        return -1


def game_lookup(summoner):
    summoner_id = get_summoner_id_and_level(summoner.lower().replace(" ", ""))[0]
    if int(summoner_id) < 0:
        return "Summoner not found!"

    r = requests.get \
        ("https://na1.api.riotgames.com/lol/spectator/v3/active-games/by-summoner/{}?api_key={}" \
         .format(summoner_id, api.LEAGUE_API_KEY))

    if r.status_code == 429:
        retry_after = r.headers["Retry-After"]
        return "Rate limited! Try again in {} seconds...".format(retry_after)
    elif r.status_code == 404:
        return "Summoner is not in game!"

    data = r.json()
    blue_ban_id = []
    red_ban_id = []

    for b in data["bannedChampions"]:
        if b["teamId"] == 100:
            blue_ban_id.append(b["championId"])
        elif b["teamId"] == 200:
            red_ban_id.append(b["championId"])

    blue_bans = [champ_lookup(c) if champ_lookup(c) is not None else str(c) for c in blue_ban_id]
    red_bans = [champ_lookup(c) if champ_lookup(c) is not None else str(c) for c in red_ban_id]
    blue_names = []
    blue = []
    red_names = []
    red = []
    game_mode = {"ODIN" : "Dominion", "ARAM" : "ARAM", "ONEFORALL" : "One For All", "ASCENSION": "Ascension"}

    game_info = "GAME TIME: {}".format(time.strftime("%M:%S", time.gmtime(180+data["gameLength"])))
    game_info += "\n**BLUE SIDE**\n"
    if len(blue_bans) > 0:
        game_info += "\tBans:\t"
        game_info += ', '.join(blue_bans)
    elif data["gameMode"] == "CLASSIC":
        game_info += "\tBLIND PICK"
    else:
        game_info += game_mode[data["gameMode"]] if data["gameMode"] in game_mode else data["gameMode"]
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

    game_info += "\n**RED SIDE**\n"
    if len(red_bans) > 0:
        game_info += "\tBans:\t"
        game_info += ', '.join(red_bans)
    elif data["gameMode"] == "CLASSIC":
        game_info += "\tBLIND PICK"
    else:
        game_info += game_mode[data["gameMode"]]
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

    for id in ids:
        r = requests.get \
            ("https://na1.api.riotgames.com/lol/league/v3/positions/by-summoner/{}?api_key={}" \
             .format(id, api.LEAGUE_API_KEY))

        if r.status_code == 429:
            retry_after = r.headers["Retry-After"]
            return "Rate limited! Try again in {} seconds...".format(retry_after)

        data = r.json()
        tier = "UNRANKED"
        division = ":monkey:"
        lp = 0

        for queue in data:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                tier = queue["tier"]
                division = queue["rank"]
                lp = queue["leaguePoints"]
                break

        info.append((tier, division, lp))
        time.sleep(0.125)

    return info


def summoner_lookup(summoner):
    summoner = get_summoner_id_and_level(summoner.lower().replace(" ", ""))
    summoner_id = summoner[0]
    summoner_level = summoner[1]
    if int(summoner_id) < 0:
        return "Summoner not found!"

    while True:
        r = requests.get("https://na1.api.riotgames.com/lol/league/v3/positions/by-summoner/{}?api_key={}".format(
            summoner_id, api.LEAGUE_API_KEY))

        if r.status_code == 429:
            retry_after = r.headers["Retry-After"]
            print(("Rate limited! Trying again in {} seconds".format(retry_after)))
            time.sleep(retry_after)

        else:
            break

    data = r.json()
    wins = 0
    losses = 0
    tier = "UNRANKED"
    division = ":monkey:"
    lp = 0
    print(data)
    for queue in data:
        if queue["queueType"] == "RANKED_SOLO_5x5":
            wins = queue["wins"]
            losses = queue["losses"]
            tier = queue["tier"]
            division = queue["rank"]
            lp = queue["leaguePoints"]
            break

    time.sleep(0.25)

    url = "https://na1.api.riotgames.com/lol/league/v3/{}leagues/by-queue/RANKED_SOLO_5x5?api_key={}"
    if tier == "CHALLENGER" or tier == "MASTER":
        if tier == "CHALLENGER":
            time.sleep(1)
            r = requests.get(url.format("challenger", api.LEAGUE_API_KEY))

        elif tier == "MASTER":
            time.sleep(1)
            r = requests.get(url.format("master", api.LEAGUE_API_KEY))

        data = r.json()
        rank = "#"
        try:
            for k in zip(sorted(data["entries"], key=lambda x: -x["leaguePoints"]), range(len(data["entries"]))):
                if k[0]["playerOrTeamId"] == str(summoner_id):
                    rank += str(k[1] + 1)
                    break
        except KeyError:
            pass

    winrate = (100 * wins / (wins + losses)) if losses != 0 else (100 * wins / wins) if wins > 0 else 0

    return summoner_level, tier, division if tier != "CHALLENGER" and tier != "MASTER" else rank, lp, wins, losses, winrate
