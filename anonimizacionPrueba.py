#!/usr/bin/python
# -*- coding: utf-8 -*-

from requests import Session  # session para realizar las peticiones mediante TOR  # pip install requests
from requests.exceptions import ConnectionError
from stem import Signal  # pip install stem
from stem.control import Controller
from random import choice
from time import sleep
from sys import exit,stderr
import argparse

# /etc/tor/torrc -> ControlPort 9051 ->
# NOTA: control requiere privilegios

def printError(msg, eexit = False):
    """Función que imprime mensaje de error y sale del programa
    Recibe: mensaje a mostrar y booleano que indica si se debe terminar la ejecución del programa"""
    stderr.write('Error:\t%s\n' % msg)
    if eexit:
        exit(1)

def addOptions():
    """
    Función para agregar las opciones al script (pruebas)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--params', action='store_true', dest='param', default=False, help='Resultados con parámetros GET.')
    # parser.add_argument('-m','--motor', dest='motor', default=None, help='Motor de búsqueda.')
    parser.add_argument('-t', '--tor', action='store_true', dest = 'tor', default = False, help = 'Las peticiones se hacen por medio de TOR.')
    parser.add_argument('-a', '--agente', action='store_true', dest = 'agente', default = False, help = 'Se cambia el agente de usuario.')

    opts = parser.parse_args()
    return opts

def checkOptions(options):
    """Función que verifica el estado de ciertas opciones para poder ejecutar el script"""
    #if options.motor is None:
    #    printError('Se debe indicar el motor de búsqueda.', True)
    pass

def buildURL(server,protocol = 'http'):
    """Función que da formato de la URL.
    Recibe: direccion(server)
    Devuelve: URL con formato.
    """
    url = '%s://%s' % (protocol,server)
    return url

def getInfoRequest(session, header):
    """
    Función que obtiene la IP desde la que se hace la petición y el agente de usuario.
    Recibe: objeto session (Session para hacer los request) y los header (para agente de usuario)
    Devuelve: en salida estándar muestra la IP actual y el agente de usuario
    """
    ip = session.get('http://httpbin.org/ip', headers = header)  # Se obtiene la ip desde la que se hace la petición
    ip = str(ip.text).replace('  "origin\":','').replace('{','').replace('}','').replace('\n','').replace(',','\"')
    ip = ip[:ip.find('\"',2)+1]
    agente = session.get('https://httpbin.org/user-agent', headers = header)  # Se obtiene el agente de usuario con el que se hace la petición
    agente = str(agente.text).replace('  \"user-agent\":','').replace('{','').replace('}','').replace('\n','')

    print 'La petición se realiza desde:%s' % (ip)
    print 'El agente de usuario es:%s' % (agente)

def changeIP():
    """Función para cambiar la dirección IP desde la que se hace la petición (se hacen desde Tor).
    Recibe: vacío. Devuelve: vacío (controller asigna la nueva dirección IP)
    """
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def makeRequest(motor, agente, tor):
    """Función que realiza las peticiones anónimas.
    Recibe: motor en donde realiza la búsqueda
    Si --tor es True se realiza la petición a través de TOR mediante los proxies y session()
    Si --agente es True se cambia el agente de usuario."""
    # User Agent list: https://udger.com/resources/ua-list
    session = Session()
    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',  # Chrome
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0',  # Firefox
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 OPR/32.0.1948.25',  # Opera
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',  # Safari
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 UBrowser/5.4.5426.1034 Safari/537.36',  # UC Browser
        'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mercury/3.4 Mobile/10A523 Safari/8536.25',  # Mercury
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3739.0 Safari/537.36 Edge/75.0.109.0'  # Microsoft Edge
    ]
    try:
        header = {'User-agent':choice(user_agent)}  # Valor que se agrega al diccionario para cambiar el agente
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'  # Proxy http y https para realizar la petición mediante TOR
        session.proxies['https'] = 'socks5h://localhost:9050'
        getInfoRequest(session, header)

    except ConnectionError:
        printError('Error en la conexion.',True)

if __name__ == '__main__':
    try:
        opts = addOptions()
        checkOptions(opts)
        # url = buildURL(server = opts.motor)
        for i in range(0,2):
            makeRequest('', opts.agente, opts.tor)
            if opts.tor:  # Para pruebas de cambio de IP con tor
                changeIP()
            sleep(5)  # Tor no permite asignar nuevas direcciones inmedaitamente

    except Exception as e:
        printError('Ocurrio un error inesperado')
        printError(e, True)