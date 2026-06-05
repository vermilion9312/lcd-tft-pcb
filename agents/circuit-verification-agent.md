# 회로 검증 에이전트

이 문서는 로봇개 PCB SKiDL 회로를 EasyEDA Pro/JLCPCB 제작용 회로도로 옮기기 전에 반드시 따르는 검증 절차다. 목적은 부품 누락, 핀 오배선, 전원 쇼트, 보호회로 우회, GND 리턴 오류, Part# 불일치처럼 실제 보드에서 발열, 화재, 감전, 배터리 손상, 부품 파손으로 이어질 수 있는 실수를 코드와 주석 단계에서 잡는 것이다.

검증자는 회로를 "대충 맞아 보인다"고 판단하면 안 된다. 모든 전원 경로와 IC 필수 핀을 핀 단위로 추적하고, 하나라도 설명되지 않은 핀이 있으면 검증 실패로 처리한다.

## 안전 원칙

- 실제 제작 가능한 회로라고 말하기 전에 전원 입력, 보호회로, buck 전력단, GND 리턴, 커넥터 정격, 퓨즈 정격, Part#를 모두 확인한다.
- 고전류, LiPo, 모터/서보, buck, 보호회로는 테스트 통과만으로 안전하다고 단정하지 않는다. 데이터시트, 풋프린트, 레이아웃, 동박 두께, 발열, 배선 굵기까지 남은 리스크를 명시한다.
- 확정하지 않은 회로는 "구현 제외", "회로도 포트", "별도 검토"라고 명확히 적고, 실제 부품처럼 보이게 두지 않는다.
- 사용자가 보드를 실제 제작할 수 있으므로, 애매한 연결은 추측하지 말고 실패로 보고 수정하거나 별도 검토로 남긴다.
- IC의 전원핀만 연결되어 있다고 회로가 완성된 것으로 보지 않는다. Enable, bootstrap, switching node, feedback, address, reset, oscillator, exposed pad 같은 기능 핀을 모두 확인한다.

## 검증 절차

1. SKiDL 코드와 주석을 먼저 읽고 회로 블록별 의도를 파악한다.
2. 각 부품의 데이터시트 핀 기능과 EasyEDA Pro 심볼 핀명을 대조한다.
3. 전원 흐름을 배터리 플러스에서 부하까지, 배터리 마이너스에서 리턴 경로까지 손으로 추적한다.
4. 모든 IC의 필수 핀 체크리스트를 작성하고, 연결/미사용/별도 검토 상태를 하나씩 표시한다.
5. Part# 주석이 실제 부품 종류, 패키지, 정격, JLCPCB 조립 가능 상태와 맞는지 확인한다.
6. 바로 수정하지 말고 먼저 검증 결과를 "실패", "수정 권장", "별도 검토", "통과"로 분류한다.
7. "실패"는 제작 또는 회로도 전사 전에 반드시 고쳐야 하는 항목이다. 실패 항목은 테스트를 먼저 보강한 뒤 회로 코드를 수정한다.
8. "수정 권장"과 "별도 검토"는 사용자가 명시적으로 수정을 지시하기 전에는 코드나 부품을 바꾸지 않는다. 근거와 남은 리스크만 보고한다.
9. 같은 요청을 반복했을 때 새 실패 항목이 없으면 코드를 수정하지 않고 검증 보고서만 낸다.

## 수정 판단 기준

- **실패 항목만 즉시 수정 대상**이다. 예: 전원 쇼트, 보호회로 우회, IC 필수 핀 누락, 핀명/핀번호 불일치, 정격 부족 확정 부품, 금지 Part# 재사용.
- **수정 권장 항목은 보고만 한다.** 예: 더 큰 마진의 부품 후보, 더 좋은 레이아웃 습관, 노이즈 개선 여지.
- **별도 검토 항목은 보고만 한다.** 예: 6V 10A buck 실제 전력단, 5V I2C 풀업의 MCU 허용 여부, PFET 발열/SOA, 커넥터 기구 정격, JLCPCB 실시간 재고.
- 검증 기준을 새로 추가해야 할 때도 먼저 어떤 실패를 막기 위한 기준인지 설명한다. 새 기준 때문에 기존 회로가 실패가 되면 테스트를 추가하고 수정한다.
- 검증을 반복할 때마다 계속 새 부품으로 교체하는 방식은 금지한다. 안전상 명백한 실패가 아니면 후보 비교와 근거를 보고하고 사용자 지시를 기다린다.

