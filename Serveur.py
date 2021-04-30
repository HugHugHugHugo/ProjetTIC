#!/usr/bin/python3
from bottle import route, run, template, request, response
import subprocess
import qrcode
import time
import zbarlight
from PIL import Image
import sys
import os



#STEGANOGRAPHIE

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
        posx_pixel +=1
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

# renvoie le contenue d'un fichier en base64
def fichier_vers_Variable64(nom_fichier):
    cmd1 = subprocess.Popen("cat "+nom_fichier+" |base64",shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE)

    (resultat,ignorer)= cmd1.communicate()
    resultat=resultat.decode()[:-1]
    return resultat

def CreateTimestamp(nom_fichier): 
    # creer un fichier 'requête'
    c_line1 = "openssl ts -query -data "+nom_fichier+" -no_nonce -sha256 -out "+nom_fichier+".tsq"
    # reçoit une réponse 
    c_line2 = "curl -H 'Content-Type: application/timestamp-query' --data-binary '@"+nom_fichier+".tsq' https://freetsa.org/tsr > "+nom_fichier+".tsr"

    cmd1 = subprocess.Popen(c_line1, shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    time.sleep(1)
    cmd2 = subprocess.Popen(c_line2, shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	

# creer une fonction qui ajoute des caractères sur une chaine.
def ajoutCaractère(chaine, tailleFinal):
    nbreAjout = tailleFinal - len(chaine)
    for i in range(0,nbreAjout):
        chaine += '+' 
    print(len(chaine))
    return chaine



@route('/creation', method='POST')
def création_attestation():
	contenu_intitulé_certification = request.forms.get('certitule')
	contenu_identité = request.forms.get('identite')
	#print('nom prénom :', contenu_identité, ' intitulé de la certification :',contenu_intitulé_certification)
	response.set_header('Content-type', 'image/png')
	#creer une l'image texte.
	cmd1='texte_attestation="'+str(contenu_intitulé_certification)+'|Attestation de réussite|délivrée à:|'+str(contenu_identité)+'" && curl -o texte.png "http://chart.apis.google.com/chart" --data-urlencode "chst=d_text_outline" --data-urlencode "chld=000000|56|h|FFFFFF|b|${texte_attestation}"'
	#cmd1='curl -o texte.png "http://chart.apis.google.com/chart" --data-urlencode "chst=d_text_outline" --data-urlencode "chld=000000|56|h|FFFFFF|b|${texte_attestation="%s|Attestation de réussite|délivrée à:|%s"}"'%(contenu_intitulé_certification,contenu_identité)
	print(cmd1)
	crea_ima_texte=subprocess.run(cmd1,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	
	#creer fichier contenant les informations à signer. 
	c_line1 = "echo "+str(contenu_identité)+str(contenu_intitulé_certification)+" > texte.txt"
	c = subprocess.Popen(c_line1, shell=True, stdin=subprocess.PIPE,stdout= subprocess.PIPE)
	time.sleep(0.2)
	
	
	#signe le fichier texte.txt et converti le contenue en base64.
	c_line2 = "openssl dgst -sha256 -sign ecc.ca.kpriv.pem texte.txt | base64" 
	cmd2 = subprocess.Popen(c_line2,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	(data, ignorer) = cmd2.communicate()
	data = data.decode()[:-2]
	datASCII=[ord(c) for c in data]
	

	#Créé un Qrcode comprenant la signature.
	nomqr='qrcode.png'
	qr=qrcode.make(datASCII)
	qr.save(nomqr,scale=2)

	
	time.sleep(0.2)
	#combine les images (image texte, Qrcode, et fond_attestation)
	redim =subprocess.Popen('mogrify -resize 1000x600 texte.png',shell=True,stdout=subprocess.PIPE)
	time.sleep(0.2)
	redim2 =subprocess.Popen('mogrify -resize 220x220 qrcode.png',shell=True,stdout=subprocess.PIPE)
	time.sleep(0.2)
	fusion1 =subprocess.Popen('composite -gravity center texte.png fond_attestation.png combinaison.png',shell=True,stdin = subprocess.PIPE,stdout=subprocess.PIPE)
	time.sleep(2)

	fusion2=subprocess.Popen('composite -geometry +1418+934 qrcode.png combinaison.png attest.png',shell=True,stdin = subprocess.PIPE,stdout=subprocess.PIPE)
	time.sleep(2)
	
	#le message a cacher = (Bloc d'information + timeStamp) 
	bloc_info = str(contenu_identité)+str(contenu_intitulé_certification)
	CreateTimestamp('texte.txt')
	time.sleep(1)
	timestamp = 'texte.txt.tsr'
	timestamp = fichier_vers_Variable64(timestamp) #timestamp en base64
	Message = ajoutCaractère(bloc_info,64)+timestamp # taille  = 64 + 1828


	mon_image = Image.open('attest.png')
	cacher(mon_image,Message)
	mon_image.save('Attestation.png')
	mon_image.close()
	time.sleep(1)

	#suppression des fichiers inutiles 
	supFichierInu=subprocess.Popen('rm texte.png && rm qrcode.png && rm texte.txt && rm texte.txt.tsr && rm texte.txt.tsq && rm attest.png && rm combinaison.png',shell=True,stdout=subprocess.PIPE)

	descripteur_fichier = open('Attestation.png','rb')
	contenu_fichier = descripteur_fichier.read()
	descripteur_fichier.close()
	return contenu_fichier




@route('/verification', method='POST')
def vérification_attestation():
	contenu_image = request.files.get('image')
	contenu_image.save('attestation_a_verifier.png',overwrite=True)
	response.set_header('Content-type', 'text/plain')
	image=Image.open('attestation_a_verifier.png')
	MessStegano=recuperer(image, 1891) # récup message de la stégano
	image.close()
	nminti=''
	g=0
	while MessStegano[g] != '+':
		nminti += MessStegano[g] # à la fin de la boucle contient Nom et Intitulé concaténés
		g+=1
	cmd7='echo "'+nminti+'" > texte.txt'
	h=subprocess.Popen(cmd7,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	cmd5='convert attestation_a_verifier.png -crop 220x220+1418+934 qrcodeA.png'
	prqr=subprocess.Popen(cmd5,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	time.sleep(1)
	qrcrop = Image.open("qrcodeA.png")
	data2 =zbarlight.scan_codes(['qrcode'],qrcrop) # début traitement QRCODE
	qrcrop.close()
	data3=data2[0].decode()
	ldt=list(data3)
	ldt.pop(0)
	ldt.pop(len(ldt)-1)
	data4=''
	for x in range(0,len(ldt)):
		data4=data4+ldt[x]
	dataf=data4.split(',')
	for y in range(0,len(dataf)):
		dataf[y]=int(dataf[y])
	dataQRCODE=''
	for z in range(0,len(dataf)):
		dataQRCODE=dataQRCODE+chr(dataf[z]) # dataQRCODE = la signature en base 64 de texte.txt avec ecc.ca.key.pem
	dataQRCODE += '='
	c_line3 = "echo '"+dataQRCODE+"' | base64 -d > signature.sign.bin"
	cmd4 = subprocess.Popen(c_line3,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	time.sleep(0.2)
	cmd6='openssl dgst -sha256 -verify ecc.ca.kpub.pem -signature signature.sign.bin texte.txt'
	i=subprocess.Popen(cmd6,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	(retour,ignorer)=i.communicate()
	QRVERIF=retour.decode()
	Tsp=MessStegano[64:]+'='
	cmd8='echo "'+Tsp+'" | base64 -d > texte.txt.tsr'
	k=subprocess.Popen(cmd8,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	time.sleep(0.2)
	cmd9='openssl ts -verify -data texte.txt -in texte.txt.tsr -CAfile cacert.pem -untrusted tsa.crt'
	l=subprocess.Popen(cmd9,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	(revers,ignorer)=l.communicate()
	TIMESTAMPVERIF=revers.decode()
	if (QRVERIF == 'Verified OK\n') :
		if (TIMESTAMPVERIF == 'Verification: OK\n'):
			return "\nAttestation authentique\n"
		else :
			return "\nFausse attestation! Appel de la police des attestations en cours...\n"
	else :
		return "\nFausse attestation! Appel de la police des attestations en cours...\n"
	time.sleep(2)
	supFichInutiles=subprocess.Popen('rm qrcodeA.png && rm texte.txt && rm signature.sign.bin && rm attestation_a_verifier.png && rm texte.txt.tsr',shell=True,stdout=subprocess.PIPE)

run(host='0.0.0.0',port=8080,debug=True)