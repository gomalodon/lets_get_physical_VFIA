# Let's get physical: Exploiting Voltage Fault Injection Vulnerabilities in Intel SGX Enclaves 
by Giel Ooghe

This is the repository of all code used in this master's thesis.

The attack setup:
![alt text](diagramv2.png "The attack setup")

The most important files to perform an VFIA are: 

pc -> sgx_attack.py and dependencies

pico -> code.c

HB -> serial_server.py, sgx-script.sh, startup.sh and the crt_rsa/ folder. 

This repository contains the following files:
```
LETS_GET_PHYSICAL
├── README.md
├── constants.py                    -> constants on the attack pc
├── diagramv2.png               -> attack setup
├── util.py                         -> util functions
│
├── HB/                             -> code for the Hackboard
│   ├── Makefile
│   ├── multiplication.c            -> the multiplication program
│   ├── mult_iterations.c           -> an improved version of the mult program
│   └── serial_server.py            -> a serial server to receive commands on the hackboard 
│
├── evaluation/                     -> evaluation code such as plots and log analyzers
│   ├── dataframe.py                -> log analyzing code
│   ├── log_reader.py               -> log filter
│   ├── plots/                      -> plots from the thesis
│   │   ├── fault_bar.py
│   │   ├── faults_per_delay.py
│   │   ├── freq_voltage.py
│   │   ├── plot_3d.py
│   │   ├── plot_stats.py
│   │   └── sgx_fault.py
│   ├── sig_eval.py                 -> faulty sig analyzer
│   ├── transform_format.py         -> transforms log from an older format to a newer
│   └── unique_output.py            -> errors analyzer
│
├── pc/                             -> pc attack code
│   ├── multiplication_attack.py    -> mult attack (might not work anymore)
│   ├── new_mult_attack.py          -> an improved mult
│   ├── pico_serial.py              -> serial comm with pico
│   ├── picoboard.py                -> older comm for micropython
│   ├── sgx_attack.py               -> sgx attack
│   └── ssh.py                      -> older ssh comm with HB
│
├── pico/                           -> pico code
│   ├── CMakeLists.txt              
│   ├── README.md                   -> instructions
│   ├── code.c                      -> all C code
│   ├── functions.py                -> micropython code
│   └── nuke.c                      -> removes all files on pico
│
├── scripts/                        -> HB scripts
│   ├── sgx-script.sh               -> RSA/SGX script
│   └── startup.sh                  -> crontab script
│
├── sgx-test/                       -> RSA/SGX code
│   └── crt_rsa/
│       ├── App/
│       │   ├── App.cpp
│       │   └── App.h
│       ├── Enclave/
│       │   ├── Enclave.config.xml
│       │   ├── Enclave.cpp
│       │   ├── Enclave.edl
│       │   ├── Enclave.h
│       │   ├── Enclave.lds
│       │   └── Enclave_private.pem
│       └── Makefile
│
├── udp/                            -> older udp comm
│   ├── broadcast_log.py
│   ├── client.py
│   ├── hackboard.py
│   ├── test.py
│   └── two_way.py
│
└── voltage/                        -> voltage reading and writing code
    ├── convert_voltage.py
    ├── dyno_plot.py
    ├── plot.py
    ├── read_voltage.py
    └── write_voltage.py
```