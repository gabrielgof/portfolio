#!/usr/bin/env python3
"""
Cyphernode Network Monitor
===========================
Script de monitoramento de infraestrutura de rede.
Verifica disponibilidade de hosts (ping), portas TCP e serviços HTTP.
Gera relatório no terminal ao final da execução.

Uso:
    python3 monitor.py              # usa config.example.json
    python3 monitor.py config.json # usa arquivo de config customizado

Dependências: Python 3.7+ (apenas stdlib — sem pip install)
"""

import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


# ============================================================
# FUNÇÕES DE MONITORAMENTO
# ============================================================

def ping_host(host: str, timeout: float = 2.0) -> dict:
    """
    Verifica se um host responde a ICMP ping.
    Retorna dict com: success (bool), rtts (list de floats em ms), error (str|None)
    """
    result = {
        "host": host,
        "success": False,
        "rtts": [],
        "error": None,
    }

    # Usa subprocess para fazer o ping — mais portátil que raw sockets
    # (ices não exigem privilégio de root em todos os sistemas)
    try:
        # -c 1: 1 pacote, -W: timeout em segundos (Linux)
        # Para macOS usar -t em vez de -W
        cmd = ["ping", "-c", "1", "-W", str(int(timeout)), host]
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 2,
            text=True,
        )

        if proc.returncode == 0:
            result["success"] = True
            # Tenta extrair o RTT da saída do ping
            for line in proc.stdout.splitlines():
                if "time=" in line:
                    try:
                        rtt_str = line.split("time=")[1].split()[0]
                        result["rtts"].append(float(rtt_str))
                    except (IndexError, ValueError):
                        pass
        else:
            result["error"] = proc.stderr.strip() or f"ping falhou (código {proc.returncode})"

    except subprocess.TimeoutExpired:
        result["error"] = f"ping expirado após {timeout}s"
    except FileNotFoundError:
        result["error"] = "comando 'ping' não encontrado no sistema"
    except Exception as e:
        result["error"] = str(e)

    return result


