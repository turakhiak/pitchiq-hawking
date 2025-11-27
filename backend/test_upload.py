import requests

url = 'http://localhost:8002/api/ingest'
files = {'file': open('test_pitchbook.pdf', 'rb')}
data = {
    'industry': 'Technology',
    'geography': 'North America',
    'deal_type': 'M&A'
}

try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
