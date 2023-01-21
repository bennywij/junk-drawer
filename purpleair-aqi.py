#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 10:32:36 2022

@author: benny
"""
SENSOR_ID = 128231
PA_API_Key = "8AF289D3-3772-11EC-B42E-42010A800002"
PA_URL = "https://api.purpleair.com/v1/sensors/"+str(SENSOR_ID)

try:

    import requests
    headers = {"X-API-Key": PA_API_Key}  
    response = requests.get(PA_URL, headers=headers)  
    response_json = response.json()


except ImportError:
    # without requests
    import json
    from urllib.request import Request, urlopen
    req = Request(PA_URL)
    req.add_header('X-API-Key', PA_API_Key)
    content = urlopen(req).read()
    encoding = urlopen(req).info().get_content_charset('utf-8')
    response_json = json.loads(content.decode(encoding))



pm25 = response_json['sensor']['stats']['pm2.5']
try: 
	humidity = response_json['sensor']['humidity']
except:
	humidity = 75




# formula from https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwi72OSY0Jn4AhUim44IHWBHBxQQFnoECAQQAQ&url=https%3A%2F%2Fcfpub.epa.gov%2Fsi%2Fsi_public_file_download.cfm%3Fp_download_id%3D540979%26Lab%3DCEMM&usg=AOvVaw1VrPwqsac3Vh-XXGPGbkfG
epa_adjusted_pm25 = pm25*0.52 + (humidity*-0.085) + 5.71


def calculate_AQI (pm) :
    
    if pm <= 12:
        aqi = pm/12*50
    elif pm <= 35.4:
        aqi = (pm-12.1)/23.4*50 + 50
    elif pm <= 55.5:
        aqi = (pm-35.5)/20*50 + 100
    elif pm <= 150.4:
        aqi = (pm-55.5)/95*50 + 150
    elif pm <= 250.4:
        aqi = (pm-150.5)/100*100 + 200
    elif pm <= 500.4:
        aqi = (pm-250.5)/250*200 + 300
    else:
        aqi = 999

    return round(aqi)


print("☁︎ "+str(calculate_AQI(epa_adjusted_pm25)))
