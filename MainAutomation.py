import utils
from InstagramAPI import InstagramAPI
from OverdriveDB import Mongoloid
import time
import pickle
from threading import Thread
import re
import generate_login
import datetime
import numpy

class MainAutomation(Thread):

    def __init__(self):
        super(MainAutomation, self).__init__()
        self.daemon = True
        
        print("Main Automation Initializing...")
        print("\n")

        self.mongoloid = Mongoloid()

        self.designated_datetime = datetime.datetime.now()
        self.timedelay = 1
        
        generate_login.logIn()

        # attempt to log in, if file is not found, generate a login session
        with open("mainaccount.p", "rb") as f:
            self.api = pickle.load(f)

        # if databse is not populated with account telemetry, then retrieve and populate
        if self.mongoloid.followers_count() == 0:
            self.mongoloid.set_followers(utils.getTotalFollowers(self.api, self.api.username_id))
        if self.mongoloid.following_count() == 0:
            self.mongoloid.set_following(utils.getTotalFollowing(self.api, self.api.username_id))    

    def run(self):
        self.designated_datetime = self.designated_datetime - datetime.timedelta(hours = self.timedelay)
        while True:
            if datetime.datetime.now() <= self.designated_datetime + datetime.timedelta(hours = self.timedelay):
                continue
            
            self.designated_datetime = datetime.datetime.now()
            print("Running Main Automation")
            print(self.designated_datetime)

            # retrieve followers and following from the account
            followers_object = utils.getTotalFollowers(self.api, self.api.username_id)
            following_object = utils.getTotalFollowing(self.api, self.api.username_id)
            
            followers = set(utils.user_pk_list(followers_object))
            following = set(utils.user_pk_list(following_object))

            # get followers from previous time
            old_followers = set(self.mongoloid.get_followers())
            old_following = set(self.mongoloid.get_following())

            self.mongoloid.set_followers(utils.getTotalFollowers(self.api, self.api.username_id))
            self.mongoloid.set_following(utils.getTotalFollowing(self.api, self.api.username_id))    

            # current followers - old followers = new following students
            new_followers = followers - old_followers
            print("New Followers")
            print(new_followers)
            
            # old followers - current followers = people who unfollowed me
            unfollowed_me = old_followers - followers
            print("Unfollowed Me")
            print(unfollowed_me)

            # everyone in following, and not in followers, means that our follow is not mutual
            # and not in my favor
            
            print("asymetric follows")
            asymetric_follows = following - followers
            asymetric_follows_object = []
            for target in asymetric_follows:
                new_target = self.mongoloid.find_pk(target)
                if(new_target == None):
                    print("Target not found, using api to get info")
                    self.mongoloid.write_api_pk(self.api, target)
                    new_target = self.mongoloid.find_pk(target)
                print(target)
                asymetric_follows_object.append(self.mongoloid.find_pk(target))

            # unfollow everyone who unfollowed me
            print("Unfollowing losers")
            for target in unfollowed_me:
                if target in following:
                    utils.unfollow_user(self.api, target)
                    # sleep for random normal distribution mu = 2 minutes sigma = 30 seconds
                    time.sleep(numpy.random.normal(120, 30))

            unfollowed = old_following - following
            print("Unfollowed")
            print(unfollowed)
            print()

            new_following = following - old_following
            print("New Following")
            print()

            new_entries = new_followers.union(new_following)
            
            # will put the new users into the database with the curent time
            for target in new_entries:
                if(self.mongoloid.find_pk(target) == None):
                    print("Writing to database:")
                    self.mongoloid.write_user_item(target)

            blacklist = unfollowed_me.union(unfollowed)
            for target in blacklist:
                print("Adding to blacklist")
                print(target)
                black = self.mongoloid.find_pk(target)
                if black == None:
                    self.mongoloid.write_api_pk(self.api, target)
                    black = self.mongoloid.find_pk(target)
                black['blacklisted'] = True
                self.mongoloid.write_user_item(black)
                self.mongoloid.blacklist_add(target)

            def lambdaThing(target):
                #print(target)
                return target['follow_time']

            print("Unfollowing random asymetric:")
            if(len(asymetric_follows) > 0):
                # unfollow random people with lowest interaction time
                sorted_by_time = sorted(asymetric_follows_object, key=lambda target: lambdaThing(target))[:6]
                for item in sorted_by_time:
                    print(item['pk'])
                    utils.unfollow_user(self.api, item['pk'])
                    time.sleep(numpy.random.normal(120, 30))

            print()

            # follow random people
            print("Following random people")
            if((len(following) < len(followers)) & (len(following) < 1000)):
                
                regex_string = "(!?(followers|follow|(\d+k)|tag|daily|god|marketing|spam|meme|nsfw|fashon|.com|)).*"
                regx = re.compile(regex_string, re.IGNORECASE)

                x = 1
                y = 1
                while (x < 5) and (y < 100):
                    y = y + 1
                    target = self.mongoloid.get_user_by_metric({ \
                    'blacklisted' : {"$exists" : False}, \
                    'scraped' : {"$exists" : True}, \
                    'follower_count' : {"$gt": 50, "$lt" : 2000}, \
                    'following_count' : {"$gt": 50, "$lt" : 2000}, \
                    'is_private' : False,
                    'biography' : {'$regex': regx} \
                    })

                    if target == None:
                        continue
                    
                    if (not self.mongoloid.blacklist_member(target['pk'])):
                        x = x + 1
                        print("Following user:")
                        print(target['pk'])
                        utils.follow_user(self.api, target['pk'])
                        target['followed'] = True
                        self.mongoloid.write_user_item(target)
                        time.sleep(numpy.random.normal(120, 30))
                    else:
                        print("retrieved blacklisted object for follow")
                        print(target['pk'])
                        target['blacklisted'] = True
                        self.mongoloid.write_user_item(target)

            print("FINISHED MAIN LOOP")
            print(datetime.datetime.now())
            print(str((self.designated_datetime + datetime.timedelta(hours = self.timedelay)) - datetime.datetime.now()))
            print("time left to go..") 