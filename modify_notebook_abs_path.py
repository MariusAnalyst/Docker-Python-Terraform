import json
import os

notebook_path = 'data_warehouse_w3/load_yellow_taxi_data.ipynb'
credentials_path = 'data_warehouse_w3/keys/teraform-mar-d29601022ad5.json'
abs_credentials_path = os.path.abspath(credentials_path)

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

for cell in notebook['cells']:
    if cell.get('id') == 'e37674ab':
        cell['source'] = [f'CREDENTIALS_FILE = r"{abs_credentials_path}"']

with open(notebook_path, 'w') as f:
    json.dump(notebook, f, indent=2)
