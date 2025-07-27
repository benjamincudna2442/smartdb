import asyncio
import json
import os
import time
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import pycountry
import pycountry_convert
from typing import Optional

app = FastAPI()
COUNTRY_JSON_DIR = "data"
BIN_INDEX = {}
COUNTRY_DATA = {}
START_TIME = time.time()

async def load_data():
    if not os.path.exists(COUNTRY_JSON_DIR):
        return
    for filename in os.listdir(COUNTRY_JSON_DIR):
        if filename.endswith('.json'):
            country_code = filename.replace('.json', '').upper()
            file_path = os.path.join(COUNTRY_JSON_DIR, filename)
            async with asyncio.Lock():
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                COUNTRY_DATA[country_code] = data
                for entry in data:
                    if 'bin' in entry:
                        BIN_INDEX[entry['bin']] = entry

def get_country_info(country_code: str) -> dict:
    country = pycountry.countries.get(alpha_2=country_code.upper())
    if not country:
        return {
            "A2": country_code.upper(),
            "A3": "",
            "N3": "",
            "Name": "",
            "Cont": ""
        }
    try:
        continent_code = pycountry_convert.country_alpha2_to_continent_code(country.alpha_2)
        continent = pycountry_convert.convert_continent_code_to_continent_name(continent_code)
    except:
        continent = ""
    return {
        "A2": country.alpha_2,
        "A3": country.alpha_3,
        "N3": country.numeric,
        "Name": country.name,
        "Cont": continent
    }

def format_entry(entry: dict) -> dict:
    country_code = entry.get('country_code', '').upper()
    country_info = get_country_info(country_code)
    return {
        "bin": entry.get('bin', ''),
        "brand": entry.get('brand', ''),
        "category": entry.get('category', ''),
        "CardTier": f"{entry.get('category', '')} {entry.get('brand', '')}".strip(),
        "country_code": country_code,
        "Type": entry.get('type', ''),
        "country_code_alpha3": entry.get('country_code_alpha3', ''),
        "Country": country_info,
        "issuer": entry.get('issuer', ''),
        "phone": entry.get('phone', ''),
        "type": entry.get('type', ''),
        "website": entry.get('website', '')
    }

@app.on_event("startup")
async def startup_event():
    await load_data()

@app.get("/api/bin")
async def get_bins(
    bank: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    bin: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, gt=0)
):
    if bank:
        if not COUNTRY_DATA:
            return {
                "status": "error",
                "message": f"Data directory not found or empty: {COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        matching_bins = []
        async for data in COUNTRY_DATA.values():
            for entry in data:
                if 'issuer' in entry and bank.lower() in entry['issuer'].lower():
                    matching_bins.append(format_entry(entry))
        if not matching_bins:
            return {
                "status": "error",
                "message": f"No matches found for bank: {bank}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        if limit is not None:
            matching_bins = matching_bins[:limit]
        return {
            "status": "SUCCESS",
            "data": matching_bins,
            "count": len(matching_bins),
            "filtered_by": "bank",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        }
    
    elif country:
        country = country.upper()
        if country not in COUNTRY_DATA:
            return {
                "status": "error",
                "message": f"No data found for country code: {country}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        data = [format_entry(entry) for entry in COUNTRY_DATA[country]]
        if limit is not None:
            data = data[:limit]
        return {
            "status": "SUCCESS",
            "data": data,
            "count": len(data),
            "filtered_by": "country",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        }
    
    elif bin:
        if not BIN_INDEX:
            return {
                "status": "error",
                "message": f"Data directory not found or empty: {COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        if bin in BIN_INDEX:
            return {
                "status": "SUCCESS",
                "data": [format_entry(BIN_INDEX[bin])],
                "count": 1,
                "filtered_by": "bin",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        return {
            "status": "error",
            "message": f"No matches found for BIN: {bin}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }
    
    else:
        return {
            "status": "error",
            "message": "Please provide either 'bank', 'country', or 'bin' query parameter",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }

@app.get("/api/binfo")
async def get_bin_info(bin: Optional[str] = Query(None)):
    if not bin:
        return {
            "status": "error",
            "message": "Please provide 'bin' query parameter",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }
    if not BIN_INDEX:
        return {
            "status": "error",
            "message": f"Data directory not found or empty: {COUNTRY_JSON_DIR}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }
    if bin in BIN_INDEX:
        return {
            "status": "SUCCESS",
            "data": [format_entry(BIN_INDEX[bin])],
            "count": 1,
            "filtered_by": "bin",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        }
    return {
        "status": "error",
        "message": f"No matches found for BIN: {bin}",
        "api_owner": "@ISmartCoder",
        "api_channel": "@TheSmartDev"
    }

@app.get("/health")
async def health_check():
    uptime = time.time() - START_TIME
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "api_info": {
            "version": "1.0.0",
            "developer": "@ISmartCoder"
        },
        "api_owner": "@ISmartCoder",
        "api_channel": "@TheSmartDev"
    }

@app.get("/", response_class=HTMLResponse)
async def welcome():
    async with asyncio.Lock():
        with open('status.html', 'r', encoding='utf-8') as file:
            return file.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
