#!/usr/bin/python3
from bottle import route, run, template, request, response
import subprocess
import qrcode
import time
import zbarlight
from PIL import Image
import sys
import os

def vers_8bit(c):
	chaine_binaire = bin(ord(c))[2:]
	return "0"*(8-len(chaine_binaire))+chaine_binaire

def modifier_pixel(pixel, bit):
	# on modifie que la composante rouge
	r_val = pixel[0]
	rep_binaire = bin(r_val)[2:]
	rep_bin_mod = rep_binaire[:-1] + bit
	r_val = int(rep_bin_mod, 2)
	return tuple([r_val] + list(pixel[1:]))

def recuperer_bit_pfaible(pixel):
	r_val = pixel[0]
	return bin(r_val)[-1]

def cacher(image,message):
	dimX,dimY = image.size
	im = image.load()
	message_binaire = ''.join([vers_8bit(c) for c in message])
	posx_pixel = 0
	posy_pixel = 0
	for bit in message_binaire:
		im[posx_pixel,posy_pixel] = modifier_pixel(im[posx_pixel,posy_pixel],bit)
		posx_pixel += 1
		if (posx_pixel == dimX):
			posx_pixel = 0
			posy_pixel += 1
		assert(posy_pixel < dimY)

def recuperer(image,taille):
	message = ""
	dimX,dimY = image.size
	im = image.load()
	posx_pixel = 0
	posy_pixel = 0
	for rang_car in range(0,taille):
		rep_binaire = ""
		for rang_bit in range(0,8):
			rep_binaire += recuperer_bit_pfaible(im[posx_pixel,posy_pixel])
			posx_pixel +=1
			if (posx_pixel == dimX):
				posx_pixel = 0
				posy_pixel += 1
		message += chr(int(rep_binaire, 2))
	return message

@route('/creation', method='POST')
def création_attestation():
	contenu_identité = request.forms.get('identite')
	contenu_intitulé_certification = request.forms.get('intitule_certif')
	#print('nom prénom :', contenu_identité, ' intitulé de la certification :',contenu_intitulé_certification)
	response.set_header('Content-type', 'image/png')
	texte_attestation=contenu_intitulé_certification+'|Attestation de réussite|délivrée à:||'+contenu_identité
	cmd1='curl -o texte.png "http://chart.apis.google.com/chart" --data-urlencode "chst=d_text_outline" --data-urlencode "chld=000000|56|h|FFFFFF|b|${'+texte_attestation+'}"'
	crea_ima_texte=subprocess.Popen(cmd1,shell=True,stdout=subprocess.PIPE)
	c_line1 = "echo "+contenu_identité+contenu_intitulé_certification+" > texte.txt"
	c = subprocess.Popen(c_line1, shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
	time.sleep(0.2)
	c_line2 = "openssl dgst -sha256 -sign ecc.ca.key.pem texte.txt | base64" 
	d = subprocess.Popen(c_line2,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	(data, ignorer) = cmd2.communicate()
	datASCII=DATA CONVERTIE EN ASCII OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
	nomqr='qrcode.png'
	qr=qrcode.make(data)
	qr.save(nomqr,scale=2)
	redim=subprocess.Popen('mogrify -resize 1000x600 texte.png',shell=True,stdout=subprocess.PIPE)
	time.sleep(0.2)
	fusion1=subprocess.Popen('composite -gravity center texte.png fond_attestation.png combinaison.png',shell=True,stdout=subprocess.PIPE)
	time.sleep(0.2)
	fusion2=subprocess.Popen('composite -geometry +1418+934 qrcode.png combinaison.png attestation.png',shell=True,stdout=subprocess.PIPE)
	mon_image = Image.open('attestation.png')
	cacher(mon_image, MESSAGE A CACHER: INFOS ET TIMESTAMPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP)
	mon_image.save('Attestation.png')
	supImTexte=subprocess.Popen('rm text.png',shell=True,stdout=subprocess.PIPE)
	supqr=subprocess.Popen('rm qrcode.png',shell=True,stdout=subprocess.PIPE)
	suptxt=subprocess.Popen('rm texte.txt',shell=True,stdout=subprocess.PIPE)
	descripteur_fichier = open('Attestation.png','rb')
	contenu_fichier = descripteur_fichier.read()
	descripteur_fichier.close()
	return contenu_fichier

@route('/verification', method='POST')
def vérification_attestation():
	contenu_image = request.files.get('image')
	contenu_image.save('attestation_a_verifier.png',overwrite=True)
	response.set_header('Content-type', 'text/plain')
	return "ok!"

run(host='0.0.0.0',port=8080,debug=True)