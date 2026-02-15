import streamlit as st
from st_supabase_connection import SupabaseConnection
import hashlib

# Configuração da página
st.set_page_config(page_title="BarberPro", page_icon="💈")

# Conexão Forçada (Pega direto dos Secrets)
try:
    conn = st.connection(
        "supabase",
        type=SupabaseConnection,
        url=st.secrets["SUPABASE_URL"],
        key=st.secrets["SUPABASE_KEY"]
    )
except Exception as e:
    st.error("Erro ao carregar segredos. Verifique os Secrets no Streamlit.")
    st.stop()

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

st.title("💈 BarberPro")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            sh = criptografar_senha(senha)
            user = conn.table("usuarios").select("*").eq("email", email).eq("senha", sh).execute()
            if user.data:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Login inválido.")
    
    with tab2:
        n_email = st.text_input("Novo Email")
        n_senha = st.text_input("Nova Senha", type="password")
        if st.button("Criar Conta"):
            try:
                conn.table("usuarios").insert({"email": n_email, "senha": criptografar_senha(n_senha)}).execute()
                st.success("Conta criada! Vá em Entrar.")
            except:
                st.error("Este email já existe.")

else:
    st.success(f"Logado como: {st.session_state.usuario}")
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
