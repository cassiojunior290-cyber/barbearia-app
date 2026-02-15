import streamlit as st
import sqlite3
from datetime import datetime, timedelta, time

# CONFIG
BARBERS = ["Igor", "Marcos", "Silva"]
SERVICES = ["Corte R$30", "Barba R$25", "Combo R$50"]
ADMIN_PASSWORD = "admin123"

st.set_page_config(page_title="Barbearia", layout="centered")

# ===== BANCO DE DADOS =====
def create_db():
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            barbeiro TEXT,
            servico TEXT,
            data TEXT,
            hora TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_agendamento(nome, barbeiro, servico, data, hora):
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO agendamentos (nome, barbeiro, servico, data, hora)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, barbeiro, servico, data, hora))
    conn.commit()
    conn.close()

def horarios_ocupados(barbeiro, data):
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute("""
        SELECT hora FROM agendamentos
        WHERE barbeiro = ? AND data = ?
    """, (barbeiro, data))
    dados = c.fetchall()
    conn.close()
    return [d[0] for d in dados]

def listar_agendamentos():
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute("SELECT * FROM agendamentos")
    dados = c.fetchall()
    conn.close()
    return dados

# ===== HORÁRIOS =====
def gerar_horarios():
    horarios = []
    inicio = datetime.combine(datetime.today(), time(9,0))
    fim = datetime.combine(datetime.today(), time(18,0))
    atual = inicio
    while atual <= fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(hours=1)
    return horarios

# ===== LOGIN =====
def tela_login():
    st.title("💈 Sistema Barbearia")

    tipo = st.radio("Entrar como:", ["Cliente", "Admin"])

    if tipo == "Cliente":
        if st.button("Entrar"):
            st.session_state["tipo"] = "cliente"

    if tipo == "Admin":
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar Admin"):
            if senha == ADMIN_PASSWORD:
                st.session_state["tipo"] = "admin"
            else:
                st.error("Senha incorreta")

# ===== CLIENTE =====
def tela_cliente():
    st.header("Agendar Horário")

    nome = st.text_input("Seu nome")
    barbeiro = st.selectbox("Barbeiro", BARBERS)
    servico = st.selectbox("Serviço", SERVICES)
    data = st.date_input("Data")

    todos = gerar_horarios()
    ocupados = horarios_ocupados(barbeiro, str(data))
    disponiveis = [h for h in todos if h not in ocupados]

    hora = st.selectbox("Horário", disponiveis)

    if st.button("Confirmar"):
        if nome == "":
            st.warning("Digite seu nome")
        else:
            salvar_agendamento(nome, barbeiro, servico, str(data), hora)
            st.success("Agendamento confirmado!")

    if st.button("Sair"):
        st.session_state["tipo"] = None

# ===== ADMIN =====
def tela_admin():
    st.header("Painel Admin")

    dados = listar_agendamentos()

    if dados:
        for d in dados:
            st.write(f"ID:{d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} | {d[5]}")
    else:
        st.info("Nenhum agendamento")

    if st.button("Sair"):
        st.session_state["tipo"] = None

# ===== MAIN =====
create_db()

if "tipo" not in st.session_state:
    st.session_state["tipo"] = None

if st.session_state["tipo"] is None:
    tela_login()
elif st.session_state["tipo"] == "cliente":
    tela_cliente()
elif st.session_state["tipo"] == "admin":
    tela_admin()
