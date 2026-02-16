import streamlit as st
from supabase import create_client
import hashlib
import pandas as pd

# =============================
# CONFIG SUPABASE (SEUS DADOS)
# =============================

SUPABASE_URL = "https://coqkmfuyikooalskaasc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNvcWttZnV5aWtvb2Fsc2thYXNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExOTUyMDEsImV4cCI6MjA4Njc3MTIwMX0.zquHCWkkjUXHdNQ2Ac2X3HLKmFirNWKO4yqENdDTjMY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="BarberSaaS", page_icon="💈", layout="wide")

# =============================
# FUNÇÕES UTILS
# =============================

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def criar_empresa(nome, email, senha):
    senha_hash = hash_senha(senha)

    barbearia = supabase.table("barbearias").insert({
        "nome": nome,
        "dono_email": email
    }).execute()

    barbearia_id = barbearia.data[0]["id"]

    supabase.table("usuarios").insert({
        "email": email,
        "senha": senha_hash,
        "role": "admin",
        "barbearia_id": barbearia_id
    }).execute()

def login(email, senha):
    senha_hash = hash_senha(senha)
    response = supabase.table("usuarios") \
        .select("*") \
        .eq("email", email) \
        .eq("senha", senha_hash) \
        .execute()

    if response.data:
        return response.data[0]
    return None

def adicionar_servico(nome, preco, barbearia_id):
    supabase.table("servicos").insert({
        "nome": nome,
        "preco": preco,
        "barbearia_id": barbearia_id
    }).execute()

def listar_servicos(barbearia_id):
    response = supabase.table("servicos") \
        .select("*") \
        .eq("barbearia_id", barbearia_id) \
        .execute()
    return response.data

def adicionar_colaborador(nome, barbearia_id):
    supabase.table("colaboradores").insert({
        "nome": nome,
        "barbearia_id": barbearia_id
    }).execute()

def listar_colaboradores(barbearia_id):
    response = supabase.table("colaboradores") \
        .select("*") \
        .eq("barbearia_id", barbearia_id) \
        .execute()
    return response.data

def salvar_agendamento(cliente, servico, colaborador, data, barbearia_id):
    supabase.table("agendamentos").insert({
        "cliente": cliente,
        "servico": servico,
        "colaborador": colaborador,
        "data": data,
        "barbearia_id": barbearia_id
    }).execute()

def listar_agendamentos(barbearia_id):
    response = supabase.table("agendamentos") \
        .select("*") \
        .eq("barbearia_id", barbearia_id) \
        .execute()
    return response.data


# =============================
# CONTROLE DE SESSÃO
# =============================

if "logado" not in st.session_state:
    st.session_state.logado = False

# =============================
# LOGIN / CADASTRO
# =============================

if not st.session_state.logado:

    st.title("💈 BarberSaaS")

    opcao = st.radio("Escolha", ["Entrar", "Criar Barbearia"])

    if opcao == "Criar Barbearia":
        nome = st.text_input("Nome da Barbearia")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Criar Empresa"):
            criar_empresa(nome, email, senha)
            st.success("Empresa criada! Agora faça login.")

    else:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = login(email, senha)
            if user:
                st.session_state.logado = True
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Login inválido")

# =============================
# DASHBOARD
# =============================

else:

    user = st.session_state.usuario
    barbearia_id = user["barbearia_id"]

    st.sidebar.write(f"👤 {user['email']}")

    menu = ["Serviços", "Colaboradores", "Agendar", "Agenda"]
    escolha = st.sidebar.radio("Menu", menu)

    # =============================
    # SERVIÇOS
    # =============================

    if escolha == "Serviços":
        st.title("Gerenciar Serviços")

        nome = st.text_input("Nome do Serviço")
        preco = st.number_input("Preço", min_value=0.0)

        if st.button("Adicionar"):
            adicionar_servico(nome, preco, barbearia_id)
            st.success("Serviço adicionado!")

        servicos = listar_servicos(barbearia_id)
        for s in servicos:
            st.write(f"{s['nome']} — R$ {float(s['preco']):.2f}")

    # =============================
    # COLABORADORES
    # =============================

    elif escolha == "Colaboradores":
        st.title("Gerenciar Colaboradores")

        nome = st.text_input("Nome do Colaborador")

        if st.button("Adicionar"):
            adicionar_colaborador(nome, barbearia_id)
            st.success("Colaborador adicionado!")

        colaboradores = listar_colaboradores(barbearia_id)
        for c in colaboradores:
            st.write(c["nome"])

    # =============================
    # AGENDAR
    # =============================

    elif escolha == "Agendar":
        st.title("Novo Agendamento")

        servicos = listar_servicos(barbearia_id)
        colaboradores = listar_colaboradores(barbearia_id)

        if servicos and colaboradores:
            servico = st.selectbox("Serviço", [s["nome"] for s in servicos])
            preco = next(s["preco"] for s in servicos if s["nome"] == servico)
            st.write(f"💰 Valor: R$ {float(preco):.2f}")

            colaborador = st.selectbox("Barbeiro", [c["nome"] for c in colaboradores])
            data = st.date_input("Data")
            hora = st.time_input("Hora")

            if st.button("Confirmar Agendamento"):
                salvar_agendamento(
                    user["email"],
                    servico,
                    colaborador,
                    f"{data} {hora}",
                    barbearia_id
                )
                st.success("Agendado com sucesso!")

    # =============================
    # AGENDA
    # =============================

    elif escolha == "Agenda":
        st.title("Agenda da Barbearia")

        dados = listar_agendamentos(barbearia_id)
        if dados:
            df = pd.DataFrame(dados)
            st.dataframe(df)
        else:
            st.info("Nenhum agendamento encontrado.")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
