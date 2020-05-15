# pyfanuc
focas fanuc protocol-analysis to python-source

The python-source is based on protocol analysis.
The problem is, that the Fanuc Focas Library does not have proper linux support.
The current target platform for protocol-analysis is an EDM-machine with a 160W control and a Robodrill 30i.

## GETTIME
### Request
Header
| Sync        | Version | Request | Request length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1 (length=length+2)
| Length | CNC1/PMC2 | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 45| 00 00 00 01 |00 00 00 00|00 00 00 00|00 00 00 00|00 00 00 00|
|        | CNC=1 PMC=2 |           | TIME=1/DATE=0 |           |           |           |           |

### Response
Header
| Sync        | Version | Response| Response length| Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC/PMC | Func      | fill   | Length payload | int16 | int16 | int16 | fill    |
|:------:|:---------:|:---------:|:------:|:------:|:-----:|:-----:|:-----:|:-------:|
|  00 1c |   00 01   |00 01 00 45| 6 x 00 | 00 0c  | e4 07 | 05 00 | 0e 00 | 6 x XX  |
|        | CNC=1 PMC=2 |           |        | 12     | 2020  | 5     | 14    |         |

## GETDIAG 980-981 for first Axis
### Request
Header
| Sync        | Version | Request | Request length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC/PMC | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 30| 00 00 03 d4 |00 00 03 d5|00 00 00 01|00 00 00 00|00 00 00 00|
|        | CNC=1 PMC=2 |           | 980         | 981       | Axis 1    |           |           |

### Response
Header
| Sync        | Version |Response |Response length | Subpacket count | 
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 62  |   00 01   |

Subpacket 1 (length=length+2)
| Length | CNC1/PMC2 | Func      | fill   | Length payload |
|:------:|:---------:|:---------:|:------:|:------:|
|  00 60 |   00 01   |00 01 00 30| 6 x 00 | 00 50  |
|        |           |           |        | 2x(4+2+2+MAX_AXISx4)=80 |

Diag-Value 980 [Length MAX_AXIS 8]
|   Name      | Axis  | Datatype  | int32       | 7 x int32       |
|:-----------:|:-----:|:---------:|:-----------:|:---------------:|
| 00 00 03 d4 | 00 01 | 00 02     | ff f6 de aa | 7 x 00 00 00 00 |
| 980         |  1    |  2-word   |  ‭-598358‬    |                 |  

Diag-Value 981 [Length MAX_AXIS 8]
|   Name      | Axis  | Datatype  | int32       | 7 x int32       |
|:-----------:|:-----:|:---------:|:-----------:|:---------------:|
| 00 00 03 d5 | 00 01 | 00 02     | ff e2 62 6c | 7 x 00 00 00 00 |
| 981         |  1    |  2-word   | ‭-1940884‬    |                 |
