from flask import Flask, jsonify, request
import os
import json
import time
import pycountry
import pycountry_convert

app = Flask(__name__)
COUNTRY_JSON_DIR = "data"
BIN_INDEX = {}
COUNTRY_DATA = {}
START_TIME = time.time()

def load_data():
    if not os.path.exists(COUNTRY_JSON_DIR):
        return
    for filename in os.listdir(COUNTRY_JSON_DIR):
        if filename.endswith('.json'):
            country_code = filename.replace('.json', '').upper()
            file_path = os.path.join(COUNTRY_JSON_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            COUNTRY_DATA[country_code] = data
            for entry in data:
                if 'bin' in entry:
                    BIN_INDEX[entry['bin']] = entry

def get_country_info(country_code):
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

def format_entry(entry):
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

load_data()

@app.route('/api/bin', methods=['GET'])
def get_bins():
    bank = request.args.get('bank')
    country = request.args.get('country')
    bin_number = request.args.get('bin')
    limit = request.args.get('limit', default=None, type=int)
    
    if bank:
        if not COUNTRY_DATA:
            return jsonify({
                "status": "error",
                "message": f"Data directory not found or empty: {COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500
        matching_bins = []
        for data in COUNTRY_DATA.values():
            for entry in data:
                if 'issuer' in entry and bank.lower() in entry['issuer'].lower():
                    matching_bins.append(format_entry(entry))
        if not matching_bins:
            return jsonify({
                "status": "error",
                "message": f"No matches found for bank: {bank}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 404
        if limit is not None and limit > 0:
            matching_bins = matching_bins[:limit]
        return jsonify({
            "status": "SUCCESS",
            "data": matching_bins,
            "count": len(matching_bins),
            "filtered_by": "bank",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        })
    
    elif country:
        country = country.upper()
        if country not in COUNTRY_DATA:
            return jsonify({
                "status": "error",
                "message": f"No data found for country code: {country}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 404
        data = [format_entry(entry) for entry in COUNTRY_DATA[country]]
        if limit is not None and limit > 0:
            data = data[:limit]
        return jsonify({
            "status": "SUCCESS",
            "data": data,
            "count": len(data),
            "filtered_by": "country",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        })
    
    elif bin_number:
        if not BIN_INDEX:
            return jsonify({
                "status": "error",
                "message": f"Data directory not found or empty: {COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500
        if bin_number in BIN_INDEX:
            return jsonify({
                "status": "SUCCESS",
                "data": [format_entry(BIN_INDEX[bin_number])],
                "count": 1,
                "filtered_by": "bin",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            })
        return jsonify({
            "status": "error",
            "message": f"No matches found for BIN: {bin_number}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 404
    
    else:
        return jsonify({
            "status": "error",
            "message": "Please provide either 'bank', 'country', or 'bin' query parameter",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 400

@app.route('/api/binfo', methods=['GET'])
def get_bin_info():
    bin_number = request.args.get('bin')
    if not bin_number:
        return jsonify({
            "status": "error",
            "message": "Please provide 'bin' query parameter",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 400
    if not BIN_INDEX:
        return jsonify({
            "status": "error",
            "message": f"Data directory not found or empty: {COUNTRY_JSON_DIR}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 500
    if bin_number in BIN_INDEX:
        return jsonify({
            "status": "SUCCESS",
            "data": [format_entry(BIN_INDEX[bin_number])],
            "count": 1,
            "filtered_by": "bin",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        })
    return jsonify({
        "status": "error",
        "message": f"No matches found for BIN: {bin_number}",
        "api_owner": "@ISmartCoder",
        "api_channel": "@TheSmartDev"
    }), 404

@app.route('/health', methods=['GET'])
def health_check():
    uptime = time.time() - START_TIME
    return jsonify({
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "api_info": {
            "version": "1.0.0",
            "developer": "@ISmartCoder"
        },
        "api_owner": "@ISmartCoder",
        "api_channel": "@TheSmartDev"
    })

@app.route('/')
def welcome():
    with open('status.html', 'r', encoding='utf-8') as file:
        return file.read()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
