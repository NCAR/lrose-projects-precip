#!/bin/csh

cd /data/spol/data.pgen/raw/cwb

while (1)
  rsync -av "tahope@172.16.197.98:cwbdata/" .
  sleep 10
end

