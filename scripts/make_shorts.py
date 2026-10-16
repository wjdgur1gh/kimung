#!/usr/bin/env python3
"""김웅 쇼츠 편집 파이프라인 — FFmpeg 만 사용 (모델 추론 없음).

하위 명령:
  compose  영상 또는 이미지 1개 → 9:16 쇼츠. 블러 배경 + 가운데 배치, 자막, 페이드, 오디오 정리.
           이미지 입력이면 켄번즈(천천히 줌) 클립을 만든다.
  concat   여러 클립 → 하나. 각 클립을 같은 규격으로 맞춘 뒤 이어붙인다.
  info     ffprobe 요약 (해상도, fps, 길이, 프레임 수, 코덱, 용량).

예:
  python3 scripts/make_shorts.py compose --input outputs/test_shot_01_raw.mp4 \
      --output outputs/test_shot_01_shorts_480p.mp4 --size test --caption "김웅 · 테스트 샷 01"
  python3 scripts/make_shorts.py compose --input assets/ref/kimung_ref_approved.png \
      --output outputs/still_test.mp4 --size test --duration 3 --zoom 1.08
  python3 scripts/make_shorts.py concat --inputs a.mp4 b.mp4 --output outputs/joined.mp4 --size test
  python3 scripts/make_shorts.py info outputs/test_shot_01_raw.mp4

--size test = 480x854 (저해상도 테스트), final = 1080x1920, 또는 WxH 직접 지정.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SIZES = {"test": (480, 854), "final": (1080, 1920)}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
FONT_CANDIDATES = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",            # macOS 기본 한글
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/Library/Fonts/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/unifont/unifont.otf",          # 이 세션의 클라우드에 있는 한글 폰트
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",        # 한글 없음(경고)
]


def need(tool: str) -> str:
    p = shutil.which(tool)
    if not p:
        sys.exit(f"[오류] {tool} 를 찾을 수 없습니다. macOS: brew install ffmpeg / Ubuntu: apt install ffmpeg")
    return p


def probe(path: str) -> dict:
    out = subprocess.run(
        [need("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def summarize(path: str) -> dict:
    info = probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
    fps = round(int(num) / int(den or 1), 3) if den else None
    return {
        "file": path,
        "size_bytes": int(info["format"].get("size", 0)),
        "duration_s": round(float(info["format"].get("duration", 0)), 3),
        "video": {"codec": v.get("codec_name"), "width": v.get("width"), "height": v.get("height"),
                  "fps": fps, "nb_frames": v.get("nb_frames"), "pix_fmt": v.get("pix_fmt")},
        "audio": None if a is None else {"codec": a.get("codec_name"), "sample_rate": a.get("sample_rate"),
                                         "channels": a.get("channels")},
    }


def parse_size(s: str) -> tuple[int, int]:
    if s in SIZES:
        return SIZES[s]
    w, h = (int(x) for x in s.lower().split("x"))
    if w % 2 or h % 2:
        sys.exit("[오류] 가로·세로는 짝수여야 합니다 (libx264 yuv420p)")
    return w, h


def pick_font(explicit: str | None) -> str | None:
    if explicit:
        if not Path(explicit).exists():
            sys.exit(f"[오류] 폰트 파일 없음: {explicit}")
        return explicit
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            if "DejaVu" in f:
                print("[경고] 한글 폰트를 찾지 못해 DejaVuSans 를 씁니다. 한글 자막은 깨집니다. --font 로 지정하세요.", file=sys.stderr)
            return f
    print("[경고] 사용할 폰트를 찾지 못했습니다. 자막을 건너뜁니다.", file=sys.stderr)
    return None


def fe(s: str) -> str:
    """filtergraph 옵션 값 이스케이프 (경로용)."""
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _cw(ch: str) -> float:
    """글자 폭 추정(fontsize 배수): 한글·CJK·전각 1.0, 그 외 0.55."""
    o = ord(ch)
    if 0x1100 <= o <= 0x11FF or 0x3000 <= o <= 0x9FFF or 0xAC00 <= o <= 0xD7A3 or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF:
        return 1.0
    return 0.55


def wrap_caption(text: str, max_width_px: float, fs: int) -> list[str]:
    """자막 줄바꿈: 명시적 줄바꿈 유지, 폭에 맞춰 단어 단위로 접고 긴 단어는 글자 단위로 자른다."""
    limit = max_width_px / fs
    width = lambda t: sum(_cw(c) for c in t)
    out: list[str] = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            cand = f"{cur} {w}" if cur else w
            if width(cand) <= limit:
                cur = cand
                continue
            if cur:
                out.append(cur)
            cur = ""
            for ch in w:
                if cur and width(cur + ch) > limit:
                    out.append(cur)
                    cur = ""
                cur += ch
        out.append(cur)
    return [l for l in out if l.strip()] or [text]


def run(cmd: list[str], dry: bool) -> None:
    print("$ " + " ".join(f"'{c}'" if " " in c or "[" in c else c for c in cmd))
    if dry:
        return
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"[오류] ffmpeg 종료 코드 {r.returncode}")


def build_compose(args, inp: str, out: str, caption: str | None, tmpdir: str) -> list[str]:
    W, H = parse_size(args.size)
    fps = args.fps
    fade = args.fade
    is_img = Path(inp).suffix.lower() in IMAGE_EXT
    inputs: list[str] = []
    parts: list[str] = []

    if is_img:
        D = float(args.duration)
        N = max(int(round(fps * D)), 2)
        inputs += ["-i", inp]
        zoom = max(float(args.zoom), 1.0)
        parts += [
            "[0:v]split=2[bg0][fg0]",
            f"[bg0]scale={2*W}:{2*H}:force_original_aspect_ratio=increase,crop={2*W}:{2*H},gblur=sigma=30,eq=brightness=-0.08[bg]",
            f"[fg0]scale={2*W}:{2*H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos[fg]",
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[comp]",
            f"[comp]zoompan=z='1+({zoom}-1)*on/{N-1}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s={W}x{H}:fps={fps}[v0]",
        ]
        src_audio = False
    else:
        info = probe(inp)
        D = float(info["format"]["duration"])
        src_audio = any(s["codec_type"] == "audio" for s in info["streams"]) and not args.mute
        inputs += ["-i", inp]
        parts += [
            "[0:v]split=2[bg0][fg0]",
            f"[bg0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=20,eq=brightness=-0.08[bg]",
            f"[fg0]scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos[fg]",
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={fps}[v0]",
        ]

    # 자막
    vchain = []
    font = pick_font(args.font) if caption else None
    if caption and font:
        fs = int(H * args.caption_scale)
        lines = wrap_caption(caption, max_width_px=W * 0.88, fs=fs)
        lh = int(fs * 1.5)                      # 줄 높이(박스 포함)
        top = f"h*{args.caption_y}-{lh * len(lines) / 2:.1f}"
        for i, line in enumerate(lines):        # 줄마다 따로 그려 각 줄을 가운데 정렬
            tf = Path(tmpdir) / f"caption_{i}.txt"
            tf.write_text(line, encoding="utf-8")
            vchain.append(
                f"drawtext=fontfile='{fe(font)}':textfile='{fe(str(tf))}':fontcolor=white:fontsize={fs}"
                f":x=(w-text_w)/2:y={top}+{i * lh}:box=1:boxcolor=black@0.45:boxborderw={max(fs // 5, 5)}"
            )
    if fade > 0:
        vchain += [f"fade=t=in:st=0:d={fade}", f"fade=t=out:st={max(D-fade,0):.3f}:d={fade}"]
    vchain.append("format=yuv420p")
    parts.append("[v0]" + ",".join(vchain) + "[v]")

    # 오디오: 원본 → 없으면 무음 트랙, 선택적 BGM 믹스
    idx = 1
    afade = f"afade=t=in:st=0:d={fade},afade=t=out:st={max(D-fade,0):.3f}:d={fade}," if fade > 0 else ""
    if src_audio:
        parts.append(f"[0:a]{afade}aresample=48000,aformat=channel_layouts=stereo[a0]")
    else:
        inputs += ["-f", "lavfi", "-t", f"{D:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        parts.append(f"[{idx}:a]anull[a0]")
        idx += 1
    if args.bgm:
        inputs += ["-stream_loop", "-1", "-i", args.bgm]
        parts.append(f"[{idx}:a]volume={args.bgm_volume},{afade}aresample=48000,aformat=channel_layouts=stereo[bgm]")
        parts.append("[a0][bgm]amix=inputs=2:duration=first:normalize=0[a]")
        idx += 1
    else:
        parts.append("[a0]anull[a]")

    crf = str(args.crf if args.crf is not None else (18 if args.size == "final" else 23))
    cmd = [need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-stats", "-y", *inputs,
           "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]", "-t", f"{D:.3f}",
           "-c:v", "libx264", "-preset", args.preset, "-crf", crf, "-pix_fmt", "yuv420p", "-r", str(fps),
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", out]
    return cmd


def cmd_compose(args) -> int:
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        run(build_compose(args, args.input, args.output, args.caption, td), args.dry_run)
    if not args.dry_run:
        print(json.dumps(summarize(args.output), ensure_ascii=False, indent=2))
    return 0


def cmd_concat(args) -> int:
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        normalized = []
        for i, inp in enumerate(args.inputs):
            tmp_out = str(Path(td) / f"part_{i:03d}.mp4")
            run(build_compose(args, inp, tmp_out, None, td), args.dry_run)
            normalized.append(tmp_out)
        lst = Path(td) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in normalized))
        crf = str(args.crf if args.crf is not None else (18 if args.size == "final" else 23))
        cmd = [need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-stats", "-y", "-f", "concat", "-safe", "0",
               "-i", str(lst), "-c:v", "libx264", "-preset", args.preset, "-crf", crf, "-pix_fmt", "yuv420p", "-r", str(args.fps),
               "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", args.output]
        run(cmd, args.dry_run)
    if not args.dry_run:
        print(json.dumps(summarize(args.output), ensure_ascii=False, indent=2))
    return 0


def cmd_info(args) -> int:
    for p in args.files:
        print(json.dumps(summarize(p), ensure_ascii=False, indent=2))
    return 0


def add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--size", default="test", help="test(480x854) | final(1080x1920) | WxH")
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--fade", type=float, default=0.3, help="페이드 인/아웃 초 (0 이면 없음)")
    p.add_argument("--duration", type=float, default=3.0, help="이미지 입력일 때 클립 길이(초)")
    p.add_argument("--zoom", type=float, default=1.08, help="이미지 입력일 때 최종 줌 배율 (1.0 = 줌 없음)")
    p.add_argument("--mute", action="store_true", help="원본 오디오 버리고 무음 트랙")
    p.add_argument("--bgm", help="배경음 파일 (루프, duration=first)")
    p.add_argument("--bgm-volume", type=float, default=0.25)
    p.add_argument("--font", help="자막 폰트 파일 경로 (기본: 시스템 한글 폰트 자동 탐색)")
    p.add_argument("--caption-scale", type=float, default=0.045, help="자막 크기 = 세로 해상도 × 이 값")
    p.add_argument("--caption-y", type=float, default=0.80, help="자막 세로 위치 비율 (0=상단, 1=하단)")
    p.add_argument("--crf", type=int, default=None, help="x264 품질 (기본 test 23 / final 18)")
    p.add_argument("--preset", default="medium")
    p.add_argument("--dry-run", action="store_true", help="ffmpeg 명령만 출력")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compose", help="영상/이미지 1개 → 쇼츠")
    c.add_argument("--input", required=True)
    c.add_argument("--output", required=True)
    c.add_argument("--caption", help="자막 문구 (줄바꿈 가능)")
    add_common(c)
    c.set_defaults(fn=cmd_compose)

    k = sub.add_parser("concat", help="여러 클립 → 하나")
    k.add_argument("--inputs", nargs="+", required=True)
    k.add_argument("--output", required=True)
    add_common(k)
    k.set_defaults(fn=cmd_concat)

    i = sub.add_parser("info", help="ffprobe 요약")
    i.add_argument("files", nargs="+")
    i.set_defaults(fn=cmd_info)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
