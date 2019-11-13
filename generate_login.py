import pickle
import credentials
from InstagramAPI import InstagramAPI
import os

def logIn():

    if not os.path.exists('loginsessions'):
        os.makedirs('loginsessions')

    # log in with instagram service
    api = InstagramAPI(credentials.instagram_username, credentials.instagram_password)
    api.login()

    # dump the logged in pickle file for retrieval
    with open("/loginsessions/mainaccount.p", "wb") as f:
        pickle.dump(api, f)