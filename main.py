from skidl import *


# lcd-tft-pcb
# 단일 파일 SKiDL 구현.
# 사용자가 AGENTS.md의 객체지향 분리 규칙 대신 main.py 하나에 모두 구현하라고 지시했으므로,
# 회로 블록은 코드/주석 섹션으로만 구분한다.


# === SKiDL 유틸리티 ===

def template(ref_prefix, value, pins):
    part = Part(
        name=value,
        ref_prefix=ref_prefix,
        dest=TEMPLATE,
        tool=SKIDL,
        pins=[Pin(num=str(num), name=str(name)) for num, name in pins],
    )
    part.footprint = f"EasyEDA:{value}"
    return part


def connect(part, pin_name, net):
    part[pin_name] += net


def make_connector(ref_prefix, value, pin_count):
    return template(ref_prefix, value, [(idx, str(idx)) for idx in range(1, pin_count + 1)])


def make_net(name):
    return Net(name)


# === 전원 입력/보호 블록 ===

# 설계 가정:
# - 보드 외부 전원 입력은 12V 한 곳만 둔다.
# - 12V에서 3.3V 로직 전원을 만들고, LCD 백라이트는 별도 정전류 LED 드라이버에서 구동한다.
# - LN80480T070IA9098 데이터시트/제품 정보에 백라이트 구동 전압이 9V 계열로 제시되어 있어
#   USB 5V 단일 입력보다 12V 단일 입력을 보수적 시작점으로 잡았다.
# - 실제 입력 전압을 5V 또는 배터리로 바꾸려면 buck/백라이트 드라이버를 다시 선정한다.

VIN_12V_IN = make_net("VIN_12V_IN")
VIN_12V_FUSED = make_net("VIN_12V_FUSED")
VIN_12V_PROTECTED = make_net("VIN_12V_PROTECTED")
VDD_3V3 = make_net("VDD_3V3")
VDD_LCD_3V3 = make_net("VDD_LCD_3V3")
VDD_TOUCH_3V3 = make_net("VDD_TOUCH_3V3")
BL_LED_A = make_net("BL_LED_A")
BL_LED_K = make_net("BL_LED_K")
GND = make_net("GND")
AGND = make_net("AGND")

# J1: 12V 전원 입력 단자대
# 한국어 명칭: 2핀 5.08mm 전원 입력 단자대
# 선택 이유: 보드의 단일 외부 전원 입력을 명확히 한다.
# 사양: 2핀, 5.08mm, 300V, 12A, pluggable terminal block. 실제 하네스 방향과 풋프린트 대조 필요.
# EasyEDA 검색어: 2EDGK-5.08-2P
# LCSC Part#: C47986637 (HanElectricity 2EDGK-5.08-2P, 5.08mm 2P 12A 300V terminal block)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB in stock 830.
# 핀 정의: Pin1=VIN_12V_IN(+), Pin2=GND(-). EasyEDA Pro에서 실제 심볼 핀 번호 대조.
J1 = make_connector("J", "2EDGK_5_08_2P_12V_INPUT", 2)()

# F1: 입력 퓨즈
# 한국어 명칭: 12V 입력 보호 퓨즈
# 선택 이유: 입력 배선과 보드 단락 보호. 부하 전류가 확정되지 않아 2A 시작점.
# 사양: 2A, 32V, 1206, disposable fuse. 백라이트 전류/주변부하 확정 후 정격 재계산.
# EasyEDA 검색어: S1206-F-2.0A
# LCSC Part#: C553922 (SART S1206-F-2.0A, 2A 32V 1206 disposable fuse)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB 페이지 확인.
# 핀 정의: 무극성, Pin1=VIN_12V_IN, Pin2=VIN_12V_FUSED.
F1 = template("F", "S1206_F_2A_INPUT_FUSE", [("1", "1"), ("2", "2")])()

# D2: 입력 역극성 보호 쇼트키
# 한국어 명칭: 12V 입력 역극성 보호 직렬 쇼트키 다이오드
# 선택 이유: 입력 극성 반대 연결 시 부하 쪽 전원 공급을 막고, 퓨즈 뒤 보호 경로를 실제 부하로 이어준다.
# 주요 사양: 3A, 40V, SMA(DO-214AC), Vf 550mV@3A.
# EasyEDA 검색어: SS34
# LCSC Part#: C8678 (MDD SS34, 3A 40V Schottky diode, SMA(DO-214AC))
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB in stock 1659208.
# 핀 정의: Pin1=K(캐소드)=VIN_12V_PROTECTED, Pin2=A(애노드)=VIN_12V_FUSED.
# 주의: 직렬 쇼트키 손실은 입력 전류와 백라이트 전류에 따라 발열 검토가 필요하다.
D2 = template("D", "SS34_INPUT_REVERSE_PROTECTION", [("1", "K"), ("2", "A")])()

# D1: 입력 TVS
# 한국어 명칭: 12V 입력 TVS 다이오드
# 선택 이유: 외부 전원 커넥터 유입 서지를 GND로 클램프한다.
# 사양: 18V standoff, 400W@10/1000us, unidirectional, DO-214AC(SMA).
# EasyEDA 검색어: SMAJ18A
# LCSC Part#: C726747 (TWGMC SMAJ18A, 18V 400W unidirectional TVS, DO-214AC)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB 페이지 확인.
# 핀 정의: Pin1=K(캐소드)=VIN_12V_PROTECTED, Pin2=A(애노드)=GND.
D1 = template("D", "SMAJ18A_INPUT_TVS", [("1", "K"), ("2", "A")])()

# U1: 3.3V buck regulator
# 한국어 명칭: 3.3V 벅 레귤레이터 IC
# 선택 이유: 12V 단일 입력에서 STM32, SDRAM, LCD 로직, AR1020, SD카드용 3.3V를 만든다.
# 주요 사양: 입력 3.8V~32V, 출력 3.3V fixed, 2A, TSOT-23-6, 동기식 buck.
# EasyEDA 검색어: AP63203WU-7
# LCSC Part#: C780769 (Diodes Incorporated AP63203WU-7, 3.3V 2A buck, TSOT-23-6)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB in stock 21551, LCSC in stock 47186.
# 핀 정의: VIN=VIN_12V_PROTECTED, GND=GND, EN=VIN_12V_PROTECTED, BST=BUCK_BST,
#          SW=BUCK_SW, FB=VDD_3V3(fixed feedback).
BUCK_SW = make_net("BUCK_SW")
BUCK_BST = make_net("BUCK_BST")
U1 = template("U", "AP63203WU_7_3V3_BUCK", [("1", "VIN"), ("2", "GND"), ("3", "EN"), ("4", "BST"), ("5", "SW"), ("6", "FB")])()

