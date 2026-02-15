import streamlit as st
from st_supabase_connection import SupabaseConnection
import hashlib

# Configuração para Mobile
st.set_page_config(page_title="BarberPro", page_icon="💈")

# Liga o aplicativo ao Supabase usando seus Secrets
conn = st.connection("supabase", type=SupabaseConnection)

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

st.title("💈 BarberPro")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    aba1, aba2 = st.tabs(["Entrar", "Cadastrar"])
    
    with aba1:
        e = st.text_input("Email")
        s = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            sh = criptografar_senha(s)
            user = conn.table("usuarios").select("*").eq("email", e).eq("senha", sh).execute()
            if user.data:
                st.session_state.logado = True
                st.session_state.usuario = e
                st.rerun()
            else:
                st.error("Erro no login")
    
    with aba2:
        ne = st.text_input("Novo Email")
        ns = st.text_input("Nova Senha", type="password")
        if st.button("Criar Conta"):
            try:
                conn.table("usuarios").insert({"email": ne, "senha": criptografar_senha(ns)}).execute()
                st.success("Conta criada! Vá em Entrar.")
            except:
                st.error("Erro ao cadastrar")
else:
    st.write(f"Bem-vindo, {st.session_state.usuario}")
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
