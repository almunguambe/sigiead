# -*- coding: utf-8 -*-
import sqlite3
import os

print("=" * 70)
print("A ASSEGURAR TODAS AS COLUNAS DA TABELA DOUTRINA EM BANCO.DB...")
print("=" * 70)

todas_colunas = [
    ('congregacao_id', 'INTEGER DEFAULT 1'),
    ('nome_aluno', 'TEXT'),
    ('classe', "TEXT DEFAULT 'Classe I - Primeiros Passos'"),
    ('professor', "TEXT DEFAULT 'Pastor Dirigente'"),
    ('licao_atual', "TEXT DEFAULT 'Lição 1 - O Pecado e o Perdão'"),
    ('data_inicio', "TEXT DEFAULT '2026-01-01'"),
    ('presencas', 'INTEGER DEFAULT 0'),
    ('situacao', "TEXT DEFAULT 'Em Formação'"),
    ('usuario', 'TEXT'),
    ('senha', 'TEXT'),
    ('aproveitamento', 'REAL DEFAULT 0.0'),
    ('progresso', 'INTEGER DEFAULT 0'),
    ('ultimo_acesso', 'TEXT'),
    ('criado_em', 'TEXT')
]

if os.path.exists('banco.db'):
    conn = sqlite3.connect('banco.db')
    cur = conn.cursor()
    
    # Criar tabela caso não exista
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doutrina (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    """)
    
    cur.execute("PRAGMA table_info(doutrina)")
    existentes = [col[1] for col in cur.fetchall()]
    
    for nome_col, tipo_col in todas_colunas:
        if nome_col not in existentes:
            try:
                cur.execute(f"ALTER TABLE doutrina ADD COLUMN {nome_col} {tipo_col}")
                print(f"✓ Coluna '{nome_col}' adicionada com sucesso em banco.db")
            except Exception as e:
                print(f"Aviso ao adicionar {nome_col}: {e}")
                
    conn.commit()
    conn.close()

print("\n" + "=" * 70)
print("A TESTAR O CARREGAMENTO DA APLICAÇÃO...")
print("=" * 70)

try:
    import app
    print("\n✓ CÓPIA RESTAURADA CARREGOU COM SUCESSO ABSOLUTO!")
except Exception as err:
    import traceback
    print("\nErro ao importar app:")
    traceback.print_exc()
