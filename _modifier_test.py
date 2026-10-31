import os, sys, json
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt6.QtWidgets import QApplication, QMessageBox
QMessageBox.information = staticmethod(lambda *a, **k: None)
QMessageBox.critical = staticmethod(lambda *a, **k: print("[CRITICAL]", a[2] if len(a)>2 else a))

import main
from pynput.keyboard import Key, KeyCode
app = QApplication([])
CFG = "_mod_option.txt"
if os.path.exists(CFG): os.remove(CFG)

w = main.AutoClicker()
w.config_file = CFG
if w.hotkey_listener: w.hotkey_listener.stop()
if w.mouse_listener: w.mouse_listener.stop()

print("=== Step 1: key_to_display mapping ===")
cases = [(Key.alt_l,"Left Alt"),(Key.alt_r,"Right Alt"),(Key.ctrl_l,"Left Ctrl"),(Key.ctrl_r,"Right Ctrl"),(Key.shift_r,"Right Shift")]
for key, expected in cases:
    got = main.AutoClicker.key_to_display(key)
    assert got == expected, f"{key}: expected {expected}, got {got}"
    print(f"  OK {key!s:20} -> {got}")
print("PASS Step 1: display mapping correct")

# capture hotkey via _apply_hotkey path (simulate dialog pressing Left Ctrl)
print("=== Step 2: capture Left Ctrl -> restore via _restore_hotkey ===")
w._apply_hotkey(Key.ctrl_l, "Left Ctrl", "booster_left")
print(f"  booster_left_hotkey={w.booster_left_hotkey!r} display={w.booster_left_hotkey_display!r}")
assert w.booster_left_hotkey == Key.ctrl_l
assert w.booster_left_hotkey_display == "Left Ctrl"
print("PASS Step 2: capture works")

# Save and reload round-trip
print("=== Step 3: save/restore round-trip ===")
w.save_config()
saved = json.load(open(CFG, encoding="utf-8"))
assert saved["booster_left_hotkey"] == "Left Ctrl", f"saved wrong: {saved.get('booster_left_hotkey')}"
print("  OK: saved as 'Left Ctrl' string")

w2 = main.AutoClicker()
w2.config_file = CFG
if w2.hotkey_listener: w2.hotkey_listener.stop()
if w2.mouse_listener: w2.mouse_listener.stop()
w2.load_config()
assert w2.booster_left_hotkey == Key.ctrl_l, f"not restored: {w2.booster_left_hotkey!r}"
assert w2.booster_left_hotkey_display == "Left Ctrl"
print("PASS Step 3: restored correctly on reload")

# Trigger via keyboard listener press logic
print("=== Step 4: press triggers booster toggle ===")
def on_press_emulate(key):
    norm_key = w2._normalize_key(key)
    try:
        if norm_key in w2._pressed_hotkeys: return
        w2._pressed_hotkeys.add(norm_key)
    except TypeError:
        pass
    if w2._is_same_key(key, w2.booster_left_hotkey):
        w2.ui_toggle_left.emit()

w2.booster_left_enabled = False
on_press_emulate(Key.ctrl_l)
assert w2.booster_left_enabled == True, "Left Ctrl did not toggle booster left"
print("PASS Step 4: Left Ctrl press toggles booster left (master switch flips)")
on_press_emulate(Key.ctrl_l)
assert w2.booster_left_enabled == False
print("PASS Step 4b: press again toggles off")

# Wrong key should not toggle
w2.booster_left_enabled = False
on_press_emulate(Key.ctrl_r)
assert w2.booster_left_enabled == False, "Right Ctrl should NOT toggle when set to Left Ctrl"
print("PASS Step 5: Left/Right distinction works (Right Ctrl does not trigger Left Ctrl setting)")

w._closing = w2._closing = True
print("ALL MODIFIER TESTS PASSED")
