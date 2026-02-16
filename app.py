import streamlit as st
import sqlite3
import hashlib
import pandas as pd

st.set_page_config(page_title="BarberPro", page_icon="💈", layout="wide")

# =============================
# ESTILO CLEAN PREMIUM
# =============================

st.markdown("""
<style>
.stApp {
    background: #0F172A;
    color: white;
    font-family: Arial, sans-serif;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

h1, h2, h3 {
    color: #D4AF37;
}

.stButton>button {
    background: #D4AF37;
    color: black;
    font-weight: bold;
    border-radius: 8px;
    border: none;
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

def cadastrar(email, senha):
    try:
        c.execute(
            "INSERT INTO usuarios (email, senha) VALUES (?, ?)",
            (email, hash_senha(senha))
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
    c.execute("SELECT id, servico, data FROM agendamentos WHERE usuario=?", (usuario,))
    return c.fetchall()

def listar_todos():
    c.execute("SELECT id, usuario, servico, data FROM agendamentos")
    return c.fetchall()

def excluir_agendamento(id):
    c.execute("DELETE FROM agendamentos WHERE id=?", (id,))
    conn.commit()

def virar_admin(email):
    c.execute("UPDATE usuarios SET role='admin' WHERE email=?", (email,))
    conn.commit()

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

    st.title("💈 BarberPro")

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

    # SUPER ADMIN SECRETO
    codigo_master = st.sidebar.text_input("Código Master", type="password")

    if codigo_master == "123superadmin":
        virar_admin(st.session_state.usuario)
        st.session_state.role = "admin"
        st.sidebar.success("Modo Super Admin ativado 👑")

    menu = ["📅 Agendar", "📋 Meus Agendamentos"]

    if st.session_state.role == "admin":
        menu.append("📊 Painel Admin")

    escolha = st.sidebar.radio("Menu", menu)

    # =============================
    # AGENDAR
    # =============================

    if escolha == "📅 Agendar":
        st.title("Novo Agendamento")

        servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte + Barba"])
        data = st.date_input("Data")
        hora = st.time_input("Hora")

        if st.button("Confirmar"):
            salvar_agendamento(
                st.session_state.usuario,
                servico,
                f"{data} {hora}"
            )
            st.success("Agendado com sucesso!")

    # =============================
    # MEUS AGENDAMENTOS (SIMPLIFICADO)
    # =============================

    elif escolha == "📋 Meus Agendamentos":
        st.title("Meus Agendamentos")

        dados = listar_usuario(st.session_state.usuario)

        if not dados:
            st.info("Você ainda não tem agendamentos.")
        else:
            for ag in dados:
                col1, col2 = st.columns([5,1])
                col1.write(f"💈 {ag[1]} — 📅 {ag[2]}")
                if col2.button("❌", key=f"user_del_{ag[0]}"):
                    excluir_agendamento(ag[0])
                    st.rerun()

    # =============================
    # PAINEL ADMIN (SIMPLIFICADO)
    # =============================

    elif escolha == "📊 Painel Admin":
        st.title("Dashboard Administrativo")

        dados = listar_todos()
        df = pd.DataFrame(dados, columns=["ID", "Usuário", "Serviço", "Data"])

        col1, col2, col3 = st.columns(3)

        col1.metric("Total", len(df))
        col2.metric("Usuários", df["Usuário"].nunique() if not df.empty else 0)
        col3.metric("Serviços", df["Serviço"].nunique() if not df.empty else 0)

        if not df.empty:
            st.bar_chart(df["Serviço"].value_counts())

            st.subheader("Todos os Agendamentos")

            for _, row in df.iterrows():
                colA, colB = st.columns([5,1])
                colA.write(f"{row['Usuário']} — {row['Serviço']} — {row['Data']}")
                if colB.button("❌", key=f"admin_del_{row['ID']}"):
                    excluir_agendamento(row["ID"])
                    st.rerun()

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
