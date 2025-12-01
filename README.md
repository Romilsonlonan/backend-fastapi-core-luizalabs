# 📋 Projeto em Desenvolvimento - CBF Manager

O **CBF Manager** é um sistema completo de gerenciamento de atletas dos clubes brasileiros da Série A, desenvolvido para a Confederação Brasileira de Futebol.

## 🏗️ Arquitetura

<div align="center">

| Componente | Tecnologia |
|------------|------------|
| **Backend** | API REST em FastAPI (Python 3.12) |
| **Frontend** | Aplicação web em Next.js 15 com TypeScript |
| **Banco de Dados** | SQLite com SQLAlchemy ORM |

</div>

---

## 🔧 Funcionalidades Implementadas

### Backend (FastAPI)

- 🔐 **Autenticação JWT** - Sistema de login com tokens seguros
- 👥 **Gestão de Usuários** - Registro e autenticação de administradores  
- ⚽ **Gestão de Clubes** - CRUD completo com informações detalhadas
- 🏃 **Gestão de Jogadores** - Cadastro com estatísticas completas (gols, assistências, cartões, etc.)
- 🏢 **Centros de Treinamento** - Gerenciamento de CTs dos clubes
- 📅 **Rotinas de Treino** - Organização de treinos por dia/hora
- 🕷️ **Web Scraping** - Integração com ESPN para coleta de dados de jogadores

### Frontend (Next.js)

- 📊 **Dashboard Principal** - Interface administrativa intuitiva
- 🏟️ **Gestão de Clubes** - Visualização e cadastro de times
- 👤 **Gestão de Jogadores** - Lista detalhada com estatísticas
- 🏢 **Centros de Treinamento** - Exibição filtrada dos CTs
- 📸 **Upload de Imagens** - Sistema de upload de escudos e fotos de perfil
- 📱 **Interface Responsiva** - Design moderno com Tailwind CSS e Radix UI

---

## 📊 Modelos de Dados Principais 

```plaintext
👤 Usuários: Sistema de autenticação
⚽ Clubes: Nome, sigla, cidade, escudo, data de fundação, títulos, CT
🏃 Jogadores: Dados pessoais, posição, estatísticas detalhadas, relacionamento com clube
📅 Rotinas de Treino: Horários e atividades por clube
```


---

## 🚀 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web de alta performance
- **SQLAlchemy** - ORM para banco de dados
- **Alembic** - Migração de banco de dados
- **JWT** - Autenticação baseada em tokens
- **Pydantic** - Validação de dados
- **Poetry** - Gerenciamento de dependências

### Frontend
- **Next.js 15** - Framework React com renderização híbrida
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework de estilização
- **Radix UI** - Componentes acessíveis
- **React Hook Form** - Gerenciamento de formulários
- **Recharts** - Gráficos e visualizações

### Infraestrutura
- **Docker / Kubernetes** - Containerização e orquestração

### Segurança
- 🔒 **Bcrypt** para senhas
- 🛡️ **CORS** configurado
- ✅ **Validação de dados** com Pydantic

---

## 🎯 Objetivo

O sistema está sendo desenvolvido para gerenciar clubes brasileiros, seus jogadores e infraestrutura de treinamento, com foco em estatísticas detalhadas e organização administrativa.

