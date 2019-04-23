#!/usr/bin/python
# -*- coding: utf-8 -*-
# Motores de búsqueda:
# 1. Google : https://google.com/search?q=
# 2. Bing : https://www.bing.com/search?q=
# 3. Yahoo
# 4. Ask.com
# 5. AOL.com
# 6. Baidu
# 7. DuckDuckGo : https://duckduckgo.com/html/?q=
import requests
import re
from bs4 import BeautifulSoup

#user agent de ejemplo
USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


def fetch_results(search_term, search_engine, number_results = 50, language_code = 'en'):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    #url a la que se hara el request... en el primer {} va a ir el query
    ####### Para cada motor de busqueda se formatea su url para hacer el get
    if search_engine == 'Google': url = 'https://www.google.com/search?q={}&num={}'.format(escaped_search_term, number_results)
    elif search_engine == 'DuckDuckGo': url = 'https://www.duckduckgo.com/html/search?q={}'.format(escaped_search_term)
    elif search_engine == 'Bing': url = 'https://www.bing.com/search?q={}&count={}'.format(escaped_search_term, number_results)
    elif search_engine == 'Yahoo': url = 'https://search.yahoo.com/search?p={}&n={}'.format(escaped_search_term, number_results)

    response = requests.get(url, headers=USER_AGENT)
    response.raise_for_status()

    return search_term, response.text.encode('utf-8')#aun no resuelvo bien esto de la codificacion, pero con este hay salida

def findAO(search,op):
	"""
	Funcion que busca un operador binario y regresa su lado
	izquierdo y derecho

	search: cadena donde buscara el operador
	op: operador que sera buscado
	"""
	opAO_exist=re.search(op,search)
	if opAO_exist:
		return search[0:opAO_exist.start()].strip() , search[opAO_exist.start()+3:].strip()
	else:
		return "NO", "NO"



def buildQuery(search, browser):
	"""
	Funcion que se encarga de construir el query a traves de una
	busqueda y de acuerdo al buscador.

	search: entrada de la busqueda
	browser: buscador para el que se creara el query
	"""
	query=''
	res_AndL,res_AndR= findAO(search,'AND') #Revisa si hay AND's
	res_OrL, res_OrR= findAO(search,'OR') #Revisa si hay OR's
	if res_AndL!='NO': #Si hay AND se llama recursivamente buildQuery para el lado derecho y el izquierdo
		query+=op_and(buildQuery(res_AndL,browser),buildQuery(res_AndR,browser),browser)
	elif res_OrL!='NO':#Si hay OR se llama recursivamente buildQuery para el lado derecho y el izquierdo
		query+=op_or(buildQuery(res_OrL,browser),buildQuery(res_OrR,browser),browser)
	else: #Si no hay ni AND ni OR prosigue revisando operadores
		operacion=re.match(r'(.+):(.+) (.*)',search)
		if operacion:#si es un operador del tipo ':'
			if 'ip' in operacion.group(1):
				query+=ip(operacion.group(2).strip(),operacion.group(3),browser)
			elif 'filetype' in operacion.group(1):
				query+=filetype(operacion.group(2).strip(),operacion.group(3),browser)
				print query
			elif 'site' in operacion.group(1):
				query+=site(operacion.group(2).strip(),operacion.group(3),browser)
			elif 'mail' in operacion.group(1):
				query+=mail(operacion.group(2).strip(),operacion.group(3),browser)
		else:# si no es del tipo ':'
			operacion2=re.match(r'(.*)[-|+](.*)',search)
			if operacion2: #Si es operador include o exclude
				if '-' in search:
					query+=exclude(operacion2.group(2), buildQuery(operacion2.group(1),browser), browser)
				if '+' in search:
					query+=include(operacion2.group(2), buildQuery(operacion2.group(1),browser), browser)
				else:# Si entra pero no es ninguno sale error
					print('Existe un error de entrada')
			else:#Si no tiene ninguno de los operadores
				operacion3=re.match(r'"(.*)"',search)
				if operacion3:
					return '"'+operacion3.group(1)+'"'
				else:
					return re.sub(' ','+',search) #se manda una busqueda normal del tipo 'departamento+barato+cdmx'
	return query