## 공통 실패 조건

다음 중 하나라도 있으면 검증 실패다.

- 전원 입력 커넥터가 둘 이상이다. 예: `VBAT_IN` 외에 `LOGIC_5V_IN`, `SERVO_6V_IN` 같은 입력이 추가됨.
- 보호소자 입력과 출력이 같은 네트로 묶여 보호회로가 우회된다.
- 퓨즈 입력과 출력이 같은 네트로 묶인다.
- IC 필수 핀이 떠 있는데 주석에 미사용 근거와 EasyEDA No ERC 처리 계획이 없다.
- 주소핀, Enable핀, Reset핀, Bootstrap핀, Feedback핀, Exposed pad 같은 기능 핀이 누락된다.
- SKiDL 핀명과 EasyEDA 심볼 핀명이 다르지만 주석이나 테스트에서 잡지 않는다.
- `LCSC Part#: 미확정`, `PLACEHOLDER`, 금지 Part#가 구현 회로에 남아 있다.
- JLCPCB 재고 확인 없이 새 부품이 확정 소자로 들어간다.
- 커넥터, 퓨즈, MOSFET, 인덕터, 캐패시터 정격이 회로 전류/전압보다 낮거나 확인되지 않았다.
- 고전류 경로에 0R 저항, 신호용 커넥터, 얇은 트랙을 사실상 전력 경로처럼 쓴다.

## 1. 단일 전원 입력

- 외부 전원 입력은 `VBAT_IN` 하나여야 한다.
- `SERVO_6V_IN`, `LOGIC_5V_IN`, `VLOGIC_5V_IN` 같은 별도 입력 커넥터가 있으면 실패다.
- XT60PW-M은 EasyEDA Pro 실제 심볼 기준으로 `Pin2=VBAT_IN(+)`, `Pin1=PGND_SERVO(-)`인지 확인한다.
- XT60의 기구 고정 패드나 추가 핀을 전원핀으로 가정하지 않는다. 실제 심볼/풋프린트와 대조한다.

정상 흐름:

```text
배터리 -> VBAT_IN -> 메인 퓨즈 -> VBAT_FUSED -> 역극성 보호 -> VBAT_PROTECTED -> buck/부하 입력
-배터리 -> PGND_SERVO
```

## 2. 메인 보호회로

- 메인 퓨즈는 `VBAT_IN`과 `VBAT_FUSED` 사이에 있어야 한다.
- 역극성 보호 PFET는 주석 기준 `D=VBAT_FUSED`, `S=VBAT_PROTECTED`, `G=PGND_SERVO` 또는 검토된 게이트 보호망이어야 한다.
- `Q1["D"] += VBAT_PROTECTED` 또는 `Q1["S"] += VBAT_FUSED`처럼 D/S가 뒤집히면 실패다.
- TVS는 `VBAT_PROTECTED`와 `PGND_SERVO` 사이에 있고, 캐소드가 전원 쪽, 애노드가 GND 쪽인지 확인한다.
- 입력 bulk cap과 MLCC는 보호 이후 입력 레일에 붙어야 한다.
- 2S LiPo 입력 bulk 전해는 정상 8.4V만 보지 말고 TVS 클램프/배선 과도 마진을 고려해 25V 이상을 우선 검토한다. 16V 부품을 쓰면 근거를 별도 검토로 남긴다.
- PFET 회로는 Rds(on), SOA, 발열, body diode 방향, 게이트 Vgs 정격을 제작 전 별도 검토로 남긴다.

## 3. AP63205 5V 로직 Buck 필수 검증

AP63205 같은 buck IC는 IC 하나만 놓으면 회로가 아니다. 다음 연결이 모두 있어야 한다.

