from bs4 import BeautifulSoup
import datetime
import json
import pytz
import requests

def get_html(url):
	resp = requests.get(url)
	return resp.text
	
locations = ["Half-Moon-Bay-California", "Huntington-Beach", "Providence-Rhode-Island",
	"Wrightsville-Beach-North-Carolina"]
	
for location in locations:
	url = f"https://www.tide-forecast.com/locations/{location}/tides/latest"
	get_text = get_html(url)
	parse = BeautifulSoup(get_text, 'html.parser')
	
	# read JSON object
	script_tags = parse.find_all('script')
	
	# find tag containing JSON object
	target_script = None
	for script_tag in script_tags:
		content = script_tag.string
		if 'window.FCGON' in content:
			target_script = script_tag
			break
			
	# extract JSON from Javascript
	script_content = target_script.string
	json_data = json.loads(script_content.split('=')[1].strip(';\n//]]>'))
	
	tide_days = json_data.get('tideDays', [])

	print(location)
	for day in tide_days:
		date = day['date']
		sunrise = day['sunrise']
		sunset = day['sunset']
		tz = pytz.timezone("America/Los_Angeles")
		
		for tide in day['tides']:
			# check if tide is low and between sunrise and sunset
			if tide['type'] == 'low' and tide['timestamp'] >= sunrise and tide['timestamp'] <= sunset:
				# if location is on the east coast, use EST/EDT, otherwise use PST/PDT
				if "Rhode-Island" in location or "North-Carolina" in location:
					tz = pytz.timezone("America/New_York")
				time_cvt = datetime.datetime.fromtimestamp(tide['timestamp'])
				output_time = time_cvt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
				# convert height from meters to feet and round
				output_height = round(tide['height'] * 3.28084, 2)
					
				print(output_time, f"{output_height} ft")
				
	print("\n")
	
	