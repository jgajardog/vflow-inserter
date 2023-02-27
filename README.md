# Graficas Internacionales

## Disclaimer
Netflow funciona en base a sampling, para que las graficas generen un resultado estimado lo mas cercano al trafico real 
es necesario que todos los elementos de red estén configurados a 1 de cada 1500 paquetes.


## Inserter
### Code
[[GitHub]](https://github.com/jgajardog/vflow-inserter.git)
### Image
[[DockerHub]](https://hub.docker.com/r/jgajardog/vflow-inserter)
```sh
docker pull jgajardog/vflow-inserter
```
### run
```sh
docker run -d --restart always --name inserter -h inserter \
-e TZ='America/Santiago' \
-e ciclosAtras=6 \
-e group=300 \
-e sampling=1500 \
-e serverMysql='ip server mysql' \
-e userMysql='username mysql' \
-e passMysql='pass mysql' \
-e dbMysql='database' \
-e serverInflux='ip server influx' \
-e dbInflux='database influx' \
-e portInflux=PortNumber \
-e measurement='measurement' \
-e tabla='tabla fuente mysql' \
jgajardog/vflow-inserter:0.0.1 
```
### re-insert last 24 hrs
```sh
/usr/bin/docker exec inserter bash -c '/usr/bin/python3 /home/insert_last24hrs.py'
```
