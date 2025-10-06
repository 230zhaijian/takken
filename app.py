import streamlit as st
import plotly.graph_objects as go

# ページ設定

st.set_page_config(page_title="宅建士試験レーダーチャート", layout="centered")

# タイトル

st.title("📊 宅建士試験レーダーチャート")

# 項目と満点

categories = ["権利関係 (14)", "法令上の制限 (8)", "税その他 (3)", "宅建業法 (20)", "免除科目 (5)"]
max_scores = [14, 8, 3, 20, 5]

# 入力フォーム

st.sidebar.header("スコア入力")
scores = []
for i, (cat, max_s) in enumerate(zip(categories, max_scores), start=1):
score = st.sidebar.number_input(f"{cat}", min_value=0, max_value=max_s, value=int(max_s
