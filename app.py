
import streamlit as st
import pandas as pd
from generate_radar import plot_radar

st.set_page_config(page_title="Takken Radar", layout="centered")
st.title("Takken Radar Chart (Streamlit版)")

uploaded_file = st.file_uploader("CSVをアップロードしてください", type=['csv'])
use_sample = st.checkbox("サンプルデータを使う", value=True)

font_path = "NotoSansCJK-Regular.ttf"
dpi = st.slider("DPI", 50, 300, 150)
fontsize = st.slider("フォントサイズ", 6, 24, 12)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif use_sample:
    df = pd.read_csv("sample_data.csv")
else:
    st.stop()

if df.shape[1] < 2:
    st.error("CSVは少なくとも2列必要です。Category, Value形式を確認してください。")
else:
    labels = df.iloc[:,0].tolist()
    values = df.iloc[:,1].tolist()
    fig = plot_radar(labels, values, font_path=font_path, dpi=dpi, fontsize=fontsize)
    st.pyplot(fig)
