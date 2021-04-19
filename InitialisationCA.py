#!/usr/bin/python3

import subprocess
import time

a=subprocess.Popen('openssl ecparam -out ecc.ca.kpriv.pem -name prime256v1 -genkey',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
time.sleep(1)
c=subprocess.Popen('openssl ec -in ecc.ca.kpriv.pem -pubout -out ecc.ca.kpub.pem',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
time.sleep(1)
print('AC prête\n')