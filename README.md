# pyfanuc
focas fanuc protocol-analysis to python-source

The python-source is based on protocol analysis.
The problem is, that the Fanuc Focas Library does not have proper linux support.
The current target platform for protocol-analysis is an EDM-machine with a 160W control and a Robodrill 30i.

## GETTIME
### Request
Header
| Sync        | Version | Request | Request | Subpacket | 
|             |         |         | length  | count     |
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC1/PMC2 | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 45| 00 00 00 01 |00 00 00 00|00 00 00 00|00 00 00 00|00 00 00 00|
|        |           |           | TIME1/DATE0 |           |           |           |           |

### Response
Header
| Sync        | Version | Response| Response| Subpacket | 
|             |         |         | length  | count     |
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC1/PMC2 | Func      | fill   | Length | int16 | int16 | int16 | fill    |
|:------:|:---------:|:---------:|:------:|:------:|:-----:|:-----:|:-----:|:-------:|
|  00 1c |   00 01   |00 01 00 45| 6x00   | 00 0c  | e4 07 | 05 00 | 0e 00 | 6 x XX  |
|        |           |           |        |        | 2020  | 5     | 14    |         |

## GETDIAG 980-981 for first Axis
### Request
Header
| Sync        | Version | Request | Request | Subpacket | 
|             |         |         | length  | count     |
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 01  |  21 01  |  00 1e  |   00 01   |

Subpacket 1
| Length | CNC1/PMC2 | Func      | int32       | int32     | int32     | int32     | int32     |
|:------:|:---------:|:---------:|:-----------:|:---------:|:---------:|:---------:|:---------:|
|  00 1c |   00 01   |00 01 00 30| 00 00 03 d4 |00 00 03 d5|00 00 00 01|00 00 00 00|00 00 00 00|
|        |           |           | 980         | 981       | Axis 1    |           |           |

### Response
Header
| Sync        | Version |Response |Response | Subpacket | 
|             |         |         | length  | count     |
|:-----------:|:-------:|:-------:|:-------:|:---------:|
| A0 A0 A0 A0 |  00 02  |  21 02  |  00 62  |   00 01   |

Subpacket 1
| Length | CNC1/PMC2 | Func      | fill   | Length |
|:------:|:---------:|:---------:|:------:|:------:|
|  00 60 |   00 01   |00 01 00 30| 6 x 00 | 00 50  |
|        |           |           |        |        |

Diag-Value 980 [Length MAX_AXIS 8]
|   Name      | Axis  | Datatype  | int32       | 7 x int32       |
|:-----------:|:-----:|:---------:|:-----------:|:---------------:|
| 00 00 03 d4 | 00 01 | 00 02     | ff f6 de aa | 7 x 00 00 00 00 |

Diag-Value 981 [Length MAX_AXIS 8]
|   Name      | Axis  | Datatype  | int32       | 7 x int32       |
|:-----------:|:-----:|:---------:|:-----------:|:---------------:|
| 00 00 03 d5 | 00 01 | 00 02     | ff e2 62 6c | 7 x 00 00 00 00 |
