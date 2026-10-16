#!/usr/bin/env bash
# 김웅 AI 쇼츠 — 맥(Apple Silicon) 준비 스크립트.
# 기본 동작은 "점검과 계획 출력"뿐이다. 설치·다운로드는 플래그로 명시해야 하며, 어떤 파일도 지우지 않는다.
# 모델 가중치(약 72 GB)는 이 스크립트가 받지 않는다 — LTX Desktop 첫 실행 화면에서 받는다.
#
#   bash scripts/mac_setup.sh                  # 점검만
#   bash scripts/mac_setup.sh --install-ffmpeg # brew install ffmpeg
#   bash scripts/mac_setup.sh --make-venv      # ~/kimung-venv 생성 + pillow, pyyaml
#   bash scripts/mac_setup.sh --download-app   # LTX Desktop 1.3.0 dmg (742 MB) 다운로드 + sha512 검증
#   bash scripts/mac_setup.sh --all --yes      # 위 전부, 확인 질문 생략
set -euo pipefail

LTX_VERSION="1.3.0"
LTX_DMG_NAME="LTX-Desktop-arm64.dmg"
LTX_DMG_URL="https://github.com/Lightricks/LTX-Desktop/releases/download/v${LTX_VERSION}/${LTX_DMG_NAME}"
LTX_DMG_SIZE=741762436                      # bytes, 릴리스 자산 latest-mac.yml (2026-10-09)
LTX_DMG_SHA512_B64="JI+qiloPkGSrUXzA3zwNwFi3M4K5Zs9EQHExHUTuLEkt9Sj97xhM2sFAOkEviRQv9KfAsIuTzfybNIY+OqXSDw=="
DL_DIR="${KIMUNG_DL_DIR:-$HOME/Downloads/kimung}"
VENV_DIR="${KIMUNG_VENV:-$HOME/kimung-venv}"
MODEL_PACK_GB=72                            # LTX 2.5 Fast 코어 팩, README 기준

DO_FFMPEG=0; DO_VENV=0; DO_APP=0; YES=0
for a in "$@"; do
  case "$a" in
    --install-ffmpeg) DO_FFMPEG=1 ;;
    --make-venv)      DO_VENV=1 ;;
    --download-app)   DO_APP=1 ;;
    --all)            DO_FFMPEG=1; DO_VENV=1; DO_APP=1 ;;
    --yes|-y)         YES=1 ;;
    -h|--help)        sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "알 수 없는 옵션: $a"; exit 2 ;;
  esac
done

ok()   { printf '  \033[32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m[주의]\033[0m %s\n' "$*"; }
bad()  { printf '  \033[31m[불가]\033[0m %s\n' "$*"; }
confirm() { [ "$YES" = 1 ] && return 0; read -r -p "$1 [y/N] " r; [[ "$r" =~ ^[Yy]$ ]]; }

echo "== 1. 맥 점검 =="
if [ "$(uname -s)" != "Darwin" ]; then bad "macOS 가 아닙니다 ($(uname -s)). 이 스크립트는 맥 전용입니다."; exit 1; fi
ARCH=$(uname -m); OSV=$(sw_vers -productVersion)
[ "$ARCH" = "arm64" ] && ok "Apple Silicon ($ARCH)" || { bad "Intel 맥($ARCH): LTX Desktop 로컬 생성 불가 (README)"; }
OSMAJ=${OSV%%.*}
[ "$OSMAJ" -ge 13 ] && ok "macOS $OSV (13 이상 필요)" || bad "macOS $OSV: 13 이상 필요"
RAM_GIB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
[ "$RAM_GIB" -ge 32 ] && ok "총 RAM ${RAM_GIB} GiB (32 GiB 이상 필요)" || bad "총 RAM ${RAM_GIB} GiB < 32 GiB: 로컬 생성 불가"
FREE_GB=$(df -g "$HOME" | awk 'NR==2{print $4}')
[ "$FREE_GB" -ge $((MODEL_PACK_GB + 10)) ] && ok "디스크 여유 ${FREE_GB} GB (모델 팩 약 ${MODEL_PACK_GB} GB + 앱 1 GB 필요)" || bad "디스크 여유 ${FREE_GB} GB 부족"
CHIP=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "?"); ok "칩: $CHIP"
if xcode-select -p >/dev/null 2>&1; then ok "Xcode 명령행 도구 있음"; else warn "Xcode 명령행 도구 없음 → xcode-select --install (MPS 확장 빌드에 필요, docs/mps-attention-memory-leak.md)"; fi
command -v brew   >/dev/null && ok "Homebrew $(brew --version | head -1)" || warn "Homebrew 없음 (ffmpeg 설치에 필요) https://brew.sh"
command -v ffmpeg >/dev/null && ok "ffmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3)" || warn "ffmpeg 없음 → --install-ffmpeg"
command -v python3 >/dev/null && ok "python3 $(python3 --version 2>&1)" || warn "python3 없음"
[ -d "/Applications/LTX Desktop.app" ] && ok "LTX Desktop 설치됨: $(defaults read '/Applications/LTX Desktop.app/Contents/Info.plist' CFBundleShortVersionString 2>/dev/null)" || warn "LTX Desktop 미설치"
MODELS="$HOME/Library/Application Support/LTXDesktop/models"
[ -d "$MODELS" ] && ok "모델 폴더: $MODELS ($(du -sh "$MODELS" 2>/dev/null | cut -f1))" || warn "모델 폴더 없음 (첫 실행 설정에서 생성)"

