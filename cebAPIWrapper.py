import asyncio
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from boltons.iterutils import remap

drop_falsey = lambda path, key, value: bool(value)

class CebAPI:
    ceb_home = "https://cebcare.ceb.lk/Incognito/DemandMgmtSchedule"
    ceb_power_cut_details_endpoint = "https://cebcare.ceb.lk/Incognito/GetLoadSheddingGeoAreas"
    ceb_load_shedding_events_endpoint = "https://cebcare.ceb.lk/Incognito/GetLoadSheddingEvents"
    token = ""
    
    def __init__(self) -> None:
        self.r_session = requests.Session()
        self.refresh_token()

    def refresh_token(self):
        self.token = self.get_verification_token() 
    
    def get_verification_token(self):
        html = self.r_session.get(self.ceb_home, verify=False).text
        soup = BeautifulSoup(html, 'html.parser')
        token = soup.find("input", attrs={ "name": "__RequestVerificationToken" })

        return token.attrs.get("value")
    
    def _get_all_power_cut_events(self):
        today = datetime.now(pytz.timezone("Asia/Colombo"))
        next_day = today + timedelta(days=1)
        
        res = self.r_session.post(self.ceb_load_shedding_events_endpoint, 
                data={
                    "StartTime": today.date(),
                    "EndTime": next_day.date()
                },
                headers={
                    "requestverificationtoken": self.token
                },
                verify=False
            )
        
        return res
    
    def get_all_power_cut_events(self):
        res = self._get_all_power_cut_events()

        if res.status_code == 400:
            self.refresh_token()
            res = self._get_all_power_cut_events()
        
        if res.status_code != 200:
            raise Exception(f"Request to CEB API failed with {res.status_code}")

        return remap(res.json(), visit=drop_falsey)
    
    def get_group_power_cut_events(self, group: str):
        details = self.get_all_power_cut_events()

        power_list = []

        for power_details in details:
            if 'loadShedGroupId' in power_details and power_details['loadShedGroupId'].capitalize() == group.capitalize():
                power_list.append(remap(power_details, visit=drop_falsey))

        return power_list
    
    def _get_power_cut_details(self,group_letter: str):
        res = self.r_session.get(self.ceb_power_cut_details_endpoint, 
                params={
                    "LoadShedGroupId":group_letter.capitalize()
                },
                headers={
                    "requestverificationtoken": self.token
                },
                verify=False
            )
        
        if res.status_code != 200:
            raise Exception(f"Request to CEB API failed with {res.status_code}")

        string = res.content.decode('unicode_escape')
        return json.loads(string[1:-1])