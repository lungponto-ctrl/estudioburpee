import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'estudio_burpee_secret_key_2026'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA = {
    "info": {
        "nome": "Estúdio Burpee",
        "telefone": "(31) 99157-8409",
        "endereco": "Avenida Imbiruçu, 65 - Bairro Petrolândia, Contagem - MG",
        "cep": "32.073-000",
        "horario_semana": "06:00 - 21:00",
        "horario_sabado": "08:00 - 12:00",
        "observacao_horario": "Atendimento exclusivo com horário agendado."
    },
    "professores": [
        {"id": 1, "nome": "Carlos Silva", "telefone": "(31) 98888-1111",
         "especialidade": "Treino Funcional & Calistenia"},
        {"id": 2, "nome": "Juliana Costa", "telefone": "(31) 97777-2222", "especialidade": "Musculação & Reabilitação"}
    ],
    "treinos_semana": {
        "Segunda-feira": [
            {"exercicio": "Kettlebell Swing", "series": "4x15", "descanso": "45s"},
            {"exercicio": "Burpees Explosivos", "series": "4x12", "descanso": "60s"}
        ],
        "Terça-feira": [
            {"exercicio": "Agachamento Livre", "series": "4x12", "descanso": "60s"},
            {"exercicio": "Prancha Abdominal", "series": "3x 1 min", "descanso": "30s"}
        ],
        "Quarta-feira": [
            {"exercicio": "Flexão de Braço", "series": "4x12", "descanso": "45s"},
            {"exercicio": "Thrusters com Halteres", "series": "3x15", "descanso": "60s"}
        ],
        "Quinta-feira": [
            {"exercicio": "Corrida estacionária / Corda", "series": "5x 1 min", "descanso": "30s"},
            {"exercicio": "Abdominal remador", "series": "4x20", "descanso": "45s"}
        ],
        "Sexta-feira": [
            {"exercicio": "Desafio Burpee & Funcional Total", "series": "Circuito 4x", "descanso": "90s"}
        ],
        "Sábado": [
            {"exercicio": "Treino Livre / Recuperação Ativa", "series": "Livre", "descanso": "-"}
        ]
    },
    "alunos": [
        {
            "id": 1,
            "nome": "Lucas Almeida",
            "telefone": "(31) 99999-3333",
            "endereco": "Rua das Flores, 123",
            "data_nascimento": "1995-06-15",
            "frequencia": "3x por semana",
            "vencimento_mensalidade": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "usuario": "lucas",
            "senha": "123",
            "avaliacao": {"peso": "78kg", "altura": "1.75m", "gordura": "14%", "imc": "25.5",
                          "meta": "Emagrecimento e Condicionamento"}
        }
    ],
    "posts": [
        {
            "id": 1,
            "aluno": "Lucas Almeida",
            "legenda": "Mais um treino funcional pago no Estúdio Burpee! 💪🔥",
            "midia_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80",
            "tipo": "imagem",
            "curtidas": 12,
            "data": "Hoje"
        }
    ]
}


def calcular_imc_e_meta(peso_str, altura_str, meta_informada):
    try:
        peso_limpo = float(peso_str.lower().replace('kg', '').replace(',', '.').strip())
        altura_limpa = float(altura_str.lower().replace('m', '').replace(',', '.').strip())

        if altura_limpa > 0:
            imc = peso_limpo / (altura_limpa ** 2)
            imc_fmt = f"{imc:.1f}"

            if not meta_informada or meta_informada.strip() == "":
                if imc < 18.5:
                    meta_auto = "Hipertrofia e Ganho de Massa"
                elif 18.5 <= imc < 25:
                    meta_auto = "Manutenção e Condicionamento Geral"
                elif 25 <= imc < 30:
                    meta_auto = "Emagrecimento e Definição"
                else:
                    meta_auto = "Emagrecimento, Saúde e Funcional Intensivo"
            else:
                meta_auto = meta_informada

            return imc_fmt, meta_auto
    except Exception:
        pass
    return "24.0", (meta_informada if meta_informada else "Condicionamento Geral")


@app.route('/')
def index():
    return render_template('index.html', info=DATA["info"], posts=DATA["posts"])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if tipo == 'admin' and usuario == 'admin' and senha == 'admin':
            session['user'] = {'role': 'admin', 'nome': 'Administrador'}
            return redirect(url_for('admin_dashboard'))
        elif tipo == 'aluno':
            aluno = next((a for a in DATA['alunos'] if a['usuario'] == usuario and a['senha'] == senha), None)
            if aluno:
                session['user'] = {'role': 'aluno', 'data': aluno}
                return redirect(url_for('aluno_dashboard'))
    return render_template('login.html', info=DATA["info"])


@app.route('/admin')
def admin_dashboard():
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', info=DATA["info"], professores=DATA["professores"], alunos=DATA["alunos"],
                           treinos_semana=DATA["treinos_semana"])


