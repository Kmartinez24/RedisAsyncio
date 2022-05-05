import json
from h2o_wave import main, app, ui, data, Q, AsyncSite
import time
import random
import redis
import asyncio
from redis import StrictRedis, ConnectionError
from synth import FakePercent

val1 = 0
val2 = 0
update_stats = False
inicio_val = False
fin_val = False

a = [
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0]
]
b = a[:]
c = a[:]

#Aqui empieza el despapaye

def connect(host, port):
        return StrictRedis(host=host, port=port, db=0, socket_keepalive=True)

def subs(r, channels):
    redis = r
    sub = redis.pubsub()
    sub.subscribe(channels)
    while True:
        message = sub.get_message('data')
        if message:
            mensaje = json.loads(message.get('data'))
            print("data: "+str(data))
            print("Si se pudo")
            return mensaje
        time.sleep(0.01)

async def update_stats_page(q, page):
    r = connect('localhost', 6379)
    card = page['temperatura']
    while update_stats:
        data = await q.run(subs, r, "canal-1")
        if data["id"] == "domotica":
            val = data['temperatura']
        else:
            val = val    
        card.value = f'{val:.1f}'
        await page.save()
#Aqui termina


async def muestras(q: Q):
    global b, nivel_rows, brix_rows, cruda_rows
    r = connect('localhost', 6379) #Agregado

    f = FakePercent()
    t1 = q.page['tiempo']
    c1 = q.page['temperatura']
    c2 = q.page['humedad']
    c3 = q.page['luminosidad']
    i = 0
    while True:
        data = await q.run(subs, r, "canal-1")
        price, percent = f.next()
        t1.data.price = price
        t1.data.percent = percent
        t1.progress = percent
        q.user.temp = temp = data['temperatura']
        q.user.hum = hum = data['humedad']
        q.user.lum = lum = random.uniform(0.0, 40000.00)
        c1.data.qux = temp
        temp_rows.pop(0)
        temp_rows.append([i, temp])
        c1.plot_data = temp_rows
        c2.data.qux = hum
        hum_rows.pop(0)
        hum_rows.append([i, hum])
        c2.plot_data = hum_rows
        c3.data.qux = lum
        lum_rows.pop(0)
        lum_rows.append([i, lum])
        c3.plot_data = lum_rows
        i = i+1
        await q.page.save()
        await q.sleep(1)

