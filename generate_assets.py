import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('assets', exist_ok=True)

# 1. Social Preview Banner (1200x630)
w, h = 1200, 630
img = Image.new('RGB', (w, h), (15, 23, 42))
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, w, 8], fill=(56, 189, 248))
draw.rectangle([60, 80, 1140, 550], outline=(51, 65, 85), width=2)
draw.text((100, 140), "DeltaDoc AI", fill=(248, 250, 252))
draw.text((100, 200), "AI-Powered Engineering Document Comparison", fill=(56, 189, 248))
draw.text((100, 250), "Revision Intelligence • Grounded RAG Chat • Visual Diff Overlays", fill=(148, 163, 184))

badges = ["FastAPI", "React", "ChromaDB", "Gemini 2.5", "EasyOCR", "Docker"]
bx = 100
for b in badges:
    bw = len(b) * 12 + 24
    draw.rectangle([bx, 340, bx + bw, 380], fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    draw.text((bx + 12, 352), b, fill=(226, 232, 240))
    bx += bw + 16

img.save('assets/social_preview.png')

# 2. Visual Diff Overlay Preview (1000x500)
w2, h2 = 1000, 500
img2 = Image.new('RGB', (w2, h2), (15, 23, 42))
draw2 = ImageDraw.Draw(img2)

# Side A
draw2.rectangle([20, 20, 480, 480], fill=(30, 41, 59), outline=(71, 85, 105), width=2)
draw2.text((40, 40), "Revision A (Baseline P&ID)", fill=(248, 250, 252))
draw2.rectangle([80, 160, 360, 240], outline=(239, 68, 68), width=3)
draw2.rectangle([80, 135, 240, 160], fill=(239, 68, 68))
draw2.text((85, 140), "Removed: Valve V-102", fill=(255, 255, 255))

# Side B
draw2.rectangle([520, 20, 980, 480], fill=(30, 41, 59), outline=(71, 85, 105), width=2)
draw2.text((540, 40), "Revision B (Updated P&ID)", fill=(248, 250, 252))
draw2.rectangle([560, 160, 840, 240], outline=(234, 179, 8), width=3)
draw2.rectangle([560, 135, 760, 160], fill=(234, 179, 8))
draw2.text((565, 140), "Modified: 26-PIT-9055", fill=(255, 255, 255))

draw2.rectangle([560, 310, 880, 390], outline=(34, 197, 94), width=3)
draw2.rectangle([560, 285, 750, 310], fill=(34, 197, 94))
draw2.text((565, 290), "Added: Pipe 6in-CS-150", fill=(255, 255, 255))

img2.save('assets/visual_diff_preview.png')
print("Assets generated cleanly in assets/")
