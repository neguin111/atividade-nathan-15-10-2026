from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuração de chave secreta da sessão
app.secret_key = 'nh_smartbox_chave_segura_dev'

# Configuração de conexão com o banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_nh_smartbox'
}

def obter_conexao_db():
    """Abre e retorna uma conexão com o MySQL."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        print(f"[ERRO DB] Falha ao conectar: {err}")
        return None

# -----------------------------------------------------------------------------
# DECORATOR DE SEGURANÇA (Proteção de Rotas)
# -----------------------------------------------------------------------------
def login_requerido(f):
    """Garante que apenas usuários autenticados acessem a rota."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------------------------------------------
# ROTAS DO SISTEMA
# -----------------------------------------------------------------------------

@app.route('/')
def inicio():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()
        senha_input = request.form.get('senha', '').strip()

        conexao = obter_conexao_db()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            # Consulta parametrizada (%s) previne SQL Injection
            query = "SELECT * FROM usuarios WHERE login = %s"
            cursor.execute(query, (login_input,))
            usuario = cursor.fetchone()
            
            cursor.close()
            conexao.close()

            # Validação segura da senha usando HASH
            if usuario and check_password_hash(usuario['senha'], senha_input):
                session['usuario_id'] = usuario['id_usuario']
                session['usuario'] = usuario['login']
                session['nome'] = usuario['nome']
                session['tipo'] = usuario['tipo']
                return redirect(url_for('dashboard'))

        return render_template('login.html', erro="Usuário ou senha incorretos.")

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        login_usuario = request.form.get('login')
        senha_plana = request.form.get('senha')
        tipo = request.form.get('tipo', 'Morador')

        # Criptografa a senha antes de salvar no banco
        senha_hash = generate_password_hash(senha_plana)

        conexao = obter_conexao_db()
        if conexao:
            try:
                cursor = conexao.cursor()
                query = "INSERT INTO usuarios (nome, login, senha, tipo) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (nome, login_usuario, senha_hash, tipo))
                conexao.commit()
                cursor.close()
                conexao.close()
                
                return redirect(url_for('login'))
            except Error as err:
                print(f"[ERRO SQL] Falha ao cadastrar: {err}")

    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_requerido  # Rota protegida por autenticação
def dashboard():
    conexao = obter_conexao_db()
    totais = {'usuarios': 0, 'credenciais': 0, 'entregas': 0}
    logs = []

    if conexao:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        totais['usuarios'] = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM credenciais_acesso WHERE status = 'Ativa'")
        totais['credenciais'] = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM entregas WHERE status_encomenda = 'Depositado'")
        totais['entregas'] = cursor.fetchone()['total']

        cursor.execute("SELECT * FROM logs_sistema ORDER BY id_log DESC LIMIT 10")
        logs = cursor.fetchall()

        cursor.close()
        conexao.close()

    return render_template(
        'dashboard.html', 
        total_usuarios=totais['usuarios'], 
        total_credenciais=totais['credenciais'], 
        total_entregas=totais['entregas'], 
        logs=logs
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)