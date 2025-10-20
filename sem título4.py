import streamlit as st
import pandas as pd

st.title("Empresa de Manufaturas")

# Inicializa df
df = pd.DataFrame(columns=[
    "Data", "Turno", "Máquina", "Peças Produzidas", "Peças Defeituosas"
])

# Upload CSV
dados = st.file_uploader("Carregar Arquivo da Empresa", type=['csv'])
if dados is not None:
    df = pd.read_csv(dados)
    df['Data'] = pd.to_datetime(df['Data'])

# Formulário lateral
st.sidebar.header("Adicionar novo registro")
data = st.sidebar.date_input("Data")
turno = st.sidebar.selectbox("Turno", ["Manhã", "Tarde", "Noite"])
maquina = st.sidebar.selectbox("Máquina", ["Manual", "Semiautomática", "Automática"])
pecas_produzidas = st.sidebar.number_input("Peças Produzidas", min_value=0)
pecas_defeituosas = st.sidebar.number_input("Peças Defeituosas", min_value=0)

if st.sidebar.button("Adicionar"):
    novo = pd.DataFrame({
        "Data": [pd.Timestamp(data)],
        "Turno": [turno],
        "Máquina": [maquina],
        "Peças Produzidas": [pecas_produzidas],
        "Peças Defeituosas": [pecas_defeituosas]
    })
    df = pd.concat([df, novo], ignore_index=True)
    st.success("✅ Registro adicionado!")

# Tabela editável
st.subheader("Produção")
df = st.data_editor(df, num_rows="dynamic")

# Se houver dados, cálculos
if not df.empty:
    # Total de peças boas
    df['Total'] = df['Peças Produzidas'] - df['Peças Defeituosas']

    # Eficiência (%) com proteção contra divisão por zero
    df['Eficiência (%)'] = (df['Total'] / df['Peças Produzidas'] * 100).fillna(0).round(1)

    # Taxa de defeitos (%) com proteção contra divisão por zero
    df['Taxa de Defeitos (%)'] = (df['Peças Defeituosas'] / df['Peças Produzidas'] * 100).fillna(0).round(1)

    # Eficiência por dia
    eficiencia = df.groupby('Data').sum().reset_index()
    eficiencia['Eficiência por dia (%)'] = (eficiencia['Total'] / eficiencia['Peças Produzidas'] * 100).fillna(0).round(1)

    # Produção abaixo de 80
    producao_baixa = df[df['Peças Produzidas'] < 80]

    # Eficiência por dia menor que 90%
    eficiencia_baixa = eficiencia[eficiencia['Eficiência por dia (%)'] < 90]

# Escolha entre cálculos ou gráficos
escolha = st.radio("O que deseja ver?", ("Cálculos e Alertas", "Gráficos"))

if escolha == "Cálculos e Alertas":
    st.subheader("Tabela de Produção")
    st.dataframe(df.assign(Data=df['Data'].dt.strftime("%Y-%m-%d")))

    if not producao_baixa.empty:
        st.error("⚠️ Produção abaixo de 80 peças:")
        st.dataframe(producao_baixa[['Data','Turno','Máquina','Peças Produzidas']].assign(Data=lambda x: x['Data'].dt.strftime("%Y-%m-%d")))

    st.subheader("Eficiência por dia (%)")
    st.dataframe(eficiencia.assign(Data=eficiencia['Data'].dt.strftime("%Y-%m-%d"))[['Data','Peças Produzidas','Total','Eficiência por dia (%)']])

    if not eficiencia_baixa.empty:
        st.error("⚠️ Alguns dias tiveram eficiência por dia menor que 90%")

if escolha == "Gráficos":
    st.subheader("Produção diária por máquina")
    graf1 = df.groupby(['Data','Máquina'])['Peças Produzidas'].sum().unstack(fill_value=0)
    st.bar_chart(graf1)

    st.subheader("Eficiência média por máquina")
    graf2 = df.groupby('Máquina')['Eficiência (%)'].mean()
    st.bar_chart(graf2)

    st.subheader("Taxa média de defeitos por dia")
    graf3 = df.groupby('Data')['Taxa de Defeitos (%)'].mean()
    st.line_chart(graf3)

# Salvar CSV
if st.button("💾 Salvar"):
    df.to_csv("C:\Senai\Empresa.csv", index=False)
    st.success("✅ Dados salvos em C:/Senai/Empresa.csv")

