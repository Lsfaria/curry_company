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
import numpy as np
from datetime import datetime

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )

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


def distance(df1, fig):
    ''' Esta função calcula a distância média dos locais de entrega.
        Parâmetros:
           Input:
                - df: Dataframe com os dados necessários para o cálculo
                - fig: Tipo de resposta que solicitada
                    'False': Para receber a distância média entre os restaurantes e os locais de entrega
                    'True': para classificar a distância média entre os restaurantes e os locais de entrega por cidade e devolver um gráfico de pizza
                    
            Output:
                -df: Dataframe com 2 colunas e 1 linha
    
    '''
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude',  'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                        haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

        avg_distance = np.round( df1['distance'].mean(), 2 )
        return avg_distance
        
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                    haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

        return fig
    

def avg_std_time_delivery(df1, festival, op):
    ''' Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - festival: Yes ou No de acordo com o filtro desejado
                - op: tipo de operação que precisa ser calculado
                
                    'Yes': Se estiver em períodode festival
                    'No': Se não estiver em período de festival
                    'avg_time': Calcula o tempo médio 
                    'std_time': Calcula o desvio padrão do tempo'
                    
            Output:
                -df: Dataframe com 2 colunas e 1 linha
    
    '''
    df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                 .groupby('Festival')
                 .agg( {'Time_taken(min)' : ['mean', 'std' ]}))


    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linhas_selecionadas, op], 2)
    
            
    return df_aux


def std_time_graph(df1):
    ''' Esta função calcula o tempo médio e o desvio padrão do tempo de entrega por cidade.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                    
            Output:
                -fig: gráfico de barras
    
    '''
                
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City']]
                 .groupby('City')
                 .agg( {'Time_taken(min)' : ['mean', 'std' ]}))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name= 'Control', x = df_aux['City'],
                                            y = df_aux['avg_time'], 
                                            error_y = dict( type = 'data', array = df_aux['std_time'])))
    fig.update_layout(barmode='group')
            
    return fig


def avg_std_time_on_traffic( df1 ):
    ''' Esta função calcula o tempo médio e o desvio padrão do tempo de entrega por cidade e por tipo de tráfego
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                    
            Output:
                -fig: gráfico sunburst
    
    '''
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time'] ) )

    return fig

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

st.header('Market Place - Visão Restaurante')

image_path = 'logo.png'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( ' # Curry Company' )
st.sidebar.markdown( ' ## Fastest Delivery in Town' )
st.sidebar.markdown("""___""")

st.sidebar.markdown( ' ## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime (2022, 4, 13 ),
    min_value=datetime(2022, 2, 11 ),
    max_value =datetime(2022, 4, 6 ),
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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        delivery_unique = len(df1.loc[:,'Delivery_person_ID' ].unique())
        col1.metric( 'Entregadores', delivery_unique)

    with col2:

        avg_distance = distance(df1, fig = False)
        col2.metric( 'Distância média', avg_distance )


    with col3:
        df_aux=avg_std_time_delivery(df1, 'Yes', 'avg_time')
        col3.metric(' Tempo médio (f)', df_aux)

    with col4:
        df_aux=avg_std_time_delivery(df1, 'Yes', 'std_time')
        col4.metric('STD entrega (f)', df_aux)

    with col5:
        df_aux=avg_std_time_delivery(df1, 'No', 'avg_time')
        col5.metric('Tempo médio', df_aux)

    with col6:
        df_aux=avg_std_time_delivery(df1, 'No', 'std_time')
        col6.metric('STD entrega', df_aux)



with st.container():
    st.markdown('''___''')
    st.markdown('###  Tempo médio e desvio padrão de entrega por cidade')

    col1, col2 = st.columns(2)

    with col1:

        fig = std_time_graph (df1)
        st.plotly_chart(fig, use_container_width = True )

    with col2:
        df_aux = (df1.loc[:, ['Time_taken(min)', 'City','Type_of_order']]
                     .groupby(['City','Type_of_order'])
                     .agg( {'Time_taken(min)' : ['mean', 'std' ]}))

        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)

with st.container():
    st.markdown('''___''')
    st.markdown('### Distribuição do tempo')

    col1, col2 = st.columns(2)

    with col1:
        fig = distance(df1, fig=True)
        st.plotly_chart(fig, use_container_width = True )

    with col2:
        fig = avg_std_time_on_traffic(df1)
        st.plotly_chart(fig, use_container_width = True )