# L1: buck 인덕터
# 한국어 명칭: 3.9uH~4.7uH 파워 인덕터
# 선택 이유: AP63203 3.3V 권장값은 3.9uH이고, 4.7uH 3A 재고품은 보수적 대체 시작점이다.
# 주요 사양: 4.7uH, 3A급 이상, 낮은 DCR, 포화전류 여유 필요.
# EasyEDA 검색어: 4.7uH 3A inductor
# LCSC Part#: C9900003590 (JLCPCB Assembly 4.7uH 3A, power inductor)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB 페이지 확인.
# 핀 정의: 무극성, Pin1=BUCK_SW, Pin2=VDD_3V3.
L1 = template("L", "LOGIC_BUCK_INDUCTOR_4U7_3A", [("1", "1"), ("2", "2")])()

# C1: buck 입력 MLCC
# 한국어 명칭: buck 입력 세라믹 캐패시터
# 선택 이유: AP63203 입력 전류 루프를 짧게 닫는다.
# 주요 사양: 10uF, 25V, X5R, 0603, Samsung.
# EasyEDA 검색어: CL10A106MA8NRNC
# LCSC Part#: C96446 (Samsung CL10A106MA8NRNC, 10uF 25V X5R 0603 MLCC, Brand:SAMSUNG)
# JLCPCB 재고: 확인됨. 2026-06-05 LCSC 검색 결과 재고 확인.
# 핀 정의: 무극성, Pin1=VIN_12V_PROTECTED, Pin2=GND.
C1 = template("C", "LOGIC_BUCK_INPUT_10UF_25V", [("1", "1"), ("2", "2")])()

# C2, C3: buck 출력 MLCC
# 한국어 명칭: buck 출력 세라믹 캐패시터
# 선택 이유: 3.3V 로직 전원 리플과 SDRAM/LTDC 피크 전류 완화.
# 주요 사양: 22uF, 25V, X5R, 1206, Samsung.
# EasyEDA 검색어: CL31A226KAHNNNE
# LCSC Part#: C12891 (Samsung CL31A226KAHNNNE, 22uF 25V X5R 1206 MLCC, Brand:SAMSUNG)
# JLCPCB 재고: 확인됨. 사용자가 금지한 22uF 10V 재고 불안정 부품 대신 C12891 사용.
# 핀 정의: 무극성, Pin1=VDD_3V3, Pin2=GND.
C2 = template("C", "LOGIC_BUCK_OUTPUT_22UF_25V_A", [("1", "1"), ("2", "2")])()
C3 = template("C", "LOGIC_BUCK_OUTPUT_22UF_25V_B", [("1", "1"), ("2", "2")])()

# C4: bootstrap capacitor
# 한국어 명칭: buck 부트스트랩 캐패시터
# 선택 이유: AP63203 high-side 구동용 BST-SW 캐패시터.
# 주요 사양: 100nF, 50V, X7R, 0603, Samsung.
# EasyEDA 검색어: CL10B104KB8NNNC
# LCSC Part#: C1591 (Samsung CL10B104KB8NNNC, 100nF 50V X7R 0603 MLCC, Brand:SAMSUNG)
# JLCPCB 재고: 확인됨. 2026-06-05 Samsung MLCC 검색 결과 확인.
# 핀 정의: 무극성, Pin1=BUCK_BST, Pin2=BUCK_SW.
C4 = template("C", "LOGIC_BUCK_BOOTSTRAP_100NF", [("1", "1"), ("2", "2")])()


# PCB 트랙 폭 가이드(mm)
# - 12V 입력/퓨즈/buck 입력: 1.00mm 이상, 짧게. 실제 백라이트 전류에 따라 2.00mm 이상 또는 copper pour 검토.
# - BUCK_SW: 1.00mm 시작점, 면적은 작고 짧게. LTDC/FMC/터치 신호와 거리 확보.
# - VDD_3V3 주 전원: 1.00mm 이상 또는 plane. STM32/SDRAM/LCD/SD카드로 분기.
# - 로직 신호/LTDC/FMC/SDIO/I2C/SWD: 0.25mm 이상, 길이/임피던스/스큐는 레이아웃에서 별도 검토.
J1["1"] += VIN_12V_IN       # 1.00mm 이상
J1["2"] += GND              # 1.00mm 이상 또는 GND plane
F1["1"] += VIN_12V_IN       # 1.00mm 이상
F1["2"] += VIN_12V_FUSED    # 1.00mm 이상
D2["A"] += VIN_12V_FUSED      # 1.00mm 이상
D2["K"] += VIN_12V_PROTECTED  # 1.00mm 이상, 쇼트키 발열 copper 확보
D1["K"] += VIN_12V_PROTECTED  # 1.00mm 이상, 입력 커넥터 근처
D1["A"] += GND                # 1.00mm 이상, GND plane/via stitching
U1["VIN"] += VIN_12V_PROTECTED  # 1.00mm 이상, C1 근접
U1["GND"] += GND               # GND plane
U1["EN"] += VIN_12V_PROTECTED  # 0.25mm, 필요 시 UVLO 분압으로 변경
U1["BST"] += BUCK_BST          # 0.25mm, C4를 U1에 근접
U1["SW"] += BUCK_SW            # 1.00mm, 짧고 작게
U1["FB"] += VDD_3V3            # 0.25mm, fixed 3.3V feedback
L1["1"] += BUCK_SW             # 1.00mm, 짧게
L1["2"] += VDD_3V3             # 1.00mm 이상
C1["1"] += VIN_12V_PROTECTED   # 1.00mm, U1 VIN 근접
C1["2"] += GND                 # GND plane
C2["1"] += VDD_3V3             # 1.00mm
C2["2"] += GND                 # GND plane
C3["1"] += VDD_3V3             # 1.00mm
C3["2"] += GND                 # GND plane
C4["1"] += BUCK_BST            # 0.25mm, U1 BST 근접
C4["2"] += BUCK_SW             # 0.25mm, U1 SW 근접


# === STM32F429IGT6 MCU 블록 ===

