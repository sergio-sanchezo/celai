from redis import Redis
import json

client = Redis.from_url('redis://localhost:6379/0')

# ADD TO BLACKLIST
# client.hset("blacklistmw", "+56352280778", '{"reason": "Spam"}')

# REMOVE FROM BLACKLIST
client.hdel("blacklistmw", "+56352280778")

# GET ENTRY
# entry = client.hget("blacklistmw", "+56352280778")
# print(json.loads(entry))