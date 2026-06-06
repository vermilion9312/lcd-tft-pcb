from skidl import *


# LCD-TFT HMI + MD5-HF14 4축 컨트롤 PCB
#
# 설계 기준:
# - 고정 부품: DWIN LN80480T070IA9098 7인치 RGB LCD, YF-07002 4선 감압식 터치.
# - HMI: STM32 + TouchGFX, 외부 SDRAM 프레임버퍼, QSPI flash 리소스 저장.
# - 모션: Autonics MD5-HF14 드라이브 4대. 각 축은 CW/CCW 출력만 PCB에서 구동한다.
# - 입력: 24V NPN 센서 8점. 각 입력은 포토커플러로 3.3V MCU 영역과 절연 수신.
# - 업로드/디버그: 온보드 STLINK-V3MODS USB 포트로 STM32H753 SWD flash/debug를 수행한다.
# - 전원: 단일 외부 입력 VIN_24V_IN에서 5V/3.3V를 만든다. STLINK USB 5V는 보드 전원 입력으로 쓰지 않는다.
#
# 주의:
# - LN80480T070IA9098의 VGH/VGL/AVDD/VCOM 및 백라이트 전류는 원본 PDF 값으로 최종 전력단을 확정해야 한다.
# - MD5-HF14는 AC 100~220V 구동 장치다. 이 PCB는 드라이브 전원/모터 전류를 다루지 않고 제어 신호만 낸다.
# - 24V NPN 센서 입력은 산업 현장 배선 노이즈가 크므로 실제 PCB에서 TVS, 이격, 실드, 접지 정책을 별도 점검한다.


# === 전원 입력/보호 블록 ===

VIN_24V_IN = Net("VIN_24V_IN")
VIN_24V_PROTECTED = Net("VIN_24V_PROTECTED")
VCTRL_5V = Net("VCTRL_5V")
VDD_3V3 = Net("VDD_3V3")
GND = Net("GND")

# J1: 24V DC 단일 전원 입력
# 한국어 명칭: 24V DC 입력 5557-02A 커넥터
# 선택 이유: 24V NPN 센서와 보드 전원을 한 입력에서 공급한다.
# 주요 사양: 2P 4.2mm 5557 계열 wire-to-board connector, through-hole, wave soldering.
# EasyEDA 검색어: FG-5557-02A
# LCSC/JLCPCB Part#: C53325659 (FG FG-5557-02A, 2P 4.2mm 5557 wire-to-board connector, Plugin,P=4.2mm)
# JLCPCB 재고: 확인됨(2026-06-05 기준). 실제 mating housing/terminal과 허용 전류는 하네스 굵기 기준으로 EasyEDA Pro에서 대조.
# 핀 정의: Pin1=VIN_24V_IN(+24V), Pin2=GND(0V). 커넥터 키 방향 기준 극성 고정.
J1 = Part(name="VIN_24V_INPUT_5557_02A_2P", dest=TEMPLATE, tool=SKIDL, ref_prefix="J", footprint="EasyEDA:VIN_24V_INPUT_5557_02A_2P", pins=[Pin(num=str(idx), name=str(idx)) for idx in range(1, 2 + 1)])()

# F1: 입력 퓨즈
# 한국어 명칭: 24V 입력 보호 퓨즈
# 선택 이유: 보드 내부 buck/센서 보조 배선 단락 시 입력 배선을 보호한다.
# 주요 사양: 2A fast blow, 1206, 32V.
# EasyEDA 검색어: S1206-F-2.0A
# LCSC Part#: C553922 (AEM S1206-F-2.0A, 2A 32V fuse, 1206)
# JLCPCB 재고: 확인됨. 교체형 아님, 홀더 해당 없음.
# 핀 정의: 무극성. Pin1=입력 커넥터 쪽, Pin2=보호 전원 쪽.
F1 = Part(name="INPUT_FUSE_2A_32V_1206", dest=TEMPLATE, tool=SKIDL, ref_prefix="F", footprint="EasyEDA:INPUT_FUSE_2A_32V_1206", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# D1: 입력 TVS
# 한국어 명칭: 24V 입력 서지 억제 TVS
# 선택 이유: 긴 센서/전원 배선에서 유입되는 과도 전압을 완화한다.
# 주요 사양: 600W급 단방향 TVS, 33V 계열, SMA.
# EasyEDA 검색어: SMAJ33A
# LCSC Part#: C113966 (MDD SMAJ33A, 33V unidirectional TVS, DO-214AC(SMA), 53.3V clamp)
# JLCPCB 재고: 확인됨. 24V 라인의 클램프 전압/서지 에너지는 현장 조건으로 재검토.
# 핀 정의: Pin1=K(캐소드)=VIN_24V_PROTECTED, Pin2=A(애노드)=GND. SMD 띠 표시는 캐소드.
D1 = Part(name="INPUT_TVS_SMAJ33A", dest=TEMPLATE, tool=SKIDL, ref_prefix="D", footprint="EasyEDA:INPUT_TVS_SMAJ33A", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("K", "K"), ("A", "A")]])()

