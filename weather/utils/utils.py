import asyncio
from aiohttp import ClientSession
async def get_latlon(city:str):
    async with ClientSession() as session:
        url = "https://api.geoapify.com/v1/geocode/search?"
        apiKey = 'bd0321853ace402aa944b77e215a5175'
        headers = {
            "Accept": "application/json"
        }
        params = {
            'city': city,
            'format': 'json',
            'apiKey': apiKey,
        }

        async with session.get(url,headers=headers, params=params) as response:
            latlon_json = await response.json()
            result = []
            for entry in latlon_json['results']:
                # print(f"{city} in {entry['country']}: lat {entry['lat']}, lon {entry['lon']}")
                result.append({'lat': entry['lat'], 'lon': entry['lon'], 'country':entry['country']})
            return {'city': city, 'result': result}
async def get_weather_by_latlon(lat:float, los:float):
    async with ClientSession() as session:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": los,
            "hourly": "temperature_2m,weather_code",
            "timezone": "Europe/Moscow",
            "forecast_days": 1
        }
        async with session.get(url, params=params) as response:
            return await response.json()
async def get_translation(text, source="auto", target='en'):
    async with ClientSession() as session:
        url = "https://deep-translator-api.azurewebsites.net/google/"
        payload = {
            "source": source,
            "target": target,
            "text": text,
        }
        async with session.post(url, json=payload) as response:
            return await response.json()
async def handle(city):
    city_eng = await get_translation(city)
    latlons = await get_latlon(city_eng['translation'])
    result = []
    for entry in latlons['result']:
        weather = await get_weather_by_latlon(entry['lat'], entry['lon'])
        weather['country'] = entry['country']
        result.append(weather)
    return result
async def main(city):
    get_weather_task = asyncio.create_task(handle(city))
    return await get_weather_task