# U2: STM32F429IGT6
# 한국어 명칭: LCD-TFT 컨트롤러 내장 STM32 MCU
# 선택 이유: LTDC, FMC SDRAM, SDIO, USB DFU/SWD를 모두 지원해 SD카드->SDRAM 캐싱->LCD 출력 구조에 적합하다.
# 주요 사양: ARM Cortex-M4 180MHz, 1MB Flash, 256KB RAM, LQFP-176(24x24), 1.8V~3.6V.
# EasyEDA 검색어: STM32F429IGT6
# LCSC Part#: C54328 (STMicroelectronics STM32F429IGT6, LQFP-176(24x24))
# JLCPCB 재고: 확인됨. 2026-06-05 JLCPCB in stock 2344, LCSC in stock 5473.
# 핀 정의: 아래 포트명은 STM32 LTDC/FMC/SDIO/SWD 대표 alternate function 기준.
#          EasyEDA Pro에서 실제 LQFP-176 심볼 핀 번호와 CubeMX 핀 충돌을 반드시 대조.
MCU_PINS = [
    ("VDD", "VDD"), ("VSS", "VSS"), ("VDDA", "VDDA"), ("VSSA", "VSSA"),
    ("NRST", "NRST"), ("BOOT0", "BOOT0"),
    ("OSC_IN", "PH0_OSC_IN"), ("OSC_OUT", "PH1_OSC_OUT"),
    ("USB_DM", "PA11_USB_DM"), ("USB_DP", "PA12_USB_DP"),
    ("SWDIO", "PA13_SWDIO"), ("SWCLK", "PA14_SWCLK"), ("SWO", "PB3_SWO"),
    ("I2C1_SCL", "PB8_I2C1_SCL"), ("I2C1_SDA", "PB9_I2C1_SDA"), ("TOUCH_IRQ", "PB7_TOUCH_IRQ"),
    ("LCD_BL_PWM", "PA8_LCD_BL_PWM"), ("SD_CARD_DETECT", "PG3_SD_CARD_DETECT"),
    ("SDIO_D0", "PC8_SDIO_D0"), ("SDIO_D1", "PC9_SDIO_D1"), ("SDIO_D2", "PC10_SDIO_D2"),
    ("SDIO_D3", "PC11_SDIO_D3"), ("SDIO_CK", "PC12_SDIO_CK"), ("SDIO_CMD", "PD2_SDIO_CMD"),
    ("LCD_CLK", "PI14_LCD_CLK"), ("LCD_DE", "PK7_LCD_DE"), ("LCD_HSYNC", "PI10_LCD_HSYNC"), ("LCD_VSYNC", "PI9_LCD_VSYNC"),
]
MCU_PINS += [(f"LCD_R{i}", pin) for i, pin in enumerate(["PI15_LCD_R0", "PJ0_LCD_R1", "PJ1_LCD_R2", "PJ2_LCD_R3", "PJ3_LCD_R4", "PJ4_LCD_R5", "PJ5_LCD_R6", "PJ6_LCD_R7"])]
MCU_PINS += [(f"LCD_G{i}", pin) for i, pin in enumerate(["PJ7_LCD_G0", "PJ8_LCD_G1", "PJ9_LCD_G2", "PJ10_LCD_G3", "PJ11_LCD_G4", "PK0_LCD_G5", "PK1_LCD_G6", "PK2_LCD_G7"])]
MCU_PINS += [(f"LCD_B{i}", pin) for i, pin in enumerate(["PJ12_LCD_B0", "PJ13_LCD_B1", "PJ14_LCD_B2", "PJ15_LCD_B3", "PK3_LCD_B4", "PI5_LCD_B5", "PI6_LCD_B6", "PI7_LCD_B7"])]
MCU_PINS += [(f"FMC_D{i}", pin) for i, pin in enumerate(["PD14_FMC_D0", "PD15_FMC_D1", "PD0_FMC_D2", "PD1_FMC_D3", "PE7_FMC_D4", "PE8_FMC_D5", "PE9_FMC_D6", "PE10_FMC_D7", "PE11_FMC_D8", "PE12_FMC_D9", "PE13_FMC_D10", "PE14_FMC_D11", "PE15_FMC_D12", "PD8_FMC_D13", "PD9_FMC_D14", "PD10_FMC_D15"])]
MCU_PINS += [(f"FMC_A{i}", pin) for i, pin in enumerate(["PF0_FMC_A0", "PF1_FMC_A1", "PF2_FMC_A2", "PF3_FMC_A3", "PF4_FMC_A4", "PF5_FMC_A5", "PF12_FMC_A6", "PF13_FMC_A7", "PF14_FMC_A8", "PF15_FMC_A9", "PG0_FMC_A10", "PG1_FMC_A11", "PG2_FMC_A12"])]
MCU_PINS += [
    ("FMC_BA0", "PG4_FMC_BA0"), ("FMC_BA1", "PG5_FMC_BA1"),
    ("FMC_SDCLK", "PG8_FMC_SDCLK"), ("FMC_SDCKE1", "PB5_FMC_SDCKE1"),
    ("FMC_SDNE1", "PB6_FMC_SDNE1"), ("FMC_SDNRAS", "PF11_FMC_SDNRAS"),
    ("FMC_SDNCAS", "PG15_FMC_SDNCAS"), ("FMC_SDNWE", "PC0_FMC_SDNWE"),
    ("FMC_NBL0", "PE0_FMC_NBL0"), ("FMC_NBL1", "PE1_FMC_NBL1"),
]
U2 = template("U", "STM32F429IGT6", MCU_PINS)()

NRST = make_net("NRST")
BOOT0 = make_net("BOOT0")
HSE_IN = make_net("HSE_IN")
HSE_OUT = make_net("HSE_OUT")
USB_DM = make_net("USB_DM")
USB_DP = make_net("USB_DP")
SWDIO = make_net("SWDIO")
SWCLK = make_net("SWCLK")
SWO = make_net("SWO")
I2C1_SCL = make_net("I2C1_SCL")
I2C1_SDA = make_net("I2C1_SDA")
TOUCH_IRQ = make_net("TOUCH_IRQ")
LCD_BL_PWM = make_net("LCD_BL_PWM")
SD_CARD_DETECT = make_net("SD_CARD_DETECT")

for power_pin in ("VDD", "VDDA"):
    connect(U2, power_pin, VDD_3V3)
for ground_pin in ("VSS", "VSSA"):
    connect(U2, ground_pin, GND)
