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

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

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


def order_metric( df1 ):
            '''Esta função separa a quantidade de pedidos pela data e devolve um gráfico de barras.
    
    
            Input: Dataframe
            Output: fig: gráfico de barras
            '''
            #Order metric
            cols = ['ID', 'Order_Date' ]
            # seleção de linhas 
            df_aux = (df1.loc[:, cols]
                         .groupby( 'Order_Date' )
                         .count()
                         .reset_index())
            df_aux.columns = ['order_date', 'qtde_entregas'] 
            # desenhar o gráfico
            fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
            
            return fig
        
def traffic_order_share( df1 ):
            '''Esta função faz a distribuição de pedidos de acordo com o tipo de tráfego e devolve um gráfico de pizza.
    
    
            Input: Dataframe
            Output: fig: gráfico de pizza
            '''
            #distribuição por tráfego
            #seleção de colunas
            cols = ['ID', 'Road_traffic_density']
            # seleção de linhas 
            df_aux = (df1.loc[:, cols]
                         .groupby( 'Road_traffic_density' )
                         .count()
                         .reset_index())
            df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )

            # desenhar o gráfico 
            fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
            
            return fig
        
def traffic_order_city( df1 ):
            '''Esta função faz a comparação de pedidos por cidade e de acordo com o tipo de tráfego e devolve um gráfico de bolhas.


            Input: Dataframe
            Output: fig: gráfico de bolhas
            '''
            # # Comparação do volume de pedidos por cidade e tipo de tráfego
            #seleção de colunas
            cols = ['ID', 'Road_traffic_density', 'City' ]
            # seleção de linhas
            df_aux = (df1.loc[:, cols]
                         .groupby( ['Road_traffic_density','City'] )
                         .count()
                         .reset_index())

            # gráfico
            fig = px.scatter( df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City' )
            
            return fig
        

def order_by_week( df1 ):
            '''Esta função separa a quantidade de pedidos por semana e devolve um gráfico de linha.


            Input: Dataframe
            Output: fig: gráfico de linha
            '''
            
            # Quantidade de pedidos por Semana
            
            #Criação  da coluna da semana      
            df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
            #seleção de colunas
            cols = ['ID', 'week_of_year']
            #seleção de linhas
            df_aux = (df1.loc[:, ]
                         .groupby( 'week_of_year' )
                         .count()
                         .reset_index())
            # gráfico
            fig = px.line( df_aux, x='week_of_year', y='ID' )
            
            return fig
            
            
def order_share_by_week( df1 ):
            '''Esta função separa a quantidade de pedidos por entregadores únicos, correlaciona por semana e  devolve um gráfico de linha.


            Input: Dataframe
            Output: fig: gráfico de linha
            '''
            # Quantidade de pedidos por entregador por semana por entregador
            df_aux1 = (df1.loc[:, ['ID', 'week_of_year']]
                          .groupby( 'week_of_year' )
                          .count()
                          .reset_index())
            
            df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                          .groupby( 'week_of_year')
                          .nunique()
                          .reset_index())
            # União dos dois dataframes
            df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
            #Cálculo da relação por entregador
            df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            # gráfico
            fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
            
            return fig
        
def country_maps( df1 ):
        '''Esta função cria um mapa com a localização média de cada entrega.


        Input: Dataframe
        Output: None
        '''
        # seleção colunas
        cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
        #seleção linhas
        df_aux = (df1.loc[:, cols]
                     .groupby( ['City','Road_traffic_density'])
                     .median()
                     .reset_index())
        #criação o mapa
        map = folium.Map()

        for index, location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],
            location_info['Delivery_location_longitude']],
            popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

        folium_static(map, width=1024 , height =600)
        
        return None
            
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

st.header('Market Place - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    #order metric
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart( fig, use_container_width = True )
    
    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart( fig, use_container_width = True )
        
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart( fig, use_container_width = True )
            
    
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart( fig, use_container_width = True )
        
    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart( fig, use_container_width = True )
        
         
with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
    