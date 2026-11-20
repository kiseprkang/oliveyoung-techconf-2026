"""Build optimized web assets for the report site.

Run from anywhere:  python site/tools/build_assets.py
Creates site/assets/... (WebP for display, JPEG originals for download).
Session PDFs are built separately from the rendered page: python site/tools/build_pdf.py
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
ASSETS = SITE / "assets"

DISPLAY_MAX = 1600
ORIGINAL_MAX = 2000
WEBP_QUALITY = 80
JPEG_QUALITY = 82

MOOD_DIR = ROOT / "컨퍼런스 분위기"
MOOD = {  # output name: source file
    "venue": "KakaoTalk_20261120_101348625_10.jpg",
    "sign": "KakaoTalk_20261120_101348625_11.jpg",
    "map": "KakaoTalk_20261120_101348625_12.jpg",
    "hall": "KakaoTalk_20261120_101348625.jpg",
    "skinscan-start": "KakaoTalk_20261120_101348625_01.jpg",
    "skinscan-face": "KakaoTalk_20261120_101348625_03.jpg",
    "skinscan-qr": "KakaoTalk_20261120_101348625_04.jpg",
    "skinscan-mobile": "KakaoTalk_20261120_101348625_06.jpg",
    "ingredient-game": "KakaoTalk_20261120_101348625_05.jpg",
    "colorfit": "KakaoTalk_20261120_101348625_07.jpg",
    "exhibit": "KakaoTalk_20261120_101348625_08.jpg",
    "olivebetter": "KakaoTalk_20261120_101348625_09.jpg",
}

S1_DIR = ROOT / "세션 1. 온오프라인이 연결된 장바구니의 3가 지키워드" / "올영_장바구니_자료_flat"
# Display images: (output name, source, crop box as fractions l, t, r, b or None)
S1_DISPLAY = [
    ("panel", "15aff32a-image.jpg", None),
    ("cart-compare", "89b4c3d4-image.jpg", (0.13, 0.30, 0.83, 0.84)),
    ("cart-legacy", "58fd6df4-image.jpg", (0.20, 0.16, 0.74, 0.97)),
    ("cart-inventory-demo", "0600980c-image.jpg", (0.08, 0.0, 0.76, 1.0)),
    ("promo-cards", "249e3212-image.jpg", (0.0, 0.12, 1.0, 0.68)),
    ("pickup-compare", "65656634-image.jpg", (0.27, 0.04, 0.88, 0.95)),
]
# Original slide photos in talk order (for per-slide download and the session PDF)
S1_ORIGINALS = [
    ("01-title", "44d8fc10-image.jpg"),
    ("02-panel", "db237238-image.jpg"),
    ("03-numbers", "4adfb622-image.jpg"),
    ("04-legacy-limits", "351dca63-image.jpg"),
    ("05-goal", "8377ff93-image.jpg"),
    ("06-cart-compare", "89b4c3d4-image.jpg"),
    ("07-inventory-types", "ed323a38-image.jpg"),
    ("08-store-selection", "c03ddee8-image.jpg"),
    ("09-inventory-demo", "0600980c-image.jpg"),
    ("10-inventory-fe", "fd3a07de-image.jpg"),
    ("11-promo-cards", "3a032814-image.jpg"),
    ("12-promo-fe", "5eed2489-image.jpg"),
    ("13-promo-be", "71cf2a5d-image.jpg"),
    ("14-pickup-90", "79d2da89-image.jpg"),
    ("15-pickup-flow", "79c507be-image.jpg"),
    ("16-pickup-compare", "65656634-image.jpg"),
    ("17-takeaways", "6842c001-image.jpg"),
    ("18-result-be", "e25c4ace-image.jpg"),
    ("19-result-fe", "933a76bd-image.jpg"),
    ("20-result-kpi", "b9da3086-image.jpg"),
    ("21-next-cart", "ce873554-image.jpg"),
]


S2_DIR = ROOT / "세션 2. 카탈로그 삼국통일  온라인, 매장, 글로벌을 하나로" / "카탈로그 발표 사진"
S2_DISPLAY = [
    ("service-cards", "IMG_0238_실제서비스적용.webp", (0.08, 0.19, 1.0, 0.83)),
]
S2_ORIGINALS = [
    ("14-service-cards", "IMG_0238_실제서비스적용.webp"),
]

S3_DIR = (ROOT / "세션 3. 리서처가 직접 구현한 글로벌 리서치 플랫폼" / "olive_young_define_omni"
          / "olive_young_define_omni" / "images")
S3_DISPLAY = [
    ("cover", "slide_07.jpg", (0.08, 0.30, 1.0, 0.80)),
    ("analysis", "slide_24.jpg", (0.08, 0.22, 0.97, 0.88)),
    ("languages", "slide_27.jpg", (0.03, 0.17, 0.93, 0.90)),
    ("store-map", "slide_28.jpg", (0.22, 0.33, 0.80, 0.74)),
    ("research-ops", "slide_36.jpg", (0.14, 0.37, 0.82, 0.85)),
]
# One original photo per slide card (numbers are the talk's photo order)
S3_ORIGINALS = [(f"{n:02d}", f"slide_{n:02d}.jpg") for n in (2, 6, 7, 10, 12, 16, 19, 20, 24, 27, 28, 31, 34, 36, 38)]

S4_DIR = ROOT / "세션 4. 올리브영은 어떻게 일할까_비즈니스 성공을 이끈 5년간의 이야기" / "olive_young_handoff_images"
S4_DISPLAY = [
    ("cover", "10_tribe.jpg", (0.0, 0.30, 0.70, 0.90)),
    ("inception", "25_inception.jpg", (0.19, 0.28, 0.86, 0.68)),
    ("simulation", "29_ai_dlc_experience.jpg", (0.13, 0.27, 0.88, 0.77)),
    ("ai-first-track", "30_ai_first_track.jpg", (0.14, 0.43, 0.88, 0.93)),
]
# One original photo per slide card: output name = source file stem
S4_ORIGINALS = [
    "02_timeline", "05_dual_os", "06_squad_prologue", "07_2022_pain", "10_tribe", "11_roles_tribe_leader",
    "14_quarterly_4weeks", "16_program_board", "17_quarterly_plan_squad", "19_way_of_working_v2",
    "20_keep_voices", "22_insight_gardening", "25_inception", "27_lets_ai_b", "29_ai_dlc_experience",
    "30_ai_first_track", "32_wrap_up",
]

S5_DIR = ROOT / "세션 5. AI가 다하면 PM은 뭐해요" / "oliveyoung_pm_session" / "oliveyoung_pm_session"
S5_DISPLAY = [  # (output name, path relative to S5_DIR, crop box)
    ("cover", "images/32_IMG_0374.jpg", (0.0, 0.26, 1.0, 0.86)),
    ("tiki", "video/frames/tiki_demo_14s.jpg", (0.31, 0.0, 0.64, 1.0)),
    ("dashboard", "images/10_IMG_0337.jpg", (0.12, 0.33, 0.90, 0.90)),
    ("ranking-sim", "images/19_IMG_0352.jpg", (0.04, 0.27, 0.88, 0.88)),
    ("prototype", "images/24_IMG_0360.jpg", (0.02, 0.25, 0.99, 0.93)),
    ("work-plate", "images/26_IMG_0364.jpg", (0.03, 0.25, 0.96, 0.90)),
    ("adoption", "images/32_IMG_0374.jpg", (0.15, 0.36, 0.80, 0.82)),
]
# One original photo per slide card (numbers are the talk's photo order)
S5_ORIGINALS = ["02", "03", "04", "08", "10", "11", "14", "16", "18", "19", "20", "21",
                "23", "24", "25", "26", "28", "29", "31", "32"]


def load(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def crop(im: Image.Image, box):
    if not box:
        return im
    w, h = im.size
    l, t, r, b = box
    return im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def fit(im: Image.Image, max_side: int) -> Image.Image:
    out = im.copy()
    out.thumbnail((max_side, max_side), Image.LANCZOS)
    return out


def save_webp(im: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fit(im, DISPLAY_MAX).save(dest, "WEBP", quality=WEBP_QUALITY, method=6)


def build_mood() -> None:
    for name, src in MOOD.items():
        save_webp(load(MOOD_DIR / src), ASSETS / "mood" / f"{name}.webp")


def build_session1() -> None:
    for name, src, box in S1_DISPLAY:
        save_webp(crop(load(S1_DIR / src), box), ASSETS / "s1" / f"{name}.webp")

    for name, src in S1_ORIGINALS:
        dest = ASSETS / "s1" / "original" / f"{name}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fit(load(S1_DIR / src), ORIGINAL_MAX).save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


def build_session2() -> None:
    for name, src, box in S2_DISPLAY:
        save_webp(crop(load(S2_DIR / src), box), ASSETS / "s2" / f"{name}.webp")
    for name, src in S2_ORIGINALS:
        dest = ASSETS / "s2" / "original" / f"{name}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fit(load(S2_DIR / src), ORIGINAL_MAX).save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


def build_session3() -> None:
    for name, src, box in S3_DISPLAY:
        save_webp(crop(load(S3_DIR / src), box), ASSETS / "s3" / f"{name}.webp")
    for name, src in S3_ORIGINALS:
        dest = ASSETS / "s3" / "original" / f"{name}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fit(load(S3_DIR / src), ORIGINAL_MAX).save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


def build_session4() -> None:
    for name, src, box in S4_DISPLAY:
        save_webp(crop(load(S4_DIR / src), box), ASSETS / "s4" / f"{name}.webp")
    for stem in S4_ORIGINALS:
        dest = ASSETS / "s4" / "original" / f"{stem}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fit(load(S4_DIR / f"{stem}.jpg"), ORIGINAL_MAX).save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


def build_session5() -> None:
    for name, src, box in S5_DISPLAY:
        save_webp(crop(load(S5_DIR / src), box), ASSETS / "s5" / f"{name}.webp")
    for num in S5_ORIGINALS:
        src = next((S5_DIR / "images").glob(f"{num}_*.jpg"))
        dest = ASSETS / "s5" / "original" / f"{num}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fit(load(src), ORIGINAL_MAX).save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


if __name__ == "__main__":
    build_mood()
    build_session1()
    build_session2()
    build_session3()
    build_session4()
    build_session5()
    total = sum(p.stat().st_size for p in ASSETS.rglob("*") if p.is_file())
    print(f"assets built: {total / 1_048_576:.1f} MB")
