import os
import sqlite3
from contextlib import closing

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.json.sort_keys = False
app.json.ensure_ascii = False
app.json.compact = False

NOME_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'banco_pi.db')
COLUNAS = 'id, nome, matricula, curso'


def obter_conexao():
    """Abre uma conexão curta com o SQLite; as linhas podem ser lidas como dicionários."""
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """Conecta ao SQLite, cria a tabela e insere registros de teste iniciais."""
    with closing(obter_conexao()) as conexao:
        cursor = conexao.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                matricula TEXT NOT NULL UNIQUE,
                curso TEXT NOT NULL
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM alunos')
        if cursor.fetchone()[0] == 0:
            alunos_iniciais = [
                ('Érick Garcia', '2026001', 'Análise e Desenvolvimento de Sistemas'),
                ('João Ortiz', '2026002', 'Análise e Desenvolvimento de Sistemas')
            ]
            cursor.executemany(
                'INSERT INTO alunos (nome, matricula, curso) VALUES (?, ?, ?)',
                alunos_iniciais
            )
            conexao.commit()


@app.route('/alunos', methods=['GET'])
def listar_alunos():
    """Endpoint REST para listar os alunos do banco em formato JSON."""
    with closing(obter_conexao()) as conexao:
        cursor = conexao.cursor()
        cursor.execute(f'SELECT {COLUNAS} FROM alunos')
        linhas = cursor.fetchall()

    lista_alunos = [dict(linha) for linha in linhas]
    return jsonify(lista_alunos), 200


@app.route('/alunos/<int:aluno_id>', methods=['GET'])
def buscar_aluno(aluno_id):
    """GET /alunos/<id>: retorna um aluno (200 OK) ou erro 404 se não existir."""
    with closing(obter_conexao()) as conexao:
        linha = conexao.execute(
            f'SELECT {COLUNAS} FROM alunos WHERE id = ?', (aluno_id,)
        ).fetchone()

    if linha is None:
        return jsonify({'erro': 'aluno_nao_encontrado'}), 404

    return jsonify(dict(linha)), 200

@app.route('/alunos', methods=['POST'])
def criar_aluno():
    """POST /alunos: cadastra um novo aluno e retorna 201 Created."""
    dados = request.get_json(silent=True)

    campos_obrigatorios = ('nome', 'matricula', 'curso')
    if not dados or not all(
        campo in dados and str(dados[campo]).strip() for campo in campos_obrigatorios
    ):
        return jsonify({'erro': 'campos_obrigatorios_ausentes'}), 400

    nome = str(dados['nome']).strip()
    matricula = str(dados['matricula']).strip()
    curso = str(dados['curso']).strip()

    try:
        with closing(obter_conexao()) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                'INSERT INTO alunos (nome, matricula, curso) VALUES (?, ?, ?)',
                (nome, matricula, curso)
            )
            conexao.commit()
            novo_id = cursor.lastrowid

        novo_aluno = {
            'id': novo_id,
            'nome': nome,
            'matricula': matricula,
            'curso': curso
        }
        return jsonify(novo_aluno), 201

    except sqlite3.IntegrityError:
        return jsonify({'erro': 'matricula_ja_cadastrada'}), 400
    

@app.route('/alunos/<int:aluno_id>', methods=['PUT'])
def atualizar_aluno(aluno_id):
    """PUT /alunos/<id>: atualiza os dados de um aluno existente (200 OK)."""
    dados = request.get_json(silent=True)

    campos_obrigatorios = ('nome', 'matricula', 'curso')
    if not dados or not all(
        campo in dados and str(dados[campo]).strip() for campo in campos_obrigatorios
    ):
        return jsonify({'erro': 'campos_obrigatorios_ausentes'}), 400

    nome = str(dados['nome']).strip()
    matricula = str(dados['matricula']).strip()
    curso = str(dados['curso']).strip()

    try:
        with closing(obter_conexao()) as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT id FROM alunos WHERE id = ?', (aluno_id,))
            if cursor.fetchone() is None:
                return jsonify({'erro': 'aluno_nao_encontrado'}), 404

            cursor.execute(
                'UPDATE alunos SET nome = ?, matricula = ?, curso = ? WHERE id = ?',
                (nome, matricula, curso, aluno_id)
            )
            conexao.commit()

        aluno_atualizado = {
            'id': aluno_id,
            'nome': nome,
            'matricula': matricula,
            'curso': curso
        }
        return jsonify(aluno_atualizado), 200

    except sqlite3.IntegrityError:
        return jsonify({'erro': 'matricula_ja_cadastrada'}), 400


@app.errorhandler(404)
def rota_nao_encontrada(_erro):
    return jsonify({'erro': 'recurso_nao_encontrado'}), 404


@app.errorhandler(405)
def metodo_nao_permitido(_erro):
    return jsonify({'erro': 'metodo_nao_permitido'}), 405


@app.errorhandler(500)
def erro_interno(_erro):
    return jsonify({'erro': 'erro_interno'}), 500


inicializar_banco()

if __name__ == '__main__':
    print("-> Servidor REST ativo em: http://127.0.0.1:5000/alunos")
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', port=5000)