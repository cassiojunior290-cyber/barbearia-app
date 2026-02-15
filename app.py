import streamlit as st
import sqlite3
import hashlib

# ==============================
# 🔹 CONEXÃO COM BANCO DE DADOS
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
# 🎨 INTERFACE
# ==============================

st.set_page_config(page_title="BarberPro", page_icon="💈")

st.title("💈 BarberPro")
st.subheader("Sistema de Login")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

col1, col2 = st.columns(2)

# ==============================
# 🔘 BOTÕES
# ==============================

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
            st.success("Login realizado com sucesso!")
            st.write("Bem-vindo ao BarberPro ✂️")
        else:
            st.error("Credenciais inválidas.")
