#!/usr/bin/env python3
"""
Shadow III - Modern S3 Logo
Clear bold S and 3 overlapping
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
from pathlib import Path

def create_modern_icon(size=2048):
    """Create modern S3 icon with clear letters"""

    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))

    cx, cy = size // 2, size // 2
    margin = int(size * 0.04)
    corner_radius = int(size * 0.18)

    # === DROP SHADOW ===
    for i in range(4):
        shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        offset = int(size * (0.006 + i * 0.005))
        alpha = 28 - i * 6
        blur = int(size * (0.012 + i * 0.01))

        sd.rounded_rectangle(
            [margin + offset, margin + offset,
             size - margin + offset, size - margin + offset],
            radius=corner_radius, fill=(0, 0, 0, alpha)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
        img = Image.alpha_composite(img, shadow)

    # === DARK GRADIENT BACKGROUND ===
    bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=corner_radius, fill=(32, 32, 36)
    )

    # Add gradient
    for y in range(margin, size - margin):
        for x in range(margin, size - margin):
            # Check corners
            in_shape = True
            if x < margin + corner_radius and y < margin + corner_radius:
                dist = math.sqrt((margin + corner_radius - x)**2 + (margin + corner_radius - y)**2)
                if dist > corner_radius: in_shape = False
            elif x > size - margin - corner_radius and y < margin + corner_radius:
                dist = math.sqrt((x - (size - margin - corner_radius))**2 + (margin + corner_radius - y)**2)
                if dist > corner_radius: in_shape = False
            elif x < margin + corner_radius and y > size - margin - corner_radius:
                dist = math.sqrt((margin + corner_radius - x)**2 + (y - (size - margin - corner_radius))**2)
                if dist > corner_radius: in_shape = False
            elif x > size - margin - corner_radius and y > size - margin - corner_radius:
                dist = math.sqrt((x - (size - margin - corner_radius))**2 + (y - (size - margin - corner_radius))**2)
                if dist > corner_radius: in_shape = False

            if not in_shape:
                continue

            progress = (y - margin) / (size - 2 * margin)
            base = 38 - int(12 * progress)

            # Radial highlight
            dist_hl = math.sqrt((x - size * 0.35)**2 + (y - size * 0.35)**2)
            hl = max(0, 1 - dist_hl / (size * 0.5)) * 12

            bg.putpixel((x, y), (int(base + hl), int(base + hl), int(base + hl + 2), 255))

    img = Image.alpha_composite(img, bg)

    # === LARGE BOLD "S" IN CRIMSON ===
    try:
        # Use SF Pro or Helvetica Bold
        font_size = int(size * 0.7)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()

    # S shadow
    s_shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ss_draw = ImageDraw.Draw(s_shadow)

    s_text = "S"
    bbox = ss_draw.textbbox((0, 0), s_text, font=font)
    sw = bbox[2] - bbox[0]
    sh = bbox[3] - bbox[1]
    sx = cx - sw // 2 - int(size * 0.12)
    sy = cy - sh // 2 - int(size * 0.05)

    # Draw shadow
    for d in range(6, 0, -1):
        alpha = 15 + (6 - d) * 8
        ss_draw.text((sx + d * 2, sy + d * 2), s_text, fill=(0, 0, 0, alpha), font=font)

    s_shadow = s_shadow.filter(ImageFilter.GaussianBlur(radius=8))
    img = Image.alpha_composite(img, s_shadow)

    # Main S with gradient effect
    s_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(s_layer)

    # Draw S
    s_draw.text((sx, sy), s_text, fill=(185, 45, 55), font=font)

    # Add highlight gradient to S
    s_mask = Image.new('L', (size, size), 0)
    sm_draw = ImageDraw.Draw(s_mask)
    sm_draw.text((sx, sy), s_text, fill=255, font=font)

    for y in range(size):
        for x in range(size):
            if s_mask.getpixel((x, y)) > 128:
                cur = s_layer.getpixel((x, y))
                # Vertical gradient - lighter at top
                progress = (y - sy) / sh if sh > 0 else 0
                progress = max(0, min(1, progress))

                r = int(cur[0] + 35 * (1 - progress) - 25 * progress)
                g = int(cur[1] + 15 * (1 - progress) - 15 * progress)
                b = int(cur[2] + 15 * (1 - progress) - 10 * progress)

                s_layer.putpixel((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    img = Image.alpha_composite(img, s_layer)

    # === "3" IN SILVER/WHITE ===
    three_shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ts_draw = ImageDraw.Draw(three_shadow)

    t_text = "3"
    bbox = ts_draw.textbbox((0, 0), t_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2 + int(size * 0.12)
    ty = cy - th // 2 - int(size * 0.05)

    # Shadow for 3
    for d in range(5, 0, -1):
        alpha = 20 + (5 - d) * 10
        ts_draw.text((tx + d * 2, ty + d * 2), t_text, fill=(0, 0, 0, alpha), font=font)

    three_shadow = three_shadow.filter(ImageFilter.GaussianBlur(radius=6))
    img = Image.alpha_composite(img, three_shadow)

    # Main 3
    three_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(three_layer)
    t_draw.text((tx, ty), t_text, fill=(235, 235, 240), font=font)

    # Gradient on 3
    t_mask = Image.new('L', (size, size), 0)
    tm_draw = ImageDraw.Draw(t_mask)
    tm_draw.text((tx, ty), t_text, fill=255, font=font)

    for y in range(size):
        for x in range(size):
            if t_mask.getpixel((x, y)) > 128:
                cur = three_layer.getpixel((x, y))
                progress = (y - ty) / th if th > 0 else 0
                progress = max(0, min(1, progress))

                # Subtle darkening towards bottom
                factor = 1 - 0.12 * progress
                r = int(cur[0] * factor)
                g = int(cur[1] * factor)
                b = int(cur[2] * factor)

                three_layer.putpixel((x, y), (r, g, b, 255))

    img = Image.alpha_composite(img, three_layer)

    # === TOP GLOSS ===
    gloss = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gloss)

    for y in range(margin, margin + int(size * 0.2)):
        progress = (y - margin) / (size * 0.2)
        alpha = int(18 * (1 - progress))
        for x in range(margin, size - margin):
            in_shape = True
            if y < margin + corner_radius:
                if x < margin + corner_radius:
                    dist = math.sqrt((margin + corner_radius - x)**2 + (margin + corner_radius - y)**2)
                    if dist > corner_radius: in_shape = False
                elif x > size - margin - corner_radius:
                    dist = math.sqrt((x - (size - margin - corner_radius))**2 + (margin + corner_radius - y)**2)
                    if dist > corner_radius: in_shape = False

            if in_shape:
                gloss.putpixel((x, y), (255, 255, 255, alpha))

    img = Image.alpha_composite(img, gloss)

    # Resize
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    return img


def create_icns(img, output_path):
    iconset_path = output_path.replace('.icns', '.iconset')
    os.makedirs(iconset_path, exist_ok=True)

    for s in [16, 32, 64, 128, 256, 512, 1024]:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(f"{iconset_path}/icon_{s}x{s}.png")
        if s <= 512:
            resized_2x = img.resize((s * 2, s * 2), Image.Resampling.LANCZOS)
            resized_2x.save(f"{iconset_path}/icon_{s}x{s}@2x.png")

    os.system(f"iconutil -c icns '{iconset_path}' -o '{output_path}'")
    import shutil
    shutil.rmtree(iconset_path, ignore_errors=True)


def main():
    base_dir = Path(__file__).parent.parent
    resources_dir = base_dir / "ShadowNinja.app/Contents/Resources"
    resources_dir.mkdir(parents=True, exist_ok=True)

    print("Creating Modern S3 icon (clear letters)...")
    icon = create_modern_icon(2048)

    png_path = resources_dir / "AppIcon.png"
    icon.save(png_path)
    print(f"  PNG: {png_path}")

    icns_path = str(resources_dir / "AppIcon.icns")
    create_icns(icon, icns_path)
    print(f"  ICNS: {icns_path}")
    print("Done!")


if __name__ == "__main__":
    main()