connect(U2, "NRST", NRST)
connect(U2, "BOOT0", BOOT0)
connect(U2, "OSC_IN", HSE_IN)
connect(U2, "OSC_OUT", HSE_OUT)
connect(U2, "USB_DM", USB_DM)
connect(U2, "USB_DP", USB_DP)
connect(U2, "SWDIO", SWDIO)
connect(U2, "SWCLK", SWCLK)
connect(U2, "SWO", SWO)
connect(U2, "I2C1_SCL", I2C1_SCL)
connect(U2, "I2C1_SDA", I2C1_SDA)
connect(U2, "TOUCH_IRQ", TOUCH_IRQ)
connect(U2, "LCD_BL_PWM", LCD_BL_PWM)
connect(U2, "SD_CARD_DETECT", SD_CARD_DETECT)


# === SDRAM W9825G6JH-6 블록 ===

# U3: W9825G6JH-6
# 한국어 명칭: 256Mbit SDRAM
# 선택 이유: LCD 프레임버퍼와 SD카드 이미지 캐싱용 외부 메모리.
# 주요 사양: 4M x 4 banks x 16 bits SDRAM, 3.3V, 166MHz(-6), TSOP-II-54.
# EasyEDA 검색어: W9825G6JH-6
# LCSC Part#: C20512714 (Winbond W9825G6JH-6, 256Mbit SDRAM, TSOP-II-54)
# JLCPCB 재고: LCSC 데이터시트 productCode 확인. JLCPCB 조립 재고는 실제 주문 전 재확인 필요.
# 핀 정의: VDD/VDDQ=VDD_3V3, VSS/VSSQ=GND, DQ0~15/FMC_D0~15,
#          A0~12/FMC_A0~12, BA0~1, CLK/CKE/CS/RAS/CAS/WE, LDQM/UDQM.
#          EasyEDA Pro에서 TSOP-II-54 실제 핀 번호와 Winbond 데이터시트 대조.
SDRAM_PINS = [("VDD", "VDD"), ("VDDQ", "VDDQ"), ("VSS", "VSS"), ("VSSQ", "VSSQ")]
SDRAM_PINS += [(f"DQ{i}", f"DQ{i}") for i in range(16)]
SDRAM_PINS += [(f"A{i}", f"A{i}") for i in range(13)]
SDRAM_PINS += [("BA0", "BA0"), ("BA1", "BA1"), ("CLK", "CLK"), ("CKE", "CKE"), ("CS_N", "CS_N"), ("RAS_N", "RAS_N"), ("CAS_N", "CAS_N"), ("WE_N", "WE_N"), ("LDQM", "LDQM"), ("UDQM", "UDQM")]
U3 = template("U", "W9825G6JH_6_SDRAM", SDRAM_PINS)()

FMC_NETS = {}
for name in [f"FMC_D{i}" for i in range(16)] + [f"FMC_A{i}" for i in range(13)]:
    FMC_NETS[name] = make_net(name)
for name in ("FMC_BA0", "FMC_BA1", "FMC_SDCLK", "FMC_SDCKE1", "FMC_SDNE1", "FMC_SDNRAS", "FMC_SDNCAS", "FMC_SDNWE", "FMC_NBL0", "FMC_NBL1"):
    FMC_NETS[name] = make_net(name)

for i in range(16):
    connect(U2, f"FMC_D{i}", FMC_NETS[f"FMC_D{i}"])
    connect(U3, f"DQ{i}", FMC_NETS[f"FMC_D{i}"])
for i in range(13):
    connect(U2, f"FMC_A{i}", FMC_NETS[f"FMC_A{i}"])
    connect(U3, f"A{i}", FMC_NETS[f"FMC_A{i}"])
connect(U2, "FMC_BA0", FMC_NETS["FMC_BA0"])
connect(U2, "FMC_BA1", FMC_NETS["FMC_BA1"])
connect(U3, "BA0", FMC_NETS["FMC_BA0"])
connect(U3, "BA1", FMC_NETS["FMC_BA1"])
connect(U2, "FMC_SDCLK", FMC_NETS["FMC_SDCLK"])
connect(U2, "FMC_SDCKE1", FMC_NETS["FMC_SDCKE1"])
connect(U2, "FMC_SDNE1", FMC_NETS["FMC_SDNE1"])
connect(U2, "FMC_SDNRAS", FMC_NETS["FMC_SDNRAS"])
connect(U2, "FMC_SDNCAS", FMC_NETS["FMC_SDNCAS"])
connect(U2, "FMC_SDNWE", FMC_NETS["FMC_SDNWE"])
connect(U2, "FMC_NBL0", FMC_NETS["FMC_NBL0"])
connect(U2, "FMC_NBL1", FMC_NETS["FMC_NBL1"])
connect(U3, "CLK", FMC_NETS["FMC_SDCLK"])
connect(U3, "CKE", FMC_NETS["FMC_SDCKE1"])
connect(U3, "CS_N", FMC_NETS["FMC_SDNE1"])
connect(U3, "RAS_N", FMC_NETS["FMC_SDNRAS"])
connect(U3, "CAS_N", FMC_NETS["FMC_SDNCAS"])
connect(U3, "WE_N", FMC_NETS["FMC_SDNWE"])
connect(U3, "LDQM", FMC_NETS["FMC_NBL0"])
connect(U3, "UDQM", FMC_NETS["FMC_NBL1"])
for pin_name in ("VDD", "VDDQ"):
    connect(U3, pin_name, VDD_3V3)
for pin_name in ("VSS", "VSSQ"):
    connect(U3, pin_name, GND)


# === DWIN LN80480T070IA9098 50핀 LCD-TFT 출력 블록 ===

# J2: LCD 50핀 FPC 커넥터
# 한국어 명칭: DWIN LN80480T070IA9098용 50핀 0.5mm FPC 커넥터
# 선택 이유: 패널 데이터시트의 RGB_24bit 50PIN_0.5mm 인터페이스에 맞춘다.
# 주요 사양: 50P, 0.5mm pitch, bottom contact, right angle, 400mA/pin, 50V.
# EasyEDA 검색어: AFC07-S50FCC-00
# LCSC Part#: C11063 (JUSHUO AFC07-S50FCC-00, 50P 0.5mm FPC bottom contact connector)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 in stock 13048.
# 핀 정의: DWIN LN80480T070IA9098 데이터시트 기준.
#          Pin1-2=LEDA, Pin3-4=LEDK, Pin5=GND, Pin6=VCOM, Pin7=DVDD,
#          Pin8=MODE, Pin9=DE, Pin10=VS, Pin11=HS, Pin12-19=B7..B0,
#          Pin20-27=G7..G0, Pin28-35=R7..R0, Pin36=GND, Pin37=DCLK,
#          Pin38=GND, Pin39=좌우 스캔 설정(GND 기본), Pin40=U/D, Pin41=VGH,
#          Pin42=VGL, Pin43=AVDD, Pin44=RESET, Pin45=NC, Pin46=VCOM,
#          Pin47=DITHB, Pin48=GND, Pin49=NC, Pin50=NC.
#          FPC 접점 방향(top/bottom contact)과 Pin1 위치는 실제 패널 FPC 실물과 반드시 대조.
J2 = make_connector("J", "DWIN_LN80480T070IA9098_LCD_50P_FPC", 50)()