echo
echo "== 2. 계획 =="
[ "$DO_FFMPEG" = 1 ] && echo "  - brew install ffmpeg (약 수백 MB)"
[ "$DO_VENV" = 1 ]   && echo "  - python3 -m venv $VENV_DIR ; pip install pillow pyyaml (약 20 MB)"
[ "$DO_APP" = 1 ]    && echo "  - $LTX_DMG_URL → $DL_DIR/$LTX_DMG_NAME ($(( LTX_DMG_SIZE / 1024 / 1024 )) MiB), sha512 검증"
echo "  - 모델 팩(약 ${MODEL_PACK_GB} GB)은 이 스크립트가 받지 않는다. LTX Desktop 첫 실행 설정에서 받으며 저장 위치는 그때 고른다."
if [ "$DO_FFMPEG$DO_VENV$DO_APP" = "000" ]; then echo "  (실행할 작업 없음. 옵션 없이 실행했으므로 점검만 했다.)"; exit 0; fi
confirm "위 작업을 진행할까요?" || { echo "중단"; exit 0; }

if [ "$DO_FFMPEG" = 1 ]; then
  echo "== 3. ffmpeg =="
  command -v ffmpeg >/dev/null && ok "이미 설치됨, 건너뜀" || brew install ffmpeg
fi

if [ "$DO_VENV" = 1 ]; then
  echo "== 4. Python venv =="
  [ -d "$VENV_DIR" ] || python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install -U pip pillow pyyaml
  ok "$VENV_DIR/bin/python"
fi

if [ "$DO_APP" = 1 ]; then
  echo "== 5. LTX Desktop $LTX_VERSION 다운로드 =="
  mkdir -p "$DL_DIR"; DST="$DL_DIR/$LTX_DMG_NAME"
  if [ -f "$DST" ] && [ "$(stat -f %z "$DST")" = "$LTX_DMG_SIZE" ]; then
    ok "이미 받은 파일이 있음 (크기 일치), 재다운로드 생략"
  else
    curl -L --progress-bar -o "$DST" "$LTX_DMG_URL"
  fi
  SZ=$(stat -f %z "$DST")
  [ "$SZ" = "$LTX_DMG_SIZE" ] && ok "크기 일치 $SZ bytes" || { bad "크기 불일치 $SZ ≠ $LTX_DMG_SIZE"; exit 1; }
  SUM=$(openssl dgst -sha512 -binary "$DST" | base64)
  [ "$SUM" = "$LTX_DMG_SHA512_B64" ] && ok "sha512 일치 (latest-mac.yml)" || { bad "sha512 불일치 — 파일을 쓰지 말 것"; exit 1; }
  echo
  echo "다음: open \"$DST\"  → 창에서 'LTX Desktop' 을 Applications 로 끌어넣기 → 실행 → docs/MAC_SETUP.md 4장(첫 실행 설정)"
fi
