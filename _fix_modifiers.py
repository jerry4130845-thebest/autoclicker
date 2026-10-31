import re

for fn in ["main.py", "main_fixed.py"]:
    with open(fn, encoding="utf-8") as f:
        s = f.read()

    # 1) key_to_display: fix string comparisons
    old_cmp = '''        if text == "Key.left_alt":
            return "Left Alt"
        if text == "Key.right_alt":
            return "Right Alt"
        if text == "Key.left_ctrl":
            return "Left Ctrl"
        if text == "Key.right_ctrl":
            return "Right Ctrl"
        if text == "Key.left_shift":
            return "Left Shift"
        if text == "Key.right_shift":
            return "Right Shift"'''
    new_cmp = '''        if text == "Key.alt_l":
            return "Left Alt"
        if text == "Key.alt_r":
            return "Right Alt"
        if text == "Key.ctrl_l":
            return "Left Ctrl"
        if text == "Key.ctrl_r":
            return "Right Ctrl"
        if text == "Key.shift_r":
            return "Right Shift"'''
    assert old_cmp in s, f"{fn}: key_to_display block not found"
    s = s.replace(old_cmp, new_cmp)

    # 2) key_map: fix attribute names (pynput uses alt_l/alt_r/ctrl_l/ctrl_r/shift_r)
    old_map = '''            "Left Alt": Key.left_alt, "Right Alt": Key.right_alt,
            "Left Ctrl": Key.left_ctrl, "Right Ctrl": Key.right_ctrl,
            "Left Shift": Key.left_shift, "Right Shift": Key.right_shift,
        }'''
    new_map = '''            "Left Alt": Key.alt_l, "Right Alt": Key.alt_r,
            "Left Ctrl": Key.ctrl_l, "Right Ctrl": Key.ctrl_r,
            "Right Shift": Key.shift_r,
        }'''
    assert old_map in s, f"{fn}: key_map block not found"
    s = s.replace(old_map, new_map)

    with open(fn, "w", encoding="utf-8") as f:
        f.write(s)
    print(fn, "fixed")

print("done")
