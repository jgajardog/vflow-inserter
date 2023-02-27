import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pyjipamlib import utils as j
import pandas as pd
import numpy as np
from influxdb import InfluxDBClient
import time

### Init
log = j.out()
log.print('Iniciando...')

###
ciclosAtras=int(os.environ['ciclosAtras'])

#
group=int(os.environ['group'])
sampling=int(os.environ['sampling'])

serverMysql=os.environ['serverMysql']
userMysql=os.environ['userMysql']
passMysql=os.environ['passMysql']
dbMysql=os.environ['dbMysql']

serverInflux=os.environ['serverInflux']
dbInflux=os.environ['dbInflux']
portInflux=int(os.environ['portInflux'])
measurement=os.environ['measurement']

#tabla='new_ims' #para pruebas
#tabla='to_export'  #productiva
tabla=os.environ['tabla']

multiplicar=sampling/group   # en script anterior ya va *8


###

my=j.mysql(serverMysql,userMysql,passMysql,dbMysql)

def ejecutar(muestra):
    log.print(f'muestra: {muestra}')
    q=f'select FROM_UNIXTIME((truncate(unix_timestamp(NOW())/{group},0)*{group})-({group}*{muestra})) as timestamp'
    hora=my.query(q)['data'].iloc[0].timestamp.tz_localize(tz=os.environ['TZ'])


    q='select distinct(customer) from ims.to_export'
    customers=my.query(q)['data']

    q=f'''
       select FROM_UNIXTIME((truncate(unix_timestamp(NOW())/{group},0)*{group})-({group}*{muestra})) as timestamp,
       customer,sum(in_bits) in_bits,direction
       from ims.{tabla}
       where timestamp >= FROM_UNIXTIME((truncate(unix_timestamp(NOW())/{group},0)*{group})-({group}*{muestra}))
       AND timestamp<FROM_UNIXTIME((truncate(unix_timestamp(NOW())/{group},0)*{group})-({group}*({muestra}-1)))
       group by customer,direction
    '''

    df=my.query(q)['data']
    df=pd.pivot_table(df, values='in_bits', index=['timestamp', 'customer'],columns=['direction'], aggfunc=np.sum).reset_index()
    data=customers.merge(df,how='left', left_on='customer', right_on='customer')
    data=data.fillna(0)
    data['timestamp']=hora
    data.rename(columns={0:'upstream',1:'downstream'},inplace=True)
    data['upstream']=data['upstream']*multiplicar
    data['downstream']=data['downstream']*multiplicar
    data['upstream']=data['upstream'].astype('int')
    data['downstream']=data['downstream'].astype('int')
    data['timestamp'] = pd.to_datetime(data['timestamp'],utc=True)
    data['timestamp']=data['timestamp'].apply(lambda x: pd.Timestamp(x).value)
    print(f'data.shape:{data.shape}')
    client = InfluxDBClient(host=serverInflux, port=portInflux)
    client.switch_database(dbInflux)

    for index, r in data.iterrows():
        timestamp = r.timestamp
        cliente = r.customer
        down = r.downstream
        up = r.upstream
        json_body = [
            {
                    "measurement": measurement,
                    "tags": {
                       "Cliente": cliente,
                            },
                    "time": timestamp,
                    "fields": {
                            "Down": down,
                            "Up": up
                              }
            }
        ]
        #print(json_body)
        client.write_points(json_body)


every=group
continuar=True
while(continuar):
    threaded_start = time.time()
    for x in range(ciclosAtras,-1,-1):
        try:
            ejecutar(x)
        except Exception as e:
            print(e)

    tiempo=time.time() - threaded_start
    if(tiempo<(every/2)):
        dormir=(every/2)-tiempo
        log.print(f'tiempo:{tiempo}; dormir:{dormir}')
        time.sleep(dormir)
