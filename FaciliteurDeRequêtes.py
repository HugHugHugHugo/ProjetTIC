#!/usr/bin/python3

import subprocess
import sys
import time

while 1:
	r=input('Souhaitez vous récupérer une attestation [R] ou en vérifier une [V] ? ')
	if r=='R':
		print('\n')
		nm=input('NOM Prénom ? ')
		print('\n')
		crtf=input('Attestation de réussite à quoi? ')
		cmd1="curl -X POST -d 'identite="+nm+"' -d 'certitule="+crtf+"' \http://localhost:8080/creation"
		a=subprocess.Popen(cmd1,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		print('\n')
		sys.exit(0)
	if r=='V':
		print('\n')
		nm=input("Nom de l'attestation à vérifier: ")
		print('\n')
		cmd2="curl -v -F image=@"+nm+" http://localhost:8080/verification"
		b=subprocess.Popen(cmd2,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		(retour,ignorer)=b.communicate()
		time.sleep(3)
		print(retour.decode('utf-8'))
		print('\n')
		sys.exit(0)
	print('\n')
	print('Veuillez entrer une réponse valide, R ou V.\n')
