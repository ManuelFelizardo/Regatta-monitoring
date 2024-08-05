#!/bin/bash
kill -9 $(lsof -t -i:5000)
kill -9 $(lsof -t -i:10000)
echo "----------------------------------"
echo "|         DOCKER START           |"
echo "----------------------------------"

sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add –

sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update

sudo apt-get install docker-ce

echo "----------------------------------"
echo "|         DOCKER END             |"
echo "----------------------------------"


echo "----------------------------------"
echo "|         ELK STACK              |"
echo "----------------------------------"

cd ELK 
sudo docker-compose up &


echo "----------------------------------"
echo "|         SERVICES           |"
echo "----------------------------------"
cd ..
cd Services
./gs_initialize.sh &
sleep 5

echo "----------------------------------"
echo "|         OFFLINE MAP            |"
echo "----------------------------------"
cd ..
cd OfflineMap
docker run --rm -it -v $(pwd):/data -p 8080:80 klokantech/tileserver-gl 2017-07-03_europe_portugal.mbtiles

