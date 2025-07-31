import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Mapa Interativo", layout="wide")

st.title("🌍 Visualização de Mapa Interativo")

# Inicializa estado
if "mostrar_mapa" not in st.session_state:
    st.session_state.mostrar_mapa = False

# Botão para ativar o mapa
if st.button("📍 Visualizar Mapa"):
    st.session_state.mostrar_mapa = True

# Renderiza o mapa apenas quando o botão for clicado
if st.session_state.mostrar_mapa:
    st.subheader("🗺️ Mapa Centralizado")
    m = folium.Map(location=[-15.775, -47.797], zoom_start=4)
    folium.Marker(
        location=[-15.775, -47.797],
        popup="Ponto Central",
        icon=folium.Icon(color="green")
    ).add_to(m)

    # Renderiza sem capturar output — evita reexecuções
    st_folium(m, width="100%", height=500)

# Espaço adicional para conteúdo futuro
st.markdown("---")
st.info("Esse mapa não será reatualizado durante interações. Para reiniciar, atualize a página.")
