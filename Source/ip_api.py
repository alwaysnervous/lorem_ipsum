import requests
import json


def get_city_by_ip(ip):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/iplocate/address"

    payload = json.dumps({
        "ip": ip
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Token a70a807dfb484766daff3ef4edc31f008c167800'
    }

    response = requests.request("POST", url,
                                headers=headers, data=payload)

    try:
        city = response.json()["location"]["value"]
    except (KeyError, TypeError):
        city = None

    return city
