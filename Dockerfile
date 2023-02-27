FROM ubuntu

RUN apt update &&  apt upgrade -y
RUN apt update &&  apt install python3  python3-pip nano  -y
RUN pip3 install pandas pyjipamlib sqlalchemy==1.4.35 pymysql influxdb 

RUN apt install -y ntpdate
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install tzdata
RUN ln -fs /usr/share/zoneinfo/America/Santiago /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
ENV TZ=America/Santiago

RUN apt upgrade -y
RUN apt-get clean all

WORKDIR /home
ADD app.py /home/
ADD insert_last24hrs.py /home/
CMD /usr/bin/python3 /home/app.py
