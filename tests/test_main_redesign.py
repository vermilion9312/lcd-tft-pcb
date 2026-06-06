from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"


def read_main():
    return MAIN.read_text(encoding="utf-8")


def test_fixed_hmi_parts_and_selected_mcu_are_present():
    text = read_main()
    required = [
        "STM32H743IIT6",
        "DWIN_LN80480T070IA9098_LCD_50P_FPC",
        "YF07002_TOUCH_4P_FPC",
        "AR1020_I_SS_TOUCH_CONTROLLER",
        "W9825G6JH_6_SDRAM",
        "W25Q128JVSIQ_QSPI_FLASH",
        "STLINK_V3MODS_ONBOARD_PROGRAMMER",
        "VIN_24V_INPUT_5557_02A_2P",
    ]
    for item in required:
        assert item in text


def test_motion_and_sensor_interfaces_are_present():
    text = read_main()
    for axis in range(1, 5):
        assert f"MD5_AXIS{axis}_CW" in text
        assert f"MD5_AXIS{axis}_CCW" in text
        assert f"MD5_AXIS{axis}_HOLD_OFF" in text
        assert f"MD5_AXIS{axis}_DIV_SEL" in text
        assert f"MD5_AXIS{axis}_ZERO_OUT" in text
        assert f"MD5_HF14_AXIS{axis}_SIGNAL_5267_6P" in text
        assert f"MD5_AXIS{axis}_PULSE" not in text
        assert f"MD5_AXIS{axis}_DIR" not in text
        assert f"MD5_HF14_AXIS{axis}_CONTROL_5267_8P" not in text
        assert f"MD5_HF14_AXIS{axis}_CONTROL_5267_5P" not in text
        assert f"MD5_HF14_AXIS{axis}_SIGNAL_5267_10P" not in text
    for channel in range(1, 9):
        assert f"SENSOR_NPN_CH{channel}" in text
        assert f"SENSOR_IN{channel}_MCU" in text
    assert "NPN_SENSOR_24V_8CH_INPUT_5267_10P" in text


def test_lcsc_annotations_use_verified_parts():
    text = read_main()
    expected_parts = {
        "C89597": ["STM32H743IIT6", "LQFP-176", "JLCPCB 재고"],
        "C97521": ["W25Q128JVSIQ", "128Mbit", "SOIC-8-208mil", "JLCPCB 재고"],
        "C20512714": ["W9825G6JH", "256Mbit", "TSOP-II-54"],
        "C2071056": ["AP63205WU-7", "5V", "2A"],
        "C780769": ["AP63203WU-7", "3.3V", "2A"],
        "C113966": ["SMAJ33A", "33V", "TVS", "DO-214AC"],
        "C11063": ["AFC07-S50FCC-00", "50P", "0.5mm"],
        "C11047": ["AFC07-S04FCC-00", "4P", "0.5mm"],
        "C2680635": ["STLINK-V3MODS", "SWD", "programmer"],
        "C3025163": ["PC817B", "SMD-4P", "5kVrms"],
        "C146353": ["TBD62783AFWG", "8-channel", "source"],
        "C53325659": ["FG-5557-02A", "2P", "4.2mm"],
        "C185191": ["Molex", "22035065", "1x6P", "5267"],
    }
    for code, fragments in expected_parts.items():
        assert code in text
        for fragment in fragments:
            assert fragment in text


def test_power_and_architecture_constraints():
    text = read_main()
    assert "VIN_24V_IN = Net(\"VIN_24V_IN\")" in text
    assert "VIN_24V_FUSED" not in text
    assert "LOGIC_5V_IN" not in text
    assert "SERVO_6V_IN" not in text
    assert "VBAT_IN" not in text
    assert "PGND" not in text
    assert "class " not in text
    assert "def " not in text
    assert "template(" not in text
    assert "make_connector(" not in text
    assert "make_net(" not in text
    assert "USB_C_" + "D" + "FU_SERVICE_PORT" not in text
    assert "ROM " + "D" + "FU" not in text
    assert "STLINK_SWDIO" in text
    assert "STLINK_SWCLK" in text


def test_forbidden_placeholders_are_not_left_in_design():
    text = read_main()
    forbidden = [
        "미" + "확정",
        "PLACE" + "HOLDER",
        "C50" + "975",
        "C720" + "477",
        "C614" + "2744",
        "C139" + "488",
    ]
    for item in forbidden:
        assert item not in text
