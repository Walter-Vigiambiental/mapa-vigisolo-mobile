import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# URL da planilha pública (CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4rNqe1-YHIaKxLgyEbhN0tNytQixaNJnVfcyI0PN6ajT0KXzIGlh_dBrWFs6R9QqCEJ_UTGp3KOmL/pub?gid=317759421&single=true&output=csv"

# Configuração da página
st.set_page_config(page_title="Mapa VigiSolo", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h2 style='text-align:center;'>🗺️ Mapa Áreas Programa VigiSolo</h2>", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv(sheet_url)
    df[['lat', 'lon']] = df['COORDENADAS'].str.split(', ', expand=True).astype(float)
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce', dayfirst=True)
    df['ANO'] = df['DATA'].dt.year
    df['MES'] = df['DATA'].dt.month
    return df

df = carregar_dados()

meses_nome = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# Inicializar estado da sessão
if "mostrar_mapa" not in st.session_state:
    st.session_state.mostrar_mapa = False

with st.expander("🔍 Filtros de busca"):
    anos = sorted(df['ANO'].dropna().unique())
    meses = sorted(df['MES'].dropna().unique())
    bairros = sorted(df['BAIRRO'].dropna().unique())
    contaminantes = sorted(df['CONTAMINANTES'].dropna().unique())

    ano = st.selectbox("Ano", ["Todos"] + list(anos), key="ano_filtro")
    mes_nome = st.selectbox("Mês", ["Todos"] + [meses_nome[m] for m in meses], key="mes_filtro")
    bairro = st.selectbox("Bairro", ["Todos"] + bairros, key="bairro_filtro")
    contaminante = st.selectbox("Contaminante", ["Todos"] + contaminantes, key="cont_filtro")

# Botão toggle para controlar exibição do mapa
exibir = st.checkbox("📍 Visualizar Mapa", value=st.session_state.mostrar_mapa)
st.session_state.mostrar_mapa = True

# Aplicar filtros
df_filtrado = df.copy()
if st.session_state.ano_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["ANO"] == st.session_state.ano_filtro]
if st.session_state.mes_filtro != "Todos":
    mes_num = [num for num, nome in meses_nome.items() if nome == st.session_state.mes_filtro][0]
    df_filtrado = df_filtrado[df_filtrado["MES"] == mes_num]
if st.session_state.bairro_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["BAIRRO"] == st.session_state.bairro_filtro]
if st.session_state.cont_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["CONTAMINANTES"] == st.session_state.cont_filtro]

# Criar mapa se checkbox estiver ativo
if st.session_state.mostrar_mapa:
    if not df_filtrado.empty:
        centro_mapa = df_filtrado[["lat", "lon"]].mean().tolist()
        m = folium.Map(location=centro_mapa, zoom_start=13, control_scale=True)
        cluster = MarkerCluster().add_to(m)

        for _, row in df_filtrado.iterrows():
            imagem_html = f'<br><img src="{row["URL_FOTO"]}" width="220">' if pd.notna(row.get("URL_FOTO")) else ""
            popup_text = (
                f"<strong>{row['DENOMINAÇÃO DA ÁREA']}</strong><br>"
                f"Bairro: {row['BAIRRO']}<br>"
                f"Contaminantes: {row['CONTAMINANTES']}<br>"
                f"População Exposta: {row['POPULAÇÃO EXPOSTA']}<br>"
                f"Data: {row['DATA'].date()}<br>"
                f"{imagem_html}"
            )

            risco = str(row['POPULAÇÃO EXPOSTA']).lower()
            cor_icon = (
                "darkred" if "alta" in risco else
                "orange" if "média" in risco or "media" in risco else
                "green" if "baixa" in risco else "gray"
            )

            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_text, max_width=280),
                icon=folium.Icon(color=cor_icon, icon="info-sign"),
            ).add_to(cluster)

        st_folium(m, width="100%", height=500)
    else:
        st.warning("🙁 Nenhum dado encontrado com os filtros aplicados.")

# Rodapé
st.markdown("<p style='text-align:center; font-size:14px;'>Desenvolvido por Walter alves</p>", unsafe_allow_html=True)
