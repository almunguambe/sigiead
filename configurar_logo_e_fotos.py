import os
import py_compile
import re
import jinja2

print("=" * 80)
print("A CONFIGURAR LOGÓTIPO OFICIAL STATIC E CAPTURA DE FOTOGRAFIAS LEVES...")
print("=" * 80)

os.makedirs('static/img', exist_ok=True)
os.makedirs('templates', exist_ok=True)
env = jinja2.Environment()

# =============================================================================
# 1. ATUALIZAR TEMPLATES/LOGO_AD.HTML PARA CARREGAR DE STATIC/IMG/LOGO.PNG
# =============================================================================
logo_template = """<img src="{{ url_for('static', filename='img/logo.png') }}" 
     alt="Igreja Evangélica Assembleia de Deus" 
     class="w-full h-full object-contain max-h-[160px] drop-shadow-md select-none pointer-events-none"
     onerror="this.onerror=null; this.src='https://placehold.co/180x180/0044cc/ffffff?text=AD+MZ';">"""

with open('templates/logo_ad.html', 'w', encoding='utf-8') as f:
    f.write(logo_template)
print("✓ templates/logo_ad.html: Configurado para carregar de static/img/logo.png!")

# =============================================================================
# 2. ATUALIZAR APP.PY PARA ASSEGURAR A COLUNA 'foto' EM MEMBROS
# =============================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_text = f.read()

# Adicionar a coluna foto na inicialização se não existir
if "('foto', 'TEXT')" not in app_text:
    app_text = app_text.replace(
        "('genero', 'TEXT DEFAULT \"Masculino\"'), ('criado_em', 'TEXT')",
        "('genero', 'TEXT DEFAULT \"Masculino\"'), ('foto', 'TEXT'), ('criado_em', 'TEXT')"
    )

# Adicionar captura da foto no método membros_gravar
if "foto = fd.get('foto_base64'" not in app_text:
    antigo_membros_gravar = """@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    sql = \"\"\"INSERT INTO membros 
              (congregacao_id, nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, genero, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\"\"\"
    params = (
        cid, fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(), fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Célula Betel').strip(), fd.get('ano_conversao', '').strip(),
        fd.get('data_batismo', '').strip(), local, local, genero, datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    executar_comando(sql, params)
    return redirect('/?aba=membros')"""

    novo_membros_gravar = """@app.route('/membros/novo', methods=['POST'])
def membros_gravar():
    cid = session.get('congregacao_id', 1)
    fd = request.form
    local = (fd.get('local_residencia') or fd.get('bairro') or '').strip()
    genero = fd.get('genero', 'Masculino').strip()
    foto = fd.get('foto_base64', '').strip()
    sql = \"\"\"INSERT INTO membros 
              (congregacao_id, nome, contacto, bi, cargo, departamento, estado_civil, zona, celula, ano_conversao, data_batismo, local_residencia, bairro, genero, foto, criado_em)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\"\"\"
    params = (
        cid, fd.get('nome', '').strip(), fd.get('contacto', '').strip(), fd.get('bi', '').strip(),
        fd.get('cargo', 'Membro em Comunhão').strip(), fd.get('departamento', 'Geral').strip(),
        fd.get('estado_civil', 'Solteiro(a)').strip(), fd.get('zona', 'Zona 1 - Central').strip(),
        fd.get('celula', 'Célula Betel').strip(), fd.get('ano_conversao', '').strip(),
        fd.get('data_batismo', '').strip(), local, local, genero, foto, datetime.now().strftime('%Y-%m-%d %H:%M')
    )
    executar_comando(sql, params)
    return redirect('/?aba=membros')"""

    if antigo_membros_gravar in app_text:
        app_text = app_text.replace(antigo_membros_gravar, novo_membros_gravar)
    else:
        # Substituição flexível se houver pequenas variações de whitespace
        app_text = re.sub(
            r"@app\.route\('/membros/novo'[\s\S]*?return redirect\('/[?]aba=membros'\)",
            novo_membros_gravar,
            app_text
        )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_text)
print("✓ app.py: Suporte à gravação de fotografia do membro adicionado!")

# =============================================================================
# 3. ATUALIZAR TEMPLATES/DASHBOARD.HTML COM COMPRESSOR E CÂMARA NO REGISTO
# =============================================================================
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

