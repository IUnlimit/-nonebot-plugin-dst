import base64
import pprint
from functools import cache
from typing import List, Dict

import requests

API_GET_REGION = "https://lobby-v2-cdn.klei.com/regioncapabilities-v2.json"
API_GET_SERVER_LIST = "https://lobby-v2-cdn.klei.com/{region}-{platform}.json.gz"
API_GET_SERVER_DETAIL = "https://lobby-v2-{region}.klei.com/lobby/read"

def extract_error(json: Dict) -> str:
    if json.get("Error") is not None:
        return json["Error"]["Code"]
    return ""

@cache
def get_regions() -> List[str] | str:
    resp = requests.get(API_GET_REGION).json()
    if len(extract_error(resp)) != 0:
        return extract_error(resp)
    return [region['Region'] for region in resp['LobbyRegions']]

def get_server_list(region, platform) -> List[Dict[str, any]] | str:
    resp = requests.get(API_GET_SERVER_LIST.format(**{
        "region": region,
        "platform": platform
    })).json()
    if len(extract_error(resp)) != 0:
        return extract_error(resp)
    return resp["GET"]

def get_server_detail(region, __row_id, token) -> List[Dict[str, any]] | str:
    resp = requests.post(API_GET_SERVER_DETAIL.format(**{
        "region": region
    }), json={
        "__token": token,
        "__gameId": "DST",
        "query": {
            "__rowId": __row_id
        }
    }).json()
    if len(extract_error(resp)) != 0:
        return extract_error(resp)
    return resp["GET"]

def parse_base64(encoded) -> str:
    decoded_bytes = base64.b64decode(encoded)
    pprint.pprint(decoded_bytes)
    return decoded_bytes.decode('gbk', errors='ignore')