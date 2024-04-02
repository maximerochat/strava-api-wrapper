from dotenv import load_dotenv
import os

from strava_api_wrapper import StravaApiWrapper

load_dotenv()
def func_cb(code):
    print(code)

api = StravaApiWrapper(int(os.getenv("CLIENT_ID")), os.getenv("CLIENT_SECRET"))
api.set_callback(func_cb)
api.run()

