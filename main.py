import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from datetime import datetime, timedelta
import pytz
from boltons.iterutils import remap

import gunicorn, uvicorn

ceb_home = "https://cebcare.ceb.lk/Incognito/DemandMgmtSchedule"
ceb_power_cut_details_endpoint = "https://cebcare.ceb.lk/Incognito/GetLoadSheddingGeoAreas"
ceb_load_shedding_events_endpoint = "https://cebcare.ceb.lk/Incognito/GetLoadSheddingEvents"

app = FastAPI()
r_session = requests.Session()

drop_falsey = lambda path, key, value: bool(value)
def get_verification_token():
    html = r_session.get(ceb_home, verify=False).text
    soup = BeautifulSoup(html, 'html.parser')
    token = soup.find("input", attrs={ "name": "__RequestVerificationToken" })
    return token.attrs.get("value")

def get_power_cut_details(group_letter: str, token: str):
    res = r_session.get(ceb_power_cut_details_endpoint, 
            params={
                "LoadShedGroupId":group_letter.capitalize()
            },
            headers={
                "requestverificationtoken": token
            },
            verify=False
        )
    
    string = res.content.decode('unicode_escape')
    return json.loads(string[1:-1])

def get_all_power_cut_events(token: str):
    today = datetime.now(pytz.timezone("Asia/Colombo"))
    next_day = today + timedelta(days=1)
    
    res = r_session.post(ceb_load_shedding_events_endpoint, 
            data={
                "StartTime": today.date(),
                "EndTime": next_day.date()
            },
            headers={
                "requestverificationtoken": token
            },
            verify=False
        )
    return res.json()

@app.get("/power_cuts")
async def power_cuts():
    token = get_verification_token()
    details = get_all_power_cut_events(token)
    return remap(details, visit=drop_falsey)

@app.get("/group/{group}/power_details")
async def power_cuts(group: str):
    token = get_verification_token()
    details = get_all_power_cut_events(token)

    for power_details in details:
        if 'loadShedGroupId' in power_details and power_details['loadShedGroupId'] == group.capitalize():
            return remap(power_details, visit=drop_falsey)
    return {}
