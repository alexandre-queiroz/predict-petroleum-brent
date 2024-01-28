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


def get_renewable_energy_data():
    url = "https://api.eia.gov/v2/international/data/"
    headers = {
        "x-params": '{"frequency":"annual","data":["value"],"facets":{"activityId":["1","12"],"productId":["2","29"],"countryRegionId":["WORL"],"unit":["BKWH"]},"start":"2000","end":null,"sort":[{"column":"period","direction":"desc"}],"offset":0,"length":5000}'
    }
    params = {
        "api_key": "3zjKYxV86AqtJWSRoAECir1wQFscVu6lxXnRVKG8"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


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
        "###### Para realização desta análise inicial usamos as seguintes fontes: https://www.eia.gov, https://guru.com.vc/glossario/brent")

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
        "##### Após esta análise podemos ver algumas grandes mudanças de preço nos períodos próximos a 2008, 2011, 2014, 2020 e 2022, vamos entender um pouco mais sobre os motivs dessas grandes variações de preço.")
    st.markdown("<br>", unsafe_allow_html=True)

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

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------- Análise de 2014      ----------------------------------------------------------
    df_2014 = df[df['Year'] == 2014]
    df_2014["Periodos de 2014"] = df_2014["Date"]

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
    col2.write(df_2014[["Periodos de 2014", "Value"]].describe())

    # Criando um gráfico de linhas com Plotly
    fig = px.line(df_2014, x='Date', y='Value', line_shape='spline',
                  title='Valores do petroleo brent em 2014')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Data',
                      yaxis_title='Valor (Preço por Barril)')

    # Exibindo o gráfico
    col1.plotly_chart(fig, use_container_width=True)

    st.markdown("A queda do preço do petróleo em 2014 foi influenciada por vários fatores, incluindo o aumento da produção de petróleo, especialmente nas áreas de xisto dos EUA, e uma demanda menor do que a esperada na Europa e na Ásia. Em novembro do mesmo ano, essa queda se acentuou, diante do excesso de oferta e da recusa dos países da Organização dos Países Exportadores de Petróleo (Opep) em reduzir seu teto de produção, independentemente do preço no mercado internacional. A Opep culpa a grande produção de óleo de xisto pelas baixas cotações da commodity e, segundo alguns analistas, estaria disposta a aceitar um preço ainda mais baixo para tirar do mercado outros produtores ou inviabilizar a exploração de rivais como os produtores norte-americanos.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------- Análise de 2020      ----------------------------------------------------------
    df_2020 = df[df['Year'] == 2020]
    df_2020["Periodos de 2020"] = df_2020["Date"]

    max_value_2020 = df_2020['Value'].max()
    min_value_2020 = df_2020['Value'].min()

    if min_value_2020 != 0:
        variacao_percentual = (
            (max_value_2020 - min_value_2020) / min_value_2020) * 100
        # Formatação para duas casas decimais
        variacao_percentual_texto = f"{variacao_percentual:.2f}%"
    else:
        variacao_percentual_texto = "Indefinido"

    # Exibindo a variação
    st.markdown(
        f"##### Período de 2020: Variação entre a máxima e mínima {variacao_percentual_texto}")

    col1, col2 = st.columns([3, 6])

    # Coluna 1: Tabela de descrição
    col1.markdown("<br>", unsafe_allow_html=True)  # Margem superior com HTML
    col1.markdown("<br>", unsafe_allow_html=True)  # Margem superior com HTML
    col1.write(df_2020[["Periodos de 2020", "Value"]].describe())

    # Criando um gráfico de linhas com Plotly
    fig = px.line(df_2020, x='Date', y='Value', line_shape='spline',
                  title='Valores do petroleo brent em 2020')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Data',
                      yaxis_title='Valor (Preço por Barril)')

    # Exibindo o gráfico
    col2.plotly_chart(fig, use_container_width=True)

    texto = """
    A crise de 2020 entre a Arábia Saudita e a Rússia foi uma queda de braço no mercado do petróleo que causou a maior queda no preço do barril desde 1991, quando Estados Unidos e aliados bombardeavam o Iraque na Guerra do Golfo. A tensão entre os países fez bolsas globais derreterem. Por trás dessa crise, está um xadrez geopolítico complexo e que vai além do petróleo. 

    O temor relacionado à provável diminuição da oferta por conta de conflitos na região fez os preços do barril de Brent (negociado na Opep, entre países europeus e asiáticos e pela Petrobras) saltarem 3,55% no dia 03 de janeiro, passando de US 66,25 para US 68,60.

    A história começa com a tentativa saudita de fazer com que os países da Opep (Organização dos Países Exportadores de Petróleo), aliança da qual o reino é líder informal, cortassem a produção diária de barris de petróleo em 1,5 milhão de barris até o final do ano. O plano era diminuir a oferta para conter a queda nos preços, diante da expectativa de redução no consumo de petróleo mundo afora. Os russos não toparam, rompendo uma união que por anos controlou esse mercado. Para retaliar, os sauditas decidiram fazer o inverso: aumentaram a produção e baixaram drasticamente os preços. “Os russos produzem muito petróleo (cerca de 10 milhões de barris por dia) e ganham dinheiro com a escala da operação.

    Coronavírus e tensão entre Arábia Saudita e Rússia:

    Conforme a covid-19 avançava pelo mundo e obrigava nações a entrarem em isolamento social, o consumo de combustíveis diminuía. Com isso, a demanda por petróleo também enfrentou uma baixa drástica.
    """

    st.markdown(texto)

    # Criando um boxplot com Plotly
    fig = px.box(df, x='Year', y='Value', labels={'Year': 'Ano', 'Value': 'Valor'},
                 title='Boxplot dos Valores do Petróleo brent (FOB) por Ano')

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Ano', yaxis_title='Valor')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        "###### Para realização desta análise do preço do petróleo brent usamos as seguintes fontes:\n"
        "https://www.eia.gov, https://blog.stoodi.com.br/blog/historia/crise-de-2008, "
        "https://economiaenegocios.com/como-a-crise-financeira-de-2008-afetou-o-setor-de-petroleo-e-gas, "
        "https://exame.com/mundo/o-que-esta-por-tras-da-queda-de-braco-entre-arabia-saudita-e-russia, "
        "https://einvestidor.estadao.com.br/investimentos/preco-petroleo-2020, "
        "https://blog.stoodi.com.br/blog/historia/crise-do-petroleo-o-que-foi, "
        "https://epoca.oglobo.globo.com/tempo/noticia/2015/01/entenda-os-motivos-para-bqueda-do-preco-do-petroleob.html, "
        "https://g1.globo.com/economia/noticia/2015/01/entenda-queda-do-preco-do-petroleo-e-seus-efeitos.html"
    )

