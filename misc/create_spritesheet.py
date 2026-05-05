from PIL import Image
import os

# --- SETTINGS ---
frames_dir = "../assets/images/huntress"  # folder with your PNGs
output_path = "./huntress.png"
# ----------------

# Load each animation strip in order
animation_files = [
    "Idle.png",    # Stand
    "Run.png",     # Run
    "Jump.png",    # Jump
    "Attack1.png", # Attack 1
    "Attack2.png", # Attack 2
    "Hit.png",     # Hit
    "Death.png",   # Die
]

strips = []
for filename in animation_files:
    path = os.path.join(frames_dir, filename)
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        strips.append(img)
        print(f"Loaded {filename}: {img.size}")
    else:
        print(f"WARNING: {filename} not found at {path}")

if not strips:
    print("No images found! Check your frames_dir path.")
    exit()

# Sheet width = widest strip, height = sum of all strip heights
sheet_w = max(img.width for img in strips)
sheet_h = sum(img.height for img in strips)

sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

y = 0
for img in strips:
    sheet.paste(img, (0, y))
    y += img.height

sheet.save(output_path)
print(f"\nDone! Saved to {output_path} ({sheet_w}x{sheet_h})")