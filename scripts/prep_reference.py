#!/usr/bin/env python3
"""승인된 김웅 이미지를 image-to-video 입력용으로 전처리한다 (Pillow만 사용, 모델 없음).

출력 (assets/ref/):
  kimung_ref_9x16_test.png  480x854  — 블러 배경 위에 원본을 가운데 배치한 세로형 입력 (쇼츠 비율로 바로 생성하고 싶을 때)
  kimung_ref_square_512.png 512x512  — 원본 비율을 유지하며 정방형으로 패딩한 입력
원본 kimung_ref_approved.png 는 수정하지 않는다.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent


def fit_on_blur(src: Image.Image, w: int, h: int, blur: float = 24.0, dim: float = 0.9) -> Image.Image:
    bg = src.copy()
    scale = max(w / bg.width, h / bg.height)
    bg = bg.resize((round(bg.width * scale), round(bg.height * scale)), Image.LANCZOS)
    left, top = (bg.width - w) // 2, (bg.height - h) // 2
    bg = bg.crop((left, top, left + w, top + h)).filter(ImageFilter.GaussianBlur(blur))
    bg = ImageEnhance.Brightness(bg).enhance(dim)
    fg = src.copy()
    scale = min(w / fg.width, h / fg.height)
    fg = fg.resize((round(fg.width * scale), round(fg.height * scale)), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    return bg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=str(ROOT / "assets/ref/kimung_ref_approved.png"))
    ap.add_argument("--outdir", default=str(ROOT / "assets/ref"))
    ap.add_argument("--portrait", default="480x854", help="세로형 크기 WxH (기본 480x854)")
    ap.add_argument("--square", type=int, default=512)
    args = ap.parse_args()

    src = Image.open(args.input).convert("RGB")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"입력: {args.input} {src.size}")

    pw, ph = (int(x) for x in args.portrait.lower().split("x"))
    p = fit_on_blur(src, pw, ph)
    p_path = outdir / "kimung_ref_9x16_test.png"
    p.save(p_path, optimize=True)
    print(f"세로형 입력: {p_path} {p.size}")

    s = fit_on_blur(src, args.square, args.square)
    s_path = outdir / "kimung_ref_square_512.png"
    s.save(s_path, optimize=True)
    print(f"정방형 입력: {s_path} {s.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
