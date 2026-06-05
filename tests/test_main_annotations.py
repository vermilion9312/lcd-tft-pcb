from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"


def test_required_blocks_and_user_parts_are_present():
    text = MAIN.read_text(encoding="utf-8")
    required = [
        "STM32F429IGT6",
        "W9825G6JH_6_SDRAM",
        "AR1020_I_SS_TOUCH_CONTROLLER",
        "DWIN_LN80480T070IA9098_LCD_50P_FPC",
        "YF07002_TOUCH_4P_FPC",
        "MICROSD_SOCKET_HYC39_TF08_180",
        "SWD_1X6_PROGRAM_HEADER",
        "USB_FS_DFU_SERVICE_PORT",
    ]
    for item in required:
        assert item in text


def test_lcsc_part_annotations_include_verified_parts():
    text = MAIN.read_text(encoding="utf-8")
    expected_parts = {
        "C54328": ["STM32F429IGT6", "LQFP-176"],
        "C20512714": ["W9825G6JH", "TSOP"],
        "C780769": ["AP63203WU-7", "3.3V", "2A"],
        "C11063": ["AFC07-S50FCC-00", "50P", "0.5mm"],
        "C11047": ["AFC07-S04FCC-00", "4P", "0.5mm"],
        "C341095": ["HYC39-TF08-180", "MicroSD"],
        "C47986637": ["2EDGK-5.08-2P", "12A", "300V"],
        "C553922": ["S1206-F-2.0A", "2A", "32V"],
        "C8678": ["SS34", "3A", "40V"],
        "C726747": ["SMAJ18A", "18V", "400W"],
        "C400090": ["TAXM8M4RDBCCT2T", "8MHz", "SMD3225"],
        "C1647": ["Samsung", "18pF", "C0G"],
        "C25804": ["10k", "1%", "0603"],
        "C25803": ["100k", "1%", "0603"],
        "C23162": ["4.7k", "1%", "0603"],
        "C12891": ["Samsung", "22uF", "25V"],
        "C1591": ["Samsung", "100nF", "50V"],
    }
    for code, fragments in expected_parts.items():
        assert code in text
        for fragment in fragments:
            assert fragment in text


def test_forbidden_placeholder_and_bad_parts_are_not_in_main():
    text = MAIN.read_text(encoding="utf-8")
    forbidden = [
        "미확정",
        "PLACEHOLDER",
        "C50975",
        "C720477",
        "C6142744",
    ]
    for item in forbidden:
        assert item not in text


def test_single_external_power_input_intent():
    text = MAIN.read_text(encoding="utf-8")
    assert "VIN_12V_IN" in text
    assert "USB 5V는 전원 입력으로 쓰지 않는다" in text
    assert "LOGIC_5V_IN" not in text
    assert "SERVO_6V_IN" not in text


def test_corrected_power_and_startup_paths_are_present():
    text = MAIN.read_text(encoding="utf-8")
    required_connections = [
        'F1["2"] += VIN_12V_FUSED',
        'D2["A"] += VIN_12V_FUSED',
        'D2["K"] += VIN_12V_PROTECTED',
        'D1["K"] += VIN_12V_PROTECTED',
        'U6["VIN"] += VIN_12V_PROTECTED',
        'LCD_NETS["LCD_RESET"] += NRST',
        'R5["1"] += BOOT0',
        'R5["2"] += GND',
        'R6["1"] += VDD_3V3',
        'R6["2"] += NRST',
        'C8["1"] += HSE_IN',
        'C9["1"] += HSE_OUT',
        'SDIO_NETS["SD_CARD_DETECT"] = SD_CARD_DETECT',
    ]
    for connection in required_connections:
        assert connection in text
