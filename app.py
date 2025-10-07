import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験 年度別分析", layout="wide")
st.title("📊 宅建士試験 年度別分析（レーダーチャート＋表）")

# --- 設定 ---
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
target_scores = [7, 6, 2, 18, 4]  # 科目ごとの目標得点

# --- セッションステートで年度データ管理 ---
if "years_data" not in st.session_state:
    st.session_state.years_data = []

# 年度の追加
st.subheader("年度管理")
new_year = st.text_input("追加する年度名", "")
if st.button("年度追加") and new_year:
    st.session_state.years_data.append({
        "年度": new_year,
        "合格ライン": 37,
        "得点": [0]*len(categories)
    })

# 年度の削除
if st.session_state.years_data:
    delete_year = st.selectbox("削除する年度", [y["年度"] for y in st.session_state.years_data])
    if st.button("年度削除"):
        st.session_state.years_data = [y for y in st.session_state.years_data if y["年度"] != delete_year]

# --- 年度ごとのデータ入力と表示 ---
for idx, year_data in enumerate(st.session_state.years_data):
    st.markdown(f"## {year_data['年度']}")
    # 合格ライン入力
    year_data["合格ライン"] = st.number_input(
        f"{year_data['年度']} 合格ライン", min_value=0, max_value=sum(max_scores),
        value=year_data.get("合格ライン",37), step=1, key=f"pass_{idx}"
    )

    # 科目ごとの得点入力
    cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cols[i]:
            year_data["得点"][i] = st.number_input(
                f"{cat}", min_value=0, max_value=max_scores[i],
                value=year_data["得点"][i], step=1, key=f"{year_data['年度']}_{cat}"
            )

    # --- レーダーチャート ---
    st.subheader("📈 レーダーチャート")
    theta = categories + [categories[0]]
    # 自分の得点率
    r_score = [s/m*100 for s,m in zip(year_data["得点"], max_scores)]
    r_score += [r_score[0]]  # 閉じる
    # 目標得点率
    r_target = [t/m*100 for t,m in zip(target_scores, max_scores)]
    r_target += [r_target[0]]

    fig = go.Figure()
    # 目標得点の薄いライン
    fig.add_trace(go.Scatterpolar(
        r=r_target,
        theta=theta,
        fill='toself',
        name='目標得点',
        line=dict(color='lightgray', width=2),
        opacity=0.4
    ))
    # 自分の得点
    fig.add_trace(go.Scatterpolar(
        r=r_score,
        theta=theta,
        fill='toself',
        name='自分の得点',
        line=dict(color='royalblue', width=3),
        marker=dict(color='royalblue', size=10)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100], ticktext=["20%","40%","60%","80%","100%"])
        ),
        showlegend=True,
        width=700,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 得点表 ---
    st.subheader("📋 得点表")
    total_score = sum(year_data["得点"])
    total_pct = total_score / sum(max_scores) * 100

    table_data = []
    for i, cat in enumerate(categories):
        table_data.append({
            "科目": cat,
            "得点": year_data["得点"][i],
            "満点": max_scores[i],
            "目標": target_scores[i],
            "達成率": f"{year_data['得点'][i]/max_scores[i]*100:.0f}%"
        })
    # 合計
    table_data.append({
        "科目": "合計",
        "得点": total_score,
        "満点": sum(max_scores),
        "目標": year_data["合格ライン"],
        "達成率": f"{total_pct:.0f}%"
    })
    df = pd.DataFrame(table_data)

    # ハイライト関数
    def highlight_cells(val, col_name, row):
        if col_name == "得点" or col_name == "達成率":
            if val < df.loc[row, "目標"]:
                return 'background-color: #FF6347; color: white; font-weight: bold'
        return ''

    # スタイル適用
    styled_df = df.style.apply(lambda x: [highlight_cells(v, x.name, i) for i,v in enumerate(x)], axis=0)
    st.dataframe(styled_df, use_container_width=True)
