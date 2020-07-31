# pyfanuc
focas fanuc protocol-analysis to python-source

The python-source is based on protocol analysis.
The problem is, that the Fanuc Focas Library does not have proper linux support.
The current target platform for protocol-analysis is an EDM-machine with a 160 control and a Robodrill 30i.

"I need more generated protocols (wireshark) for another fanuc-machines."

## implemented
|function|description|
|:------|:---------|
| getsysinfo | read sysinfos |
| readparam | read parameter(s) |
| readdiag | read diagnostic-value(s) |
| readmacro | read macro-value(s) |
| readpmc | read pmc-variables |
| readexecprog	| execute linecode |
| readprognum | actual main/run program |
| settime | set date/time |
| listprog	| listprograms |
| getprog | program read test |
| readactfeed | actual feedrate |
| readaxis | actual axis-values |
| getdate | read date |
| gettime | read time |
| getdatetime | read date+time |

### control >= 30i
|function|description|
|:------|:---------|
| readdir_current | current directory |
| readdir_info	| directory-info |
| readdir | read directory (one block) |
| readdir_complete	| read complete directory |

### subfunctions
|function|description|
|:------|:---------|
| connect | connecting |
| disconnect | disconnecting  |
| _req_rdsingle | capsulate single packet request |
| _req_rdmulti |  capsulate single packets request |
| _req_rdsub | sub-packet-pack |
| encap | encapsulate packets |
| decap | decapsulate packets |
| _decode8 | decode 8 byte values |

## Protocol samples

### GETPMC VALUE D2204
#### Request
Header
| Sync        | Version | Request | Request length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1 (length=length+2)
| Length | CNC/PMC   | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 02   |00 01 80 01| 00 00 08 9c |00 00 08 9d|00 00 00 09|00 00 00 01|00 00 00 00|
|        | CNC=1/PMC=2 |           | 2204 | 2205 | Data Table | Type short |           |

Memory Typ
| Typ | | Description |
|:-----------:|:-------:|:-------:|
| 0 | G | uplink PMC to CNC |
| 1 | F | downlink PMC from CNC |
| 2 | Y | dplink PMC to Machine |
| 3 | X | downlink PMC from Machine |
| 4 | A | message |
| 5 | R | internal Relays |
| 6 | T | Timer |
| 7 | K | Keep relays |
| 8 | C | Counter |
| 9 | D | Data |

#### Response
Header
| Sync        | Version | Response| Response length| Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 14  |   00 01   |

Subpacket 1
| Length | CNC/PMC | Func      | fill   | Length payload | int16 |
|:------:|:---------:|:---------:|:------:|:------:|:-----:|
|  00 12 |   00 02   |00 01 80 01| 6 x 00 | 00 02 | 02 58 |
|        | CNC=1/PMC=2 |           |        | 2 | 600  |

### GETTIMEDATE Date 14.05.2020
#### Request
Header
| Sync        | Version | Request | Request length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1 (length=length+2)
| Length | CNC/PMC   | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 45| 00 00 00 00 |00 00 00 00|00 00 00 00|00 00 00 00|00 00 00 00|
|        | CNC=1/PMC=2 |           | DATE=0/TIME=1 |           |           |           |           |

#### Response
Header
| Sync        | Version | Response| Response length| Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC/PMC | Func      | fill   | Length payload | int16 | int16 | int16 | fill    |
|:------:|:---------:|:---------:|:------:|:------:|:-----:|:-----:|:-----:|:-------:|
|  00 1c |   00 01   |00 01 00 45| 6 x 00 | 00 0c  | e4 07 | 05 00 | 0e 00 | 6 x XX  |
|        | CNC=1/PMC=2 |           |        | 12     | 2020  | 5     | 14    |         |

### GETTIMEDATE Time 12:15:05
#### Request
Header
| Sync        | Version | Request | Request length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1 (length=length+2)
| Length | CNC/PMC   | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 45| 00 00 00 01 |00 00 00 00|00 00 00 00|00 00 00 00|00 00 00 00|
|        | CNC=1/PMC=2 |           | DATE=0/TIME=1 |           |           |           |           |

