import streamlit as st
import pandas as pd

st.title('Empresa de Manufaturas')

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        'Data', 'Turno', 'Máquina', 'Peças Produzidas', 'Peças Defeituosas'])
dados = st.file_uploader('Carregar Arquivo da Empresa', type=['csv'])#mantém os dados atualizados
if dados is not None:
    st.session_state.df = pd.read_csv(dados)
df = st.session_state.df
#formulario
st.sidebar.header('Adicionar novo registro')
data = st.sidebar.date_input('Data').dt.date
turno = st.sidebar.selectbox('Turno', ['Manhã', 'Tarde', 'Noite'])
maquina = st.sidebar.selectbox('Máquina', ['Manual', 'Semiautomática', 'Automática'])
pecas_produzidas = st.sidebar.number_input('Peças Produzidas', min_value=0)
pecas_defeituosas = st.sidebar.number_input('Peças Defeituosas', min_value=0)
if st.sidebar.button('Adicionar'):
    novo = pd.DataFrame({
        'Data': [data],
        'Turno': [turno],
        'Máquina': [maquina],
        'Peças Produzidas': [pecas_produzidas],
        'Peças Defeituosas': [pecas_defeituosas]})
    st.session_state.df = pd.concat([st.session_state.df, novo], ignore_index=True)
    st.success('Registro adicionado!')
#editar
st.subheader('Produção')
df = st.data_editor(df, num_rows='dynamic')
st.session_state.df = df

if not st.session_state.df.empty:
    df = st.session_state.df
    df['Data'] = pd.to_datetime(df['Data'])
    df['Total'] = df['Peças Produzidas'] - df['Peças Defeituosas']
    df['Eficiência (%)'] = (df['Total'] / df['Peças Produzidas'] * 100).round(1)
    df['Taxa de Defeitos (%)'] = (df['Peças Defeituosas'] / df['Peças Produzidas'] * 100).round(1)
#eficiencia e producao
    eficiencia = df.groupby('Data').sum().reset_index()
    eficiencia['Eficiência por dia (%)'] = (eficiencia['Total'] / eficiencia['Peças Produzidas'] * 100).round(1)
    producao_baixa = df[df['Peças Produzidas'] < 80]
    eficiencia_baixa = eficiencia[eficiencia['Eficiência por dia (%)'] < 90]
#eescolhas
escolha = st.radio('Qual?', ('Cálculos e Alertas', 'Gráficos'))
if escolha == 'Cálculos e Alertas':
    st.subheader('Tabela de Produção')
    st.dataframe(df)
    if not producao_baixa.empty:
        st.error('Produção abaixo de 80 peças:')
        st.dataframe(producao_baixa[['Data','Turno','Máquina','Peças Produzidas']])
#eficiencia
    st.subheader('Eficiência por dia (%)')
    st.dataframe(eficiencia[['Data','Peças Produzidas','Total','Eficiência por dia (%)']])
    if not eficiencia_baixa.empty:
        st.error('Alguns dias tiveram eficiência por dia menor que 90%')
if escolha == 'Gráficos':
#1
    st.subheader('Produção diária por máquina')
    graf1 = df.groupby(['Data','Máquina'])['Peças Produzidas'].sum().unstack(fill_value=0)
    st.bar_chart(graf1)
#2
    st.subheader('Eficiência média por máquina')
    graf2 = df.groupby('Máquina')['Eficiência (%)'].mean()
    st.bar_chart(graf2)
#3
    st.subheader('Taxa média de defeitos por dia')
    graf3 = df.groupby('Data')['Taxa de Defeitos (%)'].mean()
    st.line_chart(graf3)
if st.button('Salvar'):
    st.session_state.df.to_csv('C:/Senai/Empresa.csv', index=False)
    st.success('✅ Dados salvos em C:\Senai\Empresa.csv')

