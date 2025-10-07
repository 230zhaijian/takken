import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="宅建士試験 年度別分析", layout="wide")
st.title("📊 宅建士試験 年度別分析（表＆レーダーチャート）")

categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
target_scores = [7, 6, 2, 18, 4]

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

# --- 年度ごとのデータ入力 ---
for idx, year_data in enumerate(st.session_state.years_data):
    st.markdown(f"### {year_data['年度']} データ入力")
    year_data["合格ライン"] = st.number_input(
        f"{year_data['年度']} 合格ライン", min_value=0, max_value=sum(max_scores),
        value=year_data.get("合格ライン",37), step=1, key=f"pass_{idx}"
    )
    cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        year_data["得点"][i] = st.number_input(
            f"{cat}", min_value=0, max_value=max_scores[i],
            value=year_data["得点"][i], step=1, key=f"{year_data['年度']}_{cat}"
        )

# --- 表作成 ---
if st.session_state.years_data:
    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("📋 年度別得点表")
        rows = []
        for y in st.session_state.years_data:
            total = sum(y["得点"])
            total_pct = total / sum(max_scores) * 100
            row = {"年度": y["年度"]}
            for i, s in enumerate(y["得点"]):
                row[categories[i]] = s
            row["合計点"] = total
            row["合格ライン"] = y["合格ライン"]
            rows.append(row)
        df = pd.DataFrame(rows)

        # ハイライト関数
        def highlight_cells(val, col_name):
            if col_name in categories:
                idx = categories.index(col_name)
                if val < target_scores[idx]:
                    return 'background-color: #FFA07A'  # 赤系
            elif col_name == "合計点":
                row_idx = df[df[col_name]==val].index[0]
                if val < df.loc[row_idx, "合格ライン"]:
                    return 'background-color: #FF6347'
            return ''

        st.dataframe(df.style.applymap(lambda val: highlight_cells(val, df.columns[df.columns.get_loc(val.name)] if hasattr(val,'name') else val)), use_container_width=True)

    # --- レーダーチャート ---
    with col2:
        st.subheader("📈 年度別レーダーチャート")
        fig = go.Figure()
        theta = categories + [categories[0]]
        for y in st.session_state.years_data:
            r = [s/max_scores[i]*100 for i,s in enumerate(y["得点"])]
            r += [r[0]]  # 閉じる
            # マーカー色
            colors = ['red' if s<t else 'royalblue' for s,t in zip(y["得点"], target_scores)]
            colors += [colors[0]]
            fig.add_trace(go.Scatterpolar(
                r=r,
                theta=theta,
                fill='toself',
                name=y["年度"],
                line=dict(color='royalblue', width=2),
                marker=dict(color=colors, size=10)
            ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(range=[0,100], tickvals=[20,40,60,80,100])
            ),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
