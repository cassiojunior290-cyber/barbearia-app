import streamlit as st
from st_supabase_connection import SupabaseConnection

st.title("Teste de Conexão")

try:
    conn = st.connection("supabase", type=SupabaseConnection)
    st.success("Conectado ao Supabase com sucesso!")
except Exception as e:
    st.error(f"Erro detalhado: {e}")
