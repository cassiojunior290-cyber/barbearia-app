import streamlit as st
import sqlite3
import hashlib
import pandas as pd

st.set_page_config(page_title="BarberPro", page_icon="💈", layout="wide")

# =============================
# ESTILO PREMIUM STARTUP
# =============================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0B0F19, #111827);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

section[data-testid="stSidebar"] {
    background: #0E1117;
}

h1, h2, h3 {
    color: #D4AF37;
}

.card {
    background: linear-gradient(145deg, #1F2937, #111827);
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 15px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    border: 1px solid rgba(212,175,55,0.2);
}

.metric-card {
    background: linear-gradient(145deg, #1F2937, #111827);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid rgba(212,175,55,0.2);
}

.metric-number {
    font-size: 28px;
    font-weight: bold;
    color: #D4AF37;
}

.stButton>button {
    background: linear-gradient(90deg, #D4AF37, #C9A227);
    color: black;
    font-weight: bold;
    border-radius: 12px;
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

    st.title("💈 BarberPro Startup")

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

    menu = ["📅 Agendar", "📋 Meus Agendamentos"]

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
            salvar_agendamento(
                st.session_state.usuario,
                servico,
                f"{data} {hora}"
            )
            st.success("Agendado com sucesso!")

    # MEUS AGENDAMENTOS
    elif escolha == "📋 Meus Agendamentos":
        st.title("📋 Meus Agendamentos")

        dados = listar_usuario(st.session_state.usuario)

        if dados:
            for ag in dados:
                col1, col2 = st.columns([4,1])

                col1.markdown(f"""
                <div class="card">
                    <h3>💈 {ag[1]}</h3>
                    <p>📅 {ag[2]}</p>
                </div>
                """, unsafe_allow_html=True)

                if col2.button("❌", key=f"user_{ag[0]}"):
                    excluir_agendamento(ag[0])
                    st.rerun()
        else:
            st.markdown("""
            <div class="card">
                <h3>Nenhum agendamento encontrado</h3>
            </div>
            """, unsafe_allow_html=True)

    # ADMIN
    elif escolha == "📊 Painel Admin":
        st.title("📊 Dashboard Administrativo")

        dados = listar_todos()
        df = pd.DataFrame(dados, columns=["ID", "Usuário", "Serviço", "Data"])

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(df)}</div>
            Total Agendamentos
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{df['Usuário'].nunique() if not df.empty else 0}</div>
            Usuários
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{df['Serviço'].nunique() if not df.empty else 0}</div>
            Serviços
        </div>
        """, unsafe_allow_html=True)

        if not df.empty:
            st.bar_chart(df["Serviço"].value_counts())

            st.subheader("Lista Geral")

            for _, row in df.iterrows():
                colA, colB = st.columns([4,1])
                colA.write(f"{row['Usuário']} | {row['Serviço']} | {row['Data']}")
                if colB.button("Excluir", key=f"admin_{row['ID']}"):
                    excluir_agendamento(row["ID"])
                    st.rerun()

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