def check_tcp_port(host: str, port: int, timeout: float = 2.0) -> dict:
    """
    Testa se uma porta TCP está aberta no host.
    Retorna dict com: host, port, open (bool), error (str|None)
    """
    result = {
        "host": host,
        "port": port,
        "open": False,
        "error": None,
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        start = time.monotonic()
        conn_result = sock.connect_ex((host, port))
        elapsed = time.monotonic() - start

        if conn_result == 0:
            result["open"] = True
            result["rtt_ms"] = round(elapsed * 1000, 2)
        else:
            result["error"] = f"porta {port} fechada ou inacessível (código: {conn_result})"

    except socket.timeout:
        result["error"] = f"timeout ao conectar porta {port} ({timeout}s)"
    except OSError as e:
        result["error"] = f"erro de socket: {e}"
    except Exception as e:
        result["error"] = str(e)
    finally:
        sock.close()

    return result


def check_http(url: str, timeout: float = 5.0) -> dict:
    """
    Verifica um endpoint HTTP/HTTPS: status code, tempo de resposta, conteúdo.
    Retorna dict com: url, status_code (int|None), elapsed_ms (float|None),
                     final_url (str), error (str|None)
    """
    result = {
        "url": url,
        "status_code": None,
        "elapsed_ms": None,
        "final_url": None,
        "error": None,
    }

    try:
        start = time.monotonic()
        req = Request(url, headers={"User-Agent": "CyphernodeMonitor/1.0"})
        response = urlopen(req, timeout=timeout)
        elapsed = time.monotonic() - start

        result["status_code"] = response.getcode()
        result["elapsed_ms"] = round(elapsed * 1000, 2)
        result["final_url"] = response.geturl()

    except HTTPError as e:
        result["status_code"] = e.code
        result["error"] = f"HTTP {e.code}: {e.reason}"
    except URLError as e:
        result["error"] = f"URL error: {e.reason}"
    except socket.timeout:
        result["error"] = f"timeout ({timeout}s)"
    except Exception as e:
        result["error"] = str(e)

    return result


# ============================================================
# RELATÓRIO
# ============================================================

def print_header(title: str):
    """Imprime um cabeçalho estilizado no terminal."""
    width = 60
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
    print()


def print_section(title: str):
    """Imprime um subtítulo de seção."""
    print(f"\n--- {title} ---\n")


def print_ping_result(res: dict):
    """Imprime resultado de um ping de forma legível."""
    host = res["host"]
    if res["success"]:
        rtt_str = ", ".join(f"{r:.1f}ms" for r in res["rtts"]) if res["rtts"] else "N/A"
        print(f"  ✅ {host:<35} online  |  RTT: {rtt_str}")
    else:
        print(f"  ❌ {host:<35} offline |  {res['error']}")


def print_tcp_result(res: dict):
    """Imprime resultado de verificação de porta."""
    host_port = f"{res['host']}:{res['port']}"
    if res["open"]:
        rtt = f"{res.get('rtt_ms', 0):.1f}ms" if res.get('rtt_ms') else "N/A"
        print(f"  ✅ {host_port:<38} aberta  |  {rtt}")
    else:
        print(f"  ❌ {host_port:<38} fechada |  {res['error']}")


def print_http_result(res: dict):
    """Imprime resultado de verificação HTTP."""
    url = res["url"]
    if res["status_code"]:
        status = res["status_code"]
        # Código de cor texto
        if 200 <= status < 300:
            icon = "✅"
            status_label = "OK"
        elif 300 <= status < 400:
            icon = "🔀"
            status_label = "Redirect"
        elif 400 <= status < 500:
            icon = "⚠️ "
            status_label = "Client Error"
        else:
            icon = "🚨"
            status_label = "Server Error"

        elapsed = f"{res['elapsed_ms']:.1f}ms" if res.get("elapsed_ms") else "N/A"
        print(f"  {icon} {url:<45} {status} ({status_label}) | {elapsed}")
    else:
        print(f"  ❌ {url:<45} — {res['error']}")


def print_summary(results: dict):
    """Imprime resumo final com estatísticas."""
    print_header("RESUMO DA EXECUÇÃO")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Pings
    pings = results.get("pings", [])
    online = sum(1 for r in pings if r["success"])
    print(f"  Pings:   {online}/{len(pings)} hosts online")

    # Portas
    ports = results.get("tcp_ports", [])
    open_ports = sum(1 for r in ports if r["open"])
    print(f"  Portas:  {open_ports}/{len(ports)} portas abertas")

    # HTTP
    http = results.get("http_endpoints", [])
    ok_http = sum(1 for r in http if 200 <= (r.get("status_code") or 0) < 400)
    print(f"  HTTP:    {ok_http}/{len(http)} endpoints OK")

    print()
    print(f"  Executado em: {now}")
    print(f"  Total de verificações: {len(pings) + len(ports) + len(http)}")
    print()


# ============================================================
# CARREGAMENTO DE CONFIGURAÇÃO
# ============================================================

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.example.json")


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carrega arquivo de configuração JSON.
    Se path for None, tenta config.example.json no mesmo diretório.
    """
    if path is None:
        path = DEFAULT_CONFIG_PATH

    if not os.path.exists(path):
        print(f"Erro: arquivo de configuração não encontrado: {path}")
        print("Crie um arquivo baseado em config.example.json")
        sys.exit(1)

    with open(path, "r") as f:
        config = json.load(f)

    return config


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def run(config: dict):
    """
    Executa todas as verificações definidas na configuração.
    Retorna dict com todos os resultados organizados por categoria.
    """
    results = {
        "pings": [],
        "tcp_ports": [],
        "http_endpoints": [],
    }

    print_header("CYPHERNODE NETWORK MONITOR")
    print(f"  Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Config: {config.get('name', 'config.example.json')}")
    print()

    # --- Pings ---
    ping_hosts = config.get("pings", [])
    if ping_hosts:
        print_section("HOST MONITORING (PING)")
        for entry in ping_hosts:
            host = entry.get("host") or entry
            timeout = entry.get("timeout", 2.0) if isinstance(entry, dict) else 2.0
            res = ping_host(str(host), timeout)
            results["pings"].append(res)
            print_ping_result(res)

    # --- Portas TCP ---
    tcp_ports = config.get("tcp_ports", [])
    if tcp_ports:
        print_section("TCP PORT CHECK")
        for entry in tcp_ports:
            if isinstance(entry, dict):
                host = entry.get("host")
                port = entry.get("port")
                timeout = entry.get("timeout", 2.0)
            else:
                host, port = entry
                timeout = 2.0

            if host and port:
                res = check_tcp_port(str(host), int(port), timeout)
                results["tcp_ports"].append(res)
                print_tcp_result(res)

    # --- Endpoints HTTP ---
    http_endpoints = config.get("http_endpoints", [])
    if http_endpoints:
        print_section("HTTP ENDPOINT CHECK")
        for entry in http_endpoints:
            if isinstance(entry, dict):
                url = entry.get("url")
                timeout = entry.get("timeout", 5.0)
            else:
                url = entry
                timeout = 5.0

            if url:
                res = check_http(str(url), timeout)
                results["http_endpoints"].append(res)
                print_http_result(res)

    # --- Resumo ---
    print_summary(results)

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    """Ponto de entrada do script."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    config = load_config(config_path)
    results = run(config)

    # Exit code: 0 se tudo OK, 1 se algo falhou
    has_failures = (
        any(not r["success"] for r in results["pings"])
        or any(not r["open"] for r in results["tcp_ports"])
        or any(not (200 <= (r.get("status_code") or 0) < 400) for r in results["http_endpoints"])
    )

    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
