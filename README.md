
# OSINT Crawler em Python

Este é um **crawler básico para investigação OSINT (Open Source Intelligence)** que realiza varreduras em sites para extrair e-mails e coletar informações WHOIS dos domínios. Ele executa um **crawl recursivo até dois níveis de profundidade**, limitado ao mesmo domínio, e salva os resultados em arquivos `.txt`.

## Funcionalidades

- Varredura recursiva de páginas dentro do mesmo domínio (até depth=2)
- Extração de e-mails presentes nas páginas HTML
- Consulta WHOIS dos domínios base
- Exportação dos resultados para arquivos:
  - `emails.txt`: e-mails únicos encontrados, com a URL correspondente
  - `results.txt`: informações WHOIS de cada domínio e URLs visitadas

## Requisitos

- Python 3.7 ou superior
- Bibliotecas:
  - `requests`
  - `beautifulsoup4`
  - `python-whois`

Você pode instalar os requisitos com:

```bash
pip install requests beautifulsoup4 python-whois
```

## Como usar

Execute o script diretamente pelo terminal:

```bash
python run.py https://exemplo.com https://outrodominio.com
```

### Exemplo:

```bash
python run.py https://policiamilitar.sp.gov.br
```

## Estrutura dos arquivos de saída

- `emails.txt`: lista de e-mails encontrados e a URL onde foram encontrados  
  ```
  contato@exemplo.com - https://exemplo.com/contato
  ```

- `results.txt`: para cada URL visitada, registra:
  - URL
  - Informações WHOIS (domínio, registrador, datas, servidores DNS)
  - Separador de linhas para facilitar leitura

## Outras informações

- O crawler respeita um atraso de 2 segundos entre requisições (`REQUEST_DELAY`)
- Só navega por links internos do domínio de origem
- Evita reprocessar URLs já visitadas

## Aviso

Este projeto é apenas para fins educacionais. O uso de crawlers deve sempre respeitar os termos de uso dos sites visitados, evitando sobrecarga de servidores ou uso indevido de dados.

## Licença

Código aberto para uso não comercial e educacional.
