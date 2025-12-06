import httpx

url = "http://localhost:8000/profile/add_comment"

payload = {"body": "228", "to": "lolkek"}
headers = {
    'Cookie': '_lolkek_access_v1=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsb2xrZWsiLCJleHAiOjE3NjUwMzEyMzF9.roWx0zG2FVYhMQV6UHnfKhlzvUh-3tl2NYnddSB-UaY; Path=/; HttpOnly'
}

with httpx.Client() as client:
    while True:
        response = client.post(url, headers=headers, data=payload)
