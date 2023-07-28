# libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )

#-----------------------------
# Funções
#-----------------------------
def clean_code( df1 ):
    '''Esta função tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados Nan
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto de variável numérica)
    
    Input: Dataframe
    Output: Dataframe
    '''
    #Retirando espaços 
    df1['Delivery_person_Age'] = df['Delivery_person_Age'].str.strip()
    df1['Weatherconditions'] = df['Weatherconditions'].str.strip()
    df1['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    df1['City'] = df['City'].str.strip()
    df1['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
    df1['Type_of_order'] = df['Type_of_order'].str.strip()
    df1['Festival'] = df['Festival'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]

    # Limpando a coluna de time taken
    #uso o split a partir do '(min) '

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split() [1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1



def top_delivers(df1, top_asc):
    '''Esta função ordena os 10 entregadores mais rápidos/lentos de cada cidade..
    
    
    Input:   - df: Dataframe com os dados necessários para o cálculo
    Output:  - df: Dataframe com 3 colunas e 30 linhas
    '''
    
            
    df2 = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
              .groupby(['Delivery_person_ID','City'])
              .mean()
              .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
              .reset_index())
            
    df_aux01 =  df2.loc[df2['City'] == 'Metropolitian', : ].head(10)
    df_aux02 =  df2.loc[df2['City'] == 'Urban', : ].head(10)
    df_aux03 =  df2.loc[df2['City'] == 'Semi-Urban', : ].head(10)

    df3 =pd.concat([df_aux01,df_aux02,df_aux03 ]).reset_index(drop = True)
                
    return df3
#----------------------------------Início da estrutura lógica do código ------------------------------------------------
#----------------------
# Importando os dados
#----------------------
df = pd.read_csv('train.csv')

#----------------------
# Limpando os dados
#----------------------
df1 = clean_code(df)

# ==========================================================================
# Barra lateral
# ==========================================================================

st.header('Market Place - Visão Entregadores')

image_path = 'logo.png'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( ' # Curry Company' )
st.sidebar.markdown( ' ## Fastest Delivery in Town' )
st.sidebar.markdown("""___""")

st.sidebar.markdown( ' ## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime (2022, 4, 13 ),
    min_value=pd.datetime(2022, 2, 11 ),
    max_value = pd.datetime(2022, 4, 6 ),
    format ='DD-MM-YYYY' )


#st.header( date_slider )
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect( 'Quais as condições do trânsito', ['Low', 'Medium', 'High', 'Jam'],
                                         default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered bu Comunidade DS' )

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


# ==========================================================================
# Layout no Streamlit
# ==========================================================================

st.markdown('Visão Gerencial')

with st.container():
    st.title('Overall Metrics')
    col1, col2, col3, col4 = st.columns(4, gap = 'large') 

    with col1:
        # A maior idade dos entregadores
        maior_idade = df1.loc[:,"Delivery_person_Age"].max()
        col1.metric('Maior idade', maior_idade) 

    with col2:
        # A menor idade dos entregadores
        menor_idade = df1.loc[:,"Delivery_person_Age"].min()
        col2.metric('Menor idade', menor_idade)

    with col3:
        # Melhor condição de veiculo
        melhor_condicao = df1.loc[:,"Vehicle_condition"].max()
        col3.metric('Melhor Condição', melhor_condicao)

    with col4:
        # Pior condição de veiculo
        pior_condicao = df1.loc[:,"Vehicle_condition"].min()
        col4.metric('Pior Condção', pior_condicao)

with st.container():
    st.markdown ( '''___''' )
    st.title ( 'Avaliações' )
    col1, col2 = st.columns (2)

    with col1:
        st.markdown ('##### Avaliações médias por entregador')
        df_avg_ratings_by_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                        .groupby('Delivery_person_ID')
                                        .mean()
                                        .reset_index())

        st.dataframe( df_avg_ratings_by_deliver )



    with col2:
        st.markdown ('##### Avaliação média por trânsito')
        df_avg_rating_by_traffic = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                                       .groupby('Road_traffic_density')
                                       .agg( {'Delivery_person_Ratings' : ['mean', 'std' ]}))

        # mudança de nome das colunas
        df_avg_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
        df_avg_rating_by_traffic = df_avg_rating_by_traffic.reset_index()

        st.dataframe( df_avg_rating_by_traffic )


        st.markdown ('##### Avaliação média por clima')


        df_avg_rating_by_weather = (df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                                       .groupby('Weatherconditions')
                                       .agg( {'Delivery_person_Ratings' : ['mean', 'std' ]}))
        df_avg_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
        df_avg_rating_by_weather = df_avg_rating_by_weather.reset_index()

        st.dataframe ( df_avg_rating_by_weather )

with st.container():
    st.markdown('''___''')
    st.title ('Velocidade de Entrega')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown ( '##### Top Entregadores mais rápidos')
        df3 = top_delivers(df1, top_asc=True)
        st.dataframe (df3)


    with col2:
        st.markdown ( '##### Top Entregadores mais lentos')
        df3 = top_delivers(df1, top_asc=False)
        st.dataframe (df3)