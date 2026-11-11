import os
import sqlite3
from contextlib import closing

from flask import Flask, jsonify

app = Flask(__name__)
app.json.sort_keys = False
app.json.ensure_ascii = False

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