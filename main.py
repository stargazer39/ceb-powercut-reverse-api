import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import gunicorn, uvicorn

ceb_home = "https://cebcare.ceb.lk/Incognito/DemandMgmtSchedule"
ceb_power_cut_details_endpoint = "https://cebcare.ceb.lk/Incognito/GetLoadSheddingGeoAreas"

app = FastAPI()
r_session = requests.Session()

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


@app.get("/group/{group}/power_cuts")
async def power_cuts(group):
    token = get_verification_token()
    details = get_power_cut_details(group, token)
    return details