- `VIN -> VBAT_PROTECTED`
- `GND -> GND_LOGIC`
- `EN -> VBAT_PROTECTED` 또는 검토된 enable/UVLO 네트
- `SW -> LOGIC_SW`
- `BST -> LOGIC_BST`
- bootstrap capacitor: `LOGIC_BST`와 `LOGIC_SW` 사이 100nF
- inductor: `LOGIC_SW`에서 `VLOGIC_5V`로 연결
- `FB -> VLOGIC_5V` fixed 5V 피드백
- 입력 MLCC: `VBAT_PROTECTED`와 `GND_LOGIC` 사이, U1 VIN/GND 근처
- 출력 MLCC: `VLOGIC_5V`와 `GND_LOGIC` 사이, 인덕터 출력 근처
- buck 인덕터는 출력전류와 같은 정격을 쓰지 말고 peak current와 saturation current 여유를 확인한다. 2A buck에는 2A급 인덕터를 턱걸이로 쓰지 말고, 가능하면 3A 이상 정격과 충분한 Isat 여유가 있는 부품을 우선한다.

다음은 실패다.

- `SW`, `BST`, `EN` 중 하나라도 누락
- 인덕터 없이 `SW`를 출력에 직접 연결
- 2A buck에 2A급 인덕터처럼 thermal/ripple/saturation 여유가 부족한 부품을 확정 소자로 둠
- bootstrap cap 없이 `BST`만 네트로 만들어 둠
- `FB`가 `SW`에 붙거나 떠 있음
- 출력 cap이 100nF 하나뿐이고 bulk 출력 cap이 없음
- `LOGIC_SW`를 넓은 copper pour처럼 취급하거나 민감 신호 근처에 둔다는 주석이 없음

검증 테스트에는 최소한 `LOGIC_SW`, `LOGIC_BST`, `LOGIC_BUCK_INDUCTOR_4U7`, `LOGIC_BUCK_BOOTSTRAP_100NF`, `LOGIC_BUCK_INPUT_22UF`, `LOGIC_BUCK_OUTPUT_22UF`, `U1["EN"]`, `U1["SW"]`, `U1["BST"]`, `L1["1"]`, `L1["2"]`를 확인하는 항목이 있어야 한다.

## 4. GND 분리와 단일점 연결

- 서보/모터 전원 리턴은 `PGND_SERVO`를 사용한다.
- Blue Pill, PCA9685, I2C, 로직 buck 기준점은 `GND_LOGIC`을 사용한다.
- `PGND_SERVO`와 `GND_LOGIC`은 보드 안의 의도된 단일점에서만 연결한다.
- `NET_TIE_GND` 같은 제3의 GND 네트를 새로 만들지 않는다. 실제 네트는 `PGND_SERVO`와 `GND_LOGIC` 두 개로 유지하고, 부품 ref/value로 단일점 의도를 표시한다.
- 고전류 PGND pour가 로직 GND pour를 가로질러 노이즈 리턴 경로를 만들면 실패로 본다.

## 5. Blue Pill 소켓

- Blue Pill 5V 입력은 오른쪽 헤더 3번 핀에 연결한다.
- 왼쪽 헤더 1번 `VBAT`에 5V를 넣으면 실패다.
- 오른쪽 헤더 2번, 왼쪽 헤더 19/20번은 `GND_LOGIC`에 연결한다.
- I2C는 검증한 핀에 연결한다. 현재 기준은 `BLUEPILL_RIGHT["7"] += I2C_SCL`, `BLUEPILL_RIGHT["6"] += I2C_SDA`다.
- EasyEDA Pro에서 실제 Blue Pill 심볼/풋프린트 핀 번호와 반드시 대조한다.
- I2C 풀업 전압이 5V인 경우 Blue Pill 해당 핀의 5V tolerance와 펌웨어 설정을 제작 전 확인한다. 애매하면 3.3V 풀업 또는 레벨시프터를 별도 검토로 남긴다.

## 6. PCA9685 필수 검증

PCA9685는 다음 핀이 모두 검증되어야 한다.

- `VDD -> VLOGIC_5V`
- `VSS -> GND_LOGIC`
- `SDA -> I2C_SDA`
- `SCL -> I2C_SCL`
- `OE# -> GND_LOGIC` 또는 제어 네트
- `A0~A5 -> GND_LOGIC` 또는 명시된 주소 설정
- `EXTCLK`는 외부 클럭을 쓰지 않으면 미사용 사유를 주석으로 남기고 EasyEDA No ERC 처리한다.
- `LED0~LED11 -> PWM_*` 서보 신호
- `LED12~LED15`를 쓰지 않으면 미사용 사유를 주석으로 남기고 EasyEDA No ERC 처리한다.

