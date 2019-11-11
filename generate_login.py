import pickle
import credentials
from InstagramAPI import InstagramAPI

def logIn():
    # log in with instagram service
    api = InstagramAPI(credentials.instagram_username, credentials.instagram_password)
    api.login()

    # dump the logged in pickle file for retrieval
    with open("/loginsessions/mainaccount.p", "wb") as f:
        pickle.dump(api, f)