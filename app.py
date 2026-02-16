import streamlit as st
import sqlite3
import hashlib
import pandas as pd

st.set_page_config(page_title="BarberPro", page_icon="💈", layout="wide")

# =============================
# ESTILO CLEAN
# =============================

st.markdown("""
<style>
.stApp { background: #0F172A; color: white; }
section[data-testid="stSidebar"] { background: #111827; }
h1, h2, h3 { color: #D4AF37; }
.stButton>button {
    background: #D4AF37;
    color: black;
    font-weight: bold;
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
    email TEXT UNIQUE,
    senha TEXT,
    role TEXT DEFAULT 'user'
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    preco REAL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    servico TEXT,
    colaborador TEXT,
    data TEXT
)
""")

conn.commit()

# =============================
# FUNÇÕES
# =============================

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def cadastrar(email, senha):
    try:
        c.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)",
                  (email, hash_senha(senha)))
        conn.commit()
        return True
    except:
        return False

def login(email, senha):
    c.execute("SELECT email, role FROM usuarios WHERE email=? AND senha=?",
              (email, hash_senha(senha)))
    return c.fetchone()

def virar_admin(email):
    c.execute("UPDATE usuarios SET role='admin' WHERE email=?", (email,))
    conn.commit()

def adicionar_servico(nome, preco):
    c.execute("INSERT INTO servicos (nome, preco) VALUES (?, ?)", (nome, preco))
    conn.commit()

def adicionar_colaborador(nome):
    c.execute("INSERT INTO colaboradores (nome) VALUES (?)", (nome,))
    conn.commit()

def listar_servicos():
    c.execute("SELECT nome, preco FROM servicos")
    return c.fetchall()

def listar_colaboradores():
    c.execute("SELECT nome FROM colaboradores")
    return [c[0] for c in c.fetchall()]

def salvar_agendamento(usuario, servico, colaborador, data):
    c.execute("""
        INSERT INTO agendamentos (usuario, servico, colaborador, data)
        VALUES (?, ?, ?, ?)
    """, (usuario, servico, colaborador, data))
    conn.commit()

def listar_usuario(usuario):
    c.execute("SELECT id, servico, colaborador, data FROM agendamentos WHERE usuario=?", (usuario,))
    return c.fetchall()

def listar_todos():
    c.execute("SELECT id, usuario, servico, colaborador, data FROM agendamentos")
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

    st.title("💈 BarberPro")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Cadastrar"):
        if cadastrar(email, senha):
            st.success("Usuário criado!")
        else:
            st.error("Email já existe.")

    if col2.button("Entrar"):
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
    st.sidebar.write(st.session_state.usuario)
    st.sidebar.write(st.session_state.role)

    # SUPER ADMIN
    codigo_master = st.sidebar.text_input("Código Master", type="password")
    if codigo_master == "123superadmin":
        virar_admin(st.session_state.usuario)
        st.session_state.role = "admin"
        st.sidebar.success("Modo Admin ativado 👑")

    menu = ["📅 Agendar", "📋 Meus Agendamentos"]

    if st.session_state.role == "admin":
        menu += ["⚙ Serviços", "✂ Colaboradores", "📊 Painel Admin"]

    escolha = st.sidebar.radio("Menu", menu)

    # =============================
    # AGENDAR
    # =============================

    if escolha == "📅 Agendar":
        st.title("Novo Agendamento")

        servicos = listar_servicos()
        colaboradores = listar_colaboradores()

        if not servicos:
            st.warning("Nenhum serviço cadastrado.")
        else:
            nomes_servicos = [s[0] for s in servicos]
            servico = st.selectbox("Serviço", nomes_servicos)

            preco = [s[1] for s in servicos if s[0] == servico][0]
            st.write(f"💰 Valor: R$ {preco:.2f}")

            colaborador = st.selectbox("Barbeiro", colaboradores)

            data = st.date_input("Data")
            hora = st.time_input("Hora")

            if st.button("Confirmar"):
                salvar_agendamento(
                    st.session_state.usuario,
                    servico,
                    colaborador,
                    f"{data} {hora}"
                )
                st.success("Agendado com sucesso!")

    # =============================
    # MEUS AGENDAMENTOS
    # =============================

    elif escolha == "📋 Meus Agendamentos":
        st.title("Meus Agendamentos")

        dados = listar_usuario(st.session_state.usuario)

        for ag in dados:
            col1, col2 = st.columns([5,1])
            col1.write(f"{ag[1]} | {ag[2]} | {ag[3]}")
            if col2.button("❌", key=ag[0]):
                excluir_agendamento(ag[0])
                st.rerun()

    # =============================
    # SERVIÇOS (ADMIN)
    # =============================

    elif escolha == "⚙ Serviços":
        st.title("Gerenciar Serviços")

        nome = st.text_input("Nome do Serviço")
        preco = st.number_input("Preço", min_value=0.0)

        if st.button("Adicionar Serviço"):
            adicionar_servico(nome, preco)
            st.success("Serviço adicionado!")

        st.subheader("Serviços Atuais")
        for s in listar_servicos():
            st.write(f"{s[0]} - R$ {s[1]:.2f}")

    # =============================
    # COLABORADORES (ADMIN)
    # =============================

    elif escolha == "✂ Colaboradores":
        st.title("Gerenciar Colaboradores")

        nome = st.text_input("Nome do Colaborador")

        if st.button("Adicionar Colaborador"):
            adicionar_colaborador(nome)
            st.success("Colaborador adicionado!")

        st.subheader("Equipe Atual")
        for c in listar_colaboradores():
            st.write(c)

    # =============================
    # PAINEL ADMIN
    # =============================

    elif escolha == "📊 Painel Admin":
        st.title("Dashboard")

        dados = listar_todos()
        df = pd.DataFrame(dados, columns=["ID","Usuário","Serviço","Barbeiro","Data"])

        st.metric("Total Agendamentos", len(df))

        if not df.empty:
            st.bar_chart(df["Serviço"].value_counts())

            for _, row in df.iterrows():
                colA, colB = st.columns([5,1])
                colA.write(f"{row['Usuário']} | {row['Serviço']} | {row['Barbeiro']} | {row['Data']}")
                if colB.button("❌", key=row["ID"]):
                    excluir_agendamento(row["ID"])
                    st.rerun()

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