def ip(ip,obj_search,browser):
	#q=ip%3A192.168.190.10+local&oq=ip%3A192.168.190.10+local
	query=''
	if search=='':
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query+='ip%3A'+ip+'&oq=ip%'+ip
	else:
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query+='ip%3A'+ip+'+'+obj_search
	return query

def filetype(tipo_archivo,obj_search,browser):
	#p=inurl%3A".pdf"+algo
	query=''
	if browser in ['Google', 'Bing']:	query += 'filetype%3A'+tipo_archivo+'+'+obj_search
	elif browser == 'DuckDuckGo':	query += obj_search+'+filetype%3A'+tipo_archivo
	elif browser == 'Yahoo': query+='inurl%3A".'+tipo_archivo+'"+'+obj_search

	return query

def site(site,obj_search,browser):
	#q=site%3Astackoverflow.com+problem&oq=site%3Astackoverflow.com+problem
	#q=site%3Astackoverflow.com&oq=site%3Astackoverflow.com
	query=''
	if search=='':
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query+='site%3A' + site+'&oq=site%3A'+site
	else:
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query+='site%3A' + site+'+'+obj_search
	return query

def mail(mail,obj_search,browser):
	#q=email%3Agmail.com+hi&oq=email%3Agmail.com+hi&
	query=''
	if obj_search=='':
		if browser in ['Google', 'DuckDuckGo', 'Bing']:   query+='email%3A'+mail+'&oq=email%3A'+mail
	else:
		if browser in ['Google', 'DuckDuckGo', 'Bing']:   query+='email%3A'+mail+'+'+obj_search
	return query

def exclude(palabra,obj_search,browser):
	#q=casa+-jardin&oq=casa+-jardin
	query=''
	if obj_search=='':
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query+='-'+ palabra
	else:
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query += obj_search+'+-'+ palabra
	return query

def include(palabra,obj_search,browser):
	#q=casa+-jardin&oq=casa+-jardin
	query=''
	if obj_search=='':
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query='%2B'+ palabra
	else:
		if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:   query += obj_search+'+%2B'+ palabra
	return query

def op_and(objL_search,objR_search,browser):
	#q=casa+AND+blanca+AND+jardin
	query=''
	if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:    query += objL_search+'+AND+'+ objR_search
	return query

def op_or(objL_search,objR_search,browser):
	#q=casa+AND+blanca+AND+jardin
	query=''
	if browser in ['Google', 'DuckDuckGo', 'Bing', 'Yahoo']:    query += objL_search+'+OR+'+ objR_search
	return query


#-------------------Para probar----------------
# redirige la salida a un archivo.html y sevisa la salida de la busqueda

#search = 'ip:192.168.201.45 algo'
#search = 'problem filetype:pdf'
#search = 'site:fciencias.unam.mx alumnos'
#search = 'something mail:gmail.com'
#search = 'Benito -Juarez'
#search = 'Benito +Juarez'
#search = 'filetype:pdf precio AND -comprar AND +jardin'  # checar
#search = 'lugar donde vivir en cdmx'
search = '"Romeo y Julieta"'


if __name__ == '__main__':
    ##### Se hace consulta por motor
    keyword_google, html_google = fetch_results(buildQuery(search, 'Google'), 'Google', 20)# 20 es el numero de resultados, se puede cambiar, en es el idioma
    keyword_duckDuckGo, html_duckDuckGo = fetch_results(buildQuery(search, 'DuckDuckGo'), 'DuckDuckGo')
    keyword_bing, html_bing = fetch_results(buildQuery(search, 'Bing'), 'Bing', 20)
    keyword_yahoo, html_yahoo = fetch_results(buildQuery(search, 'Yahoo'), 'Yahoo', 20)
    ### Salida de búsqueda en Google
    #print(buildQuery(search, 'Bing'))
    print(html_yahoo)
    ### Salida de búsqueda en DuckDuckGo
    #print(html_duckDuckGo)
    #print '+%2B'
