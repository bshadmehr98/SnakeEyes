import jwt
import datetime as dt

def get_access_token(user_id, user_role):
    return jwt.encode({"user_id": user_id, "user_role": user_role, "created_at": str(dt.datetime.now())}, "secret", algorithm="HS256")


def decode_access_token(token):
    return jwt.decode(token, "secret", algorithms=["HS256"])