LCD_NETS = {}
for name in ["LCD_CLK", "LCD_DE", "LCD_HSYNC", "LCD_VSYNC", "LCD_RESET", "LCD_MODE", "LCD_UD", "LCD_VCOM", "LCD_VGH", "LCD_VGL", "LCD_AVDD"]:
    LCD_NETS[name] = make_net(name)
for color in ("R", "G", "B"):
    for idx in range(8):
        LCD_NETS[f"LCD_{color}{idx}"] = make_net(f"LCD_{color}{idx}")

for name in ("LCD_CLK", "LCD_DE", "LCD_HSYNC", "LCD_VSYNC"):
    connect(U2, name, LCD_NETS[name])
for color in ("R", "G", "B"):
    for idx in range(8):
        connect(U2, f"LCD_{color}{idx}", LCD_NETS[f"LCD_{color}{idx}"])

# U6: LCD 패널 바이어스 전원 회로 포트
# 한국어 명칭: LCD VGH/VGL/AVDD/VCOM 바이어스 전원 포트
# 선택 이유: DWIN 50핀 raw RGB 패널의 VGH/VGL/AVDD/VCOM 핀을 떠 있게 두지 않고,
#           실제 LCD bias IC/charge pump 회로로 교체할 위치를 명확히 한다.
# 주요 사양: VIN=VIN_12V_PROTECTED 또는 VDD_3V3 입력, 출력 AVDD/VGH/VGL/VCOM.
# EasyEDA 검색어: LCD TFT bias power IC VGH VGL AVDD VCOM
# LCSC Part#: 해당 없음. 구매 부품 아님, 회로 블록 연결 표시. 패널 전압 조건 확인 후 실제 부품 선정 필요.
# 핀 정의: VIN=VIN_12V_PROTECTED, GND=GND, AVDD=LCD_AVDD, VGH=LCD_VGH, VGL=LCD_VGL, VCOM=LCD_VCOM.
# 주의: 이 포트는 완성 전력단이 아니다. DWIN 원본 PDF의 전압/시퀀싱/리플 조건으로 실제 회로를 별도 검토한다.
U6 = template("U", "LCD_BIAS_POWER_PORT_REVIEW", [("VIN", "VIN"), ("GND", "GND"), ("AVDD", "AVDD"), ("VGH", "VGH"), ("VGL", "VGL"), ("VCOM", "VCOM")])()
U6["VIN"] += VIN_12V_PROTECTED
U6["GND"] += GND
U6["AVDD"] += LCD_NETS["LCD_AVDD"]
U6["VGH"] += LCD_NETS["LCD_VGH"]
U6["VGL"] += LCD_NETS["LCD_VGL"]
U6["VCOM"] += LCD_NETS["LCD_VCOM"]

# R3/R4: LCD 모드/스캔방향 설정 저항
# 한국어 명칭: LCD 설정 풀 저항
# 선택 이유: MODE, U/D 같은 패널 설정 핀이 떠 있지 않게 기본값을 둔다.
# 주요 사양: 10k, 1%, 0603. 패널 장착 방향에 따라 VDD/GND 옵션 저항으로 변경 가능.
# EasyEDA 검색어: 10k 0603 resistor
# LCSC Part#: C25804 (Uni-Royal 0603WAF1002T5E, 10k 1% 0603 resistor)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 C25804 in stock 38507873.
# 핀 정의: 무극성. R3 Pin1=LCD_MODE, Pin2=GND. R4 Pin1=LCD_UD, Pin2=GND.
R3 = template("R", "LCD_MODE_PULLDOWN_10K", [("1", "1"), ("2", "2")])()
R4 = template("R", "LCD_UD_PULLDOWN_10K", [("1", "1"), ("2", "2")])()
R3["1"] += LCD_NETS["LCD_MODE"]
R3["2"] += GND
R4["1"] += LCD_NETS["LCD_UD"]
R4["2"] += GND

# LCD RESET은 MCU NRST와 함께 리셋되도록 묶는다. 별도 GPIO 제어가 필요하면 CubeMX 핀맵 재검토 후 변경.
LCD_NETS["LCD_RESET"] += NRST

J2["1"] += BL_LED_A       # 백라이트 전류 경로, LED driver 출력. 1.00mm 이상 권장.
J2["2"] += BL_LED_A       # 백라이트 전류 경로, 병렬 핀.
J2["3"] += BL_LED_K       # 백라이트 전류 경로, LED driver 리턴.
J2["4"] += BL_LED_K       # 백라이트 전류 경로, 병렬 핀.
J2["5"] += GND            # GND plane
J2["6"] += LCD_NETS["LCD_VCOM"]   # 0.25mm, 패널 데이터시트 전압 조건 별도 검토
J2["7"] += VDD_LCD_3V3    # 0.50mm
J2["8"] += LCD_NETS["LCD_MODE"]   # 0.25mm, DE/SYNC 모드 설정
J2["9"] += LCD_NETS["LCD_DE"]     # 0.25mm, 길이 매칭 검토
J2["10"] += LCD_NETS["LCD_VSYNC"] # 0.25mm
J2["11"] += LCD_NETS["LCD_HSYNC"] # 0.25mm
for offset, bit in enumerate(range(7, -1, -1), start=12):
    J2[str(offset)] += LCD_NETS[f"LCD_B{bit}"]  # 0.25mm, B7..B0
for offset, bit in enumerate(range(7, -1, -1), start=20):
    J2[str(offset)] += LCD_NETS[f"LCD_G{bit}"]  # 0.25mm, G7..G0
for offset, bit in enumerate(range(7, -1, -1), start=28):
    J2[str(offset)] += LCD_NETS[f"LCD_R{bit}"]  # 0.25mm, R7..R0
