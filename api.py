from flask import Flask, jsonify, request
import os
import json
import time
from datetime import datetime, timezone

app = Flask(__name__)

COUNTRY_JSON_DIR = "data"
START_TIME = time.time()

@app.route('/api/bin', methods=['GET'])
def get_bins():
    bank = request.args.get('bank')
    country = request.args.get('country')
    limit = request.args.get('limit', default=100, type=int)
    
    if bank:
        if not os.path.exists(COUNTRY_JSON_DIR):
            return jsonify({
                "status": "error",
                "message": f"Data directory not found: {COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500

        matching_bins = []
        for filename in os.listdir(COUNTRY_JSON_DIR):
            if filename.endswith('.json'):
                country_code = filename.replace('.json', '').upper()
                file_path = os.path.join(COUNTRY_JSON_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                for entry in data:
                    if 'issuer' in entry and bank.lower() in entry['issuer'].lower():
                        matching_bins.append(entry)

        if not matching_bins:
            return jsonify({
                "status": "error",
                "message": f"No matches found for bank: {bank}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 404
                
        
        if limit > 0 and len(matching_bins) > limit:
            matching_bins = matching_bins[:limit]
            
        return jsonify({
            "status": "success",
            "data": matching_bins,
            "count": len(matching_bins),
            "filtered_by": "bank",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        })

    elif country:
        country = country.upper()
        country_file = os.path.join(COUNTRY_JSON_DIR, f"{country}.json")
        
        try:
            with open(country_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if limit > 0 and len(data) > limit:
                data = data[:limit]
            return jsonify({
                "status": "success",
                "data": data,
                "count": len(data),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            })
        except FileNotFoundError:
            return jsonify({
                "status": "error",
                "message": f"No data found for country code: {country}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 404
        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "message": f"Invalid JSON in file: {country_file}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500
    
    else:
        return jsonify({
            "status": "error",
            "message": "Please provide either 'bank' or 'country' query parameter",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 400

@app.route('/')
def welcome():
    try:
        with open('status.html', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "Welcome page not found",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check if the API is running and data directory exists
        data_dir_exists = os.path.exists(COUNTRY_JSON_DIR)
        if not data_dir_exists:
            return jsonify({
                "status": "unhealthy",
                "message": f"Data directory not found: {COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500

        # Try accessing the welcome endpoint
        response = app.test_client().get('/')
        if response.status_code != 200:
            return jsonify({
                "status": "unhealthy",
                "message": "Welcome page request failed",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }), 500

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "cache_size": 5,
            "uptime": time.time() - START_TIME,
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
