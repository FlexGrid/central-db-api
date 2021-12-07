import requests
import json


class RestClient:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.token = None

    def auth(self):
        if (self.token):
            return self.token

        url = f"{self.base_url}/oauth/token"

        payload = {
            'client_id': '***REMOVED***',
            'grant_type': 'password',
            'username': 'test123',
            'password': '***REMOVED***'
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

        for obj in list:
            payload = obj
            headers = {'Authorization': f'Bearer {self.auth()}', 'Content-Type': 'application/json'}
            # print(json.dumps(payload, indent=4, sort_keys=True))

            response = requests.request("POST",
                                        url,
                                        headers=headers,
                                        data=json.dumps(payload))
            print(response.text)

    def delete_collection(self, collection):
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
            print(response.text)