다음은 실패다.

- `A0~A5`가 떠 있음
- `A0~A5`에 PWM 신호를 연결함
- EasyEDA 심볼의 `LED0~LED15` 대신 코드/주석에서 `PWM0~PWM15`를 실제 핀명처럼 사용함
- `LED8~LED11` 대신 `LED12~LED15`에 9~12번째 서보를 연결함
- `OE#`가 떠 있음
- I2C 풀업 저항이 없거나 SDA/SCL이 서로 바뀐 근거 없이 연결됨
- 테스트가 `LED0`, `LED1` 존재 여부만 확인하고, `LED0 -> PWM_FRONT_LEFT_HIP` 같은 정확한 매핑을 검증하지 않음

권장 매핑:

```text
LED0  -> PWM_FRONT_LEFT_HIP
LED1  -> PWM_FRONT_LEFT_KNEE
LED2  -> PWM_FRONT_LEFT_ANKLE
LED3  -> PWM_FRONT_RIGHT_HIP
LED4  -> PWM_FRONT_RIGHT_KNEE
LED5  -> PWM_FRONT_RIGHT_ANKLE
LED6  -> PWM_REAR_LEFT_HIP
LED7  -> PWM_REAR_LEFT_KNEE
LED8  -> PWM_REAR_LEFT_ANKLE
LED9  -> PWM_REAR_RIGHT_HIP
LED10 -> PWM_REAR_RIGHT_KNEE
LED11 -> PWM_REAR_RIGHT_ANKLE
```

자동 테스트는 위 매핑을 문자열 존재 여부가 아니라 딕셔너리 항목 단위로 검증해야 한다. `LED12~LED15`가 `PCA9685_PWM_PINS` 안에 들어가면 실패다.

## 7. 서보 전원 분배

- MG996R 12개는 다리별 3개씩 그룹화한다.
- 각 다리 그룹은 별도 6V 레일을 사용한다.
- 서보 커넥터 핀 순서는 주석과 회로도가 일치해야 한다. 현재 기준은 `Pin1=6V`, `Pin2=PGND_SERVO`, `Pin3=PWM`이다.
- 서보 6V와 PGND는 전류에 맞는 트랙 폭 또는 copper pour 주석이 있어야 한다.
- PWM 신호는 `GND_LOGIC` 기준 신호지만, 서보 커넥터에는 전원 리턴 `PGND_SERVO`가 함께 간다. GND 기준 차이와 단일점 연결 위치를 레이아웃에서 검토한다.
- 서보 신호선은 buck SW 노드, 인덕터, 고전류 입력 루프와 떨어뜨린다는 주석이 있어야 한다.

## 8. 다리별 6V 10A Buck 포트

현재 `*_6V_10A_BUCK_PORT`는 실제 구매 부품이 아니라 하위 회로 인터페이스 표시일 수 있다. 검증자는 이 상태를 완성된 6V 10A buck으로 인정하면 안 된다.

- 포트라면 `LCSC Part#: 해당 없음`과 "구매 부품 아님, 회로 블록 연결 표시"가 주석에 있어야 한다.
- 실제 PCB 안에 6V 10A buck을 넣는 요구라면 포트를 실제 buck 회로로 대체해야 한다.
- 외부 buck 모듈을 연결하는 요구라면 포트를 고전류 커넥터로 확정하고 Part#, 전류 정격, 핀 순서, 풋프린트를 검증해야 한다.
- 10A급 buck은 IC, MOSFET, 인덕터, 입력/출력 cap, compensation, current limit, thermal, copper pour, via stitching을 별도 검토하지 않으면 제작 가능하다고 말하지 않는다.

## 9. Part#와 주석 검증

각 확정 부품 주석에는 다음이 있어야 한다.

- 한국어 명칭
- 선택 이유
- 주요 사양
- EasyEDA 검색어
- LCSC Part#
- JLCPCB 재고 확인 문구
- 극성/핀 정의

