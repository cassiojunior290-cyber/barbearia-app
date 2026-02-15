import streamlit as st
from st_supabase_connection import SupabaseConnection
import hashlib

st.set_page_config(page_title="BarberPro", page_icon="💈")

# Conexão
conn = st.connection("supabase", type=SupabaseConnection, 
                     url=st.secrets["SUPABASE_URL"], 
                     key=st.secrets["SUPABASE_KEY"])

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

if "logado" not in st.session_state:
    st.session_state.logado = False

st.title("💈 BarberPro")

if not st.session_state.logado:
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    with tab1:
        e = st.text_input("Email", key="l_e")
        s = st.text_input("Senha", type="password", key="l_s")
        if st.button("Acessar"):
            res = conn.table("usuarios").select("*").eq("email", e).eq("senha", criptografar_senha(s)).execute()
            if res.data:
                st.session_state.logado = True
                st.session_state.usuario = e
                st.rerun()
            else:
                st.error("Erro no login.")
    with tab2:
        ne = st.text_input("Novo Email", key="c_e")
        ns = st.text_input("Nova Senha", type="password", key="c_s")
        if st.button("Criar Conta"):
            conn.table("usuarios").insert({"email": ne, "senha": criptografar_senha(ns)}).execute()
            st.success("Conta criada! Entre na aba ao lado.")
else:
    st.write(f"Você está logado como: **{st.session_state.usuario}**")
    
    # --- ÁREA DE AGENDAMENTO ---
    st.subheader("📅 Agende seu horário")
    servico = st.selectbox("Escolha o serviço", ["Corte", "Barba", "Combo"])
    data = st.date_input("Data")
    hora = st.time_input("Hora")
    
    if st.button("Confirmar Agendamento"):
        try:
            conn.table("agendamentos").insert({
                "usuario": st.session_state.usuario,
                "servico": servico,
                "data_hora": f"{data} {hora}"
            }).execute()
            st.balloons()
            st.success("Agendado com sucesso!")
        except:
            st.error("Erro ao salvar agendamento.")

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
