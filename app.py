import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="BarberPro", page_icon="💈")

# ==============================
# 🔹 BANCO DE DADOS
# ==============================

conn = sqlite3.connect("barberpro.db", check_same_thread=False)
c = conn.cursor()

# Tabela usuários
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    premium INTEGER DEFAULT 0
)
""")

# Tabela agendamentos
c.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    servico TEXT NOT NULL,
    data TEXT NOT NULL
)
""")

conn.commit()

# ==============================
# 🔐 FUNÇÕES
# ==============================

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(email, senha):
    try:
        senha_hash = criptografar_senha(senha)
        c.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha_hash))
        conn.commit()
        return True
    except:
        return False

def verificar_login(email, senha):
    senha_hash = criptografar_senha(senha)
    c.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))
    return c.fetchone()

def virar_premium(email):
    c.execute("UPDATE usuarios SET premium = 1 WHERE email = ?", (email,))
    conn.commit()

def verificar_premium(email):
    c.execute("SELECT premium FROM usuarios WHERE email = ?", (email,))
    return c.fetchone()[0]

def salvar_agendamento(usuario, servico, data):
    c.execute("INSERT INTO agendamentos (usuario, servico, data) VALUES (?, ?, ?)",
              (usuario, servico, data))
    conn.commit()

def listar_agendamentos(usuario):
    c.execute("SELECT servico, data FROM agendamentos WHERE usuario = ?", (usuario,))
    return c.fetchall()

# ==============================
# 🔹 CONTROLE DE SESSÃO
# ==============================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# ==============================
# 🔐 LOGIN
# ==============================

if not st.session_state.logado:

    st.title("💈 BarberPro")
    st.subheader("Sistema Profissional")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cadastrar"):
            if cadastrar_usuario(email, senha):
                st.success("Usuário cadastrado!")
            else:
                st.error("Email já cadastrado!")

    with col2:
        if st.button("Entrar"):
            if verificar_login(email, senha):
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Login inválido")

# ==============================
# 🔓 ÁREA LOGADA
# ==============================

else:
    st.title("💈 Painel BarberPro")
    st.success(f"Bem-vindo, {st.session_state.usuario}")

    menu = st.radio("Menu", ["Agendar Horário", "Meus Agendamentos", "Área Premium"])

    # ==========================
    # 📅 AGENDAMENTO
    # ==========================

    if menu == "Agendar Horário":
        st.subheader("Novo Agendamento")

        servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])
        data = st.date_input("Data")
        hora = st.time_input("Hora")

        if st.button("Confirmar Agendamento"):
            data_final = f"{data} {hora}"
            salvar_agendamento(st.session_state.usuario, servico, data_final)
            st.success("Agendamento realizado com sucesso!")

    # ==========================
    # 📋 LISTAR AGENDAMENTOS
    # ==========================

    if menu == "Meus Agendamentos":
        st.subheader("Seus horários marcados")

        agendamentos = listar_agendamentos(st.session_state.usuario)

        if agendamentos:
            for ag in agendamentos:
                st.write(f"✂️ {ag[0]} - 📅 {ag[1]}")
        else:
            st.info("Nenhum agendamento encontrado.")

    # ==========================
    # 👑 ÁREA PREMIUM
    # ==========================

    if menu == "Área Premium":

        if verificar_premium(st.session_state.usuario) == 1:
            st.subheader("👑 Área Exclusiva Premium")
            st.success("Você é membro premium!")

            st.write("Benefícios:")
            st.write("✔️ Prioridade no agendamento")
            st.write("✔️ Desconto especial")
            st.write("✔️ Horários exclusivos")

        else:
            st.warning("Você ainda não é Premium.")

            if st.button("Virar Premium"):
                virar_premium(st.session_state.usuario)
                st.success("Agora você é Premium!")
                st.rerun()

    # ==========================
    # 🚪 SAIR
    # ==========================

    if st.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.rerun()
