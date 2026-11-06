import sqlite3

NOME_BANCO = 'banco_pi.db'

def inicializar_banco():
    """Conecta ao arquivo SQLite e cria a tabela 'alunos' se não existir."""
    conexao = sqlite3.connect(NOME_BANCO)
    cursor = conexao.cursor()
    
    # Comando SQL para criar a tabela
    comando_sql = '''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL,
            curso TEXT NOT NULL
        )
    '''
    cursor.execute(comando_sql)
    conexao.commit()
    conexao.close()
    print("-> Banco de dados e tabela 'alunos' verificados/criados com sucesso!")

if __name__ == '__main__':
    inicializar_banco()