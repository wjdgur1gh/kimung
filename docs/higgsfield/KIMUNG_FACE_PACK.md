# 김웅 얼굴 팩: 45도 각도 8장 + 표정 10장

상태: **프롬프트만 준비됨. 아직 한 장도 생성하지 않음.**

- 힉스필드 무제한 생성은 Claude Code 에서 거부된다. 서버 응답: "You are using Higgsfield from Claude Code, where unlimited generations are not available. They are available in: Claude chat, Claude Cowork, ChatGPT."
- 그래서 아래 "붙여 넣기용 지시문"을 **Claude 채팅(claude.ai)** 에서 힉스필드 커넥터를 켠 상태로 실행한다. 사용자 확인 결과 무제한은 Claude 채팅에서만 쓸 수 있다.
- 얼굴 기준 01 은 이미 힉스필드 작업공간에 올려 두었다. media_id `3256fb9e-366b-4b22-acbb-b2da3acbc2da` (원본: `assets/ref/kimung_ref_approved.png`, 378x354).

## 원칙

- 얼굴은 01 이 최우선. 각진 턱선, 높은 광대, 꺼진 볼, 짙은 일자 눈썹, 가늘고 무거운 눈꺼풀, 짧은 삭발. 둥글고 앳되게 만들지 않는다.
- 과거·현대 같은 얼굴, 같은 나이감.
- 결과물은 한 장에 한 사람, 한 시점. 글자·라벨·분할 화면·콜라주 없음.
- 공통 설정: Nano Banana Pro, 2k, 3:4, 회색 무지 배경, 검은 교복(차이나 카라, 금색 단추, 흰 속깃).
- 얼굴의 흙먼지는 장면 연출이므로 기준 이미지에서는 뺐다. 필요하면 장면 생성 때 추가한다.

## 각도 정의

카메라는 고정, 인물이 시계 방향으로 돈다. 0° 는 카메라를 정면으로 본다. "화면 왼쪽"은 결과 이미지 기준이다.

| 번호 | 각도 | 보이는 모습 |
|---|---|---|
| A000 | 0° | 정면 |
| A045 | 45° | 코가 화면 왼쪽을 향한 3/4 측면, 왼쪽 뺨·왼쪽 귀가 보임 |
| A090 | 90° | 화면 왼쪽을 향한 완전 측면 |
| A135 | 135° | 뒤쪽 3/4, 뒤통수와 왼쪽 귀, 왼쪽 턱선 가장자리만 보임 |
| A180 | 180° | 완전 뒷모습 |
| A225 | 225° | 뒤쪽 3/4, 뒤통수와 오른쪽 귀, 오른쪽 턱선 가장자리만 보임 |
| A270 | 270° | 화면 오른쪽을 향한 완전 측면 |
| A315 | 315° | 코가 화면 오른쪽을 향한 3/4 측면, 오른쪽 뺨·오른쪽 귀가 보임 |

## 표정 정의 (모두 정면, 힉스필드 엘리먼트로 저장)

| 번호 | 표정 | 엘리먼트 이름 |
|---|---|---|
| E01 | 미소 | kimung-smile |
| E02 | 크게 웃음 | kimung-laugh |
| E03 | 비웃음 | kimung-smirk |
| E04 | 슬픔 | kimung-sad |
| E05 | 눈물 참기 | kimung-tears |
| E06 | 분노 | kimung-angry |
| E07 | 격분·고함 | kimung-rage |
| E08 | 놀람 | kimung-surprised |
| E09 | 두려움·불안 | kimung-fear |
| E10 | 경멸·냉담 | kimung-contempt |

## 붙여 넣기용 지시문 (Claude 채팅)

아래 블록 전체를 복사해 힉스필드 커넥터가 켜진 Claude 채팅에 붙여 넣는다.

