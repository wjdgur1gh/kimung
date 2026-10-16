#!/usr/bin/env python3
"""김웅 제작 환경 점검 — 표준 라이브러리만 사용 (클라우드·맥 공통).

사용:  python3 scripts/check_env.py [--json 저장경로] [--path 추가디스크경로 ...]
출력:  CPU / RAM / 디스크 / GPU(CUDA·MPS·Apple) / FFmpeg / Python / LTX Desktop 설치 상태 / 판정
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

NEEDED_FILTERS = ["zoompan", "drawtext", "gblur", "overlay", "fade", "afade", "anullsrc", "amix", "concat", "xfade"]


def sh(cmd: list[str], timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def gib(nbytes: float) -> float:
    return round(nbytes / 2**30, 1)


def cpu_info() -> dict:
    d = {"arch": platform.machine(), "logical_cores": os.cpu_count(), "model": ""}
    if sys.platform == "darwin":
        d["model"] = sh(["sysctl", "-n", "machdep.cpu.brand_string"])
        d["performance_cores"] = sh(["sysctl", "-n", "hw.perflevel0.physicalcpu"])
        d["efficiency_cores"] = sh(["sysctl", "-n", "hw.perflevel1.physicalcpu"])
    elif sys.platform.startswith("linux"):
        try:
            m = re.search(r"model name\s*:\s*(.+)", Path("/proc/cpuinfo").read_text())
            d["model"] = m.group(1).strip() if m else ""
        except OSError:
            pass
    return d


def ram_info() -> dict:
    if sys.platform == "darwin":
        total = int(sh(["sysctl", "-n", "hw.memsize"]) or 0)
        return {"total_gib": gib(total), "available_gib": None, "note": "통합 메모리(CPU/GPU 공유)"}
    if sys.platform.startswith("linux"):
        vals = {}
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                k, _, v = line.partition(":")
                vals[k.strip()] = int(v.strip().split()[0]) * 1024
        except OSError:
            pass
        return {"total_gib": gib(vals.get("MemTotal", 0)), "available_gib": gib(vals.get("MemAvailable", 0)), "note": ""}
    return {"total_gib": None, "available_gib": None, "note": "unsupported platform"}


def disk_info(paths: list[str]) -> dict:
    out = {}
    for p in paths:
        try:
            u = shutil.disk_usage(p)
            out[p] = {"total_gb": round(u.total / 1e9, 1), "free_gb": round(u.free / 1e9, 1)}
        except OSError as e:
            out[p] = {"error": str(e)}
    return out


def gpu_info() -> dict:
    d: dict = {"nvidia": [], "apple": None, "torch": None, "cuda": None, "mps": None}
    if shutil.which("nvidia-smi"):
        out = sh(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
        d["nvidia"] = [l.strip() for l in out.splitlines() if l.strip()]
    if sys.platform == "darwin":
        out = sh(["system_profiler", "SPDisplaysDataType"], timeout=60)
        chip = re.search(r"Chipset Model:\s*(.+)", out)
        cores = re.search(r"Total Number of Cores:\s*(\d+)", out)
        metal = re.search(r"Metal(?: Support)?:\s*(.+)", out)
        d["apple"] = {
            "chip": chip.group(1).strip() if chip else "",
            "gpu_cores": int(cores.group(1)) if cores else None,
            "metal": metal.group(1).strip() if metal else "",
        }
    try:
        import torch  # type: ignore

        d["torch"] = torch.__version__
        d["cuda"] = bool(torch.cuda.is_available())
        d["mps"] = bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
    except Exception:
        d["torch"] = None
    return d


def ffmpeg_info() -> dict:
    path = shutil.which("ffmpeg")
    if not path:
        return {"path": None}
    ver = sh([path, "-version"]).splitlines()
    filters = sh([path, "-hide_banner", "-filters"])
    encoders = sh([path, "-hide_banner", "-encoders"])
    missing = [f for f in NEEDED_FILTERS if not re.search(rf"\s{re.escape(f)}\s", filters)]
    return {
        "path": path,
        "version": ver[0] if ver else "",
        "ffprobe": shutil.which("ffprobe"),
        "libx264": " libx264 " in encoders,
        "aac": " aac " in encoders,
        "missing_filters": missing,
    }


def ltx_desktop_info() -> dict:
    if sys.platform != "darwin":
        return {"applicable": False, "note": "macOS 전용 점검 항목"}
    app = Path("/Applications/LTX Desktop.app")
    data = Path.home() / "Library/Application Support/LTXDesktop"
    models = data / "models"
    d: dict = {
        "applicable": True,
        "app_installed": app.exists(),
        "app_version": None,
        "data_dir": str(data),
        "data_dir_exists": data.exists(),
        "models_dir_exists": models.exists(),
        "models_size": None,
    }
    plist = app / "Contents/Info.plist"
    if plist.exists():
        d["app_version"] = sh(["defaults", "read", str(plist), "CFBundleShortVersionString"])
    if models.exists():
        du = sh(["du", "-sh", str(models)], timeout=300)
        d["models_size"] = du.split("\t")[0] if du else None
    return d


def verdict(ram: dict, gpu: dict) -> dict:
    total = ram.get("total_gib") or 0
    if gpu["nvidia"]:
        return {"local_video_generation": "cuda", "detail": f"NVIDIA GPU 감지: {gpu['nvidia']}"}
    if sys.platform == "darwin" and platform.machine() == "arm64":
        if total >= 32:
            return {"local_video_generation": "mps",
                    "detail": f"Apple Silicon + 총 RAM {total} GiB ≥ 32 GiB → LTX Desktop 로컬 생성 요건 충족 (README 기준)"}
        return {"local_video_generation": "none",
                "detail": f"Apple Silicon 이지만 총 RAM {total} GiB < 32 GiB → LTX Desktop 로컬 생성 불가"}
    return {"local_video_generation": "none",
            "detail": "GPU 없음 → 대용량 모델 다운로드·CPU 영상 생성을 시작하지 않는다 (FFmpeg 편집만 가능)"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", help="결과를 JSON 파일로 저장")
    ap.add_argument("--path", action="append", default=[], help="디스크 여유를 볼 추가 경로")
    args = ap.parse_args()

    paths = [os.getcwd(), str(Path.home())] + args.path
    report = {
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
                     "macos": sh(["sw_vers", "-productVersion"]) if sys.platform == "darwin" else None,
                     "hostname": platform.node()},
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "cpu": cpu_info(),
        "ram": ram_info(),
        "disk": disk_info(paths),
        "gpu": gpu_info(),
        "ffmpeg": ffmpeg_info(),
        "ltx_desktop": ltx_desktop_info(),
    }
    report["verdict"] = verdict(report["ram"], report["gpu"])

    def row(k: str, v) -> None:
        print(f"  {k:<22} {v}")

    print("== 플랫폼 ==")
    row("system", f"{report['platform']['system']} {report['platform']['release']} ({report['platform']['machine']})")
    if report["platform"]["macos"]:
        row("macOS", report["platform"]["macos"])
    row("python", f"{report['python']['version']}  {report['python']['executable']}")
    print("== CPU / RAM ==")
    row("cpu", f"{report['cpu']['model']}  x{report['cpu']['logical_cores']}")
    row("ram", f"총 {report['ram']['total_gib']} GiB, 사용가능 {report['ram']['available_gib']} GiB {report['ram']['note']}")
    print("== 디스크 ==")
    for p, v in report["disk"].items():
        row(p, v)
    print("== GPU ==")
    row("nvidia", report["gpu"]["nvidia"] or "없음")
    row("apple", report["gpu"]["apple"] or "해당 없음")
    row("torch", f"{report['gpu']['torch']}  cuda={report['gpu']['cuda']} mps={report['gpu']['mps']}")
    print("== FFmpeg ==")
    for k, v in report["ffmpeg"].items():
        row(k, v)
    print("== LTX Desktop ==")
    for k, v in report["ltx_desktop"].items():
        row(k, v)
    print("== 판정 ==")
    row("local generation", report["verdict"]["local_video_generation"])
    row("detail", report["verdict"]["detail"])

    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(f"\nJSON 저장: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
