takken_radar_fix - 完全修正版 (角度補正 + 文字位置改善済み)
===============================================

含まれるファイル:
- generate_radar.py : レーダーチャート生成スクリプト (改良版)
- sample_data.csv  : サンプルデータ (Category,Value)
- requirements.txt  : 必要ライブラリ (matplotlib, numpy)
- example_output.png: 出力例
- LICENSE.txt

使い方 (例):
  python generate_radar.py sample_data.csv example_output.png
日本語ラベルが文字化けしないようにするには、システムに日本語フォントがインストールされているか、
--font オプションでフォントファイルのパスを指定してください。
例:
  python generate_radar.py sample_data.csv example_output.png --font /path/to/NotoSansCJKjp-Regular.ttf

推奨フォント:
- Noto Sans CJK JP (Google Noto)
- IPAexGothic / IPAPGothic
- Meiryo, Yu Gothic (Windows / modern macOS)

インストールのヒント（ローカルで実行する際）:
- macOS (Homebrew):
    brew tap homebrew/cask-fonts
    brew install --cask font-noto-sans-cjk-jp
- Ubuntu / Debian:
    sudo apt-get install fonts-noto-cjk
- Windows:
    Noto フォントをダウンロードして右クリック -> インストール

追加の改善点:
- 角度の基準は matplotlib の theta_offset を使用しているため、軸のズレが起きにくくなっています。
- ラベルは polar 座標で配置し、象限に応じた水平/垂直整列を行っています。
