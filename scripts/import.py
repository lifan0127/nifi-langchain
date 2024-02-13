import requests
import json
import os

nifi_api_url = "https://localhost:8443/nifi-api"

response = requests.post(f'{nifi_api_url}/access/token', data={
  'username': os.environ['SINGLE_USER_CREDENTIALS_USERNAME'],
  'password': os.environ['SINGLE_USER_CREDENTIALS_PASSWORD'],
}, verify=False)
token = response.text

flow_definition_files = [
  'Hello_LangChain.json',
  'Retrieval_Augmented_Generation_(RAG).json',
  'Dynamic_Routing.json',
]

for file in flow_definition_files:
  with open(f'/tmp/examples/{file}', 'r') as f:
      flow_definition_content = f.read()

  flow_definition = json.loads(flow_definition_content)
  flow_name = flow_definition['flowContents']['name']
  position_x = flow_definition['flowContents']['position']['x']
  position_y = flow_definition['flowContents']['position']['y']

  response = requests.post(
    f'{nifi_api_url}/process-groups/root/process-groups/upload', 
    headers={'Authorization': f'Bearer {token}'},
    files={
      'file': ('Hello_LangChain.json', flow_definition_content, 'application/json'),
      'groupName': flow_name,
      'positionX': str(position_x),
      'positionY': str(position_y),
      'clientId': 'langchain'
    }, verify=False)

label = {
  "revision": {
    "version": 0
  },
  "component": {
    "label": "Demo of NiFi-LangChain Processors\n\nMake sure to add your OpenAI API key in the 'main' parameter context.",
    "width": 600,
    "height": 80,
    "style": {
      "font-size": "18px"
    },
    "position": {
      "x": 650,
      "y": 120
    }
  }
}

response = requests.post(
  f'{nifi_api_url}/process-groups/root/labels', 
  headers={'Authorization': f'Bearer {token}'},
  json=label, verify=False)
