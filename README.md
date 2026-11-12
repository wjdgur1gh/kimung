# 김웅(kimung) AI 쇼츠 드라마 — 제작 환경

유료 영상 API·힉스필드 크레딧 없이, 공개 모델을 **내 맥에서 직접 실행**해 영상을 만들기 위한 저장소다.
지금 단계의 목표는 승인된 김웅 이미지 1장으로 **저해상도 2초 테스트 영상 1개**를 만드는 것이며, 드라마 본편 제작은 시작하지 않는다.

## 상태 보드

| 항목 | 상태 | 근거 |
|---|---|---|
| 클라우드 하드웨어 점검 | ✅ 확인 완료 | `docs/ENV_REPORT_CLOUD.md` |
| 클라우드에서 모델 생성 | ⛔ 하지 않음 (GPU 없음, 4 vCPU / 15 GiB RAM) | 같은 문서 |
| FFmpeg 편집 파이프라인 | ✅ 클라우드에서 검증 (모델 추론 없음) | `outputs/` 의 `cloud_*` 파일, `docs/ENV_REPORT_CLOUD.md` |
| LTX Desktop 맥 지원 여부 | 📄 공식 문서로 확인 (1.3.0, Apple Silicon + RAM 32 GiB↑) | `docs/MAC_SETUP.md` |
| 맥 설치·첫 테스트 | ⏳ 아직 실행하지 않음 | `docs/MAC_SETUP.md`, `docs/MAC_TEST_LOG.md` |
| 힉스필드 얼굴 팩 (45도 8장 + 표정 10장) | ⏳ 프롬프트만 준비. 무제한은 Claude 채팅에서만 가능해 Claude Code 에서는 생성하지 않음 | `docs/higgsfield/KIMUNG_FACE_PACK.md` |

범례: ✅ 이 세션의 클라우드에서 실제 실행해 확인 · 📄 공식 문서(GitHub README/릴리스/docs)로 확인 · ⏳ 맥에서 아직 미실행

## 저장소 구조

```
assets/ref/      승인 김웅 이미지(원본), 참고용 기존 샘플 영상(480x854, 4초), 전처리 이미지
configs/         test_shot_01.yaml — 첫 테스트 샷 프롬프트·해상도·길이·시드
docs/            ENV_REPORT_CLOUD.md(클라우드 점검), MAC_SETUP.md(맥 설치·테스트 절차), MAC_TEST_LOG.md(기록 양식)
scripts/         check_env.py(환경 점검), mac_setup.sh(맥 준비), prep_reference.py(이미지 전처리), make_shorts.py(편집)
outputs/         생성·편집 결과 (git 제외)
```

## 맥에서 시작하기 (요약)

1. 저장소를 받고 환경을 점검한다. `python3 scripts/check_env.py`
2. `docs/MAC_SETUP.md` 의 순서대로 LTX Desktop 1.3.0 을 설치한다. 앱 742 MB, 모델 약 72 GB 다운로드가 필요하며 용량·경로는 문서에 적어 두었다.
3. `configs/test_shot_01.yaml` 의 값으로 image-to-video 2초를 생성해 `outputs/test_shot_01_raw.mp4` 로 저장한다.
4. `python3 scripts/make_shorts.py compose --input outputs/test_shot_01_raw.mp4 --output outputs/test_shot_01_shorts_480p.mp4 --size test --caption "김웅 · 테스트 샷 01"`
5. 결과와 소요 시간을 `docs/MAC_TEST_LOG.md` 에 적는다.

## 원칙

- 유료 API 호출, GPU 서버 결제, 구독 추가 없음. LTX Desktop 의 "클라우드 텍스트 인코딩/프롬프트 향상"은 API 키가 필요하므로 쓰지 않고 로컬 텍스트 인코더를 쓴다.
- 기존 파일을 지우지 않는다. 대용량 다운로드 전에는 용량과 저장 위치를 먼저 알린다.
- 모델 가중치와 생성물은 git 에 넣지 않는다 (`.gitignore`).
