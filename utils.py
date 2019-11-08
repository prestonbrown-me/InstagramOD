from InstagramAPI import InstagramAPI
import time
import random
import datetime
import pickle
import numpy

ratelimit = {
    # 5 minutes
    'interaction_delay': 60*5,
    # 60 minutes
    'interaction_error': 60*60,

    # 10 minutes
    'user_delay': 60 * 10,
    # 30 minutes
    'user_error': 60 * 30
}

# get followers for PK as user objects
def getTotalFollowers(api, user_id, maxRetrieve = 0):
    followers = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''

        _ = api.getUserFollowers(user_id, maxid=next_max_id)
        followers.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
        time.sleep(numpy.random.normal(30, 10))

        # we can break out and return if we have the num followers we need
        if(maxRetrieve > 0):
            if(len(followers) >= maxRetrieve):
                while(len(followers) != maxRetrieve):
                    followers.pop()
                return followers

    return followers

# get following for PK as user objects
def getTotalFollowing(api, user_id, maxRetrieve = 0):
    following = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''
        _ = api.getUserFollowings(user_id, maxid=next_max_id)
        following.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
        time.sleep(numpy.random.normal(30, 10))

        if(maxRetrieve > 0):
            if(len(following) >= maxRetrieve):
                while(len(following) != maxRetrieve):
                    following.pop()
                return following

    return following

# convert list of rich follower list into only a list of PKs
def user_pk_list(followList):
    result = []
    for item in followList:
        result.append(item["pk"])

    return result

# unfollow user with PK
def unfollow_user(api, user_id):
    while not api.unfollow(user_id):
        print("FAULT: Failed to unfollow user. Sleeping for 1 hour")
        print(datetime.datetime.now())
        time.sleep(ratelimit['interaction_error'])

# follow user with PK
def follow_user(api, user_id):
    while not api.follow(user_id):
        print("FAULT: Failed to follow user. Sleeping for 1 hour")
        print(datetime.datetime.now())
        time.sleep(ratelimit['interaction_error'])

# unfollow all accounts you currently follow
def unfollow_all():
    api = None
    with open("apiPickleFile.p", "rb") as f:
        api = pickle.load(f)

    following = getTotalFollowing(api, api.username_id)
    print(following)

    x = 0
    for item in following:
        print(str(x) + ": " + str(item['pk']))
        x = x + 1
        unfollow_user(api, item['pk'])
        time.sleep(ratelimit['interaction_delay'])

# unfollow all accounts that don't follow you back
def unfollow_nonmutuals():
    api = None
    with open("apiPickleFile.p", "rb") as f:
        api = pickle.load(f)

    following = set(map(lambda elem: elem['pk'], getTotalFollowing(api, api.username_id)))
    print(following)
    followers = set(map(lambda elem: elem['pk'], getTotalFollowers(api, api.username_id)))
    print(followers)

    ## everyone in following but not followers are losers becuause they do not reciprocate
    stupid = following - followers

    x = 0
    for pk in stupid:
        print(str(x) + ": " + str(pk))
        x = x + 1
        unfollow_user(api, pk)
        time.sleep(ratelimit['interaction_delay'] + random.randint(-60, 120))
