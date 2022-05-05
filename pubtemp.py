# publisher.py
import redis
import random
import time, json

r = redis.Redis(host='localhost', port=6379, db=0)

temp = 0.0

while True:
	temp = random.uniform(10.0, 40.0)
	hum = random.uniform(10.0, 40.0)
	json_datos = json.dumps({"id":"domo","temp": temp, "hum": hum})
	print(json_datos)
	r.publish('canal-2', json_datos)
	time.sleep(1)
