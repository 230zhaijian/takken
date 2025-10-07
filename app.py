import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="成績管理", layout="wide")

# --- サイドバーで画面切替 ---
page = st.sidebar.selectbox("画面選択", ["得点入力", "得点確認", "分析"])

# --- データ用のセッションステート ---
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "subjects" not in st.session_state:
    st.session_state.subjects = ["数学", "英語", "国語", "理科", "社会"]
if "targets" not in st.session_state:
    st.session_state.targets = [80, 85, 75, 70, 65]  # 目標得点
if "pass_line" not in st.session_state:
    st.session_state.pass_line = 60  # 合格ライン

# --- 得点入力画面 ---
if page == "得点入力":
    st.header("科目ごとの得点入力")
    for subject in st.session_state.subjects:
        score = st.number_input(
            f"{subject}:", 
            min_value=0, max_value=100, 
            value=st.session_state.scores.get(subject, 0), 
            step=1
        )
        st.session_state.scores[subject] = score

# --- 得点確認画面 ---
elif page == "得点確認":
    st.header("得点確認")
    if st.session_state.scores:
        df = pd.DataFrame({
            "科目": st.session_state.subjects,
            "得点": [st.session_state.scores[sub] for sub in st.session_stat]()
