# Portfolio — Gabriel Gof

Portfólio web pessoal de Gabriel Gof — Desenvolvedor Web & Automação.

Construído com HTML, CSS e JavaScript puros (sem frameworks). Hospedado no Cloudflare Pages.

## URL

- **Cloudflare Pages (padrão):** https://gabrielgof-portfolio.pages.dev
- **Domínio customizado (em configuração):** https://gabrielgof.dv

## Tecnologias

- HTML5 semântico
- CSS customizado com design tokens via variáveis CSS (`:root`)
- JavaScript vanilla (Intersection Observer para animações)
- Fonte Geist via Google Fonts
- Deploy automático via Cloudflare Pages

## Estrutura

```
/
├── index.html       # Página única com tudo (HTML + CSS + JS inline)
├── .gitignore       # Arquivos ignorados pelo Git
└── README.md        # Este arquivo
```

## Como editar

1. Clonar o repo:
   ```
   git clone https://github.com/gabrielgof/portfolio.git
   cd portfolio
   ```

2. Abrir `index.html` no navegador para ver as mudanças:
   ```
   open index.html      # macOS
   xdg-open index.html  # Linux
   start index.html     # Windows
   ```

3. ou subir um server local para ver os efeitos:
   ```
   python3 -m http.server 8080
   # abrir http://localhost:8080
   ```

4. Editar o `index.html` e fazer commit + push. O Cloudflare Pages faz deploy automático.

## Como adicionar/editar projetos

No HTML, procure a seção `#projects`. Cada cartão de projeto segue este padrão:

```html
<article class="project-card fade-in">
  <div class="project-header">
    <div class="project-icon">
      <!-- ícone SVG -->
    </div>
    <div class="project-links">
      <a href="LINK_GITHUB" class="project-link">...</a>
      <a href="LINK_APP" class="project-link">...</a>
    </div>
  </div>
  <h3 class="project-title">Nome do Projeto</h3>
  <p class="project-description">Descrição: problema → solução → impacto.</p>
  <div class="project-tech">
    <span class="badge">Tech1</span>
    <span class="badge accent">Tech2</span>
  </div>
  <div class="project-footer">
    <span class="project-status live">● Em produção</span>
    <span style="font-size:12px;...">2024 — presente</span>
  </div>
</article>
```

Status disponíveis: `live` (em produção, verde), `in-progress` (em desenvolvimento, azul), `closed` (encerrado, cinza).

## Como conectar domínio customizado (gabrielgof.dv)

1. Registrar o domínio `gabrielgof.dv` (ex: na Registro.br, Namecheap, ou provedor de DNS das Ilhas Faroe)
2. No Cloudflare Pages, ir em **Settings → Domains** e adicionar `gabrielgof.dv`
3. Configurar os registros DNS apontando para os servidores do Cloudflare (instruções na interface)
4. O Cloudflare emite SSL automático

## Contato

- **E-mail:** gabrielgof65@gmail.com
- **WhatsApp:** +55 (11) 97437-4198
- **GitHub:** https://github.com/gabrielgof
- **LinkedIn:** em breve

---

*Construído do zero — HTML/CSS/JS puros, sem frameworks.*
