import sqlite3

NOME_BANCO = 'banco_pi.db'

def inicializar_banco():
    """Conecta ao SQLite, cria a tabela e insere registros de teste iniciais."""
    conexao = sqlite3.connect(NOME_BANCO)
    cursor = conexao.cursor()
    
    # Criar tabela
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL,
            curso TEXT NOT NULL
        )
    ''')
    
    # Verificar se a tabela está vazia
    cursor.execute('SELECT COUNT(*) FROM alunos')
    total = cursor.fetchone()[0]
    
    if total == 0:
        alunos_iniciais = [
            ('Érick Garcia', '2026001', 'Análise e Desenvolvimento de Sistemas'),
            ('Maria Fátima', '2026002', 'Engenharia de Software')
        ]
        cursor.executemany(
            'INSERT INTO alunos (nome, matricula, curso) VALUES (?, ?, ?)', 
            alunos_iniciais
        )
        conexao.commit()
        print("-> Dados de teste inseridos com sucesso!")
        
    conexao.close()

if __name__ == '__main__':
    inicializar_banco()