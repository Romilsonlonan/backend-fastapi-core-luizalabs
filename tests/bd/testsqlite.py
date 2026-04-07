#!/usr/bin/env python3
"""
Script para verificar o status do banco de dados SQLite
"""
import sqlite3
import os
from pathlib import Path

def verificar_banco():
    """Verifica se o banco de dados foi criado corretamente"""
    print("🔍 VERIFICANDO BANCO DE DADOS SQLITE")
    print("=" * 50)
    
    db_path = "/home/romilson/Projetos/luizalabs/backend/backend-fastapi-core-luizalabs/sql_app.db"
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"✅ Banco conectado com sucesso!")
        print(f"📁 Arquivo: {db_path}")
        print(f"📊 Tamanho: {os.path.getsize(db_path)} bytes")
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"\n📋 TABELAS ENCONTRADAS: {len(tabelas)}")
        
        if not tabelas:
            print("❌ NENHUMA TABELA ENCONTRADA!")
            print("   O banco foi criado mas não tem tabelas")
            return False
        
        for tabela in tabelas:
            nome_tabela = tabela[0]
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            count = cursor.fetchone()[0]
            print(f"   - {nome_tabela}: {count} registros")
            
            # Verificar estrutura da tabela
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = cursor.fetchall()
            print(f"     Colunas: {len(colunas)}")
        
        # Verificar se tem usuários
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"\n👥 USUÁRIOS NO BANCO: {total_users}")
        
        if total_users > 0:
            cursor.execute("SELECT email, name FROM users LIMIT 3")
            usuarios = cursor.fetchall()
            print("   Primeiros usuários:")
            for email, name in usuarios:
                print(f"   - {name} ({email})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verificar_backend():
    """Verifica se o backend está rodando"""
    print(f"\n🔍 VERIFICANDO BACKEND")
    print("=" * 50)
    
    log_file = "/home/romilson/Projetos/luizalabs/backend/backend-fastapi-core-luizalabs/backend.log"
    
    if not os.path.exists(log_file):
        print("❌ Arquivo de log não encontrado!")
        return False
    
    try:
        with open(log_file, 'r') as f:
            linhas = f.readlines()
            if not linhas:
                print("❌ Arquivo de log vazio!")
                return False
            
            # Verificar últimas 20 linhas
            ultimas_linhas = linhas[-20:] if len(linhas) > 20 else linhas
            
            print("📄 Últimas mensagens do log:")
            for linha in ultimas_linhas[-5:]:  # Mostrar últimas 5
                print(f"   {linha.strip()}")
            
            # Procurar erros
            erros = [linha for linha in ultimas_linhas if "ERROR" in linha or "error" in linha.lower()]
            if erros:
                print(f"\n❌ ENCONTRADOS {len(erros)} ERROS NO LOG:")
                for erro in erros[-3:]:  # Mostrar últimos 3 erros
                    print(f"   ⚠️  {erro.strip()}")
                return False
            else:
                print("\n✅ Nenhum erro encontrado no log recente")
                return True
                
    except Exception as e:
        print(f"❌ Erro ao ler log: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO DO BANCO DE DADOS")
    print("=" * 60)
    
    resultado_banco = verificar_banco()
    resultado_backend = verificar_backend()
    
    print(f"\n📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    if resultado_banco and resultado_backend:
        print("✅ BANCO DE DADOS ESTÁ FUNCIONANDO!")
        print("   - Tabelas criadas corretamente")
        print("   - Backend sem erros recentes")
        print("   - Pronto para usar nos testes!")
    else:
        print("❌ FORAM ENCONTRADOS PROBLEMAS!")
        if not resultado_banco:
            print("   - Problemas com o banco de dados")
        if not resultado_backend:
            print("   - Problemas com o backend")