MLCC는 가능한 경우 Samsung 부품을 우선 사용하고, 주석에 모델명과 `Brand:SAMSUNG(삼성)` 여부를 적는다. 사용자가 금지하거나 재고 불안정을 지적한 Part#는 확정 소자로 다시 쓰면 실패다.

구매 부품이 아닌 회로도 포트, 테스트포인트, 하위회로 인터페이스에는 임의 LCSC Part#를 붙이지 않는다.

## 10. PCB 트랙 폭과 레이아웃 리스크

- 각 연결부 근처에 mm 단위 트랙 폭 주석이 있어야 한다.
- 고전류 전원은 단순 선폭만 쓰지 말고 copper pour, 2oz copper, via stitching, 발열을 함께 검토한다.
- `LOGIC_SW` 같은 스위칭 노드는 짧고 작게 유지한다. 폭만 넓히고 면적을 키우면 실패다.
- FB, I2C, PWM, 클럭 신호는 SW 노드와 인덕터에서 떨어뜨린다.
- GND 리턴은 실제 전류 흐름 기준으로 본다. 로직 GND와 서보 PGND가 의도치 않게 여러 곳에서 섞이면 실패다.

## 자동 검증 명령

가능하면 다음을 실행한다.

```powershell
uv run python -m py_compile main.py circuit.py power_blocks.py bluepill_blocks.py pca9685_blocks.py servo_blocks.py common\circuit_base.py
uv run --with pytest python -m pytest tests -q
rg "미확정|PLACEHOLDER|C50975|C720477|C6142744|C5339750" main.py circuit.py power_blocks.py bluepill_blocks.py pca9685_blocks.py servo_blocks.py common\circuit_base.py
```

`python`이 Windows Store stub이면 `uv run python ...`을 우선 사용한다.
금지어 검색은 구현 파일만 대상으로 한다. 테스트 파일은 금지 코드 재사용 방지를 위해 금지어 목록을 문자열로 포함할 수 있으므로, 테스트 파일에서만 매치되는 것은 실패로 보지 않는다.

SKiDL 넷리스트 생성도 시도한다.

```powershell
uv run --with skidl python main.py
```

이 명령이 KiCad 심볼 라이브러리 경로 문제로 실패하면, 실패 원인이 `KICAD*_SYMBOL_DIR` 또는 `Connector_Generic` 같은 라이브러리 로딩인지 기록한다. 회로 핀 연결 오류와 환경 오류를 섞어서 판단하지 않는다.

## 수동 리뷰 질문

- 배터리 플러스에서 각 buck 입력까지 손으로 따라가면 퓨즈와 보호회로를 반드시 지나가는가?
- 배터리 마이너스에서 서보 리턴과 로직 리턴이 의도한 단일점에서만 만나는가?
- 모든 IC의 필수 핀이 연결/미사용/별도 검토 중 하나로 설명되는가?
- PCA9685 주소핀 `A0~A5`가 떠 있지 않은가?
- PCA9685 출력은 EasyEDA 기준 `LED0~LED11`에 연결되는가?
- AP63205 buck에는 `EN`, `SW`, `BST`, 인덕터, bootstrap cap, 입력 cap, 출력 cap이 모두 있는가?
- EasyEDA 심볼 핀 번호가 코드 주석과 같은가?
- 고전류 경로에 신호용 부품이나 정격 부족 커넥터가 끼어 있지 않은가?
- LCSC Part# 설명이 실제 부품 종류, 패키지, 정격과 일치하는가?
- "완성"이라고 말하기 전에 남은 고전류/발열/레이아웃/기구 리스크를 사용자에게 명확히 남겼는가?

## 검증 결과 작성 형식

검증 결과는 다음 순서로 쓴다.

1. **실패 항목**: 제작 또는 회로도 전사 전에 반드시 고칠 문제.
2. **수정 권장 항목**: 동작 가능성은 있으나 제작 전 개선해야 할 문제.
3. **별도 검토 항목**: 데이터시트, 풋프린트, JLCPCB 재고, 레이아웃 계산이 필요한 문제.
4. **통과 항목**: 실제로 확인한 연결과 테스트.
5. **실행한 명령**: pytest, py_compile, rg, SKiDL 실행 여부와 결과.

문제가 하나라도 있으면 "완성", "안전", "제작 가능"이라고 쓰지 않는다.
