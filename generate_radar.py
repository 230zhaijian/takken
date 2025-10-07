
# generate_radar.py (改良版)
# 角度補正・ラベル位置改善・日本語フォント自動検出／指定対応
# Usage:
#   python generate_radar.py input.csv output.png [--font /path/to/font.ttf] [--dpi 150] [--fontsize 10]
#
# 概要:
# - 軸の「上（北）」を起点にし、時計回りに軸を描画します（matplotlib の theta_offset を使用）。
# - ラベルは各軸角度に基づき polar 座標で配置し、象限に応じた水平/垂直位置合わせを行います。
# - システムに日本語対応フォントがあれば自動で利用します。なければ --font オプションでフォントファイル (.ttf/.otf) を指定してください。
# - 複数のシリーズ（列）に対応します。
import sys, os, csv, math, argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    if len(reader) < 2:
        raise ValueError("CSV must have at least header + one data row")
    header = reader[0]
    # case A: two-column file Category,Value rows
    if len(header) == 2 and all(len(row) >= 2 for row in reader):
        labels = [row[0] for row in reader[1:]]
        values = [float(row[1]) if row[1] != '' else 0.0 for row in reader[1:]]
        return labels, [values], header
    # case B: first row contains categories (first cell may be label for row headers)
    if len(header) >= 2 and len(reader) >= 2:
        labels = header[1:]
        series = []
        series_names = []
        for row in reader[1:]:
            # if row shorter, pad with zeros
            vals = []
            for v in row[1:len(labels)+1]:
                try:
                    vals.append(float(v))
                except:
                    vals.append(0.0)
            if len(vals) < len(labels):
                vals += [0.0] * (len(labels)-len(vals))
            series.append(vals[:len(labels)])
            # row[0] may be series name
            series_names.append(row[0] if row and row[0] else None)
        return labels, series, series_names
    raise ValueError("Unsupported CSV format. Use either (Category,Value) rows or header+rows.")

def find_japanese_font(font_path=None):
    # If user provided font path and it exists, use it (and register with matplotlib)
    if font_path:
        if os.path.exists(font_path):
            try:
                fm.fontManager.addfont(font_path)
                return fm.FontProperties(fname=font_path)
            except Exception as e:
                print("Warning: failed to load font from path:", font_path, e)
                return None
        else:
            print("Warning: specified font path does not exist:", font_path)
            return None
    # Candidates to search for in installed font names
    candidates = ['noto', 'ipa', 'meiryo', 'yu gothic', 'hiragino', 'takao', 'ms gothic']
    # Check installed fonts
    for f in fm.fontManager.ttflist:
        name = (f.name or "").lower()
        for c in candidates:
            if c in name:
                # return a FontProperties (ensures we can pass it to text drawing functions)
                try:
                    return fm.FontProperties(fname=f.fname)
                except:
                    # fallback: try name-only
                    return fm.FontProperties(fname=f.fname)
    # If nothing found, return None (caller should warn and optionally accept --font)
    return None

def radar_angles(n):
    # return n angles evenly spaced, starting at 0 (we will set theta_offset to pi/2 to make 0 at top)
    return np.linspace(0, 2*math.pi, n, endpoint=False)

def compute_label_alignment(theta_deg):
    # theta_deg in degrees [0,360)
    # returns (ha, va)
    # map to quadrants; prefer center alignment for near-top/bottom
    if 80 < theta_deg < 100:
        return 'center', 'bottom'
    elif 260 < theta_deg < 280:
        return 'center', 'top'
    elif 0 <= theta_deg <= 80 or 280 <= theta_deg < 360:
        return 'left', 'center'
    else:
        return 'right', 'center'

def plot_radar(labels, series_list, series_names=None, title=None, outpath='output.png', font_prop=None, dpi=150, fontsize=10):
    n = len(labels)
    angles = radar_angles(n)
    angles_closed = np.concatenate([angles, [angles[0]]])

    # determine r_max
    r_max = max((max(s) if s else 0.0) for s in series_list) if series_list else 1.0
    if r_max == 0:
        r_max = 1.0

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, polar=True)
    # set 0 at top and clockwise direction
    ax.set_theta_offset(np.pi/2)   # IMPORTANT: use theta_offset to put first axis on top
    ax.set_theta_direction(-1)

    # hide default xticklabels because we draw our own labels
    ax.set_xticks(angles)
    ax.set_xticklabels(['']*n)

    ax.set_rgrids(np.linspace(0, r_max, 5), angle=90)
    ax.set_ylim(0, r_max)

    for idx, s in enumerate(series_list):
        vals = np.array(s[:n], dtype=float)
        vals_closed = np.concatenate([vals, [vals[0]]])
        ax.plot(angles_closed, vals_closed, linewidth=2)
        ax.fill(angles_closed, vals_closed, alpha=0.15)

    # label placement at radial distance slightly beyond r_max
    label_r = r_max * 1.08
    for theta, lab in zip(angles, labels):
        deg = (theta*180/math.pi) % 360
        ha, va = compute_label_alignment(deg)
        # Use polar text placement; pass fontproperties if available to avoid mojibake
        if font_prop is not None:
            ax.text(theta, label_r, lab, ha=ha, va=va, fontsize=fontsize, fontproperties=font_prop)
        else:
            ax.text(theta, label_r, lab, ha=ha, va=va, fontsize=fontsize)

    if series_names and any(series_names):
        # clean up legend labels (replace None with generic name)
        legend_labels = [n if n else f"series_{i+1}" for i,n in enumerate(series_names)]
        if font_prop is not None:
            ax.legend(legend_labels, loc='upper right', bbox_to_anchor=(1.25, 1.1), prop=font_prop)
        else:
            ax.legend(legend_labels, loc='upper right', bbox_to_anchor=(1.25, 1.1))

    if title:
        if font_prop is not None:
            plt.title(title, y=1.08, fontproperties=font_prop)
        else:
            plt.title(title, y=1.08)
    plt.tight_layout()
    plt.savefig(outpath, dpi=dpi, bbox_inches='tight')
    plt.close(fig)

def main():
    parser = argparse.ArgumentParser(description='Takken Radar Chart (improved)')
    parser.add_argument('input_csv', help='input CSV path')
    parser.add_argument('output_png', help='output PNG path')
    parser.add_argument('--font', help='Path to .ttf/.otf font file to use (recommended for Japanese)', default=None)
    parser.add_argument('--dpi', type=int, default=150)
    parser.add_argument('--fontsize', type=int, default=10)
    args = parser.parse_args()

    labels, series_list, series_names_or_header = read_csv(args.input_csv)
    # series_names_or_header may be header or series names depending on CSV format
    series_names = None
    if isinstance(series_names_or_header, list) and all(isinstance(x, str) for x in series_names_or_header):
        series_names = series_names_or_header

    font_prop = find_japanese_font(args.font)
    if font_prop is None and args.font is None:
        print(\"Warning: No Japanese-capable font detected. If you see 文字化け, supply a TTF/OTF via --font or install Noto Sans CJK / IPA fonts on your system.\")


    plot_radar(labels, series_list, series_names=series_names, title='Takken Radar (完全修正版)', outpath=args.output_png, font_prop=font_prop, dpi=args.dpi, fontsize=args.fontsize)

if __name__ == '__main__':
    main()
