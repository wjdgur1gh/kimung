# 맥(Apple Silicon) 설치·테스트 절차 — LTX Desktop 1.3.0

범례: 📄 공식 문서로 확인한 사실 · ⏳ 맥에서 아직 실행하지 않은 절차 · ⚠️ 주의

이 문서의 모든 절차는 **아직 맥에서 실행하지 않았다.** 사실 관계는 2026-10-16 기준 Lightricks 공식 GitHub(README, Releases v1.3.0, docs/)에서 확인했다.

## 1. 요구사항 대조 📄

| 요구사항 (LTX Desktop README / docs/local-compat-matrix.md) | 내 맥 (M5 Pro 48 GB) | 판정 |
|---|---|---|
| Apple Silicon(arm64) 필수, Intel 맥은 로컬 생성 불가 | M5 Pro | 충족 |
| 총 물리 RAM 32 GiB 이상 (1.3.0 릴리스 노트: 32 GB 기기도 로컬 허용) | 48 GB | 충족 |
| macOS 13(Ventura) 이상 | 맥에서 `sw_vers` 로 확인 필요 | ⏳ |
| 디스크: LTX 2.5 Fast 코어 팩 약 72 GB (+앱 0.75 GB) | 여유 약 502.8 GB | 충족 |
| 테스트된 기종: M4 Pro 48 GB (1.1.0 릴리스 노트) | M5 Pro 는 문서에 언급 없음 | ⚠️ 동작은 실행해 봐야 안다 |
| macOS 로컬 지원 기능: T2V, I2V, A2V, LoRA, IC-LoRA, Retake, Extend, 로컬 텍스트 인코더, 2.5 다운로드 모두 "Yes" | — | 충족 |

## 2. 다운로드 용량과 위치 (대용량 다운로드 전 고지) 📄

| 대상 | 크기 | 저장 위치 | 비고 |
|---|---|---|---|
| LTX Desktop 앱 `LTX-Desktop-arm64.dmg` | 741,762,436 bytes (약 707 MiB) | `~/Downloads/kimung/` → `/Applications/` | v1.3.0 (2026-10-09). 릴리스 자산 `latest-mac.yml` 의 sha512 로 검증 |
| LTX 2.5 Fast 코어 팩 (transformer, text encoder, VAE) | **약 72 GB** | 첫 실행 설정에서 고르는 모델 폴더. 기본값 `~/Library/Application Support/LTXDesktop/models/` | Hugging Face 로그인 + 라이선스 동의 필요(게이트됨). 계정은 무료 |
| 로컬 텍스트 인코더 | README 에 별도 크기 없음 | 같은 모델 폴더 | 앱 설정 화면의 표시 용량을 보고 진행 |
| "kitchen-sink" 설치 (2.3 + 이미지 모델 + 프로세서 + 프롬프트 향상기) | 72 GB 보다 큼, 정확한 수치 없음 | — | **첫 테스트에는 받지 않는다** |

앱 설치 후 디스크 사용 예상: 약 73 GB (502.8 GB 중). 모델 폴더를 외장 디스크로 두고 싶으면 첫 실행 설정에서 경로를 바꾼다.

⚠️ 유료 요소 구분: README 기준으로 **로컬 생성은 무료**다. "클라우드 텍스트 인코딩"과 "프롬프트 향상"은 무료지만 LTX API 키(계정)가 필요하고, "API 영상 생성(2.5 Fast/Pro, Retake)"은 유료다. 이 프로젝트에서는 API 키를 등록하지 않고 로컬 텍스트 인코더만 쓴다.

## 3. 설치 절차 ⏳

터미널에서 순서대로 실행한다. 어느 단계도 기존 파일을 지우지 않는다.

```bash
# 3-1. 기본 점검
sw_vers                                  # macOS 13 이상인지
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GiB"}'
df -h ~                                  # 여유 공간
xcode-select -p || xcode-select --install   # Xcode 명령행 도구 (docs/mps-attention-memory-leak.md: 없으면 번들 빌드 실패 사례)

# 3-2. 저장소와 편집용 Python
git clone https://github.com/wjdgur1gh/kimung.git ~/kimung && cd ~/kimung
python3 -m venv ~/kimung-venv && ~/kimung-venv/bin/pip install -U pip pillow pyyaml
~/kimung-venv/bin/python scripts/check_env.py --json docs/env_mac.json

# 3-3. FFmpeg (편집 스크립트용, Homebrew)
brew install ffmpeg                      # 이미 있으면 생략

# 3-4. LTX Desktop 앱 다운로드 + sha512 검증 (742 MB)
bash scripts/mac_setup.sh --download-app     # 용량을 먼저 보여주고 확인을 받은 뒤 받는다
open ~/Downloads/kimung/LTX-Desktop-arm64.dmg   # 창에서 앱을 Applications 로 끌어넣기
```

⚠️ 처음 열 때 macOS 가 막으면 Finder 에서 앱을 우클릭 → 열기. (공증 여부는 문서에 명시가 없다.)

## 4. 첫 실행 설정 ⏳ (README "first-run setup")

1. 앱 실행 → 설정 마법사에서 **모델 폴더** 선택 (기본 `~/Library/Application Support/LTXDesktop/models/`).
2. 모델 선택: **LTX 2.5 Fast 코어 팩만** 선택 (약 72 GB). kitchen-sink, 2.3, Z-Image 등은 선택 해제.
3. **로컬 텍스트 인코더**를 켠다. LTX API 키 입력란은 비워 둔다.
4. Hugging Face 로그인 → 2.5 가중치 라이선스 동의 → 다운로드. (인터넷 필요. 완료까지 회선 속도에 따라 수십 분~수 시간.)
5. 다운로드 후 `~/kimung-venv/bin/python scripts/check_env.py` 를 다시 실행해 앱 버전과 모델 폴더 크기를 `docs/MAC_TEST_LOG.md` 에 적는다.

