from redis import Redis
import json

client = Redis.from_url('redis://localhost:6379/0')

# ADD TO BLACKLIST
# client.hset("blacklistmw", "+56352280778", '{"reason": "Spam"}')
client.hset("blacklistmw", "+17542476556", '{"reason": "Spam"}')

# REMOVE FROM BLACKLIST
# client.hdel("blacklistmw", "+56352280778")
# client.hdel("blacklistmw", "+17542476556")

# GET ENTRY
# entry = client.hget("blacklistmw", "+56352280778")
# entry = client.hget("blacklistmw", "+17542476556")

# if entry:
#     print(json.loads(entry))
# else:
#     print("Not found")