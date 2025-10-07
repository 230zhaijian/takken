import streamlit as st
import pandas as pd
import numpy as np

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
            "得点": [st.session_state.scores[sub] for sub in st.session_state.subjects],
            "目標": st.session_state.targets
        })
        st.dataframe(df.style.format({"得点": "{:.0f}", "目標": "{:.0f}"}))

        # 棒グラフで代替
        chart_df = pd.DataFrame({
            "自分の得点": [st.session_state.scores[sub] for sub in st.session_state.subjects],
            "目標得点": st.session_state.targets
        }, index=st.session_state.subjects)
        st.bar_chart(chart_df)
    else:
        st.info("まず「得点入力」画面で得点を入力してください。")

# --- 分析画面 ---
elif page == "分析":
    st.header("得点分析")
    if st.session_state.scores:
        scores = [st.session_state.scores[sub] for sub in st.session_state.subjects]
        avg = np.mean(scores)
        passed = sum([1 for s in scores if s >= st.session_state.pass_line])
        st.metric("平均点", f"{avg:.1f}")
        st.metric("合格科目数", f"{passed}/{len(scores)}")
        st.bar_chart(pd.DataFrame({"得点": scores}, index=st.session_state.subjects))
    else:
        st.info("まず「得点入力」画面で得点を入力してください。")
