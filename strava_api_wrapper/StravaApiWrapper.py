import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

import os
import requests
import webbrowser
import threading

from flask import Flask, request


def func_cb(access_token):
    print("function called")
    configuration = swagger_client.Configuration()
    configuration.debug = True
    configuration.access_token = access_token
    configuration

    # create an instance of the API class
    api_instance = swagger_client.ActivitiesApi(swagger_client.ApiClient(configuration))
    id = 789  # Long | The identifier of the activity.
    includeAllEfforts = True  # Boolean | To include all segments efforts. (optional)
    before = 56  # Integer | An epoch timestamp to use for filtering activities that have taken place before a certain time. (optional)
    after = 56  # Integer | An epoch timestamp to use for filtering activities that have taken place after a certain time. (optional)
    page = 56  # Integer | Page number. Defaults to 1. (optional)
    perPage = 56  # Integer | Number of items per page. Defaults to 30. (optional) (default to 30)

    try:
        # Get Activity
        api_response = api_instance.get_logged_in_athlete_activities()

        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ActivitiesApi->getActivityById: %s\n" % e)


class Token:
    def __init__(self, access, refresh, expires_at, expires_in, save_token=True, file_path="token.txt"):
        self.access_token = access
        self.refresh_token = refresh
        self.expires_at = expires_at
        self.expires_in = expires_in
        self.base_url = "https://www.strava.com/oauth/token?"
        if self.is_valid() and save_token:
            with open(file_path, "w") as f:
                f.write("\n".join([self.access_token, self.refresh_token, str(self.expires_at), str(self.expires_in)]))

    def is_valid(self):
        if (time.time() <= self.expires_at):
            return True
        return False

    @staticmethod
    def save_exists(filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return len(f.readlines()) == 4

        return False

    @staticmethod
    def token_from_save(filename):
        with open(filename, "r") as f:
            content = f.readlines()
        content = [l.replace("\n", "") for l in content]
        return Token(content[0], content[1], int(content[2]), int(content[3]))

class StravaApiWrapper:

    def __init__(self, client_id, client_secret, save_filename="token.txt"):
        self.app = Flask(__name__)
        self.app.add_url_rule('/strava_auth', 'strava_auth', self.strava_auth)
        self.background_thread = threading.Thread(target=self.open_browser)
        self.base_url = "https://www.strava.com/"
        self.callback = None
        self.args = None
        self.server_running = False
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.save_filename = save_filename

    def open_browser(self):
        time.sleep(3)
        base_url = "https://www.strava.com/oauth/authorize?client_id=97224&redirect_uri=http://127.0.0.1:5000/strava_auth&response_type=code&approval_prompt=auto&scope=activity:read_all"
        webbrowser.open(base_url)
        return

    def trigger_callback(self, code):
        if self.callback is not None:
            if self.args is not None:
                self.callback(code, *self.args)
            else:
                self.callback(code)

    def set_callback(self, func, *args):
        self.callback = func
        self.args = args

    def strava_auth(self):
        # Extract the 'code' parameter from the URL query string
        print("a asdfjsafksakfds")
        code = request.args.get('code')
        print(code)
        if code is not None:
            self.get_access_token_from_code(code)

        self.trigger_callback(self.get_access_token())

        if code:
            return f"Received code: {code}"
        else:
            return "No code parameter found in the URL"

    def run(self):
        if Token.save_exists(self.save_filename):
            self.token = Token.token_from_save(self.save_filename)
            token = self.get_access_token()
            if token is not None:
                self.trigger_callback(token)
                return
        self.server_running = True
        self.background_thread.start()
        self.app.run(debug=True)
         # Set the flag to indicate the server is running
        # self.flask_thread.start()

        # Start background task


    def stop(self):
        # Stop the Flask server
        # self.flask_server.shutdown()
        # self.flask_thread.join()  # Wait for the server thread to exit
        self.server_running = False  # Reset the flag
        # Stop the background task
        self.background_thread.join()  # Wait for the background thread to exit

    def shutdown(self):
        # Shutdown the Flask app
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'

    def get_access_token_from_code(self, code):
        res = requests.post(
            self.base_url + f"oauth/token?client_id={self.client_id}&client_secret={self.client_secret}&code={code}&grant_type=authorization_code")
        json_res = res.json()
        self.token = Token(json_res["access_token"], json_res["refresh_token"], json_res["expires_at"],
                           json_res["expires_in"])
        return

    def refresh_token(self, client_id, client_secret, grand_type="refresh_token"):
        res = requests.post(
            self.base_url + f"client_id={client_id}&client_secret={client_secret}&refresh_token={self.refresh_token}&grant_type={grand_type}")

        json_res = res.json()
        self.token = Token(json_res["access_token"], json_res["refresh_token"], json_res["expires_at"],
                           json_res["expires_in"])

    def get_access_token(self):
        if self.token is None:
            return None
        if self.token.is_valid():
            return self.token.access_token
        self.refresh_token(self.client_id, self.client_secret)
        return self.token.access_token


