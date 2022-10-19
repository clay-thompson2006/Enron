from re import I
import pymongo
from config import config

client = pymongo.MongoClient(config.mongodb)
database = client['main']
collection_users = database.get_collection("users")
collection_guilds = database.get_collection("guilds")

x = collection_users.find()

async def check_alt_and_create(user,ip_api):
        data_user = collection_users.find_one({"ip": ip_api['ip']})
        if data_user:
            if data_user['ip'] == ip_api['ip'] and data_user['user_id'] != user.id:    
                collection_users.insert_one({
                    "user_id": user.id,
                    "verified": 'Alt',
                    'ip': ip_api['ip']
                })
            return True
        else:
            collection_users.insert_one({
                "user_id": user.id,
                "verified": True,
                'ip': ip_api['ip']
            })
            return False

async def check_alt(user,ip_api):
    data_user = collection_users.find_one({"ip": ip_api['ip']})
    if data_user:
        if data_user['ip'] == ip_api['ip'] and data_user['user_id'] != user.id:    
            collection_users.find_one_and_update({
                "user_id": user.id},
                {"$set": {
                    "verified": 'Alt',
                    "ip": ip_api['ip']
                }})
            return True
    else:
        collection_users.find_one_and_update({
            "user_id": user.id},
            {"$set": {
                "verified": True,
                "ip": ip_api['ip']
            }})
        return True
