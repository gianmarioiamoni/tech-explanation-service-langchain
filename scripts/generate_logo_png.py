#!/usr/bin/env python3
# scripts/generate_logo_png.py
#
# Convert logo.svg to logo.png (120x120)
#
# Requirements: pip install cairosvg pillow

import sys
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    import io
except ImportError:
    print("❌ Missing dependencies!")
    print("\nPlease install:")
    print("  pip install cairosvg pillow")
    print("\nOr use online converter:")
    print("  https://cloudconvert.com/svg-to-png")
    sys.exit(1)

def convert_svg_to_png(svg_path: str, png_path: str, size: int = 120):
    # Convert SVG to PNG
    #
    # Args:
    #     svg_path: Path to input SVG file
    #     png_path: Path to output PNG file
    #     size: Output size in pixels (default: 120x120)
    
    print(f"🔄 Converting {svg_path} to {png_path}...")
    
    # Read SVG
    svg_data = Path(svg_path).read_text()
    
    # Convert SVG to PNG bytes
    png_data = cairosvg.svg2png(
        bytestring=svg_data.encode('utf-8'),
        output_width=size,
        output_height=size
    )
    
    # Open with PIL to ensure quality
    img = Image.open(io.BytesIO(png_data))
    
    # Save as PNG
    img.save(png_path, 'PNG', optimize=True)
    
    print(f"✅ Logo saved: {png_path} ({size}x{size}px)")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    svg_path = project_root / "assets" / "logo.svg"
    png_path = project_root / "assets" / "logo.png"
    
    if not svg_path.exists():
        print(f"❌ SVG file not found: {svg_path}")
        sys.exit(1)
    
    # Ensure assets directory exists
    png_path.parent.mkdir(parents=True, exist_ok=True)
    
    convert_svg_to_png(str(svg_path), str(png_path), size=120)
    
    print("\n📊 File info:")
    print(f"  SVG: {svg_path.stat().st_size:,} bytes")
    print(f"  PNG: {png_path.stat().st_size:,} bytes")
    print(f"\n🎉 Done! Logo ready at: assets/logo.png")

