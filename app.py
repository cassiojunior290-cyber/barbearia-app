import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="BarberPro", page_icon="💈")
# ==============================
# 🎨 ESTILO PREMIUM
# ==============================

st.markdown("""
<style>

body {
    background-color: #0E1117;
}

.stApp {
    background: linear-gradient(145deg, #0E1117, #111827);
    color: white;
}

h1, h2, h3 {
    color: #D4AF37;
    font-weight: 700;
}

.stButton>button {
    background: linear-gradient(90deg, #D4AF37, #C9A227);
    color: black;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px;
    border: none;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #E6C55A, #D4AF37);
    transform: scale(1.02);
}

.stSuccess {
    background-color: #0F5132 !important;
}

.stWarning {
    background-color: #664D03 !important;
}

.stTextInput>div>div>input {
    background-color: #1F2937;
    color: white;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)
# ==============================
# 🔹 BANCO DE DADOS
# ==============================

conn = sqlite3.connect("barberpro.db", check_same_thread=False)
c = conn.cursor()

# Criar tabela nova correta
c.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    premium INTEGER DEFAULT 0
)
""")

# Tabela agendamentos
# Tabela agendamentos
c.execute("DROP TABLE IF EXISTS agendamentos")

c.execute("""
CREATE TABLE agendamentos (
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
# 🔓 ÁREA LOGADA PREMIUM
# ==============================

else:
    st.markdown("## 💈 Painel BarberPro")
    st.markdown(f"### 👤 {st.session_state.usuario}")

    menu = st.radio("", ["📅 Agendar", "📋 Meus Agendamentos", "👑 Premium"], horizontal=True)

    # ==========================
    # 📅 AGENDAR
    # ==========================
    if menu == "📅 Agendar":

        st.markdown("### ✂️ Novo Agendamento")

        servico = st.selectbox("Escolha o serviço",
                               ["Corte", "Barba", "Corte + Barba"])

        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data")
        with col2:
            hora = st.time_input("Hora")

        if st.button("Confirmar Agendamento"):
            data_final = f"{data} {hora}"
            salvar_agendamento(st.session_state.usuario, servico, data_final)
            st.success("Agendamento confirmado com sucesso! ✨")

    # ==========================
    # 📋 MEUS AGENDAMENTOS
    # ==========================
    elif menu == "📋 Meus Agendamentos":

        st.markdown("### 📋 Seus Horários")

        agendamentos = listar_agendamentos(st.session_state.usuario)

        if agendamentos:
            for ag in agendamentos:
                st.markdown(f"""
                <div style="
                    background: #1F2937;
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:10px;
                    border-left: 4px solid #D4AF37;">
                    
                    <b>Serviço:</b> {ag[0]} <br>
                    <b>Data:</b> {ag[1]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Você ainda não possui agendamentos.")

    # ==========================
    # 👑 PREMIUM
    # ==========================
    elif menu == "👑 Premium":

        st.markdown("### 👑 Área Exclusiva")

        resultado = c.execute(
            "SELECT premium FROM usuarios WHERE email = ?",
            (st.session_state.usuario,)
        ).fetchone()

        if resultado and resultado[0] == 1:

            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #D4AF37, #C9A227);
                padding:20px;
                border-radius:15px;
                color:black;
                font-weight:bold;">
                
                ✅ Você é membro PREMIUM<br><br>
                ✔ Prioridade nos horários<br>
                ✔ Atendimento VIP<br>
                ✔ Descontos exclusivos
            </div>
            """, unsafe_allow_html=True)

        else:
            st.warning("Você ainda não é Premium.")

            if st.button("🚀 Tornar-se Premium"):
                c.execute(
                    "UPDATE usuarios SET premium = 1 WHERE email = ?",
                    (st.session_state.usuario,)
                )
                conn.commit()
                st.success("Agora você é Premium! 👑")
                st.rerun()

    # ==========================
    # 🚪 SAIR
    # ==========================

    st.divider()

    if st.button("Sair", key="botao_sair"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.rerun()
 
