
import math, numpy as np, matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def plot_radar(labels, values, title='Takken Radar', font_path=None, dpi=150, fontsize=12):
    n = len(labels)
    angles = np.linspace(0, 2*math.pi, n, endpoint=False)
    angles_closed = np.concatenate([angles, [angles[0]]])
    vals = np.array(values)
    vals_closed = np.concatenate([vals, [vals[0]]])
    r_max = max(vals) if max(vals)>0 else 1.0

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(['']*n)
    ax.set_rgrids(np.linspace(0, r_max, 5), angle=90)
    ax.set_ylim(0, r_max)
    ax.plot(angles_closed, vals_closed, linewidth=2)
    ax.fill(angles_closed, vals_closed, alpha=0.15)

    label_r = r_max * 1.08
    if font_path:
        font_prop = FontProperties(fname=font_path)
    else:
        font_prop = None

    for theta, lab in zip(angles, labels):
        deg = (theta*180/math.pi) % 360
        if 80 < deg < 100:
            ha, va = 'center', 'bottom'
        elif 260 < deg < 280:
            ha, va = 'center', 'top'
        elif 0 <= deg <= 80 or 280 <= deg < 360:
            ha, va = 'left', 'center'
        else:
            ha, va = 'right', 'center'
        ax.text(theta, label_r, lab, ha=ha, va=va, fontsize=fontsize, fontproperties=font_prop)

    plt.title(title, y=1.08, fontproperties=font_prop)
    plt.tight_layout()
    return fig
