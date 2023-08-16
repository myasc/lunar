import sys

from kiteconnect import KiteConnect
import datetime as dt
import json


class Kite:

    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.request_token = None
        self.object = None

    def _create_kite_lib_obj(self):
        self._read_api_credentials(filepath="../api_credentials.json")
        self.object = KiteConnect(api_key=self.api_key)
        return

    def _read_api_credentials(self, filepath):
        with open(filepath, "r") as f:
            credentials_dict = json.load(f)
        self.api_key = credentials_dict["api_key"]
        self.api_secret = credentials_dict["api_secret"]
        return

    def _get_login_url(self):
        login_url = self.object.login_url()
        return login_url

    def _get_request_token(self):
        url = self._get_login_url()
        print("URL: ", url)
        token = input('Provide Request token from above url: ')
        return token

    def _save_access_token(self, token, file="../access_token.json"):
        """access taken valid till 6am the next day"""

        with open(file, "w") as f:
            time = dt.datetime.now()
            token_dict = {"access_token": token, "recorded_at": time.strftime("%Y-%m-%d_%H:%M")}
            json.dump(token_dict, f)

    def _read_access_token(self, file="../access_token.json"):
        with open(file, "r") as f:
            token_dict = json.load(f)


        recorded_at = dt.datetime.strptime(token_dict["recorded_at"], "%Y-%m-%d_%H:%M")
        print("Recorded at: ", recorded_at)
        # print(dt.datetime.now() > recorded_at + dt.timedelta(hours=6))
        if dt.datetime.now() > (recorded_at + dt.timedelta(hours=25)):
            token = None
        else:
            token = token_dict["access_token"]
        return token

    def establish_connection(self):
        self._create_kite_lib_obj()
        try:
            print("Using saved access token")
            access_token = self._read_access_token()
            if access_token is None:
                raise Exception("Access token likely expired.")
            self.object.set_access_token(access_token)
        except Exception as e:
            print(e)
            print("Generating new token")
            self.request_token = self._get_request_token()
            auth_data = self.object.generate_session(self.request_token, self.api_secret)
            self.object.set_access_token(auth_data['access_token'])
            self._save_access_token(auth_data['access_token'])

        print("Kite Connection Successful!!")

if __name__ == "__main__":
    kt = Kite()
    kt.establish_connection()
