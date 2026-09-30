# Cyphernode Network Monitor

Script de monitoramento de infraestrutura de rede — parte do portfólio de Gabriel Gof.

Verifica disponibilidade de hosts (ICMP ping), portas TCP e endpoints HTTP. Gera relatório no terminal ao final da execução.

## Por que este projeto existe

Como suporte técnico e infraestrutura, saber se os serviços estão online é essencial. Este script automatiza essa verificação — útil para:
- Monitorar servidores do cliente antes de visitas técnicas
- Validar que serviços críticos (HTTP, DNS, SSH) estão respondendo
- Ter uma ferramenta leve e portátil sem dependências externas

## Tecnologias

| Recurso | Detalhe |
|---|---|
| Linguagem | Python 3.7+ |
| Dependências | Nenhuma — usa apenas stdlib (socket, subprocess, urllib, json, datetime) |
| Tipos | Type hints com `typing.Optional`, `Dict`, `Any` |
| Saída | Terminal texto com relatório formatado |

## Instalação

Não precisa de instalação. Basta ter Python 3.7+:

```bash
# Clonar o projeto
git clone https://github.com/gabrielgof/portfolio.git
cd portfolio/cyphernode-network-monitor

# Ou copiar os arquivos para qualquer diretório
```

## Uso

```bash
# Usa o config.example.json por padrão
python3 monitor.py

# Usa um arquivo de configuração customizado
python3 monitor.py meu-config.json
```

## Saída de exemplo

```
============================================================
    CYPHERNODE NETWORK MONITOR
============================================================

  Início: 2026-09-30 13:23:19
  Config: config.example.json

--- HOST MONITORING (PING) ---

  ✅ 8.8.8.8                             online  |  RTT: 5.2ms
  ✅ 1.1.1.1                             online  |  RTT: 4.8ms
  ✅ cyphernode.com.br                   online  |  RTT: 12.1ms

--- TCP PORT CHECK ---

  ✅ 8.8.8.8:53                          aberta  |  1.2ms
  ✅ cyphernode.com.br:80                aberta  |  18.4ms
  ✅ cyphernode.com.br:443               aberta  |  20.1ms

--- HTTP ENDPOINT CHECK ---

  ✅ https://cyphernode.com.br           200 (OK)         |  223.5ms
  ✅ https://httpbin.org/status/200      200 (OK)         |  145.2ms

============================================================
  RESUMO DA EXECUÇÃO
============================================================

  Pings:   3/3 hosts online
  Portas:  3/3 portas abertas
  HTTP:    2/2 endpoints OK

  Executado em: 2026-09-30 13:23:21
  Total de verificações: 8
```

## Saída de saída com falhas

```
❌ 8.8.4.4                             offline |  ping falhou (código 1)
❌ google.com:12345                     fechada |  porta 12345 fechada ou inacessível (código: 10060)
❌ https://httpbin.org/status/500       500 (Server Error) |  ...
```

## Arquivo de configuração

Edite `config.example.json` para adicionar/remover hosts, portas e endpoints:

```json
{
  "name": "meu-ambiente",

  "pings": [
    {"host": "8.8.8.8", "timeout": 2.0},
    {"host": "meu-servidor.local", "timeout": 3.0}
  ],

  "tcp_ports": [
    {"host": "meu-servidor.local", "port": 22, "timeout": 2.0},
    {"host": "meu-servidor.local", "port": 3306, "timeout": 3.0}
  ],

  "http_endpoints": [
    {"url": "https://meusite.com.br", "timeout": 5.0}
  ]
}
```

## Código e estrutura

```
cyphernode-network-monitor/
├── monitor.py            # Script principal (toda a lógica)
├── config.example.json   # Configuração de exemplo
└── README.md             # Esta documentação
```

### Funções principais

| Função | O que faz |
|---|---|
| `ping_host(host, timeout)` | Faz ICMP ping, extrai RTT, retorna sucesso/fail |
| `check_tcp_port(host, port, timeout)` | Testa conexão TCP, mede tempo de resposta |
| `check_http(url, timeout)` | Faz requisição HTTP, pega status code e elapsed time |
| `print_*_result()` | Formata e imprime cada tipo de resultado |
| `print_summary(results)` | Estatísticas finais (online/fail counts) |
| `run(config)` | Orquestra todas as verificações e imprime relatório |
| `main()` | Ponto de entrada, lida com argumentos e exit code |

## Exit code

- `0` — todas as verificações passaram
- `1` — pelo menos uma verificação falhou (útil para integração com scripts/alertas)

## Autor

**Gabriel Gof** — github.com/gabrielgof | gabrielgof65@gmail.com | +55 (11) 97437-4198