# C1/C2: 입력 bulk/MLCC
# 한국어 명칭: 24V 입력 평활 캐패시터
# 선택 이유: buck 입력 펄스 전류와 케이블 인덕턴스에 의한 링잉을 완화한다.
# 주요 사양: 10uF 50V X5R 1206, Samsung MLCC.
# EasyEDA 검색어: CL31A106KBHNNNE
# LCSC Part#: C13585 (Samsung CL31A106KBHNNNE, 10uF 50V X5R 1206 MLCC, Brand:SAMSUNG(三星))
# JLCPCB 재고: 확인됨. DC bias로 유효 용량이 줄어드므로 2개 병렬 배치.
# 핀 정의: 무극성. Pin1=VIN_24V_PROTECTED, Pin2=GND.
C1 = Part(name="INPUT_10UF_50V_SAMSUNG_A", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:INPUT_10UF_50V_SAMSUNG_A", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
C2 = Part(name="INPUT_10UF_50V_SAMSUNG_B", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:INPUT_10UF_50V_SAMSUNG_B", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# PCB 트랙 폭 가이드(mm)
# - VIN_24V_IN/VIN_24V_PROTECTED: 1.00mm 이상, 전원 입력부는 copper pour 권장.
# - buck SW 노드: 1.00mm 정도로 짧게, FB/USB/터치/I2C에서 멀리 배치.
# - VCTRL_5V: 0.80mm 이상. MD5 입력 포토커플러 전류와 USB VBUS 감지만 공급.
# - VDD_3V3: 1.00mm 이상 또는 plane. STM32/SDRAM/QSPI/LCD/터치로 분기.
# - GND: 연속 단일 GND plane. buck 고주파 루프와 센서/USB/고속 디지털 리턴 경로는 배치로 분리 관리.
J1["1"] += VIN_24V_IN      # 1.00mm 이상
J1["2"] += GND             # GND plane
F1["1"] += VIN_24V_IN      # 1.00mm 이상
F1["2"] += VIN_24V_PROTECTED  # 1.00mm 이상
D1["K"] += VIN_24V_PROTECTED
D1["A"] += GND
C1["1"] += VIN_24V_PROTECTED
C1["2"] += GND
C2["1"] += VIN_24V_PROTECTED
C2["2"] += GND


# === 24V -> 5V / 3.3V buck 전원 블록 ===

BUCK5_SW = Net("BUCK5_SW")
BUCK5_BST = Net("BUCK5_BST")
BUCK3V3_SW = Net("BUCK3V3_SW")
BUCK3V3_BST = Net("BUCK3V3_BST")

# U1: AP63205WU-7
# 한국어 명칭: 5V buck regulator
# 선택 이유: 24V 입력에서 MD5 제어 입력 구동용 5V와 USB VBUS 감지 보조 전원을 만든다.
# 주요 사양: 입력 3.8V~32V, 출력 5V fixed, 2A, 1.1MHz, TSOT-23-6.
# EasyEDA 검색어: AP63205WU-7
# LCSC Part#: C2071056 (Diodes AP63205WU-7, fixed 5V 2A buck regulator, TSOT-23-6)
# JLCPCB 재고: 확인됨. 24V 입력 사용 시 레이아웃과 열을 데이터시트대로 검토.
# 핀 정의: VIN=VIN_24V_PROTECTED, GND=GND, SW=BUCK5_SW, FB=VCTRL_5V, EN=VIN_24V_PROTECTED, BST=BUCK5_BST.
U1 = Part(name="AP63205WU_7_5V_BUCK", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:AP63205WU_7_5V_BUCK", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("VIN", "VIN"), ("GND", "GND"), ("SW", "SW"), ("FB", "FB"), ("EN", "EN"), ("BST", "BST")]])()

# U2: AP63203WU-7
# 한국어 명칭: 3.3V buck regulator
# 선택 이유: STM32H7, SDRAM, QSPI flash, LCD/터치 로직용 3.3V를 만든다.
# 주요 사양: 입력 3.8V~32V, 출력 3.3V fixed, 2A, 1.1MHz, TSOT-23-6.
# EasyEDA 검색어: AP63203WU-7
# LCSC Part#: C780769 (Diodes AP63203WU-7, fixed 3.3V 2A buck regulator, TSOT-23-6)
# JLCPCB 재고: 확인됨. TouchGFX 구동 중 LTDC/SDRAM 피크 전류와 발열을 실측 검증.
# 핀 정의: VIN=VIN_24V_PROTECTED, GND=GND, SW=BUCK3V3_SW, FB=VDD_3V3, EN=VIN_24V_PROTECTED, BST=BUCK3V3_BST.
U2 = Part(name="AP63203WU_7_3V3_BUCK", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:AP63203WU_7_3V3_BUCK", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("VIN", "VIN"), ("GND", "GND"), ("SW", "SW"), ("FB", "FB"), ("EN", "EN"), ("BST", "BST")]])()

# L1/L2: buck 인덕터
# 한국어 명칭: buck 전력 인덕터
# 선택 이유: AP6320x 권장 범위의 4.7uH 차폐 인덕터를 사용한다.
# 주요 사양: 4.7uH, 차폐형, 5x5mm급, 포화전류 2A 이상 권장.
# EasyEDA 검색어: MWSA0503S-4R7MT
# LCSC Part#: C408410 (Sunlord MWSA0503S-4R7MT, 4.7uH shielded power inductor)
# JLCPCB 재고: 확인됨. 실제 Isat/Irms와 온도 상승은 AP6320x 데이터시트 계산으로 재검토.
# 핀 정의: 무극성. Pin1=SW, Pin2=출력 전원.
L1 = Part(name="BUCK5_INDUCTOR_4R7UH", dest=TEMPLATE, tool=SKIDL, ref_prefix="L", footprint="EasyEDA:BUCK5_INDUCTOR_4R7UH", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
L2 = Part(name="BUCK3V3_INDUCTOR_4R7UH", dest=TEMPLATE, tool=SKIDL, ref_prefix="L", footprint="EasyEDA:BUCK3V3_INDUCTOR_4R7UH", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# C3/C4/C5/C6: buck 출력 캐패시터
# 한국어 명칭: buck 출력 캐패시터
# 선택 이유: 5V/3.3V buck의 부하 과도 응답과 리플 완화.
# 주요 사양: 22uF 25V X5R 1206, Samsung MLCC.
# EasyEDA 검색어: CL31A226KAHNNNE
# LCSC Part#: C12891 (Samsung CL31A226KAHNNNE, 22uF 25V X5R 1206 MLCC, Brand:SAMSUNG(三星))
# JLCPCB 재고: 확인됨. 재고 불안정으로 지적된 22uF MLCC 코드는 쓰지 않는다.
# 핀 정의: 무극성. Pin1=출력 전원, Pin2=GND.
C3 = Part(name="BUCK5_OUTPUT_22UF_25V_A", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:BUCK5_OUTPUT_22UF_25V_A", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
C4 = Part(name="BUCK5_OUTPUT_22UF_25V_B", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:BUCK5_OUTPUT_22UF_25V_B", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
C5 = Part(name="BUCK3V3_OUTPUT_22UF_25V_A", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:BUCK3V3_OUTPUT_22UF_25V_A", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
C6 = Part(name="BUCK3V3_OUTPUT_22UF_25V_B", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:BUCK3V3_OUTPUT_22UF_25V_B", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# C7/C8: bootstrap capacitors
# 한국어 명칭: buck bootstrap 캐패시터
# 선택 이유: AP6320x high-side 스위치 구동에 필요하다.
# 주요 사양: 100nF 50V X7R 0603, Samsung MLCC.
# EasyEDA 검색어: CL10B104KB8NNNC
# LCSC Part#: C1591 (Samsung CL10B104KB8NNNC, 100nF 50V X7R 0603 MLCC, Brand:SAMSUNG(三星))
# JLCPCB 재고: 확인됨.
# 핀 정의: 무극성. Pin1=BST, Pin2=SW.
C7 = Part(name="BUCK5_BOOTSTRAP_100NF", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:BUCK5_BOOTSTRAP_100NF", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
C8 = Part(name="BUCK3V3_BOOTSTRAP_100NF", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:BUCK3V3_BOOTSTRAP_100NF", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

for regulator, sw, bst, output, inductor, cap_a, cap_b, boot in [
    (U1, BUCK5_SW, BUCK5_BST, VCTRL_5V, L1, C3, C4, C7),
    (U2, BUCK3V3_SW, BUCK3V3_BST, VDD_3V3, L2, C5, C6, C8),
]:
    regulator["VIN"] += VIN_24V_PROTECTED
    regulator["GND"] += GND
    regulator["SW"] += sw
    regulator["FB"] += output
    regulator["EN"] += VIN_24V_PROTECTED
    regulator["BST"] += bst
    inductor["1"] += sw
    inductor["2"] += output
    cap_a["1"] += output
    cap_a["2"] += GND
    cap_b["1"] += output
    cap_b["2"] += GND
    boot["1"] += bst
    boot["2"] += sw


# === STM32H753IIT6 MCU 블록 ===

# U3: STM32H753IIT6
# 한국어 명칭: TouchGFX HMI용 STM32H7 MCU
# 선택 이유: 7인치 800x480급 RGB LCD 구동에 필요한 LTDC, DMA2D, FMC SDRAM, QSPI, SWD debug/programming을 모두 갖는다.
# 주요 사양: Arm Cortex-M7, 최대 480MHz 계열, 2MB Flash, 1MB RAM, LQFP-176(24x24), 1.62V~3.6V.
# EasyEDA 검색어: STM32H753IIT6
# LCSC Part#: C146558 (STMicroelectronics STM32H753IIT6, LQFP-176, direct hand solder by user)
# JLCPCB 재고: MCU는 사용자가 직접 조달/수납땜하는 조건. ST 공식 Active/LQFP176 및 LCSC C146558 확인.
# 핀 정의: 아래 핀명은 기능 중심 표기다. 실제 LQFP-176 pin number와 alternate function은 CubeMX와 EasyEDA Pro 심볼에서 대조.
MCU_PINS = [
    ("VDD", "VDD"), ("VSS", "VSS"), ("VDDA", "VDDA"), ("VSSA", "VSSA"), ("VREFP", "VREFP"),
    ("VCAP1", "VCAP1"), ("VCAP2", "VCAP2"), ("NRST", "NRST"), ("BOOT0", "BOOT0"),
    ("OSC_IN", "PH0_OSC_IN"), ("OSC_OUT", "PH1_OSC_OUT"),
    ("USB_DM", "PA11_USB_OTG_FS_DM"), ("USB_DP", "PA12_USB_OTG_FS_DP"), ("USB_VBUS", "PA9_USB_VBUS"),
    ("SWDIO", "PA13_SWDIO"), ("SWCLK", "PA14_SWCLK"), ("SWO", "PB3_SWO"),
    ("I2C1_SCL", "PB8_I2C1_SCL"), ("I2C1_SDA", "PB9_I2C1_SDA"), ("TOUCH_IRQ", "PI13_TOUCH_IRQ"),
    ("LCD_BL_PWM", "PA8_TIM1_CH1_LCD_BL_PWM"),
    ("QSPI_CLK", "PB2_QUADSPI_CLK"), ("QSPI_NCS", "PG6_QUADSPI_BK1_NCS"),
    ("QSPI_IO0", "PD11_QUADSPI_BK1_IO0"), ("QSPI_IO1", "PD12_QUADSPI_BK1_IO1"),
    ("QSPI_IO2", "PE2_QUADSPI_BK1_IO2"), ("QSPI_IO3", "PD13_QUADSPI_BK1_IO3"),
    ("LCD_CLK", "PI14_LTDC_CLK"), ("LCD_DE", "PK7_LTDC_DE"), ("LCD_HSYNC", "PI10_LTDC_HSYNC"), ("LCD_VSYNC", "PI9_LTDC_VSYNC"),
]
MCU_PINS += [(f"LCD_R{i}", pin) for i, pin in [(3, "PJ2_LTDC_R3"), (4, "PJ3_LTDC_R4"), (5, "PJ4_LTDC_R5"), (6, "PJ5_LTDC_R6"), (7, "PJ6_LTDC_R7")]]
MCU_PINS += [(f"LCD_G{i}", pin) for i, pin in [(2, "PJ9_LTDC_G2"), (3, "PJ10_LTDC_G3"), (4, "PJ11_LTDC_G4"), (5, "PK0_LTDC_G5"), (6, "PK1_LTDC_G6"), (7, "PK2_LTDC_G7")]]
MCU_PINS += [(f"LCD_B{i}", pin) for i, pin in [(3, "PJ15_LTDC_B3"), (4, "PK3_LTDC_B4"), (5, "PI5_LTDC_B5"), (6, "PI6_LTDC_B6"), (7, "PI7_LTDC_B7")]]
MCU_PINS += [(f"FMC_D{i}", pin) for i, pin in enumerate(["PD14_FMC_D0", "PD15_FMC_D1", "PD0_FMC_D2", "PD1_FMC_D3", "PE7_FMC_D4", "PE8_FMC_D5", "PE9_FMC_D6", "PE10_FMC_D7", "PE11_FMC_D8", "PE12_FMC_D9", "PE13_FMC_D10", "PE14_FMC_D11", "PE15_FMC_D12", "PD8_FMC_D13", "PD9_FMC_D14", "PD10_FMC_D15"])]
MCU_PINS += [(f"FMC_A{i}", pin) for i, pin in enumerate(["PF0_FMC_A0", "PF1_FMC_A1", "PF2_FMC_A2", "PF3_FMC_A3", "PF4_FMC_A4", "PF5_FMC_A5", "PF12_FMC_A6", "PF13_FMC_A7", "PF14_FMC_A8", "PF15_FMC_A9", "PG0_FMC_A10", "PG1_FMC_A11", "PG2_FMC_A12"])]
MCU_PINS += [
    ("FMC_BA0", "PG4_FMC_BA0"), ("FMC_BA1", "PG5_FMC_BA1"),
    ("FMC_SDCLK", "PG8_FMC_SDCLK"), ("FMC_SDCKE1", "PB5_FMC_SDCKE1"),
    ("FMC_SDNE1", "PB6_FMC_SDNE1"), ("FMC_SDNRAS", "PF11_FMC_SDNRAS"),
    ("FMC_SDNCAS", "PG15_FMC_SDNCAS"), ("FMC_SDNWE", "PC0_FMC_SDNWE"),
    ("FMC_NBL0", "PE0_FMC_NBL0"), ("FMC_NBL1", "PE1_FMC_NBL1"),
]
for axis in range(1, 5):
    MCU_PINS += [
        (f"MD5_AXIS{axis}_CW", f"MD5_AXIS{axis}_CW_GPIO"),
        (f"MD5_AXIS{axis}_CCW", f"MD5_AXIS{axis}_CCW_GPIO"),
    ]
for channel in range(1, 9):
    MCU_PINS += [(f"SENSOR_IN{channel}_MCU", f"SENSOR_IN{channel}_MCU_GPIO")]
MCU_PINS += [("BUZZER_EN", "BUZZER_EN_GPIO")]
U3 = Part(name="STM32H753IIT6", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:STM32H753IIT6", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in MCU_PINS])()

MD5_AXIS_SIGNAL_NAMES = [
    "MD5_AXIS1_CW", "MD5_AXIS1_CCW",
    "MD5_AXIS2_CW", "MD5_AXIS2_CCW",
    "MD5_AXIS3_CW", "MD5_AXIS3_CCW",
    "MD5_AXIS4_CW", "MD5_AXIS4_CCW",
]
MD5_AXIS_PORT_NAMES = [
    "MD5_HF14_AXIS1_SIGNAL_5267_6P",
    "MD5_HF14_AXIS2_SIGNAL_5267_6P",
    "MD5_HF14_AXIS3_SIGNAL_5267_6P",
    "MD5_HF14_AXIS4_SIGNAL_5267_6P",
]
SENSOR_SIGNAL_NAMES = [
    "SENSOR_NPN_CH1", "SENSOR_NPN_CH2", "SENSOR_NPN_CH3", "SENSOR_NPN_CH4",
    "SENSOR_NPN_CH5", "SENSOR_NPN_CH6", "SENSOR_NPN_CH7", "SENSOR_NPN_CH8",
    "SENSOR_IN1_MCU", "SENSOR_IN2_MCU", "SENSOR_IN3_MCU", "SENSOR_IN4_MCU",
    "SENSOR_IN5_MCU", "SENSOR_IN6_MCU", "SENSOR_IN7_MCU", "SENSOR_IN8_MCU",
]

NRST = Net("NRST")
BOOT0 = Net("BOOT0")
HSE_IN = Net("HSE_IN")
HSE_OUT = Net("HSE_OUT")
USB_DM = Net("USB_DM")
USB_DP = Net("USB_DP")
USB_VBUS_SENSE = Net("USB_VBUS_SENSE")
STLINK_SWDIO = Net("STLINK_SWDIO")
STLINK_SWCLK = Net("STLINK_SWCLK")
STLINK_SWO = Net("STLINK_SWO")
I2C1_SCL = Net("I2C1_SCL")
I2C1_SDA = Net("I2C1_SDA")
TOUCH_IRQ = Net("TOUCH_IRQ")
LCD_BL_PWM = Net("LCD_BL_PWM")
BUZZER_EN = Net("BUZZER_EN")

for pin_name in ("VDD", "VDDA", "VREFP"):
    U3[pin_name] += VDD_3V3
for pin_name in ("VSS", "VSSA"):
    U3[pin_name] += GND
U3["NRST"] += NRST
U3["BOOT0"] += BOOT0
U3["OSC_IN"] += HSE_IN
U3["OSC_OUT"] += HSE_OUT
U3["USB_DM"] += USB_DM
U3["USB_DP"] += USB_DP
U3["USB_VBUS"] += USB_VBUS_SENSE
U3["SWDIO"] += STLINK_SWDIO
U3["SWCLK"] += STLINK_SWCLK
U3["SWO"] += STLINK_SWO
U3["I2C1_SCL"] += I2C1_SCL
U3["I2C1_SDA"] += I2C1_SDA
U3["TOUCH_IRQ"] += TOUCH_IRQ
U3["LCD_BL_PWM"] += LCD_BL_PWM
U3["BUZZER_EN"] += BUZZER_EN


# === STM32H7 리셋/부트/클럭 블록 ===

# Y1: HSE crystal
# 한국어 명칭: STM32H7 외부 고속 클럭
# 선택 이유: LTDC 픽셀클럭과 USB 주변장치 기준 클럭 안정성을 위해 외부 HSE를 둔다.
# 주요 사양: 8MHz, SMD3225, 10ppm급.
# EasyEDA 검색어: TAXM8M4RDBCCT2T
# LCSC Part#: C400090 (YXC TAXM8M4RDBCCT2T, 8MHz SMD3225 crystal)
# JLCPCB 재고: 확인됨. STM32H7 PLL 설정과 CL 값은 CubeMX에서 결정.
# 핀 정의: 무극성. Pin1=HSE_IN, Pin2=HSE_OUT.
Y1 = Part(name="HSE_8MHZ_CRYSTAL", dest=TEMPLATE, tool=SKIDL, ref_prefix="Y", footprint="EasyEDA:HSE_8MHZ_CRYSTAL", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# C9/C10: HSE load capacitors
# 한국어 명칭: HSE 로드 캐패시터
# 선택 이유: 8MHz crystal 부하 용량 설정.
# 주요 사양: 18pF 50V C0G 0603, Samsung MLCC.
# EasyEDA 검색어: CL10C180JB8NNNC
# LCSC Part#: C1647 (Samsung CL10C180JB8NNNC, 18pF 50V C0G 0603 MLCC, Brand:SAMSUNG(三星))
# JLCPCB 재고: 확인됨. 실제 CL은 크리스탈 데이터시트와 stray capacitance로 재계산.
# 핀 정의: 무극성. Pin1=HSE 노드, Pin2=GND.
C9 = Part(name="HSE_LOAD_18PF_A", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:HSE_LOAD_18PF_A", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
C10 = Part(name="HSE_LOAD_18PF_B", dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint="EasyEDA:HSE_LOAD_18PF_B", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# R1/R2: BOOT0/NRST
# 한국어 명칭: STM32 부트 및 리셋 기본 설정 저항
# 선택 이유: STLINK-V3MODS SWD 업로드 중 안정적인 리셋과 기본 부트 모드를 유지한다.
# 주요 사양: 10k, 100k 0603 저항.
# EasyEDA 검색어: 0603 resistor
# LCSC Part#: C25804 (Uni-Royal 0603WAF1002T5E, 10k 1% 0603 resistor), C25803 (Uni-Royal 0603WAF1003T5E, 100k 1% 0603 resistor)
# JLCPCB 재고: 확인됨.
# 핀 정의: 무극성. R1=NRST pull-up, R2=BOOT0 pull-down.
R1 = Part(name="NRST_PULLUP_10K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:NRST_PULLUP_10K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R2 = Part(name="BOOT0_PULLDOWN_100K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:BOOT0_PULLDOWN_100K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

# SW1: RESET button
# 한국어 명칭: 리셋 버튼
# 선택 이유: STLINK-V3MODS 업로드/디버그 중 수동 리셋과 보드 bring-up 확인에 사용한다.
# 주요 사양: SMD tactile switch.
# EasyEDA 검색어: TS-1187A-B-A-B
# LCSC Part#: C318884 (XKB TS-1187A-B-A-B, SMD tactile switch)
# JLCPCB 재고: 확인됨.
# 핀 정의: 무극성. Pin1=NRST, Pin2=GND.
SW1 = Part(name="RESET_BUTTON", dest=TEMPLATE, tool=SKIDL, ref_prefix="SW", footprint="EasyEDA:RESET_BUTTON", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()

Y1["1"] += HSE_IN
Y1["2"] += HSE_OUT
C9["1"] += HSE_IN
C9["2"] += GND
C10["1"] += HSE_OUT
C10["2"] += GND
R1["1"] += VDD_3V3
R1["2"] += NRST
R2["1"] += BOOT0
R2["2"] += GND
SW1["1"] += NRST
SW1["2"] += GND


# === SDRAM 프레임버퍼 블록 ===

# U4: W9825G6JH-6 SDRAM
# 한국어 명칭: TouchGFX 프레임버퍼용 외부 SDRAM
# 선택 이유: 800x480 RGB565 더블버퍼와 그래픽 작업 메모리를 MCU 내부 RAM만으로 처리하지 않는다.
# 주요 사양: 256Mbit, 16-bit SDRAM, 3.3V, TSOP-II-54.
# EasyEDA 검색어: W9825G6JH-6
# LCSC Part#: C20512714 (Winbond W9825G6JH-6, 256Mbit SDRAM, TSOP-II-54)
# JLCPCB 재고: 확인됨. FMC 타이밍은 STM32H7 FMC SDRAM 설정에서 확정.
# 핀 정의: VDD/VDDQ=VDD_3V3, VSS/VSSQ=GND, DQ/A/BA/CLK/CKE/CS/RAS/CAS/WE/DQM=FMC.
SDRAM_PINS = [("VDD", "VDD"), ("VDDQ", "VDDQ"), ("VSS", "VSS"), ("VSSQ", "VSSQ")]
SDRAM_PINS += [(f"DQ{i}", f"DQ{i}") for i in range(16)]
SDRAM_PINS += [(f"A{i}", f"A{i}") for i in range(13)]
SDRAM_PINS += [("BA0", "BA0"), ("BA1", "BA1"), ("CLK", "CLK"), ("CKE", "CKE"), ("CS_N", "CS_N"), ("RAS_N", "RAS_N"), ("CAS_N", "CAS_N"), ("WE_N", "WE_N"), ("LDQM", "LDQM"), ("UDQM", "UDQM")]
U4 = Part(name="W9825G6JH_6_SDRAM", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:W9825G6JH_6_SDRAM", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in SDRAM_PINS])()

FMC_NETS = {}
for name in [f"FMC_D{i}" for i in range(16)] + [f"FMC_A{i}" for i in range(13)] + [
    "FMC_BA0", "FMC_BA1", "FMC_SDCLK", "FMC_SDCKE1", "FMC_SDNE1", "FMC_SDNRAS", "FMC_SDNCAS", "FMC_SDNWE", "FMC_NBL0", "FMC_NBL1",
]:
    FMC_NETS[name] = Net(name)
    U3[name] += FMC_NETS[name]
for idx in range(16):
    U4[f"DQ{idx}"] += FMC_NETS[f"FMC_D{idx}"]
for idx in range(13):
    U4[f"A{idx}"] += FMC_NETS[f"FMC_A{idx}"]
U4["BA0"] += FMC_NETS["FMC_BA0"]
U4["BA1"] += FMC_NETS["FMC_BA1"]
U4["CLK"] += FMC_NETS["FMC_SDCLK"]
U4["CKE"] += FMC_NETS["FMC_SDCKE1"]
U4["CS_N"] += FMC_NETS["FMC_SDNE1"]
U4["RAS_N"] += FMC_NETS["FMC_SDNRAS"]
U4["CAS_N"] += FMC_NETS["FMC_SDNCAS"]
U4["WE_N"] += FMC_NETS["FMC_SDNWE"]
U4["LDQM"] += FMC_NETS["FMC_NBL0"]
U4["UDQM"] += FMC_NETS["FMC_NBL1"]
for pin_name in ("VDD", "VDDQ"):
    U4[pin_name] += VDD_3V3
for pin_name in ("VSS", "VSSQ"):
    U4[pin_name] += GND


# === QSPI flash 리소스 저장 블록 ===

# U5: W25Q128JVSIQ
# 한국어 명칭: TouchGFX 리소스용 QSPI NOR flash
# 선택 이유: 가장 흔히 쓰이는 Winbond W25Q 계열이며, JLCPCB Basic 부품으로 재고가 매우 많다.
# 주요 사양: 128Mbit(16MB), 2.7V~3.6V, SPI/QPI, 133MHz, SOIC-8-208mil.
# EasyEDA 검색어: W25Q128JVSIQ
# LCSC Part#: C97521 (Winbond W25Q128JVSIQ, 128Mbit SPI/QSPI NOR Flash, SOIC-8-208mil)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB Basic, in stock 143000개 이상으로 확인.
# 핀 정의: CS_N=QSPI_NCS, CLK=QSPI_CLK, IO0=QSPI_IO0/MOSI, IO1=QSPI_IO1/MISO, IO2=QSPI_IO2/WP, IO3=QSPI_IO3/HOLD, VCC=VDD_3V3, GND=GND.
U5 = Part(name="W25Q128JVSIQ_QSPI_FLASH", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:W25Q128JVSIQ_QSPI_FLASH", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("CS_N", "CS_N"), ("IO1", "IO1_DO"), ("IO2", "IO2_WP"), ("GND", "GND"), ("IO0", "IO0_DI"), ("CLK", "CLK"), ("IO3", "IO3_HOLD"), ("VCC", "VCC")]])()
QSPI_CLK = Net("QSPI_CLK")
QSPI_NCS = Net("QSPI_NCS")
QSPI_IO0 = Net("QSPI_IO0")
QSPI_IO1 = Net("QSPI_IO1")
QSPI_IO2 = Net("QSPI_IO2")
QSPI_IO3 = Net("QSPI_IO3")
for pin_name, net in [
    ("QSPI_CLK", QSPI_CLK), ("QSPI_NCS", QSPI_NCS), ("QSPI_IO0", QSPI_IO0), ("QSPI_IO1", QSPI_IO1), ("QSPI_IO2", QSPI_IO2), ("QSPI_IO3", QSPI_IO3),
]:
    U3[pin_name] += net
U5["CS_N"] += QSPI_NCS
U5["CLK"] += QSPI_CLK
U5["IO0"] += QSPI_IO0
U5["IO1"] += QSPI_IO1
U5["IO2"] += QSPI_IO2
U5["IO3"] += QSPI_IO3
U5["VCC"] += VDD_3V3
U5["GND"] += GND


# === LCD-TFT 50핀 FPC 블록 ===

# J2: LCD 50핀 FPC 커넥터
# 한국어 명칭: DWIN LN80480T070IA9098용 50핀 0.5mm FPC 커넥터
# 선택 이유: 고정 LCD 패널의 50PIN_0.5mm 인터페이스에 맞추되 MCU 핀 여유를 위해 LCD RGB565로 구동한다.
# 주요 사양: 50P, 0.5mm pitch, bottom contact, right angle, 400mA/pin, 50V.
# EasyEDA 검색어: AFC07-S50FCC-00
# LCSC Part#: C11063 (JUSHUO AFC07-S50FCC-00, 50P 0.5mm FPC bottom contact connector)
# JLCPCB 재고: 확인됨.
# 핀 정의: LN80480T070IA9098 자료 기준. Pin1-2=LEDA, Pin3-4=LEDK, Pin5=GND, Pin6=VCOM, Pin7=DVDD,
#          Pin8=MODE, Pin9=DE, Pin10=VS, Pin11=HS, Pin12-19=B7..B0, Pin20-27=G7..G0, Pin28-35=R7..R0,
#          Pin36=GND, Pin37=DCLK, Pin38=GND, Pin39=L/R, Pin40=U/D, Pin41=VGH, Pin42=VGL, Pin43=AVDD,
#          Pin44=RESET, Pin45=NC, Pin46=VCOM, Pin47=DITHB, Pin48=GND, Pin49=NC, Pin50=NC.
#          FPC 접점 방향과 Pin1 위치는 실제 패널 FPC 마킹으로 대조.
J2 = Part(name="DWIN_LN80480T070IA9098_LCD_50P_FPC", dest=TEMPLATE, tool=SKIDL, ref_prefix="J", footprint="EasyEDA:DWIN_LN80480T070IA9098_LCD_50P_FPC", pins=[Pin(num=str(idx), name=str(idx)) for idx in range(1, 50 + 1)])()

LCD_NETS = {}
for name in ["LCD_CLK", "LCD_DE", "LCD_HSYNC", "LCD_VSYNC", "LCD_RESET", "LCD_MODE", "LCD_LR", "LCD_UD", "LCD_VCOM", "LCD_VGH", "LCD_VGL", "LCD_AVDD", "BL_LED_A", "BL_LED_K"]:
    LCD_NETS[name] = Net(name)
for color, bits in {"R": range(3, 8), "G": range(2, 8), "B": range(3, 8)}.items():
    for idx in bits:
        LCD_NETS[f"LCD_{color}{idx}"] = Net(f"LCD_{color}{idx}")
LCD_UNUSED_RGB_LSB = Net("LCD_UNUSED_RGB_LSB")
for name in ("LCD_CLK", "LCD_DE", "LCD_HSYNC", "LCD_VSYNC"):
    U3[name] += LCD_NETS[name]
for color, bits in {"R": range(3, 8), "G": range(2, 8), "B": range(3, 8)}.items():
    for idx in bits:
        U3[f"LCD_{color}{idx}"] += LCD_NETS[f"LCD_{color}{idx}"]

# U6: LCD bias/backlight power interface
# 한국어 명칭: LCD 바이어스/백라이트 전원 회로 연결 포트
# 선택 이유: 패널에 필요한 AVDD/VGH/VGL/VCOM 및 LEDA/LEDK를 회로도에서 분리하지 않고 명확히 둔다.
# 주요 사양: VIN_24V_PROTECTED 입력, LCD_AVDD/VGH/VGL/VCOM/BL_LED_A/BL_LED_K 출력.
# EasyEDA 검색어: LCD TFT bias backlight power design port
# LCSC Part#: 해당 없음. 구매 부품이 아니라 LCD 전력단 하위 회로 연결 포트이다.
# 핀 정의: VIN=VIN_24V_PROTECTED, GND=GND, AVDD/VGH/VGL/VCOM=LCD bias, LEDA/LEDK=백라이트 정전류 경로, PWM=LCD_BL_PWM.
# 주의: 이 포트는 부품 확정이 아니라 전력단 연결 의도다. 패널 원본 전압/전류/시퀀싱 조건으로 실제 IC를 선정해야 한다.
U6 = Part(name="LCD_BIAS_BACKLIGHT_POWER_PORT", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:LCD_BIAS_BACKLIGHT_POWER_PORT", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("VIN", "VIN"), ("GND", "GND"), ("AVDD", "AVDD"), ("VGH", "VGH"), ("VGL", "VGL"), ("VCOM", "VCOM"), ("LEDA", "LEDA"), ("LEDK", "LEDK"), ("PWM", "PWM")]])()

R5 = Part(name="LCD_MODE_PULLDOWN_10K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:LCD_MODE_PULLDOWN_10K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R6 = Part(name="LCD_LR_PULLDOWN_10K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:LCD_LR_PULLDOWN_10K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R7 = Part(name="LCD_UD_PULLDOWN_10K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:LCD_UD_PULLDOWN_10K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R5["1"] += LCD_NETS["LCD_MODE"]
R5["2"] += GND
R6["1"] += LCD_NETS["LCD_LR"]
R6["2"] += GND
R7["1"] += LCD_NETS["LCD_UD"]
R7["2"] += GND
LCD_NETS["LCD_RESET"] += NRST

U6["VIN"] += VIN_24V_PROTECTED
U6["GND"] += GND
U6["AVDD"] += LCD_NETS["LCD_AVDD"]
U6["VGH"] += LCD_NETS["LCD_VGH"]
U6["VGL"] += LCD_NETS["LCD_VGL"]
U6["VCOM"] += LCD_NETS["LCD_VCOM"]
U6["LEDA"] += LCD_NETS["BL_LED_A"]
U6["LEDK"] += LCD_NETS["BL_LED_K"]
U6["PWM"] += LCD_BL_PWM

J2["1"] += LCD_NETS["BL_LED_A"]       # 1.00mm 이상, LED driver 출력
J2["2"] += LCD_NETS["BL_LED_A"]       # 1.00mm 이상
J2["3"] += LCD_NETS["BL_LED_K"]       # 1.00mm 이상, LED return
J2["4"] += LCD_NETS["BL_LED_K"]       # 1.00mm 이상
J2["5"] += GND
J2["6"] += LCD_NETS["LCD_VCOM"]
J2["7"] += VDD_3V3
J2["8"] += LCD_NETS["LCD_MODE"]
J2["9"] += LCD_NETS["LCD_DE"]
J2["10"] += LCD_NETS["LCD_VSYNC"]
J2["11"] += LCD_NETS["LCD_HSYNC"]
for offset, bit in enumerate(range(7, -1, -1), start=12):
    J2[str(offset)] += LCD_NETS[f"LCD_B{bit}"] if bit >= 3 else LCD_UNUSED_RGB_LSB  # 0.25mm, RGB565 B7..B3
for offset, bit in enumerate(range(7, -1, -1), start=20):
    J2[str(offset)] += LCD_NETS[f"LCD_G{bit}"] if bit >= 2 else LCD_UNUSED_RGB_LSB  # 0.25mm, RGB565 G7..G2
for offset, bit in enumerate(range(7, -1, -1), start=28):
    J2[str(offset)] += LCD_NETS[f"LCD_R{bit}"] if bit >= 3 else LCD_UNUSED_RGB_LSB  # 0.25mm, RGB565 R7..R3
LCD_UNUSED_RGB_LSB += GND
J2["36"] += GND
J2["37"] += LCD_NETS["LCD_CLK"]
J2["38"] += GND
J2["39"] += LCD_NETS["LCD_LR"]
J2["40"] += LCD_NETS["LCD_UD"]
J2["41"] += LCD_NETS["LCD_VGH"]
J2["42"] += LCD_NETS["LCD_VGL"]
J2["43"] += LCD_NETS["LCD_AVDD"]
J2["44"] += LCD_NETS["LCD_RESET"]
J2["46"] += LCD_NETS["LCD_VCOM"]
J2["47"] += GND
J2["48"] += GND


# === YF-07002 터치 + AR1020 블록 ===

# J3: YF-07002 터치 FPC 커넥터
# 한국어 명칭: 7인치 4선 감압식 터치 FPC 커넥터
# 선택 이유: 고정 터치 패널 YF-07002의 4P 0.5mm FPC를 받는다.
# 주요 사양: 4P, 0.5mm pitch, bottom contact, right angle.
# EasyEDA 검색어: AFC07-S04FCC-00
# LCSC Part#: C11047 (JUSHUO AFC07-S04FCC-00, 4P 0.5mm FPC bottom contact connector)
# JLCPCB 재고: 확인됨.
# 핀 정의: Pin1=XL, Pin2=YD, Pin3=XR, Pin4=YU. 실제 FPC 방향과 접점면 대조.
J3 = Part(name="YF07002_TOUCH_4P_FPC", dest=TEMPLATE, tool=SKIDL, ref_prefix="J", footprint="EasyEDA:YF07002_TOUCH_4P_FPC", pins=[Pin(num=str(idx), name=str(idx)) for idx in range(1, 4 + 1)])()
TOUCH_XL = Net("TOUCH_XL")
TOUCH_YD = Net("TOUCH_YD")
TOUCH_XR = Net("TOUCH_XR")
TOUCH_YU = Net("TOUCH_YU")
J3["1"] += TOUCH_XL
J3["2"] += TOUCH_YD
J3["3"] += TOUCH_XR
J3["4"] += TOUCH_YU

# U7: AR1020
# 한국어 명칭: 4선 감압식 터치 컨트롤러
# 선택 이유: YF-07002 4-wire resistive touch를 I2C로 STM32H7에 연결한다.
# 주요 사양: 4/5/8-wire resistive 지원, 10-bit 위치, I2C/SPI, 2.5V~5.5V, SSOP-20.
# EasyEDA 검색어: AR1020-I/SS
# LCSC Part#: 해당 없음. Microchip AR1020은 사용자 지정 터치 컨트롤러이며 JLCPCB 조립 재고 부품으로 확인되지 않았다.
# 핀 정의: VDD=VDD_3V3, VSS=GND, M1/M2=I2C+4wire 설정, SCL/SDA=I2C1, IRQ=TOUCH_IRQ, X+/X-/Y+/Y-=YF-07002 전극.
U7 = Part(name="AR1020_I_SS_TOUCH_CONTROLLER", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:AR1020_I_SS_TOUCH_CONTROLLER", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("VDD", "VDD"), ("VSS", "VSS"), ("M1", "M1"), ("M2", "M2"), ("WAKE", "WAKE"), ("IRQ", "IRQ"), ("SDA", "SDA"), ("SCL", "SCL"), ("XPLUS", "XPLUS"), ("XMINUS", "XMINUS"), ("YPLUS", "YPLUS"), ("YMINUS", "YMINUS")]])()
U7["VDD"] += VDD_3V3
U7["VSS"] += GND
U7["SCL"] += I2C1_SCL
U7["SDA"] += I2C1_SDA
U7["IRQ"] += TOUCH_IRQ
U7["XMINUS"] += TOUCH_XL
U7["YMINUS"] += TOUCH_YD
U7["XPLUS"] += TOUCH_XR
U7["YPLUS"] += TOUCH_YU
U7["M1"] += GND
U7["M2"] += GND
U7["WAKE"] += TOUCH_IRQ

R8 = Part(name="I2C_SCL_PULLUP_4K7", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:I2C_SCL_PULLUP_4K7", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R9 = Part(name="I2C_SDA_PULLUP_4K7", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:I2C_SDA_PULLUP_4K7", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R8["1"] += VDD_3V3
R8["2"] += I2C1_SCL
R9["1"] += VDD_3V3
R9["2"] += I2C1_SDA


# === 온보드 ST-LINK USB 업로드/디버그 블록 ===

# U_PROG: STLINK-V3MODS
# 한국어 명칭: 온보드 ST-LINK V3 프로그래머/디버거 모듈
# 선택 이유: STM32F429I-DISC1의 내장 ST-LINK처럼 USB를 꽂으면 STM32CubeProgrammer/IDE에서 바로 flash/debug가 가능하다.
# 주요 사양: STM32용 compact in-circuit debugger/programmer, SWD/JTAG, SWV, VCP, 2x16 1.27mm castellated module, onboard USB Micro-B.
# EasyEDA 검색어: STLINK-V3MODS
# LCSC Part#: C2680635 (STMicroelectronics STLINK-V3MODS, embedded ST-LINK V3 SWD programmer/debugger module)
# JLCPCB 재고: 확인됨. 2026-06-05 검색 기준 JLCPCB 재고는 소량이므로 양산 전 재고 재확인 필요.
# 핀 정의: VTREF=VDD_3V3 target sense, GND=GND, SWDIO/SWCLK/SWO/NRST=STM32H753 SWD, VCP_TX/VCP_RX=선택 UART.
# 주의: STLINK-V3MODS의 USB 5V 출력은 보드 전원 입력으로 쓰지 않는다. 보드는 VIN_24V_IN 단일 입력으로만 동작한다.
U_STLINK = Part(
    name="STLINK_V3MODS_ONBOARD_PROGRAMMER",
    dest=TEMPLATE,
    tool=SKIDL,
    ref_prefix="U",
    footprint="EasyEDA:STLINK_V3MODS_ONBOARD_PROGRAMMER",
    pins=[
        Pin(num=str(num), name=str(pin_name))
        for num, pin_name in [
            ("VTREF", "VTREF"), ("GND", "GND"), ("SWDIO", "SWDIO"), ("SWCLK", "SWCLK"),
            ("SWO", "SWO"), ("NRST", "NRST"), ("VCP_TX", "VCP_TX"), ("VCP_RX", "VCP_RX"),
            ("USB_5V_OUT", "USB_5V_OUT"),
        ]
    ],
)()
STLINK_USB_5V_OUT = Net("STLINK_USB_5V_OUT")
STLINK_VCP_TX = Net("STLINK_VCP_TX")
STLINK_VCP_RX = Net("STLINK_VCP_RX")
U_STLINK["VTREF"] += VDD_3V3
U_STLINK["GND"] += GND
U_STLINK["SWDIO"] += STLINK_SWDIO
U_STLINK["SWCLK"] += STLINK_SWCLK
U_STLINK["SWO"] += STLINK_SWO
U_STLINK["NRST"] += NRST
U_STLINK["VCP_TX"] += STLINK_VCP_TX
U_STLINK["VCP_RX"] += STLINK_VCP_RX
U_STLINK["USB_5V_OUT"] += STLINK_USB_5V_OUT


# === MD5-HF14 4축 제어 출력 블록 ===

# U8/U9: TBD62783AFWG source driver arrays
# 한국어 명칭: MD5-HF14 제어 입력용 8채널 source driver
# 선택 이유: MD5-HF14 회로도는 CW/CCW 입력을 +5V로 인가하는 방식이므로 source driver로 구동한다.
# 주요 사양: 8채널 DMOS source transistor array, 50V, 500mA/ch급, SOP-18.
# EasyEDA 검색어: TBD62783AFWG
# LCSC Part#: C146353 (Toshiba TBD62783AFWG,EL, 8-channel source type DMOS transistor array, SOP-18)
# JLCPCB 재고: 확인됨. MD5 입력 전류 7.5~16mA급에는 충분하나 출력 high 전압과 발열은 실측 검증.
# 핀 정의: VCC=VCTRL_5V, GND=GND, IN1~IN8=MCU GPIO, OUT1~OUT8=MD5 신호 입력핀(+5V source).
SOURCE_DRIVER_PINS = [("VCC", "VCC"), ("GND", "GND")]
SOURCE_DRIVER_PINS += [(f"IN{i}", f"IN{i}") for i in range(1, 9)]
SOURCE_DRIVER_PINS += [(f"OUT{i}", f"OUT{i}") for i in range(1, 9)]
U8 = Part(name="TBD62783AFWG_MD5_SOURCE_OUTPUTS_A", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint="EasyEDA:TBD62783AFWG_MD5_SOURCE_OUTPUTS_A", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in SOURCE_DRIVER_PINS])()
U8["VCC"] += VCTRL_5V
U8["GND"] += GND

MD5_OUTPUT_NETS = {}
MD5_SOURCE_NETS = {}
output_index = 1
for axis in range(1, 5):
    for signal in ("CW", "CCW"):
        mcu_net = Net(f"MD5_AXIS{axis}_{signal}")
        source_net = Net(f"MD5_AXIS{axis}_{signal}_SRC")
        MD5_OUTPUT_NETS[(axis, signal)] = mcu_net
        MD5_SOURCE_NETS[(axis, signal)] = source_net
        U3[f"MD5_AXIS{axis}_{signal}"] += mcu_net
        U8[f"IN{output_index}"] += mcu_net
        U8[f"OUT{output_index}"] += source_net
        output_index += 1

# J5~J8: MD5-HF14 axis control ports
# 한국어 명칭: Autonics MD5-HF14 제어 신호 포트
# 선택 이유: MD5-HF14의 Signal 1~10 중 GND 리턴(2/4/6/8/10)은 공통이므로 축별 하네스는 6선으로 줄인다.
# 주요 사양: CW/CCW 입력 2선, 공통 GND 1선. 입력 전류는 CW/CCW 약 7.5~14mA 계열.
# EasyEDA 검색어: Molex 22035065 5267 6P
# LCSC/JLCPCB Part#: C185191 (Molex 22035065, Mini-SPOX/5267 계열 1x6P 2.5mm wire-to-board header, 3A 250V, through-hole)
# JLCPCB 재고: 확인됨(2026-06-05 기준). 5267 mating housing/terminal은 하네스 BOM에서 별도 확정.
# 핀 정의: Pin1=CW, Pin2=CCW, Pin3=NC, Pin4=NC, Pin5=NC, Pin6=GND_COMMON.
# MD5-HF14 실제 단자대 연결: J Pin1->MD5 Signal1(CW), Pin2->Signal3(CCW), Pin6->Signal2/4/6/8/10 공통 GND. Pin3~5는 PCB에서 미사용.
MD5_PORTS = {}
for axis in range(1, 5):
    port = Part(name=f"MD5_HF14_AXIS{axis}_SIGNAL_5267_6P", dest=TEMPLATE, tool=SKIDL, ref_prefix="J", footprint=f"EasyEDA:MD5_HF14_AXIS{axis}_SIGNAL_5267_6P", pins=[Pin(num=str(idx), name=str(idx)) for idx in range(1, 6 + 1)])()
    MD5_PORTS[axis] = port
    port["1"] += MD5_SOURCE_NETS[(axis, "CW")]
    port["2"] += MD5_SOURCE_NETS[(axis, "CCW")]
    port["6"] += GND


# === 24V NPN 센서 입력 8점 블록 ===

# J9: 24V NPN sensor input connector
# 한국어 명칭: 24V NPN 센서 8점 입력 포트
# 선택 이유: 8개 NPN 오픈컬렉터 센서 출력을 받아 HMI/모션 상태 판단에 사용한다.
# 주요 사양: +24V, 0V, IN1~IN8 현장 배선.
# EasyEDA 검색어: Molex 22035105 5267 10P
# LCSC Part#: 해당 없음. Molex 5267-10A/22035105 1x10P 2.5mm header를 우선 사용하되, JLCPCB 조립 재고가 불안정하면 동등한 Molex 5267 호환 10P 부품으로 대체 검토.
# JLCPCB 재고: Molex 정품 10P는 최종 BOM 직전 재확인 필요. 센서 입력 포트는 반드시 Molex 5267 계열 10P로 EasyEDA Pro에서 풋프린트/키 방향 대조.
# 핀 정의: Pin1=+24V sensor supply, Pin2=0V, Pin3~10=SENSOR_NPN_CH1~CH8. NPN 센서는 active 시 출력이 0V로 sink된다.
J9 = Part(name="NPN_SENSOR_24V_8CH_INPUT_5267_10P", dest=TEMPLATE, tool=SKIDL, ref_prefix="J", footprint="EasyEDA:NPN_SENSOR_24V_8CH_INPUT_5267_10P", pins=[Pin(num=str(idx), name=str(idx)) for idx in range(1, 10 + 1)])()
J9["1"] += VIN_24V_PROTECTED
J9["2"] += GND

# U10~U17: PC817B optocoupler inputs
# 한국어 명칭: 24V NPN 입력 절연 포토커플러
# 선택 이유: 24V 현장 입력과 STM32 3.3V 로직을 분리하고 배선 노이즈 내성을 높인다.
# 주요 사양: Phototransistor output optocoupler, 5kVrms, SMD-4P.
# EasyEDA 검색어: PC817B SMD-4P
# LCSC Part#: C3025163 (GOODWORK PC817B, SMD-4P phototransistor optocoupler, 5kVrms)
# JLCPCB 재고: 확인됨. 센서 응답 속도는 일반 근접/리미트 센서 용도 기준이며 고속 카운터 입력은 별도 회로 필요.
# 핀 정의: A=LED 애노드(24V pull-up resistor 쪽), K=LED 캐소드(센서 출력 쪽), C=MCU 입력 pull-up 쪽, E=GND.
SENSOR_NETS = {}
SENSOR_MCU_NETS = {}
for channel in range(1, 9):
    sensor_net = Net(f"SENSOR_NPN_CH{channel}")
    sensor_mcu = Net(f"SENSOR_IN{channel}_MCU")
    SENSOR_NETS[channel] = sensor_net
    SENSOR_MCU_NETS[channel] = sensor_mcu
    J9[str(channel + 2)] += sensor_net
    U3[f"SENSOR_IN{channel}_MCU"] += sensor_mcu

    opto = Part(name=f"PC817B_SENSOR_INPUT_CH{channel}", dest=TEMPLATE, tool=SKIDL, ref_prefix="U", footprint=f"EasyEDA:PC817B_SENSOR_INPUT_CH{channel}", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("A", "A"), ("K", "K"), ("C", "C"), ("E", "E")]])()
    led_res = Part(name=f"SENSOR_CH{channel}_LED_RES_4K7_1206", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint=f"EasyEDA:SENSOR_CH{channel}_LED_RES_4K7_1206", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
    pull = Part(name=f"SENSOR_CH{channel}_MCU_PULLUP_10K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint=f"EasyEDA:SENSOR_CH{channel}_MCU_PULLUP_10K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
    led_res["1"] += VIN_24V_PROTECTED
    led_res["2"] += opto["A"]
    opto["K"] += sensor_net
    opto["C"] += sensor_mcu
    opto["E"] += GND
    pull["1"] += VDD_3V3
    pull["2"] += sensor_mcu


# === Buzzer alert block ===

# BZ1: 5V active buzzer
# 한국어 명칭: 알림용 5V 능동 부저
# 선택 이유: MCU PWM 음계가 필요 없는 단순 알림음을 1개 GPIO로 낸다.
# 주요 사양: 5V active buzzer, 2.4kHz, 30mA, 88dB, SMD 12.8x12.8mm.
# EasyEDA 검색어: KTG1205CL
# LCSC/JLCPCB Part#: C7496511 (KINGSTATE KTG1205CL, 5V Active Buzzer, SMD 12.8x12.8mm)
# JLCPCB 재고: 확인됨(소량). 부저류 재고는 주문 직전 JLCPCB Assembly 화면에서 재확인.
# 핀 정의: Pin1=+(VCTRL_5V), Pin2=-(MOSFET drain 쪽). 실제 EasyEDA 심볼/풋프린트 극성 마킹 대조.
BZ1 = Part(name="BUZZER_ACTIVE_5V_KTG1205CL", dest=TEMPLATE, tool=SKIDL, ref_prefix="BZ", footprint="EasyEDA:BUZZER_ACTIVE_5V_KTG1205CL", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "+"), ("2", "-")]])()

# Q1: buzzer low-side switch
# 한국어 명칭: 부저 로우사이드 N-MOSFET
# 선택 이유: 3.3V MCU GPIO가 부저 전류를 직접 구동하지 않게 한다.
# 주요 사양: 2N7002, N-channel, 60V, 115mA, SOT-23.
# EasyEDA 검색어: 2N7002
# LCSC/JLCPCB Part#: C8545 (JSCJ 2N7002, N-channel MOSFET, SOT-23)
# JLCPCB 재고: 확인됨.
# 핀 정의: G=BUZZER_GATE, D=부저 -, S=GND. 2N7002 SOT-23 핀 번호는 EasyEDA Pro에서 실제 심볼과 대조.
Q1 = Part(name="BUZZER_LOW_SIDE_2N7002", dest=TEMPLATE, tool=SKIDL, ref_prefix="Q", footprint="EasyEDA:BUZZER_LOW_SIDE_2N7002", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("G", "G"), ("D", "D"), ("S", "S")]])()

# R10/R11: buzzer gate resistors
# 한국어 명칭: 부저 MOSFET 게이트 직렬/풀다운 저항
# 선택 이유: MCU 리셋 중 부저 오동작을 막고 게이트 충전 전류를 완만하게 한다.
# 주요 사양: R10=1k 0603, R11=100k 0603.
# EasyEDA 검색어: 0603WAF1001T5E, 0603WAF1003T5E
# LCSC/JLCPCB Part#: C21190 (1k 1% 0603), C25803 (100k 1% 0603)
# JLCPCB 재고: 확인됨. 무극성.
BUZZER_GATE = Net("BUZZER_GATE")
R10 = Part(name="BUZZER_GATE_SERIES_1K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:BUZZER_GATE_SERIES_1K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
R11 = Part(name="BUZZER_GATE_PULLDOWN_100K", dest=TEMPLATE, tool=SKIDL, ref_prefix="R", footprint="EasyEDA:BUZZER_GATE_PULLDOWN_100K", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
BZ1["1"] += VCTRL_5V       # 0.50mm
BZ1["2"] += Q1["D"]        # 0.50mm
Q1["S"] += GND             # 0.50mm
Q1["G"] += BUZZER_GATE     # 0.25mm
R10["1"] += BUZZER_EN      # 0.25mm
R10["2"] += BUZZER_GATE    # 0.25mm
R11["1"] += BUZZER_GATE    # 0.25mm
R11["2"] += GND            # 0.25mm


# === 디커플링/테스트포인트 블록 ===

# C11/C12/C13/C14: 대표 디커플링
# 한국어 명칭: MCU/SDRAM/QSPI/LCD/터치 디커플링 대표 캐패시터
# 선택 이유: 각 IC 전원 핀 가까이에 100nF를 다수 배치한다는 의도를 회로도에 남긴다.
# 주요 사양: 100nF 50V X7R 0603, Samsung MLCC.
# EasyEDA 검색어: CL10B104KB8NNNC
# LCSC Part#: C1591 (Samsung CL10B104KB8NNNC, 100nF 50V X7R 0603 MLCC, Brand:SAMSUNG(三星))
# JLCPCB 재고: 확인됨. 실제 PCB에서는 STM32H753 전원 핀별로 충분한 개수를 배치.
# 핀 정의: 무극성. Pin1=VDD_3V3, Pin2=GND.
for name in ("MCU_DECOUPLING_100NF_ARRAY", "SDRAM_DECOUPLING_100NF_ARRAY", "QSPI_DECOUPLING_100NF", "LCD_TOUCH_DECOUPLING_100NF_ARRAY"):
    cap = Part(name=name, dest=TEMPLATE, tool=SKIDL, ref_prefix="C", footprint=f"EasyEDA:{name}", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1"), ("2", "2")]])()
    cap["1"] += VDD_3V3
    cap["2"] += GND

# TP1~TP6: test points
# 한국어 명칭: 제작/디버그용 전원 테스트 포인트
# 선택 이유: 온보드 STLINK를 쓰더라도 전원 레일과 리셋/부트 상태 확인은 필요하다.
# LCSC Part#: 해당 없음. 테스트 패드/회로도 포트이며 구매 부품이 아니다.
# 핀 정의: Pin1=측정 노드.
for tp_name, net in [
    ("TP_VIN_24V", VIN_24V_PROTECTED), ("TP_5V", VCTRL_5V), ("TP_3V3", VDD_3V3),
    ("TP_GND", GND), ("TP_BOOT0", BOOT0), ("TP_NRST", NRST),
]:
    tp = Part(name=tp_name, dest=TEMPLATE, tool=SKIDL, ref_prefix="TP", footprint=f"EasyEDA:{tp_name}", pins=[Pin(num=str(num), name=str(pin_name)) for num, pin_name in [("1", "1")]])()
    tp["1"] += net


# === 설계 메모 ===

# TouchGFX 데이터 흐름:
# STLINK-V3MODS USB로 STM32 내부 flash에 펌웨어 업로드/디버그 -> W25Q128JVSIQ QSPI flash에 이미지/폰트/리소스 저장
# -> STM32H753 QUADSPI memory-mapped read -> W9825G6JH SDRAM framebuffer
# -> LTDC LCD RGB565 -> LN80480T070IA9098 50핀 FPC 출력.
#
# MD5-HF14 제어:
# STM32 GPIO -> TBD62783AFWG source output -> MD5-HF14 CW/CCW 입력.
# 드라이브 전원 100~220VAC와 모터 배선은 이 PCB에 들어오지 않는다.
#
# USB 업로드:
# STLINK-V3MODS의 USB를 PC에 연결하면 STM32CubeProgrammer/IDE에서 SWD로 STM32H753 내부 flash를 쓴다.
# BOOT0 조작 없이 업로드/디버그가 가능하며, STLINK USB 5V는 보드 전원 입력으로 사용하지 않는다.
#
# 레이아웃 주의:
# - LTDC/FMC/QSPI는 4층 PCB, 연속 GND plane, 짧은 리턴 경로, 클럭 라인 스큐 관리 권장.
# - 24V 센서 입력과 USB/LCD/SDRAM 고속 신호는 물리적으로 떨어뜨린다.
# - buck SW 노드는 작고 짧게, 입력/출력 캐패시터는 IC 핀에 밀착 배치한다.


if __name__ == "__main__":
    generate_netlist(file_="lcd_tft_hmi_md5_hf14.net")
