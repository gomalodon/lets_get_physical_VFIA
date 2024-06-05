#!/bin/bash
if [ $# -lt 3 ]; then
    >&2 echo "Delay, core and cycles arguments required"
    exit 1
fi
# echo "time delay: $1"
# echo "cpu: $2"
# echo "cycles: $3"

taskset -c $2 ./sgx-test/crt_rsa/app $1 $3