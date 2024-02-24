from unicodedata import name
import redis

def get_redis():
    return redis.Redis(host='redis', port=6379, decode_responses=True)

#  хэндлеры с бизнесовой логикой

def fill_in_db(client, data):
    for el in data:
        client.hset(el.id, mapping={
            'name': el.name,
            'middlename': el.middlename,
            "surname": el.surname,
            "groupId": el.groupId,
        })
