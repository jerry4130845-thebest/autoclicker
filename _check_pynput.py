from pynput.keyboard import Key
attrs = [a for a in dir(Key) if not a.startswith('_') and a not in ('Value',)]
print("Modifier keys containing ctrl/alt/shift:")
for name in sorted(attrs):
    if 'ctrl' in name or 'alt' in name or 'shift' in name or 'win' in name:
        k = getattr(Key, name)
        print(f"  Key.{name} -> str={str(k)!r}")
print()
for name in ['left_ctrl','right_ctrl','left_alt','right_alt','left_shift','right_shift','ctrl_l','ctrl_r','alt_l','alt_r','shift_l','shift_r']:
    print(f"Key.{name}: {'EXISTS' if hasattr(Key, name) else 'MISSING'}")
