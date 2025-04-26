# -*- coding: utf-8 -*-
import requests
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import sys
import codecs

GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
GREY = "\033[1;30m"
RESET = "\033[0m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"

COLORS = [GREEN, BLUE, GREY, YELLOW]

def print_banner():
    # Arte ASCII para "NeXuZZ WebScout"
    banner = """
 __          __  _     _____                 _   
 \ \        / / | |   / ____|               | |  
  \ \  /\  / /__| |__| (___   ___ ___  _   _| |_ 
   \ \/  \/ / _ \ '_ \\___ \ / __/ _ \| | | | __|
    \  /\  /  __/ |_) |___) | (_| (_) | |_| | |_ 
     \/  \/ \___|_.__/_____/ \___\___/ \__,_|\__|
"""
    print(random.choice(COLORS) + banner + RESET)

def validate_url(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code >= 400:
            print(RED + "[!] La URL %s no es accesible (Status: %s)" % (url, response.status_code) + RESET)
            sys.exit(1)
    except requests.RequestException as e:
        print(RED + "[!] Error al conectar con %s: %s" % (url, e) + RESET)
        sys.exit(1)

def scan_directory(url, directory, timeout=5):
    try:
        full_url = urljoin(url, directory.strip())
        response = requests.get(full_url, timeout=timeout, allow_redirects=False)
        status = response.status_code
        if status == 200:
            print(GREEN + "[+] Directorio encontrado: %s (Status: %s)" % (full_url, status) + RESET)
        elif status == 403:
            print(YELLOW + "[!] Acceso denegado: %s (Status: %s)" % (full_url, status) + RESET)
        elif status == 301 or status == 302:
            print(BLUE + "[*] Redirección encontrada: %s (Status: %s)" % (full_url, status) + RESET)
        else:
            print(RED + "[-] No existe: %s (Status: %s)" % (full_url, status) + RESET)
    except requests.RequestException as e:
        print(GREY + "[!] Error al intentar acceder a %s: %s" % (full_url, e) + RESET)

def main():
    parser = argparse.ArgumentParser(description="Herramienta para descubrir directorios en un sitio web")
    parser.add_argument("-d", "--domain", required=True, help="Dominio a escanear (ejemplo: http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Ruta al archivo de wordlist")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Número de hilos para escaneo paralelo (predeterminado: 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Tiempo de espera por solicitud en segundos (predeterminado: 5)")
    args = parser.parse_args()

    url = args.domain if args.domain.endswith('/') else args.domain + '/'
    
    print_banner()
    print(BLUE + "[*] Objetivo: %s" % url + RESET)
    print(BLUE + "[*] Wordlist: %s" % args.wordlist + RESET)
    print(BLUE + "[*] Hilos: %s" % args.threads + RESET)

    validate_url(url)

    try:
        with codecs.open(args.wordlist, 'r', encoding='utf-8') as file:
            directories = file.readlines()
            if directories:
                print(BLUE + "[*] Primeros 5 directorios de la wordlist: %s" % directories[:5] + RESET)
            else:
                print(YELLOW + "[!] La wordlist está vacía." + RESET)
                sys.exit(1)
    except IOError:
        print(RED + "[!] Error: No se encontró la wordlist en %s" % args.wordlist + RESET)
        sys.exit(1)
    except UnicodeDecodeError:
        print(RED + "[!] Error: La wordlist no está en formato UTF-8" + RESET)
        sys.exit(1)

    print(BLUE + "[*] Total de directorios a probar: %s" % len(directories) + RESET)

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        executor.map(lambda d: scan_directory(url, d, args.timeout), directories)

    elapsed_time = time.time() - start_time
    print(YELLOW + "\n[*] Escaneo completado en %.2f segundos" % elapsed_time + RESET)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(RED + "\n[!] Escaneo interrumpido por el usuario" + RESET)
        sys.exit(0)
