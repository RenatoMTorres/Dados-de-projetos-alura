import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
st.sidebar.header("🔍 Filtros")
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)
cargos_disponiveis = sorted(df['cargo'].unique())
cargos_selecionados = st.sidebar.multiselect('cargo', cargos_disponiveis, default=[])
# Monta a máscara de filtros (a seleção de cargo NÃO afetará os filtros globais)
mask = (
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
)

df_filtrado = df[mask]

st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")
st.subheader("Métricas gerais (Salário anual em USD)")
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")
st.subheader("Gráficos")
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
            color='usd',
            color_continuous_scale=px.colors.sequential.Reds
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''},
        )
        grafico_hist.update_layout(title_x=0.1)
        grafico_hist.update_traces(marker_color="#00ffd5")
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color='quantidade',
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

# Prepara os dados limpos a partir dos filtros aplicados (cargo não afeta os filtros globais)
df_limpo = df_filtrado.dropna(subset=['empresa', 'usd']).copy()
df_limpo = df_limpo.assign(ano = df_limpo['ano'].astype('int64'))
# Aplica filtro de cargo apenas para o gráfico de empresas (col_graf4)
if cargos_selecionados:
    df_para_grafico = df_limpo[df_limpo['cargo'].isin(cargos_selecionados)].copy()
else:
    df_para_grafico = df_limpo

# Agrupa por empresa usando os cargos selecionados (se houver)
df_media_salarial_por_pais = (
    df_para_grafico.groupby('empresa')['usd']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

# Título dinâmico de acordo com os cargos selecionados
if cargos_selecionados:
    cargos_title = ', '.join(cargos_selecionados[:3]) + (', ...' if len(cargos_selecionados) > 3 else '')
    chart_title = f"Média Salarial por Empresa para: {cargos_title}"
else:
    chart_title = "Média Salarial por Empresa (Todos os cargos)"

with col_graf4:
    # Mostra o gráfico apenas se houver dados filtrados
    if not df_media_salarial_por_pais.empty:
        fig = px.bar(
            df_media_salarial_por_pais,
            x='empresa',
            y='usd',
            hover_data=['empresa', 'usd'],
            labels={'empresa': 'Empresa', 'usd': 'Média Salarial Anual (USD)'},
            title=chart_title,
            color='usd',  # Usa a coluna 'usd' para definir a cor em degradê
            color_continuous_scale=px.colors.sequential.Greens,
        )
        fig.update_layout(
            width=760,
            height=500,
            plot_bgcolor='black',
            paper_bgcolor='darkgray',
            coloraxis_colorbar_title_text=''
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de empresas para os cargos selecionados.")
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
     







