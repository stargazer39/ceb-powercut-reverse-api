from concurrent.futures import thread
from fastapi import FastAPI
from cebAPIWrapper import CebAPI
from utils import retry_util

app = FastAPI()
ceb_api = CebAPI()

@app.get("/power_cuts")
async def power_cuts():
    return retry_util(ceb_api.get_all_power_cut_events)

@app.get("/group/{group}/power_details")
async def power_cuts(group: str):
    return retry_util(ceb_api.get_group_power_cut_events, group)
