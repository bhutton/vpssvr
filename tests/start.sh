#!/bin/sh
/sbin/ifconfig tap204 create

/Users/ben/repos/vpssvr/tests/bhyveload.sh -m 512 -d /Users/ben/repos/vpssvr/tests//254 878

/Users/ben/repos/vpssvr/tests/bhyve.sh -A -H -P -s 0:0,hostbridge -s 1:0,lpc  -s 3:0,virtio-net,tap204  -s 3:0,virtio-blk,/Users/ben/repos/vpssvr/tests//254 -l com1,/dev/nmdm204A -c 4 -m 512 878 &

/sbin/ifconfig bridge0 addm tap204

/Users/ben/repos/vpssvr/tests/shellinabox.sh
