#!/usr/bin/env python3
from pyfanuc import pyfanuc

conn=pyfanuc('192.168.0.61')
if conn.connect():
	print("Verbunden")
	print("Lese Achsen")
	for key,val in conn.readaxis(conn.ABS | conn.SKIP | conn.REL | conn.REF).items():
		print(key,val)

