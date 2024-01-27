import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout="wide")


@st.cache_data
def get_fob_data():
    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    headers = {
        "x-params": "{\"frequency\":\"daily\",\"data\":[\"value\"],\"facets\":{\"series\":[\"RBRTE\"]},\"start\":null,\"end\":null,\"sort\":[{\"column\":\"period\",\"direction\":\"desc\"}],\"offset\":0,\"length\":5000}"
    }
    params = {
        "api_key": "3zjKYxV86AqtJWSRoAECir1wQFscVu6lxXnRVKG8"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def process_fob(data):
    df = pd.DataFrame(data['response']['data'])
    df.rename(columns={'period': 'Date', 'value': 'Value'}, inplace=True)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df = df[['Date', 'Value']]

    # Extraindo apenas o ano da data
    df['Year'] = df['Date'].dt.year

    # Extraindo mês e ano da data
    df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)

    # Média móvel simples de 7 dias
    df['SMA_7'] = df['Value'].rolling(window=7).mean()
    # Média móvel simples de 30 dias
    df['SMA_30'] = df['Value'].rolling(window=30).mean()

    # Desvio padrão móvel de 7 dias
    df['STD_7'] = df['Value'].rolling(window=7).std()
    # Desvio padrão móvel de 30 dias
    df['STD_30'] = df['Value'].rolling(window=30).std()

    # Mínimo móvel de 7 dias
    df['MIN_7'] = df['Value'].rolling(window=7).min()
    # Máximo móvel de 7 dias
    df['MAX_7'] = df['Value'].rolling(window=7).max()

    df = df.iloc[30:]

    # Removendo quaisquer linhas com 'Value' NaN, pois não podemos plotá-los
    df.dropna(subset=['Value'], inplace=True)

    return df


# Options Menu
st.sidebar.image("assets/logo.jpg")
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.title("Menu")

# Inicializa a variável de sessão se ainda não estiver definida
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = 'case'


def set_option(option):
    st.session_state.selected_option = option


st.sidebar.button('Apresentação do case', on_click=set_option, args=('case',))
st.sidebar.button('Petróleo Brent (FOB)', on_click=set_option, args=('brent',))
st.sidebar.button('Energia Renovável',
                  on_click=set_option, args=('renewable',))
st.sidebar.button('Estoque Petróleo', on_click=set_option, args=('stock',))
st.sidebar.button('Consumo Petróleo', on_click=set_option,
                  args=('consumption',))
st.sidebar.button('Predição Petróleo Brent',
                  on_click=set_option, args=('predict',))
st.sidebar.button('Tomada de decisão', on_click=set_option, args=('decision',))
st.sidebar.button('Sobre nós', on_click=set_option, args=('more',))


if st.session_state.selected_option == 'case':
    st.title("Predição do preço do petróleo bruto brent (FOB)")

    st.markdown("##### Foi proposto que fizemos a análise dos dados do preço do petróleo brent, criando um dashboard interativo que gere insights relevantes para tomada de decisão. Além disso desenvolvemos um modelo de Machine Learning para fazer o forecasting do preço do petróleo.")
    st.image("assets/header.jpg")
    st.markdown("Brent é uma sigla, que normalmente acompanha a cotação do petróleo e indica a origem do óleo e o mercado onde ele é negociado. O petróleo Brent foi batizado assim porque era extraído de uma base da Shell chamada Brent. Atualmente, a palavra Brent designa todo o petróleo extraído no Mar do Norte e comercializado na Bolsa de Londres.")

    st.markdown(
        "Os preços dependem principalmente do custo de produção e transporte.")

    st.markdown(
        "O petróleo Brent é produzido próximo ao mar, então os custos de transporte são significativamente menores.")

    st.markdown("O Brent tem uma qualidade menor, mas, se tornou um padrão do petróleo e tem maior preço por causa das exportações mais confiáveis.")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        "###### Para realização inicial da análise usamos as seguintes fontes: https://www.eia.gov, https://guru.com.vc/glossario/brent")

