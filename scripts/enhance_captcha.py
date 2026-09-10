#!/usr/bin/env python3
"""
CAPTCHA Image Enhancer
放大并增强验证码图片，便于 AI 视觉识别。

用法:
  python3 enhance_captcha.py <input_image> [output_image] [--scale 6] [--contrast 2.5] [--threshold]

参数:
  input_image   验证码图片路径（支持 png/jpg/gif/bmp）
  output_image  输出路径（默认: /tmp/captcha_enhanced.png）
  --scale N     放大倍数（默认: 6）
  --contrast N  对比度增强倍数（默认: 2.5）
  --threshold   二值化处理（黑白），对部分验证码效果更好
  --sharpen     额外锐化（默认开启）
  --invert      反色处理

示例:
  python3 enhance_captcha.py captcha.png
  python3 enhance_captcha.py captcha.png out.png --scale 8 --contrast 3.0 --threshold
"""

import argparse
import sys
import os

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    print("ERROR: Pillow not installed. Run: pip3 install Pillow", file=sys.stderr)
    sys.exit(1)


def enhance_captcha(input_path, output_path, scale=6, contrast=2.5,
                    threshold=False, sharpen=True, invert=False):
    """Enhance a CAPTCHA image for better readability."""
    img = Image.open(input_path)
    print(f"Input: {img.size}, mode={img.mode}")

    # Convert to grayscale
    gray = img.convert('L')

    # Invert if requested
    if invert:
        gray = ImageOps.invert(gray)

    # Enlarge
    big = gray.resize((gray.width * scale, gray.height * scale), Image.LANCZOS)

    # Increase contrast
    big = ImageEnhance.Contrast(big).enhance(contrast)

    # Sharpen
    if sharpen:
        big = big.filter(ImageFilter.SHARPEN)

    # Optional threshold (binarize)
    if threshold:
        big = big.point(lambda x: 0 if x < 128 else 255, '1')

    big.save(output_path)
    print(f"Output: {big.size}, saved to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Enhance CAPTCHA images for AI recognition')
    parser.add_argument('input', help='Input CAPTCHA image path')
    parser.add_argument('output', nargs='?', default='/tmp/captcha_enhanced.png',
                        help='Output image path (default: /tmp/captcha_enhanced.png)')
    parser.add_argument('--scale', type=int, default=6, help='Scale factor (default: 6)')
    parser.add_argument('--contrast', type=float, default=2.5, help='Contrast factor (default: 2.5)')
    parser.add_argument('--threshold', action='store_true', help='Apply binarization threshold')
    parser.add_argument('--no-sharpen', action='store_true', help='Disable sharpening')
    parser.add_argument('--invert', action='store_true', help='Invert colors')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    enhance_captcha(
        args.input, args.output,
        scale=args.scale, contrast=args.contrast,
        threshold=args.threshold, sharpen=not args.no_sharpen,
        invert=args.invert
    )


if __name__ == '__main__':
    main()