campo_foto_formulario = """                    <!-- FOTOGRAFIA: FICHEIRO OU CÂMARA EM TEMPO REAL (COMPRIMIDA) -->
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <label class="block font-bold text-slate-700 text-[11px] uppercase">Fotografia Tipo Passe (Leve / ~40KB)</label>
                        <input type="hidden" id="foto_base64" name="foto_base64">
                        
                        <div class="flex items-center gap-3">
                            <div id="preview_box" class="w-16 h-20 bg-slate-200 border-2 border-dashed border-slate-300 rounded-lg flex items-center justify-center text-slate-400 overflow-hidden shrink-0">
                                <span id="preview_placeholder" class="text-xs font-bold">Sem Foto</span>
                                <img id="preview_img" class="hidden w-full h-full object-cover">
                            </div>
                            <div class="space-y-1.5 flex-1">
                                <label class="block px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-center cursor-pointer font-bold text-[10px] shadow">
                                    📁 Carregar Imagem
                                    <input type="file" accept="image/*" class="hidden" onchange="processarFicheiroFoto(this)">
                                </label>
                                <button type="button" onclick="ativarCamera()" class="w-full px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-center font-bold text-[10px] shadow">
                                    📷 Tirar Foto c/ Câmara
                                </button>
                            </div>
                        </div>

                        <!-- MODAL DE CAPTURA PELA WEBCAM -->
                        <div id="modal_camera" class="hidden fixed inset-0 bg-slate-900/70 z-50 flex items-center justify-center p-4">
                            <div class="bg-white rounded-2xl p-4 max-w-xs w-full space-y-3 text-center shadow-2xl">
                                <h4 class="font-bold text-xs uppercase text-slate-800">Capturar Foto Tipo Passe</h4>
                                <video id="video_cam" autoplay playsinline class="w-full h-48 bg-black rounded-xl object-cover"></video>
                                <div class="flex gap-2">
                                    <button type="button" onclick="fecharCamera()" class="flex-1 py-2 bg-slate-200 text-slate-700 rounded-lg font-bold text-[10px]">Cancelar</button>
                                    <button type="button" onclick="capturarFotoCamera()" class="flex-1 py-2 bg-emerald-600 text-white rounded-lg font-bold text-[10px] shadow">Capturar</button>
                                </div>
                            </div>
                        </div>
                    </div>"""

if 'Fotografia Tipo Passe' not in dash_html:
    dash_html = dash_html.replace(
        '<div>\n                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>',
        campo_foto_formulario + '\n                    <div>\n                        <label class="block font-semibold text-slate-600 mb-1">Nome Completo *</label>'
    )

# Script de processamento de imagem em Canvas para 300x380 px / 40KB
scripts_foto = """
    <script>
        let streamCam = null;

        function otimizarImagemCanvas(imgSrc) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                canvas.width = 300;
                canvas.height = 380;
                const ctx = canvas.getContext('2d');
                
                // Recorte proporcional centralizado
                const ratio = Math.max(canvas.width / img.width, canvas.height / img.height);
                const x = (canvas.width - img.width * ratio) / 2;
                const y = (canvas.height - img.height * ratio) / 2;
                ctx.drawImage(img, x, y, img.width * ratio, img.height * ratio);
                
                // Converte para JPEG 80% (produz apenas ~35-45KB)
                const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
                document.getElementById('foto_base64').value = dataUrl;
                document.getElementById('preview_img').src = dataUrl;
                document.getElementById('preview_img').classList.remove('hidden');
                document.getElementById('preview_placeholder').classList.add('hidden');
            };
            img.src = imgSrc;
        }

        function processarFicheiroFoto(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    otimizarImagemCanvas(e.target.result);
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        async function ativarCamera() {
            document.getElementById('modal_camera').classList.remove('hidden');
            try {
                streamCam = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 640, height: 480 } });
                document.getElementById('video_cam').srcObject = streamCam;
            } catch (err) {
                alert('Não foi possível aceder à câmara: ' + err.message);
                fecharCamera();
            }
        }

        function fecharCamera() {
            if (streamCam) {
                streamCam.getTracks().forEach(t => t.stop());
                streamCam = null;
            }
            document.getElementById('modal_camera').classList.add('hidden');
        }

        function capturarFotoCamera() {
            const video = document.getElementById('video_cam');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            otimizarImagemCanvas(canvas.toDataURL('image/jpeg', 0.9));
            fecharCamera();
        }
    </script>
</body>"""

if 'otimizarImagemCanvas' not in dash_html:
    dash_html = dash_html.replace('</body>', scripts_foto)

env.parse(dash_html)
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)
print("✓ templates/dashboard.html: Formulário atualizado com compressão leve de fotos!")

# =============================================================================
# 4. ATUALIZAR TEMPLATES/CARTAO_MEMBRO.HTML PARA EXIBIR A FOTO REAL
# =============================================================================
with open('templates/cartao_membro.html', 'r', encoding='utf-8') as f:
    cartao_html = f.read()

box_foto_cartao = """                <div class="w-16 h-20 bg-slate-100 border border-slate-300 rounded-lg flex flex-col items-center justify-center text-slate-400 shrink-0 overflow-hidden shadow-inner">
                    {% if m.foto %}
                    <img src="{{ m.foto }}" alt="{{ m.nome }}" class="w-full h-full object-cover">
                    {% else %}
                    <span class="text-2xl">👤</span>
                    <span class="text-[7px] uppercase font-bold">Sem Foto</span>
                    {% endif %}
                </div>"""

cartao_html = re.sub(
    r'<div class="w-16 h-20 bg-slate-100 border border-slate-300 rounded-lg flex flex-col items-center justify-center text-slate-400 shrink-0">[\s\S]*?<\/div>',
    box_foto_cartao,
    cartao_html
)

env.parse(cartao_html)
with open('templates/cartao_membro.html', 'w', encoding='utf-8') as f:
    f.write(cartao_html)
print("✓ templates/cartao_membro.html: Cartão configurado para imprimir a fotografia real do membro!")

# Validar sintaxe
try:
    py_compile.compile('app.py', doraise=True)
    print("✓ Validação de sintaxe: app.py compilado sem nenhum erro!")
except Exception as e:
    print(f"Erro em app.py: {e}")

print("=" * 80)
print(">>> TUDO PRONTO! LOGÓTIPO OFICIAL STATIC E FOTOGRAFIAS ATIVADOS! <<<")
print("=" * 80)