@app.route('/admin/info/editar', methods=['POST'])
def admin_editar_info():
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    DATA["info"]["nome"] = request.form.get('nome', DATA["info"]["nome"])
    DATA["info"]["telefone"] = request.form.get('telefone', DATA["info"]["telefone"])
    DATA["info"]["endereco"] = request.form.get('endereco', DATA["info"]["endereco"])
    DATA["info"]["cep"] = request.form.get('cep', DATA["info"]["cep"])
    DATA["info"]["horario_semana"] = request.form.get('horario_semana', DATA["info"]["horario_semana"])
    DATA["info"]["horario_sabado"] = request.form.get('horario_sabado', DATA["info"]["horario_sabado"])
    DATA["info"]["observacao_horario"] = request.form.get('observacao_horario', DATA["info"]["observacao_horario"])
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/aluno/adicionar', methods=['POST'])
def admin_adicionar_aluno():
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))

    vencimento_automatico = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    peso_input = request.form.get('peso', '70kg')
    altura_input = request.form.get('altura', '1.70m')
    meta_input = request.form.get('meta', '')
    gordura_input = request.form.get('gordura', '').strip()

    imc_calc, meta_calc = calcular_imc_e_meta(peso_input, altura_input, meta_input)

    novo_aluno = {
        "id": len(DATA["alunos"]) + 1,
        "nome": request.form.get('nome'),
        "telefone": request.form.get('telefone'),
        "endereco": request.form.get('endereco', ''),
        "data_nascimento": request.form.get('data_nascimento', ''),
        "frequencia": request.form.get('frequencia', '3x por semana'),
        "vencimento_mensalidade": vencimento_automatico,
        "usuario": request.form.get('usuario'),
        "senha": request.form.get('senha'),
        "avaliacao": {
            "peso": peso_input,
            "altura": altura_input,
            "gordura": gordura_input if gordura_input else "15%",
            "imc": imc_calc,
            "meta": meta_calc
        }
    }
    DATA["alunos"].append(novo_aluno)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/aluno/editar/<int:aluno_id>', methods=['POST'])
def admin_editar_aluno(aluno_id):
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))

    aluno = next((a for a in DATA['alunos'] if a['id'] == aluno_id), None)
    if aluno:
        peso_input = request.form.get('peso', aluno['avaliacao']['peso'])
        altura_input = request.form.get('altura', aluno['avaliacao']['altura'])
        meta_input = request.form.get('meta', '')
        gordura_input = request.form.get('gordura', '').strip()

        imc_calc, meta_calc = calcular_imc_e_meta(peso_input, altura_input, meta_input)

        aluno['nome'] = request.form.get('nome')
        aluno['telefone'] = request.form.get('telefone')
        aluno['frequencia'] = request.form.get('frequencia')
        aluno['usuario'] = request.form.get('usuario')
        aluno['senha'] = request.form.get('senha')
        aluno['avaliacao']['peso'] = peso_input
        aluno['avaliacao']['altura'] = altura_input
        aluno['avaliacao']['gordura'] = gordura_input if gordura_input else aluno['avaliacao'].get('gordura', '15%')
        aluno['avaliacao']['imc'] = imc_calc
        aluno['avaliacao']['meta'] = meta_calc

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/aluno/excluir/<int:aluno_id>', methods=['POST'])
def admin_excluir_aluno(aluno_id):
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    DATA["alunos"] = [a for a in DATA["alunos"] if a["id"] != aluno_id]
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/professor/adicionar', methods=['POST'])
def admin_adicionar_professor():
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    novo_prof = {
        "id": len(DATA["professores"]) + 1,
        "nome": request.form.get('nome'),
        "telefone": request.form.get('telefone'),
        "especialidade": request.form.get('especialidade')
    }
    DATA["professores"].append(novo_prof)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/professor/editar/<int:prof_id>', methods=['POST'])
def admin_editar_professor(prof_id):
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    prof = next((p for p in DATA['professores'] if p['id'] == prof_id), None)
    if prof:
        prof['nome'] = request.form.get('nome')
        prof['telefone'] = request.form.get('telefone')
        prof['especialidade'] = request.form.get('especialidade')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/professor/excluir/<int:prof_id>', methods=['POST'])
def admin_excluir_professor(prof_id):
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    DATA["professores"] = [p for p in DATA["professores"] if p["id"] != prof_id]
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/treino/adicionar', methods=['POST'])
def admin_adicionar_treino_dia():
    if session.get('user', {}).get('role') != 'admin':
        return redirect(url_for('login'))
    dia = request.form.get('dia')
    exercicio = request.form.get('exercicio')
    series = request.form.get('series')
    descanso = request.form.get('descanso', '45s')
    if dia in DATA["treinos_semana"] and exercicio and series:
        DATA["treinos_semana"][dia].append({"exercicio": exercicio, "series": series, "descanso": descanso})
    return redirect(url_for('admin_dashboard'))


@app.route('/aluno')
def aluno_dashboard():
    user = session.get('user')
    if not user or user.get('role') != 'aluno':
        return redirect(url_for('login'))
    aluno_id = user['data']['id']
    aluno = next((a for a in DATA['alunos'] if a['id'] == aluno_id), user['data'])
    venc_date = datetime.strptime(aluno['vencimento_mensalidade'], "%Y-%m-%d")
    dias_restantes = (venc_date - datetime.now()).days
    alerta_vencimento = dias_restantes <= 7
    return render_template('aluno.html', info=DATA["info"], aluno=aluno, dias_restantes=dias_restantes,
                           alerta=alerta_vencimento, posts=DATA["posts"], treinos_semana=DATA["treinos_semana"])


@app.route('/aluno/publicar', methods=['POST'])
def aluno_publicar():
    user = session.get('user')
    if not user or user.get('role') != 'aluno':
        return redirect(url_for('login'))

    aluno_nome = user['data']['nome']
    legenda = request.form.get('legenda')
    file = request.files.get('foto_galeria')

    midia_url = "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80"

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        midia_url = f"/{filepath}"

    if legenda:
        novo_post = {
            "id": len(DATA["posts"]) + 1,
            "aluno": aluno_nome,
            "legenda": legenda,
            "midia_url": midia_url,
            "tipo": "imagem",
            "curtidas": 0,
            "data": "Hoje"
        }
        DATA["posts"].insert(0, novo_post)

    return redirect(url_for('aluno_dashboard'))


@app.route('/post/curtir/<int:post_id>', methods=['POST'])
def post_curtir(post_id):
    post = next((p for p in DATA['posts'] if p['id'] == post_id), None)
    if post:
        post['curtidas'] += 1
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)