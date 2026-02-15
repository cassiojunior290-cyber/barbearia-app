import streamlit as st
from st_supabase_connection import SupabaseConnection

st.title("💈 BarberPro - Sistema de Agendamento")

# Conexão direta
try:
    conn = st.connection("supabase", type=SupabaseConnection)
    st.success("✅ Conectado ao Banco de Dados!")
    
    email = st.text_input("Seu e-mail para teste")
    if st.button("Salvar Teste"):
        conn.table("usuarios").insert({"email": email, "senha": "123"}).execute()
        st.write("E-mail salvo no Supabase!")
except Exception as e:
    st.error(f"Erro de configuração: {e}")