elif st.session_state.selected_option == 'brent':
    st.title("Analisando o preço do petróleo ao longo do tempo")

    st.markdown(
        "Para podermos começar a manipular os dados, precisamos entendê-los melhor, para isso vamos exibir nossos dados em forma de gráficos utilizando séries temporais.")

    fob_data = get_fob_data()
    df = process_fob(fob_data)

    # Criando um gráfico de linhas com Plotly
    fig = px.line(df, x='Date', y='Value',
                  title='Valores do petroleo brent FOB ao Longo do Tempo (Preço por Barril)')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Data',
                      yaxis_title='Valor (Preço por Barril)')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "###### Após esta análise podemos ver 3 grandes mudanças de preço nos períodos próximos a 2008, 2014 e 2020.")

    # ------------------------------------- Análise de 2008 ----------------------------------------------------------
    df_2008 = df[df['Year'] == 2008]
    df_2008["Periodos de 2008"] = df_2008["Date"]

    max_value_2008 = df_2008['Value'].max()
    min_value_2008 = df_2008['Value'].min()

    if min_value_2008 != 0:
        variacao_percentual = (
            (max_value_2008 - min_value_2008) / min_value_2008) * 100
        # Formatação para duas casas decimais
        variacao_percentual_texto = f"{variacao_percentual:.2f}%"
    else:
        variacao_percentual_texto = "Indefinido"

    # Exibindo a variação
    st.markdown(
        f"##### Período de 2008: Variação entre a máxima e mínima {variacao_percentual_texto}")

    col1, col2 = st.columns([3, 6])

    # Coluna 1: Tabela de descrição
    col1.markdown("<br>", unsafe_allow_html=True)  # Margem superior com HTML
    col1.markdown("<br>", unsafe_allow_html=True)  # Margem superior com HTML
    col1.write(df_2008[["Periodos de 2008", "Value"]].describe())

    # Criando um gráfico de linhas com Plotly
    fig = px.line(df_2008, x='Date', y='Value', line_shape='spline',
                  title='Valores do petroleo brent em 2008')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Data',
                      yaxis_title='Valor (Preço por Barril)')

    # Exibindo o gráfico
    col2.plotly_chart(fig, use_container_width=True)

    st.markdown("A crise de 2008 começou em razão da especulação imobiliária nos Estados Unidos. Foi a chamada bolha, causada por um aumento abusivo nos valores dos imóveis. Ao atingir preços bem acima do mercado, o setor acabou entrando em colapso, pois a supervalorização não foi acompanhada pela capacidade financeira dos cidadãos de arcar com os custos. Assim, as hipotecas acabaram não tendo a liquidez esperada, ou seja, houve uma quebra econômica em razão do aumento dos juros e da inflação.")

    st.markdown("A crise financeira global e a Grande Recessão que se seguiu tiveram um impacto negativo pronunciado no setor de petróleo e gás, uma vez que levou a uma queda acentuada nos preços do petróleo e gás e uma contração no crédito. A queda nos preços resultou em queda nas receitas das empresas de petróleo e gás. A crise financeira também levou a condições de crédito restritivas que resultaram em muitos exploradores e produtores pagando altas taxas de juros ao levantar capital, reduzindo assim os ganhos futuros.")

    # ------------------------------------- Análise de 2014      ----------------------------------------------------------
    df_2014 = df[df['Year'] == 2014]
    df_2014["Periodos de 2008"] = df_2014["Date"]

    max_value_2014 = df_2014['Value'].max()
    min_value_2014 = df_2014['Value'].min()

    if min_value_2014 != 0:
        variacao_percentual = (
            (max_value_2014 - min_value_2014) / min_value_2014) * 100
        # Formatação para duas casas decimais
        variacao_percentual_texto = f"{variacao_percentual:.2f}%"
    else:
        variacao_percentual_texto = "Indefinido"

    # Exibindo a variação
    st.markdown(
        f"##### Período de 2014: Variação entre a máxima e mínima {variacao_percentual_texto}")

    col1, col2 = st.columns([6, 3])

    # Coluna 1: Tabela de descrição
    col2.markdown("<br>", unsafe_allow_html=True)  # Margem superior com HTML
    col2.markdown("<br>", unsafe_allow_html=True)  # Margem superior com HTML
    col2.write(df_2008[["Periodos de 2008", "Value"]].describe())

    # Criando um gráfico de linhas com Plotly
    fig = px.line(df_2008, x='Date', y='Value', line_shape='spline',
                  title='Valores do petroleo brent em 2008')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Data',
                      yaxis_title='Valor (Preço por Barril)')

    # Exibindo o gráfico
    col1.plotly_chart(fig, use_container_width=True)

    st.markdown("")

    st.markdown("")

    # Criando um boxplot com Plotly
    fig = px.box(df, x='Year', y='Value', labels={'Year': 'Ano', 'Value': 'Valor'},
                 title='Boxplot dos Valores do Petróleo brent (FOB) por Ano')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Ano', yaxis_title='Valor')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)
