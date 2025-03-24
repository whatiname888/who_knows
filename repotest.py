import requests
import json

url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "deepseek",
  "gl": "cn",
  "hl": "zh-cn"
})
headers = {
  'X-API-KEY': '85d38035be4dfdd584582b9f88b5503481dea12c',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)