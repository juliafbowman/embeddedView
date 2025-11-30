import json

# load historical file for geojson data
input_file = 'COVID-19_Cases,_Tests,_and_Deaths_by_ZIP_Code_-_Historical_20251018.geojson'
output_file = 'chicago_zipcodes.geojson'

print(f"Loading geojson data from {input_file}...")

with open(input_file, 'r') as f:
    data = json.load(f)
    
target_date = '2024-01-27T00:00:00.000'

clean_features = [
    feature for feature in data['features']
    if feature['properties'].get('week_end') == target_date
]

clean_data = {
    "type": "FeatureCollection",
    "features": clean_features
}

with open(output_file, 'w') as f:
    json.dump(clean_data, f)
    
print(f"Created output")