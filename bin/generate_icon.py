#!/usr/bin/env python3
"""Generate SS3 app icon - Simple geometric design"""
import subprocess
from pathlib import Path

icon_dir = Path("/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/bin/AppIcon.iconset")
icon_dir.mkdir(exist_ok=True)

try:
    from PIL import Image, ImageDraw

    def create_icon(size):
        """Create SS3 icon - dark purple with gold accents"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Rounded rectangle background - dark purple gradient
        margin = size // 8
        for y in range(margin, size - margin):
            r = int(25 + ((y - margin) / (size - 2*margin)) * 35)
            g = int(12 + ((y - margin) / (size - 2*margin)) * 18)
            b = int(45 + ((y - margin) / (size - 2*margin)) * 55)
            draw.line([(margin, y), (size - margin, y)], fill=(r, g, b, 255))

        # Gold border
        border = max(2, size // 64)
        draw.rectangle([margin, margin, size-margin-1, size-margin-1],
                       outline=(255, 215, 0, 255), width=border)

        # Draw stylized "S3" using geometric shapes
        cx, cy = size // 2, size // 2

        # First S (left)
        s_width = size // 6
        s_height = size // 3
        gold = (255, 215, 0, 255)

        # S shape using lines - left S
        lw = max(2, size // 32)
        sx = cx - s_width
        draw.arc([sx - s_width//2, cy - s_height//2, sx + s_width//2, cy],
                 180, 0, fill=gold, width=lw)
        draw.arc([sx - s_width//2, cy, sx + s_width//2, cy + s_height//2],
                 0, 180, fill=gold, width=lw)

        # 3 on the right
        tx = cx + s_width // 2
        draw.arc([tx - s_width//2, cy - s_height//2, tx + s_width//2, cy],
                 270, 90, fill=gold, width=lw)
        draw.arc([tx - s_width//2, cy, tx + s_width//2, cy + s_height//2],
                 270, 90, fill=gold, width=lw)

        return img

    # Create all required sizes for iconset
    for size in [16, 32, 128, 256, 512]:
        img = create_icon(size)
        img.save(icon_dir / f"icon_{size}x{size}.png")
        # @2x versions
        img_2x = create_icon(size * 2)
        img_2x.save(icon_dir / f"icon_{size}x{size}@2x.png")

    print("Icon images created!")

except Exception as e:
    print(f"PIL icon creation failed: {e}")
    print("Creating simple colored PNG instead...")

# Convert iconset to icns
icns_path = "/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/bin/SovereignShadow3.app/Contents/Resources/AppIcon.icns"
try:
    result = subprocess.run([
        "iconutil", "-c", "icns",
        str(icon_dir),
        "-o", icns_path
    ], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Icon created at {icns_path}")
    else:
        print(f"iconutil: {result.stderr}")
except Exception as e:
    print(f"iconutil failed: {e}")