```text
힉스필드로 김웅 캐릭터 기준 이미지 18장을 만들어줘. 반드시 무제한 생성(use_unlim: true)만 써. 무제한이 거부되면 크레딧으로 바꾸지 말고 멈춘 뒤 알려줘.

공통 설정
- 모델: Nano Banana Pro, resolution 2k, aspect_ratio 3:4
- 얼굴 기준 이미지: 내 힉스필드 작업공간의 media_id 3256fb9e-366b-4b22-acbb-b2da3acbc2da 를 role image_references 로 모든 요청에 넣어. 이 media_id 를 쓸 수 없으면 생성하지 말고 01 이미지를 다시 올려 달라고 말해.
- 18장을 독립 요청으로 나눠 배치로 생성하고, 모두 끝나면 한 번에 보여줘.
- 프롬프트는 [COMMON] 문단 뒤에 각 항목의 문장을 붙여서 써.

[COMMON]
Photorealistic character reference photo of the exact same young Korean man shown in the reference image. Preserve his facial identity precisely: lean angular face, sharp defined jawline and chin, high cheekbones, slightly hollow cheeks, thick straight dark eyebrows, narrow intense eyes with heavy low eyelids, the same straight nose, the same full lips, the same ears, very short black buzz cut. Same age and maturity as the reference; do NOT make the face rounder, softer, chubbier, cuter or younger. He wears a black high-collar Korean school uniform jacket (gakuran) with brass buttons and a thin white inner collar. Framing: head and upper chest, centered. Plain seamless medium-gray studio backdrop, soft even light, natural skin texture, clean face, no makeup. One person in one single photo. No text, no letters, no labels, no watermark, no border, no split screen, no collage, no multiple views.

각도 8장 (표정은 모두 무표정, 입 다문 진지한 얼굴)
A000: View: straight-on FRONT view, face and shoulders square to the camera, eyes looking into the lens, neutral serious expression, mouth closed.
A045: View: THREE-QUARTER view. Head and shoulders rotated 45 degrees so his nose points toward the left edge of the frame; his left cheek and left ear face the camera; eyes looking where his nose points, not at the camera; neutral serious expression.
A090: View: full SIDE PROFILE. Head and shoulders rotated 90 degrees so he faces the left edge of the frame; only the left side of his face is visible, one eye, left ear centered; neutral serious expression.
A135: View: BACK THREE-QUARTER. Rotated 135 degrees, mostly turned away from the camera toward the back-left of the frame; we see the back of his buzz-cut head, the back of the collar, his left ear and only the edge of his left jaw and cheek; his eyes and face are not visible.
A180: View: directly from BEHIND. Back of his buzz-cut head, nape of the neck, back of the high collar and shoulders; no face visible at all.
A225: View: BACK THREE-QUARTER. Rotated 225 degrees, mostly turned away from the camera toward the back-right of the frame; we see the back of his buzz-cut head, the back of the collar, his right ear and only the edge of his right jaw and cheek; his eyes and face are not visible.
A270: View: full SIDE PROFILE. Head and shoulders rotated 270 degrees so he faces the right edge of the frame; only the right side of his face is visible, one eye, right ear centered; neutral serious expression.
A315: View: THREE-QUARTER view. Head and shoulders rotated 315 degrees so his nose points toward the right edge of the frame; his right cheek and right ear face the camera; eyes looking where his nose points, not at the camera; neutral serious expression.

표정 10장 (모두 정면, 카메라를 봄)
E01 kimung-smile: View: straight-on front view, looking into the lens. Expression: a small genuine closed-mouth smile, warmth reaching his eyes, eyes slightly narrowed by the smile.
E02 kimung-laugh: View: straight-on front view. Expression: laughing openly, mouth open showing teeth, eyes squinting with laughter, head tilted slightly back.
E03 kimung-smirk: View: straight-on front view, looking into the lens. Expression: cocky one-sided smirk, one corner of the mouth raised, cold half-lidded eyes, chin slightly raised.
E04 kimung-sad: View: straight-on front view. Expression: quiet sadness, eyes downcast and slightly glossy, inner brows raised, mouth corners turned down, lips pressed together.
E05 kimung-tears: View: straight-on front view, looking into the lens. Expression: holding back tears, eyes red-rimmed and wet, a single tear running down one cheek, jaw clenched, lips trembling.
E06 kimung-angry: View: straight-on front view, glaring into the lens. Expression: intense controlled anger, brows drawn down hard, nostrils flared, jaw clenched, lips pressed tight.
E07 kimung-rage: View: straight-on front view. Expression: explosive rage, shouting with mouth wide open, teeth bared, neck tendons straining, brows knotted.
E08 kimung-surprised: View: straight-on front view, looking into the lens. Expression: sudden surprise, eyes wide open, eyebrows raised high, mouth slightly open.
E09 kimung-fear: View: straight-on front view. Expression: fear and anxiety, eyes wide and glancing slightly off-camera, inner brows pulled up and together, lips parted, shoulders tense.
E10 kimung-contempt: View: straight-on front view, looking down his nose into the lens. Expression: cold contempt, upper lip slightly curled on one side, emotionless heavy-lidded eyes.

생성이 끝나면
1. 18장 모두를 보여주고, 얼굴이 기준 이미지와 다르거나 둥글고 어려 보이는 장, 글자나 분할 화면이 들어간 장을 표시해줘.
2. 표정 10장(E01~E10)만 각각 힉스필드 레퍼런스 엘리먼트로 저장해줘. 카테고리 character, 이름은 위의 kimung-xxx 그대로.
3. 마지막에 18장의 job_id 와 10개 엘리먼트의 element_id 를 표로 정리해줘.
```

## 생성 후 이 저장소에 기록할 것

`docs/higgsfield/KIMUNG_FACE_PACK_RESULTS.md` 를 만들어 job_id, element_id, 탈락·재생성 여부를 적는다.
