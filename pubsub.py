import redis
import json
import asyncio

r = redis.Redis(host='localhost', port=6379, db=0)

p = r.pubsub()

p.subscribe("canal-2")

temperatura = 1
humedad = 1

async def subs(r, channels):
    redis = r
    sub = redis.pubsub()
    sub.subscribe(channels)
    while True:
        message = sub.get_message('data')
        if message:
            mensaje = json.loads(message.get('data'))
            print("Temperatura: ", mensaje['temp'])
            print("Humedad", mensaje['hum'])
            global temperatura, humedad
            temperatura = mensaje['temp']
            humedad = mensaje['hum']
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)


async def pub(r):
    while True:
        global temperatura, humedad
        temp = temperatura * 2
        hum = humedad * 2
        json_datos = json.dumps({"id":"domotica","temperatura": temp, "humedad": hum})
        print(json_datos)
        r.publish('canal-1', json_datos)
        #time.sleep(1)
        await asyncio.sleep(1.1)
        

#def main():
#    while True:
#        asyncio.run(subs(r, "canal-2"))
#        asyncio.run(pub(r))
#main()

loop = asyncio.get_event_loop()
asyncio.ensure_future(subs(r, "canal-2"))
asyncio.ensure_future(pub(r))
loop.run_forever()