## 5. 첫 테스트: test_shot_01 ⏳

설정값은 `configs/test_shot_01.yaml` 에 있다.

1. (선택) `~/kimung-venv/bin/python scripts/prep_reference.py` 로 세로형 입력 이미지 `assets/ref/kimung_ref_9x16_test.png` 를 만든다. 원본 `kimung_ref_approved.png` 를 그대로 써도 된다.
2. LTX Desktop → Image to Video → 입력 이미지 선택 → `prompt_en` 붙여넣기.
3. 해상도: **가장 낮은 프리셋(540p 이하)**. 길이 **2초**, 24 fps, 시드 20261016.
   - 근거 📄 `docs/mps-attention-memory-leak.md`: 48 GB M4 Pro 에서 5초(121프레임)는 메모리 누수로 완료 못 함, 49프레임(약 2초)·480×256 1단계는 약 5 GB 로 안정, 2단계 업스케일 최고 29 GB. 1.2.7 릴리스 노트에 "Apple Silicon 메모리 급증 수정"이 있지만 1.3.0 에서 2초 초과는 직접 확인 전까지 보수적으로 간다.
   - 근거 📄 1.3.0 릴리스 노트: 720p 이상은 맥에서 느릴 수 있다는 경고가 뜬다.
4. 생성 시작 → 활성 상태 보기에서 메모리 최고치와 소요 시간을 적는다.
5. 결과 mp4 를 `outputs/test_shot_01_raw.mp4` 로 저장.
6. 쇼츠 규격으로 편집:
   ```bash
   ~/kimung-venv/bin/python scripts/make_shorts.py info outputs/test_shot_01_raw.mp4
   ~/kimung-venv/bin/python scripts/make_shorts.py compose \
     --input outputs/test_shot_01_raw.mp4 --output outputs/test_shot_01_shorts_480p.mp4 \
     --size test --caption "김웅 · 테스트 샷 01"
   ```
7. `docs/MAC_TEST_LOG.md` 를 채우고 커밋한다 (mp4 는 git 제외).

## 6. 문제가 생기면 📄

| 증상 | 원인·대응 (출처) |
|---|---|
| 디노이즈 중 메모리가 계속 늘고 멈춤, 앱이 백엔드를 재시작 | MPS 어텐션 메모리 누수. 프레임 수를 49(2초)로 줄인다. 재시작은 복구만 될 뿐 누수를 막지 못한다 (docs/mps-attention-memory-leak.md) |
| 720p 선택 시 느림 경고 | 맥에서는 540p 이하로 (1.3.0 릴리스 노트) |
| LoRA 결과가 녹색/회색 프레임 | 1.3.0 에서 수정됨. 앱 버전 확인 |
| RAM 32 GB 기기에서 로컬 생성 불가 표시 | 1.3.0 에서 수정됨 |
| 처음 실행 시 "약 15 GB 여유 RAM" 검사 실패 → API 전용 모드 | 다른 앱을 닫고 앱을 재실행 (1.1.0 릴리스 노트: 실행 시 1회 검사) |
| Xcode 명령행 도구 없음 | `xcode-select --install` 후 재실행 |

## 7. 대안 도구 (LTX Desktop 이 안 될 때)

| 도구 | 검증 상태 | 메모 |
|---|---|---|
| ComfyUI (수동 설치 / Desktop) | 📄 공식 docs(Comfy-Org/docs 저장소): macOS Apple Silicon M1~M4 지원, PyTorch MPS 백엔드, Python 3.13 권장. Desktop 맥(ARM) 버전은 베타 | LTX-2 fp8 체크포인트는 MPS 에서 안 돌므로 bf16 계열만 가능. 워크플로우 구성은 아직 안 함 |
| Draw Things (Mac App Store, 무료) | ⚠️ 이 세션에서 공식 위키·App Store 페이지가 차단되어 **검색 결과 요약만 확인**: LTX-2/2.3, Wan 2.2 5B/14B I2V 지원 | 맥에서 App Store 설명을 직접 확인한 뒤 판단 |
| 커뮤니티 MLX 포트(ltx-2-mlx 등) | 비공식. 공식 문서 검증 대상 아님 | 사용하지 않음 |

## 출처

- https://github.com/Lightricks/LTX-Desktop (README: 요구사항, 모델 팩 72 GB, 텍스트 인코더, 저장 경로, 무료/유료 구분, Apache-2.0)
- https://github.com/Lightricks/LTX-Desktop/releases (v1.3.0 2026-10-09: 맥 32 GB 허용, 720p 경고, LoRA 수정 / 1.2.7: Apple Silicon 메모리 급증 수정 / 1.1.0: M4 Pro 48 GB 테스트, 15 GB 여유 RAM 검사)
- https://github.com/Lightricks/LTX-Desktop/releases/download/v1.3.0/latest-mac.yml (dmg 741,762,436 bytes, sha512)
- https://github.com/Lightricks/LTX-Desktop/blob/main/docs/local-compat-matrix.md (Darwin 지원 표, RAM 32 GiB 하한)
- https://github.com/Lightricks/LTX-Desktop/blob/main/docs/mps-attention-memory-leak.md (2초 권장 근거)
- https://github.com/Comfy-Org/docs/blob/main/installation/system_requirements.mdx (ComfyUI 맥 요구사항)
