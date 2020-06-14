import requests
from helper import utils

USA = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands': 'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

Canada = {
    "Newfoundland": "NL",
    "Prince Edward Island": "PE",
    "Nova Scotia": "NS",
    "New Brunswick": "NB",
    "Québec": "QC",
    "Ontario": "ON",
    "Manitoba": "MB",
    "Saskatchewan": "SK",
    "Alberta": "AB",
    "British Columbia": "BC",
    "Yukon": "YT",
    "Northwest Territories": "NT",
    "Nunavut": "NU"
}

districts = {
    "mar": "fma",
    "nc": "fnc",
    "tx": "fit",
    "in": "fin",
}


auth_key = "XeUIxlvO4CPc44NlLE3ncevDg7bAhp6CRy6zC9M2aQb2zGfys0M30eKwavFJSEJr"
read_pre = "https://www.thebluealliance.com/api/v3/"
session = requests.Session()
session.headers.update({'X-TBA-Auth-Key': auth_key, 'X-TBA-Auth-Id': ''})


def get(url):
    return session.get(read_pre+url).json()


def getTeamInfo(number):
    data = get("team/frc"+str(number)+"/simple")
    name = data["nickname"]
    state = data["state_prov"]
    country = data["country"]

    years = len(get("team/frc"+str(number)+"/years_participated"))

    try:
        district = get("team/frc"+str(number)+"/districts")[-1]["abbreviation"]
    except Exception:
        district = "None"

    if(state in USA):
        state = USA[state]
    elif(state in Canada):
        state = Canada[state]
    elif(country != "USA" and country != "Canada"):
        state = "All"

    if(district in districts):
        district = districts[district]

    return [name, country, state, district, years]


def saveAllTeamsInfo():
    out = utils.loadAllTeamsInfo()
    count = 0

    for team in utils.loadAllTeams():
        count += 1

        if count % 100 == 0:
            print(count)
            utils.saveAllTeamsInfo(out)

        if team in out:
            pass
        else:
            out[team] = getTeamInfo(team)

    utils.saveAllTeamsInfo(out)


def cleanState(state):
    if state in USA:
        return USA[state]
    if state in Canada:
        return Canada[state]
    return "All"


def cleanDistrict(district):
    if district in districts:
        return districts[district]
    return district
