import streamlit as st
import sqlite3
import hashlib

# ==============================
# 🔹 CONFIG
# ==============================

st.set_page_config(page_title="BarberPro", page_icon="💈")

# ==============================
# 🔹 BANCO
# ==============================

conn = sqlite3.connect("barberpro.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
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

# ==============================
# 🔹 CONTROLE DE SESSÃO
# ==============================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# ==============================
# 🔐 TELA DE LOGIN
# ==============================

if not st.session_state.logado:

    st.title("💈 BarberPro")
    st.subheader("Sistema de Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cadastrar"):
            if email and senha:
                if cadastrar_usuario(email, senha):
                    st.success("Usuário cadastrado com sucesso!")
                else:
                    st.error("Email já cadastrado!")
            else:
                st.warning("Preencha todos os campos!")

    with col2:
        if st.button("Entrar"):
            if verificar_login(email, senha):
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

# ==============================
# 🔓 ÁREA LOGADA
# ==============================

else:
    st.title("💈 BarberPro - Painel")
    st.success(f"Bem-vindo, {st.session_state.usuario} ✂️")

    st.write("Aqui será o painel do sistema.")

    if st.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.rerun()