J2["36"] += GND
J2["37"] += LCD_NETS["LCD_CLK"]    # 0.25mm, LTDC clock. skew/return path 주의.
J2["38"] += GND
J2["39"] += GND                    # 좌/우 스캔 기본 GND. 패널 방향에 맞춰 옵션 저항화 검토.
J2["40"] += LCD_NETS["LCD_UD"]     # 상/하 스캔 설정. 옵션 저항화 검토.
J2["41"] += LCD_NETS["LCD_VGH"]    # 패널 내부/외부 전원 조건 대조 필요.
J2["42"] += LCD_NETS["LCD_VGL"]    # 패널 내부/외부 전원 조건 대조 필요.
J2["43"] += LCD_NETS["LCD_AVDD"]   # 패널 내부/외부 전원 조건 대조 필요.
J2["44"] += LCD_NETS["LCD_RESET"]  # 0.25mm, RC reset 또는 MCU GPIO 연결 검토.
J2["46"] += LCD_NETS["LCD_VCOM"]
J2["47"] += GND                    # DITHB=L: 8bit 해상도 기본 설정.
J2["48"] += GND
VDD_LCD_3V3 += VDD_3V3


# === 백라이트 LED 드라이버 검토 블록 ===

# U4: 백라이트 드라이버 자리
# 한국어 명칭: LCD 백라이트 정전류 드라이버 자리
# 선택 이유: LN80480T070IA9098의 LEDA/LEDK를 MCU 로직 전원에 직접 물리지 않는다.
# 주요 사양: 입력 VIN_12V_PROTECTED, 출력 BL_LED_A/BL_LED_K, PWM dimming 입력.
# EasyEDA 검색어: LCD backlight LED driver 12V 9V constant current
# LCSC Part#: 해당 없음. 패널 백라이트 전류, LED 직렬/병렬 구성, 목표 밝기, 발열 계산 후 확정한다.
# 핀 정의: VIN=VIN_12V_PROTECTED, GND=GND, LEDA=BL_LED_A, LEDK=BL_LED_K, PWM=LCD_BL_PWM.
# 주의: 이 블록은 연결 의도를 명시하는 회로 자리이며, 실제 제작 전 확정 LED 드라이버로 교체해야 한다.
U4 = template("U", "LCD_BACKLIGHT_DRIVER_REVIEW", [("VIN", "VIN"), ("GND", "GND"), ("LEDA", "LEDA"), ("LEDK", "LEDK"), ("PWM", "PWM")])()
U4["VIN"] += VIN_12V_PROTECTED
U4["GND"] += GND
U4["LEDA"] += BL_LED_A
U4["LEDK"] += BL_LED_K
U4["PWM"] += LCD_BL_PWM


# === YF-07002 4핀 감압식 터치 + AR1020 블록 ===

# J3: YF-07002 터치 FPC 커넥터
# 한국어 명칭: 4선 감압식 터치 패널 FPC 커넥터
# 선택 이유: YF-07002는 7인치 4-wire resistive touch panel이므로 별도 4핀 FPC를 받는다.
# 주요 사양: 4P, 0.5mm pitch, bottom contact, right angle.
# EasyEDA 검색어: AFC07-S04FCC-00
# LCSC Part#: C11047 (JUSHUO AFC07-S04FCC-00, 4P 0.5mm FPC bottom contact connector)
# JLCPCB 재고: 확인됨. 2026-06-05 LCSC 이미지/재고 검색 기준 in stock 11438.
# 핀 정의: YF-07002 단품 자료에서 핀 순서 이미지를 실제 FPC와 대조한다.
#          DWIN LCD-TR 자료의 4선 터치 표기는 Pin1=XL, Pin2=YD, Pin3=XR, Pin4=YU이다.
J3 = make_connector("J", "YF07002_TOUCH_4P_FPC", 4)()

TOUCH_XL = make_net("TOUCH_XL")
TOUCH_YD = make_net("TOUCH_YD")
TOUCH_XR = make_net("TOUCH_XR")
TOUCH_YU = make_net("TOUCH_YU")
J3["1"] += TOUCH_XL   # 0.25mm, Pin1=XL. 실제 FPC 대조.
J3["2"] += TOUCH_YD   # 0.25mm, Pin2=YD.
J3["3"] += TOUCH_XR   # 0.25mm, Pin3=XR.
J3["4"] += TOUCH_YU   # 0.25mm, Pin4=YU.

# U5: AR1020
# 한국어 명칭: 4선 감압식 터치 컨트롤러
# 선택 이유: 사용자가 AR1020을 지정했고, I2C/SPI로 STM32와 통신 가능한 resistive touch controller이다.
# 주요 사양: 4/5/8-wire resistive 지원, 10-bit 위치, I2C/SPI, 2.5V~5.5V, 20-SSOP.
# EasyEDA 검색어: AR1020-I/SS
# LCSC Part#: 해당 없음. Microchip AR1020은 사용자 지정 부품이며 JLCPCB 조립 재고는 확인하지 못했다.
#               실제 제작 시 별도 구매/위탁 조립 또는 AR1021 등 대체품 검토 필요.
# 핀 정의: VDD=VDD_TOUCH_3V3, VSS=GND, M1/M2=I2C+4wire 설정,
#          SCL/SDA=I2C1, IRQ=TOUCH_IRQ, X+/X-/Y+/Y-=YF-07002 전극.
#          AR1020 SSOP-20 실제 핀 번호는 Microchip 데이터시트와 대조.
U5 = template(
    "U",
    "AR1020_I_SS_TOUCH_CONTROLLER",
    [
        ("VDD", "VDD"), ("VSS", "VSS"), ("M1", "M1"), ("M2", "M2"), ("WAKE", "WAKE"),
        ("IRQ", "SIQ_IRQ"), ("SDA", "SDI_SDA_RX"), ("SCL", "SCK_SCL_TX"),
        ("XPLUS", "XPLUS"), ("XMINUS", "XMINUS"), ("YPLUS", "YPLUS"), ("YMINUS", "YMINUS"),
    ],
)()
VDD_TOUCH_3V3 += VDD_3V3
U5["VDD"] += VDD_TOUCH_3V3
U5["VSS"] += GND
U5["SCL"] += I2C1_SCL
U5["SDA"] += I2C1_SDA
U5["IRQ"] += TOUCH_IRQ
U5["XMINUS"] += TOUCH_XL
U5["YMINUS"] += TOUCH_YD
U5["XPLUS"] += TOUCH_XR
U5["YPLUS"] += TOUCH_YU
U5["M1"] += GND   # I2C/SPI 선택은 데이터시트 표와 대조 후 확정. 기본은 I2C 의도.
U5["M2"] += GND   # 4-wire 센서 선택 의도. 실제 M1/M2 strap 표 대조 필요.
U5["WAKE"] += TOUCH_IRQ

