#!/bin/sh

echo "Run MBTiles file of Portugal on Doker "  
docker run --rm -it -v $(pwd):/data -p 8080:80 klokantech/tileserver-gl 2017-07-03_europe_portugal.mbtiles

echo "Done"

