import hashlib
import hmac
import base64

secret = bytes('<webwidget-hmac-token>', 'utf-8')
message = bytes('<identifier>', 'utf-8')

hash = hmac.new(secret, message, hashlib.sha256)
hash.hexdigest()