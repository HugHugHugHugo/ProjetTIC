#!/usr/bin/python3
from bottle import route, run, template, request, response
import subprocess
import qrcode
import time

@route('/creation', method='POST')
def création_attestation():
	contenu_identité = request.forms.get('identite')
	contenu_intitulé_certification = request.forms.get('intitule_certif')
	print('nom prénom :', contenu_identité, ' intitulé de la certification :',contenu_intitulé_certification)
	response.set_header('Content-type', 'image/png')
	blocInfos=contenu_identité+' '+contenu_intitulé_certification
	texte_attestation=contenu_intitulé_certification+'|Attestation de réussite|délivrée à:||'+contenu_identité
	cmd1=' curl -o texte.png "http://chart.apis.google.com/chart" --data-urlencode "chst=d_text_outline" --data-urlencode "chld=000000|56|h|FFFFFF|b|${'+texte_attestation+'}"'
	crea_ima_texte=subprocess.Popen(cmd1,shell=True,stdout=subprocess.PIPE)
	data=INFORMATION CONVERTIE EN ASCII
	nomqr='qrcode.png'
	qr=qrcode.make(data)
	qr.save(nomqr,scale=2)
	redim=subprocess.Popen('mogrify -resize 1000x600 texte.png',shell=True,stdout=subprocess.PIPE)
	time.sleep(0.2)
	fusion1=subprocess.Popen('composite -gravity center texte.png fond_attestation.png combinaison.png',shell=True,stdout=subprocess.PIPE)
	time.sleep(0.2)
	fusion2=subprocess.Popen('composite -geometry +1418+934 qrcode.png combinaison.png attestation.png',shell=True,stdout=subprocess.PIPE)
	supImTexte=subprocess.Popen('rm text.png',shell=True,stdout=subprocess.PIPE)
	supqr=subprocess.Popen('rm qrcode.png',shell=True,stdout=subprocess.PIPE)
	descripteur_fichier = open('attestation.png','rb')
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