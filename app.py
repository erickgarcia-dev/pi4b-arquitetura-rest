from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
NOME_BANCO = 'banco_pi.db'

def obter_conexao():
    """Abre uma conexão curta com o SQLite; as linhas podem ser lidas como dicionários."""
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao

def inicializar_banco():
    """Conecta ao SQLite, cria a tabela e insere registros de teste iniciais."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL,
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
        
    conexao.close()


@app.route('/alunos', methods=['GET'])
def listar_alunos():
    """Endpoint REST para listar os alunos do banco em formato JSON."""
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM alunos')
    linhas = cursor.fetchall()
    conexao.close()
    
    # Converter resultado para lista de dicionarios
    lista_alunos = [dict(linha) for linha in linhas]
    
    return jsonify(lista_alunos), 200


if __name__ == '__main__':
    inicializar_banco()
    print("-> Servidor REST ativo em: http://127.0.0.1:5000/alunos")
    app.run(debug=True, port=5000)