import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ===== 日本語フォントの指定（クラウド側に入っているフォントを優先） =====
rcParams['font.family'] = ['Noto Sans CJK JP', 'Yu Gothic', 'Hiragino Maru Gothic Pro', 'Meiryo', 'DejaVu Sans']

# 科目と満点
categories = ["権利関係", "法令上の制限", "税その他", "宅建業法", "免除科目"]
max_scores = [14, 8, 3, 20, 5]
max_total = sum(max_scores)

st.title("📊 宅建士試験 レーダーチャート")

# 入力欄
scores = []
for i, cat in enumerate(categories):
    scores.append(st.number_input(f"{cat}（満点 {max_scores[i]}）", min_value=0, max_value=max_scores[i], value=0))

# レーダーチャート準備
angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]
scores_plot = scores + scores[:1]
max_plot = max_scores + max_scores[:1]

# プロット
fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
ax.set_theta_offset(np.pi/2)
ax.set_theta_direction(-1)

# 満点
ax.plot(angles, max_plot, 'o-', linewidth=2, label="満点", color="gray")
ax.fill(angles, max_plot, alpha=0.1, color="gray")

# 自分のスコア
ax.plot(angles, scores_plot, 'o-', linewidth=2, label="自分のスコア", color="blue")
ax.fill(angles, scores_plot, alpha=0.25, color="blue")

# 日本語ラベル
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12)
ax.set_yticklabels([])

# 合計点と合格ライン
total_score = sum(scores)
ax.set_title(f"合計: {total_score}点 / {max_total}点\n合格ライン: 37点", size=14)

ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))

st.pyplot(fig)
