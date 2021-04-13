#!/usr/bin/python3

import sys, os, subprocess, qrcode, zbarlight
from PIL import Image


#commande de signature (SIGN, VERIFY): 
# 'openssl dgst -sha256 -sign private.key.pem fichier > signature.sign 
# 'openssl dgst -sha256 -verify public.key.pem -signature signature.sign fichier




#Création d'un Qrcode représentant la signature des éléments demandé 
# (nom + prénom + intitulé de certification)

prénom= 'prénom'
nom = 'nom'
intitule = 'SecuTIC'

#creer un fichier composer des données à signer. 
c_line1 = "echo "+prénom+nom+intitule+" > texte.txt"
cmd1 = subprocess.Popen(c_line1, shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)



# creer la signature en base 64.
c_line2 = "openssl dgst -sha256 -sign ecc.ca.key.pem texte.txt | base64" 
cmd2 = subprocess.Popen(c_line2,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
(data, ignorer) = cmd2.communicate()

data = data.decode()[:-2] # signature en base64


nom_fichier = "qrcode3.png"

qr = qrcode.make(data)
qr.save(nom_fichier,scale =2)

#QRcode fait !!


# Etape inverse:

#Récupération des données du Qrcode
image = Image.open("qrcode3.png")
data2 =zbarlight.scan_codes(['qrcode'],image)
data2 = data2[0].decode()

#ajout des données du Qrcode dans un fichier
data_cmd = "echo '"+data2+"' > signature.sign"
cmd3 =subprocess.Popen(data_cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)


'''
#isole la clé publique du certificat de l'AC : 
c_line = "openssl x509 -in certificat -pubkey -noout > ca.pub.key.pem "
'''

# decode la signature. 
c_line3 = "base64 -d signature.sign > signature.sign.bin"
cmd4 = subprocess.Popen(c_line3,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)

# permet de verifier la  signature.
c_line4 = "openssl dgst -sha256 -verify pub.key.pem -signature signature.sign.bin texte.txt"

cmd5 = subprocess.Popen(c_line4,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
(verif,ignorer) = cmd5.communicate()
verif = verif.decode()

print(verif)




