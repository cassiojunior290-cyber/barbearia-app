import streamlit as st
import sqlite3
import hashlib
import pandas as pd

st.set_page_config(page_title="BarberSaaS", page_icon="💈", layout="wide")

# =========================
# CONFIG SUPER ADMIN
# =========================
SUPER_ADMIN_EMAIL = "admin@barbersaas.com"

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp { background: #0F172A; color: white; }
section[data-testid="stSidebar"] { background: #111827; }
h1, h2, h3 { color: #D4AF37; }
.stButton>button { background: #D4AF37; color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =========================
# BANCO
# =========================
conn = sqlite3.connect("barbersaas.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS barbearias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    dono_email TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    senha TEXT,
    role TEXT DEFAULT 'user',
    barbearia_id INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    preco REAL,
    barbearia_id INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    barbearia_id INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    servico TEXT,
    colaborador TEXT,
    data TEXT,
    barbearia_id INTEGER
)
""")

conn.commit()

# =========================
# FUNÇÕES
# =========================

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def criar_barbeiro_empresa(nome_barbearia, email, senha):
    c.execute("INSERT INTO barbearias (nome, dono_email) VALUES (?, ?)",
              (nome_barbearia, email))
    barbearia_id = c.lastrowid

    c.execute("""
        INSERT INTO usuarios (email, senha, role, barbearia_id)
        VALUES (?, ?, 'admin', ?)
    """, (email, hash_senha(senha), barbearia_id))
    conn.commit()

def login(email, senha):
    c.execute("""
        SELECT email, role, barbearia_id
        FROM usuarios
        WHERE email=? AND senha=?
    """, (email, hash_senha(senha)))
    return c.fetchone()

def adicionar_servico(nome, preco, barbearia_id):
    c.execute("""
        INSERT INTO servicos (nome, preco, barbearia_id)
        VALUES (?, ?, ?)
    """, (nome, preco, barbearia_id))
    conn.commit()

def listar_servicos(barbearia_id):
    c.execute("SELECT nome, preco FROM servicos WHERE barbearia_id=?",
              (barbearia_id,))
    return c.fetchall()

def adicionar_colaborador(nome, barbearia_id):
    c.execute("""
        INSERT INTO colaboradores (nome, barbearia_id)
        VALUES (?, ?)
    """, (nome, barbearia_id))
    conn.commit()

def listar_colaboradores(barbearia_id):
    c.execute("SELECT nome FROM colaboradores WHERE barbearia_id=?",
              (barbearia_id,))
    return [x[0] for x in c.fetchall()]

def salvar_agendamento(usuario, servico, colaborador, data, barbearia_id):
    c.execute("""
        INSERT INTO agendamentos (usuario, servico, colaborador, data, barbearia_id)
        VALUES (?, ?, ?, ?, ?)
    """, (usuario, servico, colaborador, data, barbearia_id))
    conn.commit()

def listar_agendamentos(barbearia_id):
    c.execute("""
        SELECT usuario, servico, colaborador, data
        FROM agendamentos
        WHERE barbearia_id=?
    """, (barbearia_id,))
    return c.fetchall()

# =========================
# SESSÃO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

# =========================
# LOGIN / CADASTRO EMPRESA
# =========================

if not st.session_state.logado:

    st.title("💈 BarberSaaS")

    escolha = st.radio("Escolha", ["Entrar", "Criar Barbearia"])

    if escolha == "Criar Barbearia":
        nome_barbearia = st.text_input("Nome da Barbearia")
        email = st.text_input("Email do Dono")
        senha = st.text_input("Senha", type="password")

        if st.button("Criar Empresa"):
            criar_barbeiro_empresa(nome_barbearia, email, senha)
            st.success("Empresa criada! Faça login.")

    else:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = login(email, senha)
            if user:
                st.session_state.logado = True
                st.session_state.email = user[0]
                st.session_state.role = user[1]
                st.session_state.barbearia_id = user[2]
                st.rerun()
            else:
                st.error("Login inválido")

# =========================
# DASHBOARD
# =========================

else:

    st.sidebar.write(st.session_state.email)

    menu = ["Agendar", "Serviços", "Colaboradores", "Agenda"]

    escolha = st.sidebar.radio("Menu", menu)

    if escolha == "Serviços":
        nome = st.text_input("Nome do Serviço")
        preco = st.number_input("Preço", min_value=0.0)

        if st.button("Adicionar"):
            adicionar_servico(nome, preco, st.session_state.barbearia_id)
            st.success("Adicionado")

        st.subheader("Serviços")
        for s in listar_servicos(st.session_state.barbearia_id):
            st.write(f"{s[0]} - R$ {s[1]:.2f}")

    elif escolha == "Colaboradores":
        nome = st.text_input("Nome")

        if st.button("Adicionar"):
            adicionar_colaborador(nome, st.session_state.barbearia_id)
            st.success("Adicionado")

        for c in listar_colaboradores(st.session_state.barbearia_id):
            st.write(c)

    elif escolha == "Agendar":
        servicos = listar_servicos(st.session_state.barbearia_id)
        colaboradores = listar_colaboradores(st.session_state.barbearia_id)

        if servicos:
            nomes = [s[0] for s in servicos]
            servico = st.selectbox("Serviço", nomes)
            preco = [s[1] for s in servicos if s[0]==servico][0]
            st.write(f"Valor: R$ {preco:.2f}")

            colab = st.selectbox("Barbeiro", colaboradores)
            data = st.date_input("Data")
            hora = st.time_input("Hora")

            if st.button("Confirmar"):
                salvar_agendamento(
                    st.session_state.email,
                    servico,
                    colab,
                    f"{data} {hora}",
                    st.session_state.barbearia_id
                )
                st.success("Agendado")

    elif escolha == "Agenda":
        dados = listar_agendamentos(st.session_state.barbearia_id)
        df = pd.DataFrame(dados, columns=["Cliente","Serviço","Barbeiro","Data"])
        st.dataframe(df)

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