elif st.session_state.selected_option == 'renewable':
    st.title("Analisando o crescimento da energia renovável")

    st.markdown(
        "Um ponto interessante que podemos analisar é o crescimento das fontes de energia renovável e seu impacto no consumo/preço do petróleo.")

    renewable_data = get_renewable_energy_data()
    df2 = pd.DataFrame(renewable_data['response']['data'])
    df2 = df2[["period", "productName", "value"]]
    df2['value'] = pd.to_numeric(df2['value'], errors='coerce')

    # Supondo que df2 seja o seu DataFrame e que ele contenha as colunas 'period', 'value' e 'productName'
    # Separando os dados para "Renewables" e "Electricity"
    df_renewables = df2[df2['productName'] == 'Renewables']
    df_electricity = df2[df2['productName'] == 'Electricity']

    # Juntando os dados com base no 'period'
    merged_df = pd.merge(df_renewables, df_electricity,
                         on='period', suffixes=('_renew', '_elec'))

    # Calculando a porcentagem de "Renewables" em relação a "Electricity" para cada período
    merged_df['renewable_percentage'] = (
        merged_df['value_renew'] / merged_df['value_elec']) * 100

    # Agora, você pode adicionar esta porcentagem ao seu DataFrame original para uso no gráfico
    # Por simplicidade, vou adicionar apenas a 'percentage' de volta ao df2, mas você pode ajustar conforme necessário
    df2 = pd.merge(
        df2, merged_df[['period', 'renewable_percentage']], on='period', how='left')

    fig = px.line(df2, x='period', y='value', color='productName',
                  title='Consumo de energia ao longo do tempo por Produto (BKWH)',
                  hover_data={'renewable_percentage': ':.2f'})

    # Personalizando o layout do gráfico
    fig.update_layout(xaxis_title='Data', yaxis_title='Valor',
                      legend_title='Produto')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Antes de iniciar a avaliação do impacto da energia renovável ao preço do petróleo, vamos entender o que é energia renovável.\n"
                "Quando falamos de energia, falamos da energia elétrica, ou da eletricidade, utilizada no nosso quotidiano, e quando a qualificamos como renovável, dizemos que esta fonte de energia é renovada rapidamente pela natureza.\n"
                "Ou seja, uma fonte de energia renovável é aquela reposta tão ou mais rapidamente do que a podemos consumir. Dessa forma, não estamos a extrair da natureza mais do que ela nos possa dar. Pelo contrário: é uma lógica de consumo sustentável. E atenção: não apenas extraímos menos recursos, como extraímos recursos melhores, que não agridem o planeta.\n\n"
                "##### Os 7 tipos de energia renovável conhecidos até ao momento:\n"
                "* Energia Solar: Energia renovável obtida através da transformação da energia luminosa do sol em elétrica. \n"
                "* Energia Eólica: Tipo de energia renovável obtida através da transformação da energia cinética dos ventos em elétrica.\n"
                "* Energia Hidráulica: Modalidade de energia renovável obtida através da transformação da energia cinética dos cursos de água em elétrica.\n"
                "* Energia Geotérmica: Energia renovável obtida através da transformação da energia térmica das águas quentes e vapores do interior da Terra em elétrica.\n"
                "* Energia Maremotriz: Tipo de energia renovável obtida através da transformação da energia cinética das ondas e marés em elétrica.\n"
                "* Energia do Hidrogénio: Energia obtida a partir da combinação entre o hidrogénio e o oxigénio, que liberta energia térmica, posteriormente convertida em eletricidade.\n"
                "* Biomassa: Energia obtida durante a transformação de derivados de organismos vivos para a produção de energia calorífica, que é de seguida convertida em elétrica.\n"
                "\n\n"
                "##### E como a energia renovável pode afetar o preço do petróleo?\n\n"
                "A consequência imediata da redução no preço do barril do petróleo é o crescimento da demanda por combustíveis fósseis e fontes de energia proveniente do petróleo, porém, existem outros efeitos desastrosos a longo prazo, tais como os impactos nos investimentos em geração de energia renováveis, pois a energia é uma commodity, e os consumidores não querem pagar mais caro pela energia, estes desejam energia sustentável com baixa emissão de gases de efeito estufa (GEEs), mas com preço baixos.\n\n"
                "É importante salientar que o preço do petróleo é balizador do preço da energia, ou seja, quanto menor o preço do petróleo menor o preço da energia, diminuindo as taxas de retorno dos projetos em energia, incluindo os projetos de energia renováveis.\n\n"
                "A deterioração do preço do petróleo deve continuar, pois recentemente as sanções comerciais ao Irã (7º maior produtor do mundo) se encerram, criando mais excedente de petróleo.\n\n"
                "Esse cenário vem impactando às ações de empresas de energia listadas na FTSE e NYSE e levantando dúvidas sobre a capacidade de endividamento e a viabilidade de novos projetos de energia, principalmente, a energias renováveis.\n\n"
                "E como está o consumo de energia do petróleo x consumo de energia renovável atualmente?\n\n"
                "O Relatório de Estado Global de Energias Renováveis ​​2022 da REN21 (GSR 2022) declara que a transição global para energia limpa não está a acontecer, tornando improvável que o mundo seja capaz de cumprir metas climáticas críticas nesta década.\n\n"
                "“Ainda que muitos outros governos se comprometam com zero emissões de gases de efeito estufa em 2021, a realidade é que, em resposta à crise energética, a maioria dos países voltou a utilizar novas fontes de combustíveis fósseis e a queimar ainda mais carvão, petróleo e gás natural”, declarou Rana Adib, Directora Executiva da REN21.\n\n"
                "O GSR faz anualmente um balanço da implantação de energia renovável em todo o mundo. O relatório de 2022 é a 17ª edição consecutiva e comprova o que os especialistas têm alertado: a participação geral das energias renováveis ​​no consumo final de energia do mundo estagnou – subindo apenas de 8,7% em 2009 para 11,7% em 2019 – e o crescimento global a mudança do sistema energético para as energias renováveis ​​não está a acontecer.\n\n"
                "No sector de electricidade, foram atingidos valores recorde em capacidade de energia renovável (314,5 gigawatts, 17% acima de 2020) e geração (7.793 terawatts-hora) não conseguiram corresponder ao aumento geral no consumo de electricidade de 6%. No aquecimento e arrefecimento, a quota de energias renováveis ​​no consumo final de energia aumentou de 8,9% em 2009 para 11,2% em 2019. No sector dos transportes, onde a quota de energias renováveis ​​passou de 2,4% em 2009 para 3,7% em 2019, a falta de progressos é particularmente preocupante, já que o sector responde por quase um terço do consumo global de energia.\n\n"
                "\n\n"
                "##### Qual a previsão sobre o uso das Energias Renovaveis?\n\n"
                "A geração de energia por meio da luz solar cresceu 12% no mundo e, segundo a Agência Internacional de Energia (IEA), esse progresso não deve parar. Muito pelo contrário, visto que diversos países pretendem investir em fontes renováveis com o intuito de reduzir substancialmente a emissão de carbono durante a próxima década.\n\n"
                "Por conta disso, a tendência é que o uso primário de energias renováveis cresça em torno de 60% nos próximos 30 anos. Segundo a multinacional British Petroleum, esse aumento será uma resposta inevitável à queda das fontes que dependem de combustíveis fósseis.\n\n"
                "Não é à toa que a empresa investiu mais de um bilhão de dólares em usinas de energia eólica dos Estados Unidos. Uma decisão estratégica que não ignora a força ainda maior que a energia renovável terá no futuro.")
