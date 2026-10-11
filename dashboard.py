#importar as bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard Análise de vendas de Chocolates",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("dados_tratados.csv", sep =",")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# 📅 filtro por período
anos_disponiveis = sorted(df["Ano"].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# 🌎 filtro por país
paises_disponiveis = sorted(df["País"].unique())
paises_selecionados = st.sidebar.multiselect("País", paises_disponiveis, default=paises_disponiveis)

# 🍫 filtro por produto
produtos_disponiveis = sorted(df["Produto"].unique())
produtos_selecionados = st.sidebar.multiselect("Produto", produtos_disponiveis, default=produtos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['Ano'].isin(anos_selecionados)) &
    (df['País'].isin(paises_selecionados)) &
    (df['Produto'].isin(produtos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🍫 Dashboard de Análise de Vendas de Chocolate")
st.markdown("Explore os dados das vendas dos produtos nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# 📊 KPIs no topo
st.subheader("Métricas gerais ")

if not df_filtrado.empty:
    # Faturamento Total
    faturamento_total = df_filtrado["Valor"].sum()
    # Quantidade Vendida
    quantidade_vendida_caixas = df_filtrado["Caixas Enviadas"].sum()
    # Ticket Médio
    ticket_medio = (df_filtrado["Valor"].sum()/ df_filtrado["Caixas Enviadas"].sum())
    # Crescimento (%)
    crescimento =  (
        df_filtrado["Valor"].sum() /
        df_filtrado["Valor"].iloc[0] - 1) * 100
else:
    faturamento_total, quantidade_vendida, ticket_medio, crescimento= 0,0,0,0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento total", f"${faturamento_total:,.0f}")
col2.metric("Quantidade vendida de Caixas", f"{quantidade_vendida_caixas:,.0f}")
col3.metric("Ticket Médio", f"${ticket_medio:,.2f}")
col4.metric("Crescimento (%)", f"{crescimento:,.2f}%")

st.markdown("---")
#gráficos
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)
# 📈 evolução das vendas(faturamento por mes)
with col_graf1:
    if not df_filtrado.empty:
        grafico_bar = px.bar(
            df_filtrado,
            x ="Mes" , 
            y="Valor",
            title= "Evolução das vendas( Mês x Faturamento)",
            labels= {'Mes': 'Mes', 'Valor': 'Faturamento'},
        )
        grafico_bar.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_bar, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico.")

# 📦 vendas por produto(quantidade vendida)
with col_graf2:
    if not df_filtrado.empty:
        df_vendas_produto = df_filtrado.groupby("Produto")["Caixas Enviadas"].sum().sort_values(ascending=False).reset_index()
        grafico_bar2 = px.bar(
            df_vendas_produto,
            x= "Produto",
            y="Caixas Enviadas",
            title= "Vendas por produto( Produto x Caixas Enviadas)",
            labels= {'Produto': 'Produto', 'Caixas Enviadas': 'Caixas Enviadas'},
            )
        grafico_bar2.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_bar2, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico.")

col_graf3, col_graf4 = st.columns(2)
# 🌍 mapa de vendas (vendas por localização)
with col_graf3:
    if not df_filtrado.empty:
        mapa_iso = {
    "Austrália": "AUS",
    "Canadá": "CAN",
    "EUA": "USA",
    "Nova Zelândia": "NZL",
    "Reino Unido": "GBR",
    "Índia": "IND"
}
        df_filtrado["ISO3"] = df_filtrado["País"].map(mapa_iso)
        faturamento_por_pais = df_filtrado.groupby(["País", "ISO3"])["Valor"].sum().reset_index()

        grafico_ranking = px.choropleth(
            faturamento_por_pais,
            locations= "ISO3",
            color="Valor",
            hover_name="País",
            color_continuous_scale="RdYlGn",
            title="Países que mais realizam compras",
            labels={"País": "País", "Valor": "Faturamento"}
        )

        grafico_ranking.update_layout(title_x=0.1)
        st.plotly_chart(grafico_ranking,use_container_width=True)

    else:
        st.warning("Nenhum dado para exibir no gráfico.")

 # 📊 ranking dos produtos(faturamento)
with col_graf4:
    if not df_filtrado.empty:
        faturamento_produto = df_filtrado.groupby("Produto")["Valor"].sum().nlargest(5).sort_values(ascending = True).reset_index()
        grafico_ranking= px.bar(
            faturamento_produto,
            x="Valor",
            y="Produto",
            orientation='h',
            title="Top 5 produtos por faturamento",
            labels={'Produto': 'Produto', 'Valor': 'Faturamento'}
        )

        grafico_ranking.update_layout(title_x=0.1)
        st.plotly_chart(grafico_ranking,use_container_width=True)

    else:
        st.warning("Nenhum dado para exibir no gráfico.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)