#### Response
Header
| Sync        | Version | Response| Response length| Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC/PMC | Func      | fill   | Length payload | fill    | int16 | int16 | int16 | 
|:------:|:---------:|:---------:|:------:|:------:|:-----:|:-----:|:-----:|:-------:|
|  00 1c |   00 01   |00 01 00 45| 6 x 00 | 00 0c  | 6 x XX  | 00 0c |  00 0f |  00 05 | 
|        | CNC=1/PMC=2 |           |        | 12     |         | 12  | 15     | 5   | 


### GETDIAG 980-981 for first Axis
#### Request
Header
| Sync        | Version | Request | Request length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC/PMC | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 30| 00 00 03 d4 |00 00 03 d5|00 00 00 01|00 00 00 00|00 00 00 00|
|        | CNC=1/PMC=2 |           | 980         | 981       | Axis 1    |           |           |

#### Response
Header
| Sync        | Version |Response |Response length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 62  |   00 01   |

Subpacket 1 (length=length+2)
| Length | CNC/PMC | Func      | fill   | Length payload |
|:------:|:---------:|:---------:|:------:|:------:|
|  00 60 |   00 01   |00 01 00 30| 6 x 00 | 00 50  |
|        | CNC=1/PMC=2 |           |        | 2x(4+2+2+MAX_AXISx4)=80 |

Diag-Value 980 [MAX_AXIS=8 Values]
|   Name      | Axis  | Datatype  | int32       | 7 x int32       |
|:-----------:|:-----:|:---------:|:-----------:|:---------------:|
| 00 00 03 d4 | 00 01 | 00 02     | ff f6 de aa | 7 x 00 00 00 00 |
| 980         |  1    |  2-word   |  ‭-598.358‬   |                 |  

Diag-Value 981 [MAX_AXIS=8 Values]
|   Name      | Axis  | Datatype  | int32       | 7 x int32       |
|:-----------:|:-----:|:---------:|:-----------:|:---------------:|
| 00 00 03 d5 | 00 01 | 00 02     | ff e2 62 6c | 7 x 00 00 00 00 |
| 981         |  1    |  2-word   | ‭-1.940.884  |                 |


## Programmtransfer

getprog(self,name) ist the test-implementation for programm-transfer.

programtransfer-stream connects with a0 a0 a0 a0 00 01 01 01 00 02 00 01

controltransfer-stream (params etc.) connects with a0 a0 a0 a0 00 01 01 01 00 02 00 02

Start Transfer
| Sync        | Version | Request | Request length | unknown | zeroterm. Prognames |
|:-----------:|:-------:|:-------:|:-------:|:---------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  15 01  |  02 04  |   00 00 00 01   | "O2200-O2200" 00 .. |


| Sync        | Version | Response| Response length| unknown | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  15 02  |  02 01  |   ..   |

# if not exist
Receive block
| Sync        | Version | Response| Response length|
|:-----------:|:-------:|:-------:|:-------:|
| A0 A0 A0 A0 |  00 02  |  16 04  |  00 00  |

# if exist
Receive block
| Sync        | Version | Response| Response length| Programtext | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  16 04  |  05 00  |   ..   |

Receive block
| Sync        | Version | Response| Response length| Programtext | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  16 04  |  05 00  |  ... "%" |

Transfer end
| Sync        | Version | Response| Response length|
|:-----------:|:-------:|:-------:|:-------:|
| A0 A0 A0 A0 |  00 02  |  17 01  |  00 00  |

Stop Transfer
| Sync        | Version | Request | Request length |
|:-----------:|:-------:|:-------:|:-------:|
| A0 A0 A0 A0 |  00 01  |  17 02  |  00 00  |

## sample on raspberry pi 2 only with python3 and without x86-emu/wine etc.

![Test Image](/images/test.png)

