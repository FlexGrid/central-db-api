import requests
import json
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)


class RestClient:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.token = None

    def auth(self):
        if (self.token):
            return self.token

        url = f"{self.base_url}/oauth/token"

        payload = {
            'client_id': os.getenv('CLIENT_ID'),
            'grant_type': 'password',
            'username': os.getenv('USER_NAME'),
            'password': os.getenv('PASSWORD')
        }

        files = []
        headers = {}

        response = requests.request("POST",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    files=files)

        print(response.text)

        self.token = json.loads(response.text)['access_token']
        return self.token

    def get_collection(self, collection):
        url = f"{self.base_url}/{collection}"

        payload = {}
        headers = {'Authorization': f'Bearer {self.auth()}'}

        result = []
        while True:
            response = requests.request("GET",
                                        url,
                                        headers=headers,
                                        data=payload)

            print(response.text)
            resp_json = json.loads(response.text)
            result.extend(resp_json["_items"])
            if not 'next' in resp_json['_links']:
                break
            url = f"{self.base_url}/{resp_json['_links']['next']['href']}"
        return result
        # print(json.dumps(result, indent=4, sort_keys=True))

    def post_collection(self, collection, list):
        url = f"{self.base_url}/{collection}"
        print(f"Trying to post to {url}")

        payload = list
        headers = {
            'Authorization': f'Bearer {self.auth()}',
            'Content-Type': 'application/json'
        }
        # print(json.dumps(payload, indent=4, sort_keys=True))

        response = requests.request("POST",
                                    url,
                                    headers=headers,
                                    data=json.dumps(payload))
        print(response.text)
        return [obj["_id"] for obj in json.loads(response.text)["_items"]]

    def delete_collection(self, collection):
        print(f"Deleting {collection}")
        for obj in self.get_collection(collection):
            url = f"{self.base_url}/{collection}/{obj['_id']}"
            headers = {
                'Authorization': f'Bearer {self.auth()}',
                'If-Match': obj['_etag']
            }
            response = requests.request("DELETE",
                                        url,
                                        headers=headers,
                                        data={})
            if response.text:
                print(response.text)
