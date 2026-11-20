"""Build offline copies of the report for networks that block hosting sites.

Run from anywhere:  python site/tools/build_offline.py
Outputs (in <project>/배포용/):
  올리브영_테크컨퍼런스_참관기.html      one self-contained file (images inlined, no downloads)
  올리브영_테크컨퍼런스_참관기_전체.zip  the whole site folder incl. PDFs and originals;
                                         unzip and open index.html
"""
import base64
import re
import zipfile
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
OUT_DIR = SITE.parent / "배포용"
SINGLE = OUT_DIR / "올리브영_테크컨퍼런스_참관기.html"
BUNDLE = OUT_DIR / "올리브영_테크컨퍼런스_참관기_전체.zip"
BUNDLE_ROOT = "올리브영_테크컨퍼런스_참관기"

MIME = {".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml"}
OFFLINE_NOTE = "이 파일은 사내 전달용 단일 파일이라 PDF·원본 다운로드가 빠져 있습니다. 전체 자료는 '전체.zip'을 받아 주세요."
OFFLINE_CSS = ".slide-dl, .deck-actions { display: none !important; }"


def data_uri(rel_path: str) -> str:
    path = SITE / rel_path
    mime = MIME.get(path.suffix.lower())
    if mime is None:
        raise ValueError(f"no MIME type for {rel_path}")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def build_single(html: str) -> str:
    css = (SITE / "assets/css/style.css").read_text(encoding="utf-8")
    js = (SITE / "assets/js/app.js").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="assets/css/style.css">',
                        f"<style>\n{css}\n{OFFLINE_CSS}\n</style>")
    html = re.sub(r'<script src="assets/js/app\.js"[^>]*></script>', lambda _: f"<script>\n{js}\n</script>", html)
    html = re.sub(r'src="(assets/[^"]+)"', lambda m: f'src="{data_uri(m.group(1))}"', html)
    note = f'<p class="footnote" style="margin-top:12px">{OFFLINE_NOTE}</p>'
    return html.replace("</footer>", f"{note}\n</footer>", 1)


def build_bundle() -> None:
    files = [SITE / "index.html", *sorted(p for p in (SITE / "assets").rglob("*") if p.is_file())]
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, f"{BUNDLE_ROOT}/{path.relative_to(SITE).as_posix()}")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    html = (SITE / "index.html").read_text(encoding="utf-8")
    if 'src="assets/js/app.js"' not in html:
        raise SystemExit("index.html: app.js script tag not found")
    SINGLE.write_text(build_single(html), encoding="utf-8")
    build_bundle()
    for path in (SINGLE, BUNDLE):
        print(f"{path.name}: {path.stat().st_size / 1_048_576:.1f} MB")


if __name__ == "__main__":
    main()