# R1/R2: I2C pull-up
# 한국어 명칭: I2C 풀업 저항
# 선택 이유: AR1020 I2C 통신용 SDA/SCL 풀업.
# 주요 사양: 4.7k, 1%, 0603.
# EasyEDA 검색어: 4.7k 0603 resistor
# LCSC Part#: C23162 (Uni-Royal 0603WAF4701T5E, 4.7k 1% 0603 resistor)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 C23162 in stock 13489639.
# 핀 정의: 무극성, Pin1=VDD_3V3, Pin2=I2C line.
R1 = template("R", "I2C_SCL_PULLUP_4K7", [("1", "1"), ("2", "2")])()
R2 = template("R", "I2C_SDA_PULLUP_4K7", [("1", "1"), ("2", "2")])()
R1["1"] += VDD_3V3
R1["2"] += I2C1_SCL
R2["1"] += VDD_3V3
R2["2"] += I2C1_SDA


# === microSD 카드 블록 ===

# J4: microSD socket
# 한국어 명칭: microSD 카드 소켓
# 선택 이유: SD카드에서 이미지/리소스를 읽고 SDRAM에 캐싱한 뒤 LTDC로 출력한다.
# 주요 사양: microSD/TF card socket, hinged lid, SMD.
# EasyEDA 검색어: HYC39-TF08-180
# LCSC Part#: C341095 (HOAUC HYC39-TF08-180, MicroSD Card connector)
# JLCPCB 재고: 확인됨. 2026-06-05 JLCPCB 검색 결과 확인.
# 핀 정의: DAT0~3, CLK, CMD, VDD, GND, CD. 실제 소켓 심볼 핀 번호 대조.
J4 = template("J", "MICROSD_SOCKET_HYC39_TF08_180", [("DAT0", "DAT0"), ("DAT1", "DAT1"), ("DAT2", "DAT2"), ("DAT3", "DAT3"), ("CLK", "CLK"), ("CMD", "CMD"), ("VDD", "VDD"), ("GND", "GND"), ("CD", "CD")])()
SDIO_NETS = {name: make_net(name) for name in ("SDIO_D0", "SDIO_D1", "SDIO_D2", "SDIO_D3", "SDIO_CK", "SDIO_CMD")}
SDIO_NETS["SD_CARD_DETECT"] = SD_CARD_DETECT
for name in ("SDIO_D0", "SDIO_D1", "SDIO_D2", "SDIO_D3", "SDIO_CK", "SDIO_CMD"):
    connect(U2, name, SDIO_NETS[name])
J4["DAT0"] += SDIO_NETS["SDIO_D0"]
J4["DAT1"] += SDIO_NETS["SDIO_D1"]
J4["DAT2"] += SDIO_NETS["SDIO_D2"]
J4["DAT3"] += SDIO_NETS["SDIO_D3"]
J4["CLK"] += SDIO_NETS["SDIO_CK"]
J4["CMD"] += SDIO_NETS["SDIO_CMD"]
J4["VDD"] += VDD_3V3
J4["GND"] += GND
J4["CD"] += SDIO_NETS["SD_CARD_DETECT"]


# === 펌웨어 업로드/디버그 블록 ===

# J5: SWD programming header
# 한국어 명칭: STM32 SWD 업로드/디버그 헤더
# 선택 이유: 플래시 펌웨어 업로드와 디버깅을 안정적으로 지원한다.
# 주요 사양: 1x6 2.54mm header 또는 Tag-Connect로 변경 가능.
# EasyEDA 검색어: PinHeader 1x6 2.54
# LCSC Part#: 해당 없음. 개발/디버그용 헤더로 실제 기구 조건에 맞춰 확정한다.
# 핀 정의: Pin1=VDD_3V3, Pin2=SWDIO, Pin3=SWCLK, Pin4=SWO, Pin5=NRST, Pin6=GND.
J5 = make_connector("J", "SWD_1X6_PROGRAM_HEADER", 6)()
J5["1"] += VDD_3V3
J5["2"] += SWDIO
J5["3"] += SWCLK
J5["4"] += SWO
J5["5"] += NRST
J5["6"] += GND

# J6: USB FS DFU/service connector
# 한국어 명칭: USB FS 펌웨어 업로드/서비스 커넥터 자리
# 선택 이유: BOOT0로 ROM DFU 진입 후 USB를 통한 펌웨어 업로드를 가능하게 한다.
# 주요 사양: USB D+/D-/5V/GND. USB 5V는 전원 입력으로 쓰지 않는다. 감지/서비스용으로만 둔다.
# EasyEDA 검색어: USB-C connector USB2 only
# LCSC Part#: 해당 없음. 기구 위치와 조립 가능 커넥터 확정 후 선정.
# 핀 정의: Pin1=USB_5V_SENSE, Pin2=USB_DM, Pin3=USB_DP, Pin4=GND.
USB_5V_SENSE = make_net("USB_5V_SENSE")
J6 = make_connector("J", "USB_FS_DFU_SERVICE_PORT", 4)()
J6["1"] += USB_5V_SENSE  # 전원 입력으로 사용하지 않음. 0.25mm.
J6["2"] += USB_DM        # 0.25mm, differential pair routing 필요.
J6["3"] += USB_DP        # 0.25mm, differential pair routing 필요.
J6["4"] += GND

# JP1: BOOT0 선택 점퍼
# 한국어 명칭: BOOT0 부트모드 점퍼
# 선택 이유: STM32 ROM DFU/부트로더 진입 지원.
# 주요 사양: 3핀 점퍼 또는 0R 옵션. 기본 BOOT0=GND.
# EasyEDA 검색어: solder jumper 3pin
# LCSC Part#: 해당 없음. 디버그용 옵션 자리.
# 핀 정의: Pin1=VDD_3V3, Pin2=BOOT0, Pin3=GND.
JP1 = make_connector("JP", "BOOT0_SELECT_JUMPER", 3)()
JP1["1"] += VDD_3V3
JP1["2"] += BOOT0
JP1["3"] += GND

