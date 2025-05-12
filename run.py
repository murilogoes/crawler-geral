#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Configurações do crawler
# USER_AGENT: Identifica o bot para os servidores web
# HEADERS: Cabeçalhos HTTP usados nas requisições
# MAX_DEPTH: Profundidade máxima da navegação recursiva
# REQUEST_DELAY: Tempo de espera entre requisições para não sobrecarregar servidores
# EMAILS_FILENAME: Nome do arquivo para salvar emails encontrados
# RESULTS_FILENAME: Nome do arquivo para salvar resultados gerais

# Funções utilitárias:

# get_domain(): 
# - Extrai e retorna o domínio base de uma URL
# - Exemplo: https://site.com/pagina -> site.com

# normalize_url():
# - Converte links relativos em URLs absolutas
# - Exemplo: /pagina -> https://site.com/pagina

# extract_emails():
# - Usa expressão regular para encontrar emails em texto
# - Retorna conjunto (set) com emails únicos encontrados

# fetch_whois():
# - Realiza consulta WHOIS para obter informações do domínio
# - Retorna dicionário com dados como registrador, datas, etc

"""
osint_crawler_txt.py

Crawler OSINT básico em Python:
- Crawl recursivo (mesmo domínio, depth=2)
- Extrai e-mails
- Consulta WHOIS
- Exporta resultados para TXT
"""

import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import whois
import re
import sys
import time

# ------------ Configurações ------------
USER_AGENT = "OSINT-Crawler/1.0 (+https://yourdomain.com)"
HEADERS = {"User-Agent": USER_AGENT}
MAX_DEPTH = 2
REQUEST_DELAY = 2  # segundos entre requisições
EMAILS_FILENAME = "emails.txt"
RESULTS_FILENAME = "results.txt"

# ------------ Funções utilitárias ------------
def get_domain(url):
    """Retorna o domínio base de uma URL."""
    parsed = urlparse(url)
    return parsed.netloc


def normalize_url(base, link):
    """Converte um link relativo em URL absoluta."""
    return urljoin(base, link)


def extract_emails(text):
    """Encontra todos os e‑mails em um texto."""
    return set(re.findall(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+", text))


def fetch_whois(domain):
    """Consulta WHOIS e retorna dicionário simples."""
    try:
        w = whois.whois(domain)
        return {
            "domain_name": w.domain_name,
            "registrar": w.registrar,
            "creation_date": w.creation_date,
            "expiration_date": w.expiration_date,
            "name_servers": w.name_servers
        }
    except Exception as e:
        return {"error": str(e)}

# ------------ Crawler principal ------------
def crawl(seed_urls, emails_filename, results_filename):
    visited = set()
    saved_emails = set() # Para garantir emails únicos no arquivo
    to_visit = [(url, 0) for url in seed_urls]
    # results = [] # Não precisamos mais da lista em memória

    # WHOIS de cada domínio inicial
    whois_cache = {}
    for url in seed_urls:
        dom = get_domain(url)
        if dom not in whois_cache:
            print(f"[WHOIS] consultando {dom} …")
            whois_cache[dom] = fetch_whois(dom)
            time.sleep(REQUEST_DELAY)

    # Abre os arquivos de saída uma vez
    with open(emails_filename, "a", encoding="utf-8") as emails_file, \
         open(results_filename, "a", encoding="utf-8") as results_file:

        while to_visit:
            url, depth = to_visit.pop(0)
            dom_base = get_domain(url)
            if url in visited or depth > MAX_DEPTH:
                continue

            print(f"[CRAWL] ({depth}) {url}")
            visited.add(url)

            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                resp.raise_for_status()
                body = resp.text
            except Exception as e:
                print(f"  ❌ Falha ao acessar {url}: {e}")
                continue

            # Extrai e‑mails e salva os únicos no arquivo de emails
            emails_found = extract_emails(body)
            for email in emails_found:
                if email not in saved_emails:
                    # emails_file.write(f"{email}\n")
                    emails_file.write(f"{email} - {url}\n") # Adiciona a URL na linha

                    saved_emails.add(email)
                    emails_file.flush() # Garante que o email seja escrito imediatamente

            # Salva informações da URL e WHOIS no arquivo de resultados
            results_file.write(f"URL: {url}\n")
            whois_info = whois_cache.get(dom_base, {})
            for key in ['domain_name', 'registrar', 'creation_date', 'expiration_date', 'name_servers', 'error']:
                 if key in whois_info:
                     results_file.write(f"{key.replace('_', ' ').title()}: {whois_info.get(key)}\n")
            results_file.write("-" * 40 + "\n")
            results_file.flush() # Garante que os dados sejam escritos imediatamente

            # Parse de links e agendamento
            soup = BeautifulSoup(body, "html.parser")
            for a in soup.find_all("a", href=True):
                link = normalize_url(url, a["href"])
                if get_domain(link) == dom_base and link not in visited:
                    to_visit.append((link, depth + 1))

            time.sleep(REQUEST_DELAY)

    print(f"\n[OK] Crawling concluído.")
    print(f" - E-mails únicos salvos em: {emails_filename}")
    print(f" - Resultados das páginas salvos em: {results_filename}")

# ------------ Export TXT (REMOVIDO) ------------
# def save_to_txt(data, filename="osint_results.txt"):
#    ... (função removida) ...

# ------------ Main ------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python osint_crawler_txt.py https://exemplo.com [https://outro.com ...]")
        sys.exit(1)

    seeds = sys.argv[1:]
    print(f"Iniciando crawler em: {seeds}...")
    print(f"Salvando e-mails em: {EMAILS_FILENAME}")
    print(f"Salvando resultados em: {RESULTS_FILENAME}")
    crawl(seeds, emails_filename=EMAILS_FILENAME, results_filename=RESULTS_FILENAME)
    # save_to_txt(data) # Chamada removida