async def show_domo(q: Q):
    global temp, hum, lum, i, temp_rows, hum_rows, lum_rows
    temp_rows = a
    hum_rows = b
    lum_rows = c
    temp = q.user.temp or 0.0
    hum = q.user.hum or 0.0
    lum = q.user.lum_rows or 0.0
    inicio_val = q.user.inicio_val or False
    fin_val = q.user.fin_val or False

    if q.args.iniciar:
        q.user.inicio_val = inicio_val = True
        q.page['titulo'].items[0].button.disabled = inicio_val
        await q.page.save()
        
    if q.args.finalizar: 
        q.user.inicio_val = inicio_val = False
        q.page['titulo'].items[0].button.disabled = inicio_val
        await q.page.save()   


    update_stats = q.user.update_stats or False
    if q.args.monitoreo:
        q.user.update_stats = update_stats = True
        if q.user.update_stats==True:
            q.user.update_stats = update_stats = False
            await q.run(muestras, q)
    
    if not q.client.initialized:
        q.client.initialized = True
        q.page['meta'] = ui.meta_card(box='', layouts=[
            ui.layout(
                breakpoint='xs',
                #width='768px',
                zones=[
                    ui.zone('title'),
                    #ui.zone('top', direction=ui.ZoneDirection.ROW, size='90px'),
                    #ui.zone('top1', direction=ui.ZoneDirection.ROW, size='90px'),
                    ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                        ui.zone('izq1', size='260px', zones=[
                            ui.zone('izq1_1'),
                        ]),
                        ui.zone('der1', zones=[
                            ui.zone('der1_1', direction=ui.ZoneDirection.ROW, zones=[
                                ui.zone('der1_11', direction=ui.ZoneDirection.ROW),
                                ui.zone('der1_12', direction=ui.ZoneDirection.ROW),
                                ui.zone('der1_13', direction=ui.ZoneDirection.ROW)
                            ]),
                            ui.zone('der1_2', zones=[
                                ui.zone('der1_21', direction=ui.ZoneDirection.ROW),
                            ]),
                            ui.zone('der1_3', zones=[
                                ui.zone('der1_31', direction=ui.ZoneDirection.ROW),
                            ]),
                        ]),
                        ui.zone('der2', size='260px', zones=[
                            ui.zone('der2_1'),
                        ]),                 
                    ]),
                ],
            ),
        ], theme='nature')

        await q.page.save()

        q.page['titulo'] = ui.section_card(
            box='title',
            title='DOMOTICA',
            subtitle='Simulación Domótica',
            items=[
                ui.button(
                    name='iniciar',
                    label='Iniciar',
                    #caption=' ',
                    #width= '100px',
                    disabled = False,
                    primary=True,
                ),
                ui.button(
                    name='finalizar',
                    label='Fin',
                    #caption=' Finalizar ',
                    #width= '100px',
                    disabled = False,
                    primary=True,
                ),
                ui.button(
                    name='monitoreo',
                    label='Monitoreo',
                    #caption=' Finalizar ',
                    #width= '100px',
                    disabled = False,
                    primary=True,
                ),
            ],
        )
        
        await q.page.save()

        q.page['tiempo'] = ui.wide_gauge_stat_card(
            box=ui.box('der1_11', order=1),
            title='Tiempo (min)',
            value='=${{intl price minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='={{intl percent style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            plot_color='$red',
            progress=0,
            data=dict(price=0, percent=0),
        )

        # q.page['tiempo'] = ui.small_stat_card(
        #     box=ui.box('der1_11', order=1),
        #     title='Tiempo (min)',
        #     #width= '134px',
        #     value=f'{mezcla1:.0f}',
        # )
        q.page['algo1'] = ui.small_stat_card(
            box=ui.box('der1_12', order=2),
            title='Algo 1',
            value=f'{val1:.0f}',
        )
        q.page['algo2'] = ui.small_stat_card(
            box=ui.box('der1_12', order=3),
            title='Algo 2',
            value=f'{val2:.0f}',
        )

        c1 = q.page['temperatura'] = ui.tall_series_stat_card(
            box=ui.box('der1_21', order=1),
            title='Temperatura (°C)',
            value='={{intl qux minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='={{intl quux style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            data=dict(qux=temp),
            plot_type='area',
            plot_category='foo',
            plot_value='qux',
            plot_color='$cyan',
            plot_data=data('foo qux', 15, rows=temp_rows),
            plot_zero_value=0,
            plot_curve='linear',
        )
        
        q.page['humedad'] = ui.tall_series_stat_card(
            box=ui.box('der1_21', order=2),
            title='Humedad Relativa (%)',
            value='={{intl qux minimum_fraction_digits=1 maximum_fraction_digits=2}}',
            aux_value='={{intl quux style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            data=dict(qux=hum),
            plot_type='area',
            plot_category='foo',
            plot_value='qux',
            plot_color='$yellow',
            plot_data=data('foo qux', 15, rows=hum_rows),
            plot_zero_value=0,
            plot_curve='linear',
        )

        q.page['luminosidad'] = ui.tall_series_stat_card(
            box=ui.box('der1_21', order=3),
            title='Luminosidad (lux) ',
            value='={{intl qux minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='={{intl quux style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            data=dict(qux=lum),
            plot_type='area',
            plot_category='foo',
            plot_value='qux',
            plot_color='$cyan',
            plot_data=data('foo qux', 15, rows=lum_rows),
            plot_zero_value=0,
            plot_curve='linear',
        )

        q.page['otro'] = ui.tall_series_stat_card(
            box=ui.box('der1_21', order=4),
            title='Otro (otro)',
            value='={{intl qux minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='={{intl quux style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            data=dict(qux=800),
            plot_type='area',
            plot_category='foo',
            plot_value='qux',
            plot_color='$cyan',
        	plot_data=data('foo qux', 3, rows=[[90, 0.9], [50, 0.5], [80, 0.8]]),
            plot_zero_value=0,
            plot_curve='linear',
        )

        
        await q.page.save()
        
    
     


@app('/domo', mode = 'multicast')
async def serve(q: Q):
    await show_domo(q)