# R5: BOOT0 기본 풀다운
# 한국어 명칭: STM32 BOOT0 풀다운 저항
# 선택 이유: 점퍼 미장착 시 BOOT0가 떠서 부트 모드가 불안정해지는 것을 막는다.
# 주요 사양: 100k, 1%, 0603.
# EasyEDA 검색어: 100k 0603 resistor
# LCSC Part#: C25803 (Uni-Royal 0603WAF1003T5E, 100k 1% 0603 resistor)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 C25803 in stock 12851894.
# 핀 정의: 무극성, Pin1=BOOT0, Pin2=GND.
R5 = template("R", "BOOT0_PULLDOWN_100K", [("1", "1"), ("2", "2")])()
R5["1"] += BOOT0
R5["2"] += GND


# === 리셋/클럭/디커플링 블록 ===

# R6/C7: MCU/LCD reset network
# 한국어 명칭: STM32 및 LCD 리셋 RC 네트워크
# 선택 이유: NRST와 LCD_RESET이 전원 인가 시 안정적으로 High로 올라가고, SWD 헤더에서 강제 리셋 가능하게 한다.
# 주요 사양: R=10k 0603, C=100nF 0603.
# EasyEDA 검색어: 10k 0603 resistor, CL10B104KB8NNNC
# LCSC Part#: R6 C25804 (Uni-Royal 0603WAF1002T5E, 10k 1% 0603 resistor)
# LCSC Part#: C7 C1591 (Samsung CL10B104KB8NNNC, 100nF 50V X7R 0603 MLCC, Brand:SAMSUNG)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 R6 C25804 in stock 38507873, C7 C1591 재고 확인.
# 핀 정의: R6 무극성 Pin1=VDD_3V3, Pin2=NRST. C7 무극성 Pin1=NRST, Pin2=GND.
R6 = template("R", "NRST_PULLUP_10K", [("1", "1"), ("2", "2")])()
C7 = template("C", "NRST_RESET_CAP_100NF", [("1", "1"), ("2", "2")])()
R6["1"] += VDD_3V3
R6["2"] += NRST
C7["1"] += NRST
C7["2"] += GND

# Y1: HSE crystal
# 한국어 명칭: STM32 HSE 크리스털
# 선택 이유: LTDC 픽셀클럭/SDIO/FMC 안정성을 위해 외부 클럭 소스를 둔다.
# 주요 사양: 8MHz, 10pF load, +/-10ppm, SMD3225-4P. CubeMX PLL 설정과 함께 최종 확인.
# EasyEDA 검색어: TAXM8M4RDBCCT2T
# LCSC Part#: C400090 (Yajingxin TAXM8M4RDBCCT2T, 8MHz 10pF SMD3225-4P crystal)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB in stock 137791.
# 핀 정의: 무극성, Pin1=HSE_IN, Pin2=HSE_OUT.
Y1 = template("Y", "TAXM8M4RDBCCT2T_HSE_8MHZ", [("1", "1"), ("2", "2")])()
Y1["1"] += HSE_IN
Y1["2"] += HSE_OUT

# C8/C9: HSE 부하 캐패시터
# 한국어 명칭: HSE 크리스털 부하 캐패시터
# 선택 이유: 외부 크리스털이 부하용량 조건 없이 떠 있는 것을 막는다.
# 주요 사양: 18pF 시작점, 50V, C0G/NP0, 0603. 실제 값은 선택한 Y1 CL과 stray capacitance로 재계산.
# EasyEDA 검색어: 18pF C0G 0603
# LCSC Part#: C1647 (Samsung CL10C180JB8NNNC, 18pF 50V C0G 0603 MLCC, Brand:SAMSUNG)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB/LCSC 페이지 확인.
# 핀 정의: 무극성, C8 Pin1=HSE_IN Pin2=GND, C9 Pin1=HSE_OUT Pin2=GND.
C8 = template("C", "HSE_LOAD_CAP_IN_18PF", [("1", "1"), ("2", "2")])()
C9 = template("C", "HSE_LOAD_CAP_OUT_18PF", [("1", "1"), ("2", "2")])()
C8["1"] += HSE_IN
C8["2"] += GND
C9["1"] += HSE_OUT
C9["2"] += GND

# C5/C6: STM32/SDRAM/LCD 디커플링 대표 캐패시터
# 한국어 명칭: 로직 전원 디커플링 MLCC 묶음
# 선택 이유: STM32 LQFP176, SDRAM, LCD FPC 전원 가까이에 100nF 다수 배치.
# 주요 사양: 100nF, 50V, X7R, 0603, Samsung.
# EasyEDA 검색어: CL10B104KB8NNNC
# LCSC Part#: C1591 (Samsung CL10B104KB8NNNC, 100nF 50V X7R 0603 MLCC, Brand:SAMSUNG)
# JLCPCB 재고: 확인됨.
# 핀 정의: 무극성, Pin1=VDD_3V3, Pin2=GND. 실제 회로도에서는 각 전원핀 근처에 개별 배치.
C5 = template("C", "MCU_SDRAM_DECOUPLING_100NF_ARRAY_A", [("1", "1"), ("2", "2")])()
C6 = template("C", "LCD_TOUCH_DECOUPLING_100NF_ARRAY_B", [("1", "1"), ("2", "2")])()
C5["1"] += VDD_3V3
C5["2"] += GND
C6["1"] += VDD_3V3
C6["2"] += GND


# === 기능 흐름 메모 ===

# 데이터 흐름:
# microSD(J4, SDIO 4-bit) -> STM32F429 SDIO/DMA -> W9825G6JH SDRAM(FMC, 16-bit)
# -> STM32 LTDC framebuffer fetch -> LN80480T070IA9098 RGB24 50핀 출력.
#
# 펌웨어 업로드:
# - 기본: J5 SWD 헤더로 STM32 Flash 업로드/디버그.
# - 대안: JP1로 BOOT0=High, J6 USB FS로 ROM DFU 진입. USB 5V는 보드 전원 입력으로 쓰지 않는다.
#
# 남은 필수 검토:
# - LCD Pin41 VGH, Pin42 VGL, Pin43 AVDD, Pin6/46 VCOM이 패널 내부 생성인지 외부 입력인지 DWIN 원본 PDF로 재확인.
# - LCD 백라이트 정전류 드라이버는 전류/발열/밝기 목표가 정해진 뒤 확정 부품으로 교체.
# - LTDC/FMC/SDIO 핀맵은 CubeMX에서 충돌 없이 확정하고 EasyEDA LQFP176 핀 번호와 대조.
# - 24bit RGB/FMC SDRAM은 고속 병렬 버스이므로 4층 PCB, 연속 GND plane, 짧은 리턴 경로, 길이 스큐 관리 권장.


if __name__ == "__main__":
    ERC()
    generate_netlist(file_="lcd_tft_stm32f429.net")
