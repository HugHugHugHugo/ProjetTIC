#!/usr/bin/python3

import subprocess
import time

x=subprocess.Popen('openssl ecparam -out ecc.key.pem -name prime256v1 -genkey', shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
time.sleep(1)
y=subprocess.Popen('openssl req -config <(printf "[req]\ndistinguished_name=dn\n[dn]\n[ext]\nbasicConstraints=CA:FALSE") -new -subj "/C=FR/L=Limoges/O=CRYPTIS/OU=SecuTIC/CN=localhost" -reqexts ext -sha256 -key ecc.key.pem -text -out ecc.csr.pem', shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
time.sleep(1)
z=subprocess.Popen('openssl x509 -req -days 3650 -CA ecc.ca.cert.pem -CAkey ecc.ca.key.pem -CAcreateserial -extfile <(printf "basicConstraints=critical,CA:FALSE") -in ecc.csr.pem -text -out ecc.serveur.pem', shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
time.sleep(1)
a=subprocess('cat ecc.serveur.key.pem ecc.serveur.pem > bundle_serveur.pem', shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
time.sleep(1)
b=subprocess.Popen('socat \ openssl-listen:9000,fork,cert=bundle_serveur.pem,cafile=ecc.ca.cert.pem,verify=0 \ tcp:127.0.0.1:8080', shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
time.sleep(1)
print('Serveur écran prêt\n')