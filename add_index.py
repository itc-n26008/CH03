import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

# このプログラムが置かれている場所 = リポジトリの一番上
root = Path(__file__).resolve().parent

# 入力がなければ、今いるディレクトリを対象にする
targets = sys.argv[1:] if len(sys.argv) > 1 else ["."]

# 一番上の index.html を開く
list_file = root / "index.html"
html = list_file.read_text(encoding="utf-8")

# すでに登録されているリンクを調べる
existing = {
    value.rstrip("/") for value in re.findall(r'href=["\']([^"\']+)["\']', html)
}
new_links = []

for target in targets:
    # 入力されたパスを絶対パスに変換
    directory = (Path.cwd() / target).resolve()

    # リポジトリの外に出ていないか確認
    try:
        relative = directory.relative_to(root)
    except ValueError:
        print(f"リポジトリの外です: {target}")
        continue

    # 対象ディレクトリに index.html があるか確認
    if not (directory / "index.html").is_file():
        print(f"index.html がありません: {target}")
        continue

    # リポジトリの一番上から見た相対パス
    href = quote(relative.as_posix(), safe="/-._~") + "/"

    # 二重登録を防ぐ
    if href in existing:
        print(f"追加済みです！: {href}")
        continue

    print(f"新しく追加します！: {href}")

    # ディレクトリ名を表示名にする
    name = directory.name

    new_links.append(
        f'        <li><a href="{escape(href, quote=True)}">{escape(name)}</a></li>'
    )

    existing.add(href)

# 新しいリンクを ul の中に追加
if new_links:
    closing = re.search(r"</ul\s*>", html, re.IGNORECASE)

    if closing:
        html = (
            html[: closing.start()]
            + "\n".join(new_links)
            + "\n    "
            + html[closing.start() :]
        )

        list_file.write_text(html, encoding="utf-8")
        print(f"{len(new_links)} 件追加しました！")
    else:
        print("index.html に </ul> が見つかりません")
else:
    print("追加するものはありません")
