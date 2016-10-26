import requests

roles = {"Top"     : ("top", "Top"),
         "Jungle"  : ("Jungle", "jungle", "jg", "jung"),
         "Mid"     : ("Middle", "middle", "Mid", "mid"),
         "ADC"     : ("ADC", "adc", "AD", "ad" "Bot", "bot"),
         "Support" : ("Support", "support", "Supp", "supp", "Sup", "sup")}

def role_lookup(role):
    corrected_role = None
    for k in roles:
        if role in roles[k]:
            corrected_role = k
            break

    if corrected_role:
        pass
    else:
        return "Could not find role {}.".format(role)
