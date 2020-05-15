# pyfanuc
focas fanuc protocol-analysis to python-source

The python-source is based on protocol analysis.
The problem is, that the Fanuc Focas Library does not have proper linux support.
The current target platform for protocol-analysis is an EDM-machine with a 160W control and a Robodrill 30i.

## GETTIME                                                                                 
| Sync | Version | Request | Request | Subpacket | Subpacket 1 | CNC1/PMC2 | Func | int32 | int32 | int32 | int32 | int32 |
|:----:|:-------:|:-------:|:-------:|:---------:|:-----------:|:---------:|:----:|:-----:|:-----:|:-----:|:-----:|:-----:|
|      |         |         | length  | count      | length |   |   | TIME1/DATE0 | | | | |
|4xA0|00 01|21 01|00 1e|00 01|00 1c|00 01|00 01 00 45|00 00 00 01|00 00 00 00|00 00 00 00|00 00 00 00|00 00 00 00|

## GETDIAG 980-981 for first Axis
                                                                                   [   980   ]  [   981   ]  [  AXIS 1 ]
#A0 A0 A0 A0   00 01     21 01     00 1e      00 01      00 1c      00 01   00 01  00 30  00 00 03 d4  00 00 03 d5  00 00 00 01  00 00 00 00  00 00 00 00
