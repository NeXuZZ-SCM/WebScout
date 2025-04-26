import requests
import time
import argparse
import random
from pyfiglet import Figlet
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import sys

GREEN = "\033[1;32m"
BLUE = "\033[1;34m"
GREY = "\033[1;30m"
RESET = "\033[0m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"

COLORS = [GREEN, BLUE, GREY, YELLOW]

def print_banner():
    """Imprime un banner estilizado con el nombre NeXuZZ WebScout."""
    figlet = Figlet(font="cybermedium")
    print(random.choice(COLORS) + figlet.renderText('NeXuZZ WebScout') + RESET)

def validate_url(url):
    """Valida que la URL sea accesible antes de iniciar el escaneo."""
    try:
        response = requests.head(url, timeout=5)
        if response.status_code >= 400:
            print(RED + f"[!] La URL {url} no es accesible (Status: {response.status_code})" + RESET)
            sys.exit(1)
    except requests.RequestException as e:
        print(RED + f"[!] Error al conectar con {url}: {e}" + RESET)
        sys.exit(1)

def scan_directory(url, directory, timeout=5):
    """Escanea un directorio específico y maneja la respuesta."""
    try:
        full_url = urljoin(url, directory.strip())
        response = requests.get(full_url, timeout=timeout, allow_redirects=False)
        status = response.status_code
        if status == 200:
            print(GREEN + f"[+] Directorio encontrado: {full_url} (Status: {status})" + RESET)
        elif status == 403:
            print(YELLOW + f"[!] Acceso denegado: {full_url} (Status: {status})" + RESET)
        elif status == 301 or status == 302:
            print(BLUE + f"[*] Redirección encontrada: {full_url} (Status: {status})" + RESET)
        else:
            print(RED + f"[-] No existe: {full_url} (Status: {status})" + RESET)
    except requests.RequestException as e:
        print(GREY + f"[!] Error al intentar acceder a {full_url}: {e}" + RESET)

def main():
    parser = argparse.ArgumentParser(description="Herramienta para descubrir directorios en un sitio web")
    parser.add_argument("-d", "--domain", required=True, help="Dominio a escanear (ejemplo: http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Ruta al archivo de wordlist")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Número de hilos para escaneo paralelo (predeterminado: 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Tiempo de espera por solicitud en segundos (predeterminado: 5)")
    args = parser.parse_args()

    url = args.domain if args.domain.endswith('/') else args.domain + '/'
    
    print_banner()
    print(BLUE + f"[*] Objetivo: {url}" + RESET)
    print(BLUE + f"[*] Wordlist: {args.wordlist}" + RESET)
    print(BLUE + f"[*] Hilos: {args.threads}" + RESET)

    validate_url(url)

    try:
        with open(args.wordlist, 'r', encoding='utf-8') as file:
            directories = file.readlines()
    except FileNotFoundError:
        print(RED + f"[!] Error: No se encontró la wordlist en {args.wordlist}" + RESET)
        sys.exit(1)
    except UnicodeDecodeError:
        print(RED + "[!] Error: La wordlist no está en formato UTF-8" + RESET)
        sys.exit(1)

    print(BLUE + f"[*] Total de directorios a probar: {len(directories)}" + RESET)

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        executor.map(lambda d: scan_directory(url, d, args.timeout), directories)

    elapsed_time = time.time() - start_time
    print(YELLOW + f"\n[*] Escaneo completado en {elapsed_time:.2f} segundos" + RESET)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(RED + "\n[!] Escaneo interrumpido por el usuario" + RESET)
        sys.exit(0)
