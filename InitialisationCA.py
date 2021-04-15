#!/usr/bin/python3

import subprocess
import time

a=subprocess.Popen('openssl ecparam -out ecc.ca.key.pem -name prime256v1 -genkey',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
time.sleep(1)
b=subprocess.Popen('openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:TRUE") -new -nodes -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=ACSECUTIC" -x509 -extensions ext -sha256 -key ecc.ca.key.pem -text -out ecc.ca.cert.pem',shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
time.sleep(1)
print('AC prête\n')