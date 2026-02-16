import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BarberPro", page_icon="💈", layout="wide")

# =============================
# ESTILO PREMIUM STARTUP
# =============================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0E1117, #111827);
    color: white;
}
.card {
    background: #1F2937;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    border-left: 5px solid #D4AF37;
}
.metric {
    font-size: 22px;
    font-weight: bold;
    color: #D4AF37;
}
</style>
""", unsafe_allow_html=True)

# =============================
# BANCO
# =============================

conn = sqlite3.connect("barberpro.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    premium INTEGER DEFAULT 0,
    role TEXT DEFAULT 'user'
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    servico TEXT NOT NULL,
    data TEXT NOT NULL
)
""")

conn.commit()

# =============================
# FUNÇÕES
# =============================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar(email, senha, role="user"):
    try:
        c.execute(
            "INSERT INTO usuarios (email, senha, role) VALUES (?, ?, ?)",
            (email, hash_senha(senha), role)
        )
        conn.commit()
        return True
    except:
        return False

def login(email, senha):
    c.execute(
        "SELECT email, role FROM usuarios WHERE email=? AND senha=?",
        (email, hash_senha(senha))
    )
    return c.fetchone()

def salvar_agendamento(usuario, servico, data):
    c.execute(
        "INSERT INTO agendamentos (usuario, servico, data) VALUES (?, ?, ?)",
        (usuario, servico, data)
    )
    conn.commit()

def listar_usuario(usuario):
    c.execute("SELECT servico, data FROM agendamentos WHERE usuario=?", (usuario,))
    return c.fetchall()

def listar_todos():
    c.execute("SELECT id, usuario, servico, data FROM agendamentos")
    return c.fetchall()

def excluir_agendamento(id):
    c.execute("DELETE FROM agendamentos WHERE id=?", (id,))
    conn.commit()

def virar_premium(email):
    c.execute("UPDATE usuarios SET premium=1 WHERE email=?", (email,))
    conn.commit()

def verificar_premium(email):
    c.execute("SELECT premium FROM usuarios WHERE email=?", (email,))
    resultado = c.fetchone()
    return resultado[0] if resultado else 0

# =============================
# SESSÃO
# =============================

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.role = ""

# =============================
# LOGIN
# =============================

if not st.session_state.logado:

    st.title("💈 BarberPro PRO")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cadastrar"):
            if cadastrar(email, senha):
                st.success("Usuário criado!")
            else:
                st.error("Email já existe.")

    with col2:
        if st.button("Entrar"):
            user = login(email, senha)
            if user:
                st.session_state.logado = True
                st.session_state.usuario = user[0]
                st.session_state.role = user[1]
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

# =============================
# ÁREA LOGADA
# =============================

else:

    st.sidebar.title("💈 BarberPro")
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"🔐 {st.session_state.role}")

    menu = ["📅 Agendar", "📋 Meus Agendamentos", "👑 Premium"]

    if st.session_state.role == "admin":
        menu.append("📊 Painel Admin")

    escolha = st.sidebar.radio("Menu", menu)

    # AGENDAR
    if escolha == "📅 Agendar":
        st.title("Novo Agendamento")

        servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])
        data = st.date_input("Data")
        hora = st.time_input("Hora")

        if st.button("Confirmar"):
            data_final = f"{data} {hora}"
            salvar_agendamento(st.session_state.usuario, servico, data_final)
            st.success("Agendado com sucesso!")

    # MEUS AGENDAMENTOS
    elif escolha == "📋 Meus Agendamentos":
        st.title("Meus Horários")

        dados = listar_usuario(st.session_state.usuario)

        if dados:
            for ag in dados:
                st.markdown(f"""
                <div class="card">
                <b>Serviço:</b> {ag[0]}<br>
                <b>Data:</b> {ag[1]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum agendamento.")

    # PREMIUM
    elif escolha == "👑 Premium":
        st.title("Área Premium")

        if verificar_premium(st.session_state.usuario):
            st.success("Você é Premium 👑")
        else:
            st.warning("Você ainda não é Premium.")

            if st.button("Ativar Premium"):
                virar_premium(st.session_state.usuario)
                st.success("Premium ativado!")

    # ADMIN
    elif escolha == "📊 Painel Admin":
        st.title("Dashboard Administrativo")

        dados = listar_todos()

        df = pd.DataFrame(dados, columns=["ID", "Usuário", "Serviço", "Data"])

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Agendamentos", len(df))
        col2.metric("Usuários Únicos", df["Usuário"].nunique())
        col3.metric("Serviços Oferecidos", df["Serviço"].nunique())

        st.bar_chart(df["Serviço"].value_counts())

        st.subheader("Lista Geral")

        for _, row in df.iterrows():
            colA, colB = st.columns([4,1])
            colA.write(f"{row['Usuário']} | {row['Serviço']} | {row['Data']}")
            if colB.button("Excluir", key=row["ID"]):
                excluir_agendamento(row["ID"])
                st.rerun()

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
