#!/bin/sh
main_core=0
bg_core=1

echo "=================================="
echo `date`

while [ "$(hostname -I)" = "" ]; do
  sleep 1
done

stdbuf -oL taskset --cpu-list $bg_core /bin/python3 /home/hackboard/udp/two_way.py &
stdbuf -oL taskset --cpu-list $bg_core /bin/python3 /home/hackboard/serial_server.py &
#taskset --cpu-list $bg_core /home/hackboard/HB/multiplication 0 &

# sleep 1
# stdbuf -oL taskset -c $main_core ./sgx-test/crt_rsa/app 0 0 &
