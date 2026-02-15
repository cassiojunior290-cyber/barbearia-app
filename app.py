import streamlit as st
import sqlite3
from datetime import datetime, timedelta, time
import hashlib

st.set_page_config(page_title="BarberPro", layout="centered")

st.markdown("""
<style>
body { background-color: #0E1117; }
h1, h2, h3 { color: white; }
.stButton>button {
    background-color: #C6A75E;
    color: black;
    border-radius: 8px;
    height: 45px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =============================
# BANCO
# =============================

def conectar():
    return sqlite3.connect("barberpro.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS barbearias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        plano TEXT,
        data_criacao TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS barbeiros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barbearia_id INTEGER,
        nome TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barbearia_id INTEGER,
        nome TEXT,
        preco TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barbearia_id INTEGER,
        cliente TEXT,
        barbeiro TEXT,
        servico TEXT,
        data TEXT,
        hora TEXT
    )
    """)

    conn.commit()
    conn.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =============================
# CADASTRO
# =============================

def tela_cadastro():
    st.title("💈 BarberPro")
    st.subheader("Criar Conta")

    nome = st.text_input("Nome da Barbearia")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    plano = st.selectbox("Plano", ["Básico - R$49", "Pro - R$79", "Premium - R$129"])

    if st.button("Criar Conta"):
        conn = conectar()
        c = conn.cursor()
        try:
            c.execute("""
            INSERT INTO barbearias (nome, email, senha, plano, data_criacao)
            VALUES (?, ?, ?, ?, ?)
            """, (nome, email, hash_senha(senha), plano, str(datetime.now())))
            conn.commit()
            st.success("Conta criada com sucesso!")
        except:
            st.error("Email já cadastrado.")
        conn.close()

# =============================
# LOGIN
# =============================

def tela_login():
    st.title("💈 BarberPro")
    st.subheader("Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT * FROM barbearias WHERE email=? AND senha=?",
                  (email, hash_senha(senha)))
        usuario = c.fetchone()
        conn.close()

        if usuario:
            st.session_state["barbearia_id"] = usuario[0]
            st.session_state["barbearia_nome"] = usuario[1]
        else:
            st.error("Credenciais inválidas.")

# =============================
# DASHBOARD
# =============================

def dashboard():
    st.title(f"💈 {st.session_state['barbearia_nome']}")
    st.subheader("Organize. Automatize. Lucre.")

    conn = conectar()
    c = conn.cursor()

    st.subheader("⚙ Configurações")

    novo_barbeiro = st.text_input("Adicionar Barbeiro")
    if st.button("Salvar Barbeiro"):
        c.execute("INSERT INTO barbeiros (barbearia_id, nome) VALUES (?, ?)",
                  (st.session_state["barbearia_id"], novo_barbeiro))
        conn.commit()

    novo_servico = st.text_input("Adicionar Serviço")
    preco_servico = st.text_input("Preço")
    if st.button("Salvar Serviço"):
        c.execute("INSERT INTO servicos (barbearia_id, nome, preco) VALUES (?, ?, ?)",
                  (st.session_state["barbearia_id"], novo_servico, preco_servico))
        conn.commit()

    c.execute("SELECT nome FROM barbeiros WHERE barbearia_id=?",
              (st.session_state["barbearia_id"],))
    BARBEIROS = [b[0] for b in c.fetchall()]

    c.execute("SELECT nome FROM servicos WHERE barbearia_id=?",
              (st.session_state["barbearia_id"],))
    SERVICOS = [s[0] for s in c.fetchall()]

    st.subheader("📅 Novo Agendamento")

    nome_cliente = st.text_input("Nome do Cliente")
    if BARBEIROS:
        barbeiro = st.selectbox("Barbeiro", BARBEIROS)
    else:
        barbeiro = None

    if SERVICOS:
        servico = st.selectbox("Serviço", SERVICOS)
    else:
        servico = None

    data = st.date_input("Data")

    horarios = []
    inicio = datetime.combine(datetime.today(), time(9,0))
    fim = datetime.combine(datetime.today(), time(18,0))
    atual = inicio
    while atual <= fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(hours=1)

    hora = st.selectbox("Horário", horarios)

    if st.button("Confirmar Agendamento") and barbeiro and servico:
        c.execute("""
        INSERT INTO agendamentos
        (barbearia_id, cliente, barbeiro, servico, data, hora)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (st.session_state["barbearia_id"],
              nome_cliente, barbeiro, servico, str(data), hora))
        conn.commit()
        st.success("Agendamento realizado!")

    conn.close()

    if st.button("Sair"):
        st.session_state.clear()

# =============================
# MAIN
# =============================

criar_tabelas()

if "barbearia_id" not in st.session_state:
    opcao = st.sidebar.selectbox("Menu", ["Login", "Criar Conta"])
    if opcao == "Login":
        tela_login()
    else:
        tela_cadastro()
else:
    dashboard()
