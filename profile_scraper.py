import utils
from InstagramAPI import InstagramAPI
from OverdriveDB import Mongoloid
import time
import pickle
from threading import Thread
import re

#### Class that performs botnet scraping
class ProfileScraper(Thread):

    target_queue = []

    def __init__(self, username, password, mongoloid):
        super(ProfileScraper, self).__init__()
        self.daemon = True
        self.mongoloid = mongoloid

        # initialize login info
        self.username = username
        self.password = password

        print("Bot initialized: " + self.username)


        # attempt to reuse a session, if not regenerate a pickle file

        try:
            with open ("/loginsessions/" + (str(self.username) + ".p", "rb") as f:
                self.api = pickle.load(f)
        except:
            self.api = InstagramAPI(self.username, self.password)
            self.api.login()

            with open("/loginsessions/" + str(self.username) + ".p", "wb") as f:
                pickle.dump(self.api, f)
        

    def run(self):
        print("Bot loop starting")

        regex_string = "(!?(followers|follow|(\d+k)|tag|daily|god|marketing|spam|meme|nsfw|fashon|.com|)).*"
        regx = re.compile(regex_string, re.IGNORECASE)

        while True:
            self.target = self.mongoloid.get_user_by_metric({ \
                'scraped' : {"$exists" : False}, \
                'follower_count' : {"$gt": 100, "$lt" : 1000}, \
                'following_count' : {"$gt": 100, "$lt" : 1000}, \
                'is_private' : False,
                'biography' : {'$regex': regx} \
                })

            print(self.username)
            print(self.target['pk'])                
            print()

            # retrieve sets of followers and following from target profile
            followers = set(utils.user_pk_list(utils.getTotalFollowers(self.api, self.target['pk'])))
            following = set(utils.user_pk_list(utils.getTotalFollowing(self.api, self.target['pk'])))
            result = followers.union(following)
            
            # save the individual accounts in each for scraping in the future
            for item in result:
                self.mongoloid.write_api_pk(self.api, item)

            # append these lists to the target object
            self.target['followers'] = list(followers)
            self.target['following'] = list(following)

            # store target with new rich download information to the database
            self.mongoloid.write_user_item(self.target)
            self.mongoloid.mark_user_scraped(self.target['pk'])


        