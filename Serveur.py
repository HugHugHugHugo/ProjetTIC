#!/usr/bin/python3
from bottle import route, run, template, request, response

@route('/creation', method='POST')
def création_attestation():
	contenu_identité = request.forms.get('identite')
	contenu_intitulé_certification = request.forms.get('intitule_certif')
	print('nom prénom :', contenu_identité, ' intitulé de la certification :',contenu_intitulé_certification)
	response.set_header('Content-type', 'text/plain')
	return "ok!"

@route('/verification', method='POST')
def vérification_attestation():
	contenu_image = request.files.get('image')
	contenu_image.save('attestation_a_verifier.png',overwrite=True)
	response.set_header('Content-type', 'text/plain')
	return "ok!"

@route('/fond')
def récupérer_fond():
	response.set_header('Content-type', 'image/png')
	descripteur_fichier = open('fond_attestation.png','rb')
	contenu_fichier = descripteur_fichier.read()
	descripteur_fichier.close()
	return contenu_fichier

run(host='0.0.0.0',port=8080,debug=True)