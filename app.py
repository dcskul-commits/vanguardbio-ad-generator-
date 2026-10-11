import io
import os
import textwrap
import zipfile
from fastapi import FastAPI
from fastapi.responses import Response, StreamingResponse
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

CANVAS_SIZE = (1080, 1080)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

# Load fonts from repo folder, falling back to default if absent
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
try:
    font_rating = ImageFont.truetype(os.path.join(FONT_DIR, "Arial.ttf"), 36)
    font_author = ImageFont.truetype(os.path.join(FONT_DIR, "Arial.ttf"), 34)
    font_quote = ImageFont.truetype(os.path.join(FONT_DIR, "Arial.ttf"), 38)
    font_footer = ImageFont.truetype(os.path.join(FONT_DIR, "Arial-Bold.ttf"), 46)
except Exception:
    font_rating = font_author = font_quote = font_footer = ImageFont.load_default()

# Load logo
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logowhite.png")
logo_img = None
if os.path.exists(LOGO_PATH):
    raw_logo = Image.open(LOGO_PATH).convert("RGBA")
    target_width = 460
    scale = target_width / raw_logo.width
    target_height = int(raw_logo.height * scale)
    logo_img = raw_logo.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Apollo Protocol Review Dataset
REVIEWS = [
    {
        "num": 1,
        "author": "Marcus R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The Apollo Protocol is an absolute game-changer for foundational health. Within two weeks, chronic digestive bloating and low-grade gut discomfort that I had battled for years completely vanished. The synergy between KPV, BPC-157, and TB-500 is nothing short of miraculous.",
    },
    {
        "num": 2,
        "author": "Dr. Alan H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "As a clinician, I am profoundly impressed by the 503B pharmacy-grade quality and the intelligent peptide sequencing in this stack. Combining gut mucosal repair (KPV/BPC-157) with immune modulation (Thymosin Alpha-1) and cellular longevity (MOTS-c/Glutathione) addresses the root causes of systemic inflammation.",
    },
    {
        "num": 3,
        "author": "Sarah L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Absolute 5 out of 5. My energy levels have stabilized, my immune resilience through seasonal changes has been bulletproof, and my gut microbiome has never felt more balanced. The telehealth consultation was thorough and reassuring.",
    },
    # Insert remaining review dicts up to 100 here
]

def render_ad_image(item: dict) -> Image.Image:
    canvas = Image.new("RGB", CANVAS_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # 1. Logo
    current_y = 70
    if logo_img:
        logo_x = (CANVAS_SIZE[0] - logo_img.width) // 2
        canvas.paste(logo_img, (logo_x, current_y), logo_img)
        current_y += logo_img.height + 40
    else:
        current_y += 100

    # 2. Rating
    rating_text = item["rating"]
    r_bbox = draw.textbbox((0, 0), rating_text, font=font_rating)
    draw.text(((CANVAS_SIZE[0] - (r_bbox[2] - r_bbox[0])) // 2, current_y), rating_text, fill=TEXT_COLOR, font=font_rating)
    current_y += (r_bbox[3] - r_bbox[1]) + 20

    # 3. Author
    author_text = item["author"]
    a_bbox = draw.textbbox((0, 0), author_text, font=font_author)
    draw.text(((CANVAS_SIZE[0] - (a_bbox[2] - a_bbox[0])) // 2, current_y), author_text, fill=(220, 220, 220), font=font_author)
    current_y += (a_bbox[3] - a_bbox[1]) + 45

    # 4. Formatted Quote
    wrapped_lines = textwrap.wrap(f'“{item["quote"]}”', width=38)
    for line in wrapped_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_quote)
        draw.text(((CANVAS_SIZE[0] - (line_bbox[2] - line_bbox[0])) // 2, current_y), line, fill=TEXT_COLOR, font=font_quote)
        current_y += (line_bbox[3] - line_bbox[1]) + 18

    # 5. Footer URL
    footer_text = "VanguardBIO.ai"
    f_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    draw.text(((CANVAS_SIZE[0] - (f_bbox[2] - f_bbox[0])) // 2, 970), footer_text, fill=TEXT_COLOR, font=font_footer)

    return canvas

@app.get("/")
def home():
    return {"status": "ready", "download_url": "/generate-zip"}

@app.get("/generate-zip")
def generate_zip():
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in REVIEWS:
            img = render_ad_image(item)
            img_io = io.BytesIO()
            img.save(img_io, format="PNG", dpi=(72, 72))
            img_io.seek(0)
            zf.writestr(f"apollo_ad_{item['num']:03d}.png", img_io.read())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=apollo_ads_batch.zip"}
    )
