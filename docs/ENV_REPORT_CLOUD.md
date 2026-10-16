# 클라우드 환경 점검 결과 (2026-10-16)

이 문서의 수치는 **이 세션의 클라우드 컨테이너에서 직접 실행해 확인한 값**이다. 사용자의 맥(MacBook Pro 16, M5 Pro, 48 GB, 여유 약 502.8 GB)과는 전혀 다른 기계다.

## 하드웨어

| 항목 | 값 | 확인 명령 |
|---|---|---|
| CPU | Intel Xeon @ 2.10 GHz, 4 vCPU (x86_64, 1 thread/core) | `nproc`, `lscpu` |
| RAM | 총 15 GiB, 사용 가능 15 GiB, 스왑 0 | `free -h` |
| 디스크 | 루트 252 GB 중 여유 30 GB (세션별 쓰기 할당량 기준) | `df -h /` |
| GPU | **없음** — `nvidia-smi` 없음, `/dev/nvidia*` 없음, `lspci` 에 GPU 항목 없음 | `nvidia-smi`, `ls /dev/nvidia*`, `lspci` |
| GPU 메모리 | 해당 없음 | — |

## 소프트웨어

| 항목 | 값 |
|---|---|
| 작업용 Python | `/opt/kimung-venv/bin/python` → Python 3.13.16 |
| venv 패키지 | pillow 12.3.0, PyYAML 6.0.3, pip 26.2.1 (torch 없음) |
| FFmpeg | `/usr/bin/ffmpeg` 6.1.1 (Ubuntu), libx264·libx265·aac 인코더, zoompan·drawtext·gblur·xfade·loudnorm 필터 확인 |
| 한글 폰트 | `/usr/share/fonts/opentype/unifont/unifont.otf`, `wqy-zenhei.ttc` (자막 테스트용) |
| 저장소 | `/home/user/kimung` (원격에 커밋 없음 → 이 브랜치가 첫 커밋), `/home/user/STUDY-2026` (HTML 3개, 이번 작업과 무관) |

## 결론

- GPU 가 없고 RAM 15 GiB, 디스크 여유 30 GB 이므로 **LTX 2.5 Fast(모델 팩 약 72 GB) 다운로드와 CPU 영상 생성은 시작하지 않았다.** 디스크 용량만으로도 불가능하다.
- 클라우드에서 실행한 것은 **FFmpeg 편집 파이프라인 검증뿐**이다 (`scripts/make_shorts.py`). 아래 파일은 AI 생성물이 아니라 편집 코드 동작 확인용이다.
  - `outputs/cloud_ffmpeg_test_still_480p.mp4` — 승인 이미지 1장 → 3초 켄번즈(줌) + 자막 + 페이드. 모델 추론 없음.
  - `outputs/cloud_ffmpeg_test_sample_480p.mp4` — 기존 힉스필드 샘플(480x854, 4초)을 같은 파이프라인으로 재구성.
- 실제 image-to-video 생성은 맥에서 `docs/MAC_SETUP.md` 절차로 진행한다.

## 네트워크 메모

이 세션의 프록시에서 `ltx.io`, `help.ltx.io`, `wiki.drawthings.ai`, `docs.comfy.org`, `apps.apple.com` 은 차단되어 원문을 읽지 못했다. LTX Desktop 검증은 전부 `github.com/Lightricks/LTX-Desktop` (README, releases, docs/) 와 릴리스 자산 `latest-mac.yml` 로 했다.
