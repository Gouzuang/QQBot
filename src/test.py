import requests
import json

url = "http://192.168.3.100:3000/send_private_msg"

payload = json.dumps({
   "user_id": 3282631297,
   "message": [{'type': 'reply', 'data': {'id': 1233361447}}, {'type': 'text', 'data': {'text': "发生错误: 'echo_message' object is not callable"}}]
})
headers = {
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)