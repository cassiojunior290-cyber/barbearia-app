import streamlit as st
import hashlib
import pandas as pd

st.set_page_config(page_title="BarberSaaS", page_icon="💈", layout="wide")

# ==============================
# BANCO EM MEMÓRIA (Cloud Safe)
# ==============================

if "barbearias" not in st.session_state:
    st.session_state.barbearias = []

if "usuarios" not in st.session_state:
    st.session_state.usuarios = []

if "servicos" not in st.session_state:
    st.session_state.servicos = []

if "colaboradores" not in st.session_state:
    st.session_state.colaboradores = []

if "agendamentos" not in st.session_state:
    st.session_state.agendamentos = []

if "logado" not in st.session_state:
    st.session_state.logado = False


# ==============================
# FUNÇÕES
# ==============================

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def criar_empresa(nome, email, senha):
    barbearia_id = len(st.session_state.barbearias) + 1

    st.session_state.barbearias.append({
        "id": barbearia_id,
        "nome": nome,
        "dono": email
    })

    st.session_state.usuarios.append({
        "email": email,
        "senha": hash_senha(senha),
        "role": "admin",
        "barbearia_id": barbearia_id
    })

def login(email, senha):
    senha_hash = hash_senha(senha)

    for user in st.session_state.usuarios:
        if user["email"] == email and user["senha"] == senha_hash:
            return user
    return None

# ==============================
# LOGIN / CADASTRO
# ==============================

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

# ==============================
# DASHBOARD
# ==============================

else:

    user = st.session_state.usuario
    barbearia_id = user["barbearia_id"]

    st.sidebar.write(user["email"])

    menu = ["Serviços", "Colaboradores", "Agendar", "Agenda"]
    escolha = st.sidebar.radio("Menu", menu)

    if escolha == "Serviços":
        nome = st.text_input("Nome do Serviço")
        preco = st.number_input("Preço", min_value=0.0)

        if st.button("Adicionar"):
            st.session_state.servicos.append({
                "nome": nome,
                "preco": preco,
                "barbearia_id": barbearia_id
            })
            st.success("Adicionado")

        for s in st.session_state.servicos:
            if s["barbearia_id"] == barbearia_id:
                st.write(f"{s['nome']} - R$ {s['preco']:.2f}")

    elif escolha == "Colaboradores":
        nome = st.text_input("Nome")

        if st.button("Adicionar"):
            st.session_state.colaboradores.append({
                "nome": nome,
                "barbearia_id": barbearia_id
            })
            st.success("Adicionado")

        for c in st.session_state.colaboradores:
            if c["barbearia_id"] == barbearia_id:
                st.write(c["nome"])

    elif escolha == "Agendar":

        servicos = [s for s in st.session_state.servicos if s["barbearia_id"] == barbearia_id]
        colaboradores = [c for c in st.session_state.colaboradores if c["barbearia_id"] == barbearia_id]

        if servicos and colaboradores:
            servico = st.selectbox("Serviço", [s["nome"] for s in servicos])
            preco = next(s["preco"] for s in servicos if s["nome"] == servico)

            st.write(f"Valor: R$ {preco:.2f}")

            colab = st.selectbox("Barbeiro", [c["nome"] for c in colaboradores])
            data = st.date_input("Data")
            hora = st.time_input("Hora")

            if st.button("Confirmar"):
                st.session_state.agendamentos.append({
                    "cliente": user["email"],
                    "servico": servico,
                    "colaborador": colab,
                    "data": f"{data} {hora}",
                    "barbearia_id": barbearia_id
                })
                st.success("Agendado!")

    elif escolha == "Agenda":

        dados = [
            a for a in st.session_state.agendamentos
            if a["barbearia_id"] == barbearia_id
        ]

        if dados:
            df = pd.DataFrame(dados)
            st.dataframe(df)

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
