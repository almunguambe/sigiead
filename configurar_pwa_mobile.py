import os
import re
import py_compile
import jinja2

print("=" * 80)
print("A CONFIGURAR SIGIEAD COMO APP INSTALÁVEL DE TELEMÓVEL (PWA)...")
print("=" * 80)

os.makedirs('static', exist_ok=True)
os.makedirs('static/img', exist_ok=True)

# =============================================================================
# 1. CRIAR STATIC/MANIFEST.JSON (CONFIGURAÇÃO DO APLICATIVO)
# =============================================================================
manifest_json = """{
  "name": "SIGIEAD - Assembleia de Deus",
  "short_name": "SIGIEAD",
  "description": "Sistema Integrado de Gestão da Igreja Evangélica Assembleia de Deus em Moçambique",
  "start_url": "/login",
  "display": "standalone",
  "background_color": "#090d16",
  "theme_color": "#1e1b4b",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/static/img/logo.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/static/img/logo.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}"""

with open('static/manifest.json', 'w', encoding='utf-8') as f:
    f.write(manifest_json)
print("✓ static/manifest.json criado!")

# =============================================================================
# 2. CRIAR STATIC/SW.JS (SERVICE WORKER PARA EXECUÇÃO COMO APP)
# =============================================================================
sw_js = """// Service Worker SIGIEAD
const CACHE_NAME = 'sigiead-v1';
const ASSETS_TO_CACHE = [
  '/login',
  '/static/img/logo.png',
  '/static/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Estratégia: Tenta rede primeiro para garantir dados atualizados; se offline usa cache
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
"""

with open('static/sw.js', 'w', encoding='utf-8') as f:
    f.write(sw_js)
print("✓ static/sw.js criado!")

# =============================================================================
# 3. ATUALIZAR APP.PY COM ROTAS DO SERVICE WORKER E REQUIREMENTS
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

rotas_pwa = """
# =============================================================================
# ROTAS DO APLICATIVO MOBILE (PWA)
# =============================================================================
@app.route('/manifest.json')
def pwa_manifest():
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def pwa_sw():
    return app.send_static_file('sw.js')
"""

if "/manifest.json" not in app_text:
    app_text = app_text.replace(
        "if __name__ == '__main__':",
        rotas_pwa + "\nif __name__ == '__main__':"
    )
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_text)
    print("✓ app.py: Rotas /manifest.json e /sw.js adicionadas!")

try:
    py_compile.compile('app.py', doraise=True)
    print("✓ app.py compilado sem erros!")
except Exception as e:
    print(f"Erro em app.py: {e}")

# =============================================================================
# 4. INJETAR TAGS DO APP NOS TEMPLATES (LOGIN, DASHBOARD, PORTAL_ALUNO)
# =============================================================================
tags_cabecalho_pwa = """    <!-- PWA MOBILE CONFIGURAÇÃO -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#1e1b4b">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="SIGIEAD">
    <link rel="apple-touch-icon" href="/static/img/logo.png">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').then(reg => {
                    console.log('SIGIEAD App registado com sucesso!');
                }).catch(err => {
                    console.log('Falha ao registar Service Worker PWA:', err);
                });
            });
        }
    </script>
</head>"""

for template_nome in ['login.html', 'dashboard.html', 'portal_aluno.html']:
    caminho = os.path.join('templates', template_nome)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            t_content = f.read()
        if 'rel="manifest"' not in t_content:
            t_content = t_content.replace('</head>', tags_cabecalho_pwa)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(t_content)
            print(f"✓ {template_nome} configurado para suportar instalação mobile!")

print("=" * 80)
print(">>> INSTALAÇÃO PWA CONCLUÍDA! O SISTEMA JÁ É UM APLICATIVO DE TELEMÓVEL! <<<")
print("=" * 80)