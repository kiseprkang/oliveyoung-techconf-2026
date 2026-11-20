"""Build per-session 'slide deck' PDFs (and per-slide PNGs) from the rendered site.

Run from anywhere:  python site/tools/build_pdf.py [s1 s2 ...]
Serves site/ on a local port, captures each session block with Playwright
(cover, 3-minute summary, primer, every slide card, results, insight),
and lays each capture onto a 16:9 page.

Outputs per session N:
  site/assets/sN/define-OMNI_sessionNN.pdf
  site/assets/sN/slides/NN.png   (only for slide cards whose download link points there)
"""
import functools
import http.server
import sys
import threading
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parents[1]
ASSETS = SITE / "assets"
DEFAULT_SESSIONS = ("s1", "s2", "s3", "s4", "s5")

PAGE_W, PAGE_H = 1920, 1080
MARGIN_X, MARGIN_TOP, FOOTER_H = 80, 64, 72
PAGE_BG = (251, 250, 248)
FOOTER_FG = (120, 120, 116)
ACCENT = (63, 143, 0)
VIEWPORT = {"width": 1280, "height": 900}
SCALE = 2
PDF_JPEG_QUALITY = 88
FONT_PATHS = ("C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/malgunbd.ttf")

# Make every block render flat and static: no header, no reveal animation,
# the carousel laid out as a vertical list, no on-screen controls.
CAPTURE_CSS = """
.site-header, .deck-nav, .slide-dl { display: none !important; }
.reveal { opacity: 1 !important; transform: none !important; }
html { scroll-behavior: auto !important; }
.deck-track { grid-auto-flow: row !important; grid-auto-columns: auto !important;
  overflow: visible !important; scroll-snap-type: none !important; }
"""

BLOCKS = (".session-cover", ".tldr", ".primer", "__slides__", ".results", ".insight")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


def serve(directory: Path) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def compose_page(shot: Image.Image, label: str, page_no: int, total: int) -> Image.Image:
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAGE_BG)
    box_w, box_h = PAGE_W - 2 * MARGIN_X, PAGE_H - MARGIN_TOP - FOOTER_H
    ratio = min(box_w / shot.width, box_h / shot.height)
    fitted = shot.resize((round(shot.width * ratio), round(shot.height * ratio)), Image.LANCZOS)
    x = (PAGE_W - fitted.width) // 2
    y = MARGIN_TOP + (box_h - fitted.height) // 2
    page.paste(fitted, (x, y))

    draw = ImageDraw.Draw(page)
    font = load_font(22)
    base_y = PAGE_H - FOOTER_H + 22
    draw.rectangle((MARGIN_X, base_y + 6, MARGIN_X + 10, base_y + 16), fill=ACCENT)
    draw.text((MARGIN_X + 22, base_y), label, font=font, fill=FOOTER_FG)
    counter = f"{page_no:02d} / {total:02d}"
    draw.text((PAGE_W - MARGIN_X - draw.textlength(counter, font=font), base_y), counter, font=font, fill=FOOTER_FG)
    return page


def element_png(locator) -> Image.Image:
    return Image.open(BytesIO(locator.screenshot(animations="disabled"))).convert("RGB")


def capture_session(page, sid: str) -> list[Image.Image]:
    section = page.locator(f"section#{sid}")
    if section.count() == 0:
        raise SystemExit(f"section #{sid} not found in index.html")

    slide_dir = ASSETS / sid / "slides"
    page_html = (SITE / "index.html").read_text(encoding="utf-8")
    shots = []
    for selector in BLOCKS:
        if selector == "__slides__":
            slides = section.locator(".slide")
            for i in range(slides.count()):
                shot = element_png(slides.nth(i))
                png_name = f"{i + 1:02d}.png"
                if f"assets/{sid}/slides/{png_name}" in page_html:
                    slide_dir.mkdir(parents=True, exist_ok=True)
                    shot.save(slide_dir / png_name, optimize=True)
                shots.append(shot)
            continue
        block = section.locator(selector)
        if block.count():
            shots.append(element_png(block.first))
    return shots


def build_pdf(sid: str, shots: list[Image.Image]) -> Path:
    number = sid.lstrip("s").zfill(2)
    label = f"define:OMNI 참관 리포트 · Session {number}"
    pages = [compose_page(s, label, i + 1, len(shots)) for i, s in enumerate(shots)]
    out = ASSETS / sid / f"define-OMNI_session{number}.pdf"
    pages[0].save(out, "PDF", save_all=True, append_images=pages[1:], resolution=144, quality=PDF_JPEG_QUALITY)
    return out


def main(sessions: list[str]) -> None:
    server = serve(SITE)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport=VIEWPORT, device_scale_factor=SCALE)
            page.goto(url, wait_until="networkidle")
            page.add_style_tag(content=CAPTURE_CSS)
            page.evaluate("document.fonts.ready")
            for sid in sessions:
                shots = capture_session(page, sid)
                out = build_pdf(sid, shots)
                print(f"{sid}: {len(shots)} pages -> {out.relative_to(SITE)} ({out.stat().st_size / 1_048_576:.1f} MB)")
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main(sys.argv[1:] or list(DEFAULT_SESSIONS))
