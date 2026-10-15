import io
import os
import zipfile
from fastapi import FastAPI
from fastapi.responses import Response, StreamingResponse
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

CANVAS_SIZE = (1080, 1080)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
SUBTEXT_COLOR = (215, 215, 215)
MAX_TEXT_WIDTH = 900  # Leaves 90px margin on each side

# Directory for custom fonts
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

def get_font(font_name: str, size: int):
    # Try custom folder, system fonts, or fallback
    paths = [
        os.path.join(FONT_DIR, font_name),
        font_name,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("Arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

# Base fonts
font_rating = get_font("Arial-Bold.ttf", 46)
font_author = get_font("Arial.ttf", 36)
font_footer = get_font("Arial-Bold.ttf", 50)

# Load Logo
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logowhite.png")
logo_img = None
if os.path.exists(LOGO_PATH):
    raw_logo = Image.open(LOGO_PATH).convert("RGBA")
    target_width = 560  # Increased from 460 for prominent branding
    scale = target_width / raw_logo.width
    target_height = int(raw_logo.height * scale)
    logo_img = raw_logo.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Wrap text strictly by pixel boundary
def wrap_text_pixels(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)

# Base fonts
font_rating = get_font("Arial-Bold.ttf", 46)
font_author = get_font("Arial.ttf", 36)
font_footer = get_font("Arial-Bold.ttf", 50)

# Load Logo
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logowhite.png")
logo_img = None
if os.path.exists(LOGO_PATH):
    raw_logo = Image.open(LOGO_PATH).convert("RGBA")
    target_width = 560  # Increased from 460 for prominent branding
    scale = target_width / raw_logo.width
    target_height = int(raw_logo.height * scale)
    logo_img = raw_logo.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Wrap text strictly by pixel boundary
def wrap_text_pixels(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_w = bbox[2] - bbox[0]
        if line_w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

# Complete Athena Protocol Review Dataset (1 to 129)
REVIEWS = [
    {
        "num": 1,
        "author": "Elena V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The Athena Protocol completely transformed my skin luminosity and texture within three weeks. The combination of Glutathione and GHK-Cu gave me a radiant glow that my dermatologist couldn't stop asking about."
    },
    {
        "num": 2,
        "author": "Sophia R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ infusions paired with the copper peptide completely reset my energy levels and smoothed out fine lines around my eyes. Absolute game-changer for women over 40."
    },
    {
        "num": 3,
        "author": "Dr. Claire M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "From a clinical standpoint, the multi-vector formulation in the Athena stack is brilliant. Dermal density and skin elasticity improved measurably on ultrasound by week six."
    },
    {
        "num": 4,
        "author": "Chloe S. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Incredible results on skin radiance and overall vitality. The Melanotan II component provided a gorgeous, even glow without harsh sun exposure."
    },
    {
        "num": 5,
        "author": "Victoria L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My hair density and skin firmness have never looked better. VanguardBIO delivers true pharmaceutical-grade anti-aging results."
    },
    {
        "num": 6,
        "author": "Hannah B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep quality skyrocketed thanks to the HGH and NAD+ synergy. I wake up looking and feeling fully refreshed every single morning."
    },
    {
        "num": 7,
        "author": "Jessica T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The tele-health onboarding was seamless, and the protocol documentation made self-administration effortless. Worth every single dollar."
    },
    {
        "num": 8,
        "author": "Rachel K. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable tightening of skin tone and a dramatic reduction in oxidative stress fatigue. Truly feels like a fountain of youth stack."
    },
    {
        "num": 9,
        "author": "Natalie P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "GHK-Cu is magic for skin elasticity. My friends keep asking what facial treatments I've been doing—it's all thanks to Athena."
    },
    {
        "num": 10,
        "author": "Samantha W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Crystal-clear protocol guidance, rapid shipping, and pristine 503B compounding quality. Exceptional experience."
    },
    {
        "num": 11,
        "author": "Lauren H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione cleared up my skin tone completely. The oxidative glow is real and sustainable."
    },
    {
        "num": 12,
        "author": "Megan D. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Solid body composition changes alongside remarkable anti-aging skin improvements. Exceptional stack for women."
    },
    {
        "num": 13,
        "author": "Amanda C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 keeps my joint mobility and skin tissue resilient against everyday stress. Complete cellular rejuvenation."
    },
    {
        "num": 14,
        "author": "Brittany N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My biological age markers on my tracking dashboard dropped significantly over 8 weeks. Unbelievable science."
    },
    {
        "num": 15,
        "author": "Taylor F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The combination of NAD+ and Glutathione gave me boundless daily energy while clearing my skin entirely."
    },
    {
        "num": 16,
        "author": "Ashley M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "A premium investment in longevity and appearance. The results speak for themselves on every mirror check."
    },
    {
        "num": 17,
        "author": "Danielle R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Fine lines around my mouth and forehead have visibly softened. GHK-Cu is an absolute miracle worker."
    },
    {
        "num": 18,
        "author": "Nicole G. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional packaging, precise dosing instructions, and outstanding customer care from VanguardBIO."
    },
    {
        "num": 19,
        "author": "Amber J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Melanotan II gave me a beautiful, sun-kissed photoprotective glow without any UV damage or burning."
    },
    {
        "num": 20,
        "author": "Stephanie K. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Body tone and skin luminosity improved in tandem. Very happy with the monthly auto-refill schedule."
    },
    {
        "num": 21,
        "author": "Kayla B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My recovery from workouts is faster and my skin texture is tighter. The Athena Protocol covers every base."
    },
    {
        "num": 22,
        "author": "Alexis W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cellular energy and skin clarity both reached all-time highs. Highly recommend to any woman serious about longevity."
    },
    {
        "num": 23,
        "author": "Morgan T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy compounding standard gives total peace of mind. Purity and efficacy are unmatched."
    },
    {
        "num": 24,
        "author": "Brianna S. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable reduction in skin dullness and improved sleep architecture within the first ten days."
    },
    {
        "num": 25,
        "author": "Jasmine L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH and GHK-Cu working together restored my youthful skin bounce. Truly remarkable biohacking."
    },
    {
        "num": 26,
        "author": "Courtney P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Systemic inflammation markers dropped, and my complexion looks clearer than it did in my twenties."
    },
    {
        "num": 27,
        "author": "Paige D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Comprehensive health expert oversight during onboarding ensured my protocol was custom-tailored."
    },
    {
        "num": 28,
        "author": "Sydney V. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Fantastic results on skin thickness and hair follicle vitality. Worth every penny."
    },
    {
        "num": 29,
        "author": "Brooke M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ repletion completely eliminated my afternoon brain fog. Sharp focus all day long."
    },
    {
        "num": 30,
        "author": "Kaitlyn R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The master antioxidant blend in Athena keeps my skin luminous even through stressful work weeks."
    },
    {
        "num": 31,
        "author": "Allison C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Dermal density ultrasound scans showed incredible collagen synthesis after just two months."
    },
    {
        "num": 32,
        "author": "Jenna K. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Smooth delivery, beautiful packaging, and high-end clinical documentation."
    },
    {
        "num": 33,
        "author": "Whitney B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin elasticity and overall muscle tone improved dramatically. Flawless formulation."
    },
    {
        "num": 34,
        "author": "Savannah T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My recovery and skin radiance have both reached peak levels. VanguardBIO sets the benchmark."
    },
    {
        "num": 35,
        "author": "Kelsey H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "GHK-Cu and Glutathione are a powerhouse pairing for anyone seeking radiant, youthful skin."
    },
    {
        "num": 36,
        "author": "Mackenzie W. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Noticeable smoothing of fine lines and a vibrant, healthy glow across my face and neck."
    },
    {
        "num": 37,
        "author": "Audrey L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The quarterly plan ensures my routine stays uninterrupted. Fantastic anti-aging results."
    },
    {
        "num": 38,
        "author": "Claire S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Energy levels are through the roof thanks to NAD+ and HGH. I feel ten years younger."
    },
    {
        "num": 39,
        "author": "Maya P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Photoprotection from Melanotan II has been fantastic during my outdoor runs. Zero sunburn."
    },
    {
        "num": 40,
        "author": "Paige M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Professional medical oversight made me feel secure starting my first peptide protocol."
    },
    {
        "num": 41,
        "author": "Zoe R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin texture is velvet-smooth and deep sleep scores are pristine. Unbelievable stack."
    },
    {
        "num": 42,
        "author": "Lily C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Collagen production stimulated by GHK-Cu has visibly firmed up my jawline and neck."
    },
    {
        "num": 43,
        "author": "Grace H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Detoxification support from Glutathione cleared up my skin and boosted my daily vitality."
    },
    {
        "num": 44,
        "author": "Stella W. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "High-tier formulation with zero guesswork. The instructional videos made setup foolproof."
    },
    {
        "num": 45,
        "author": "Victoria K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My biological clock metrics have never looked better. Athena is an elite longevity protocol."
    },
    {
        "num": 46,
        "author": "Penelope B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 and GHK-Cu keep my tissue repair and skin elasticity at peak performance."
    },
    {
        "num": 47,
        "author": "Scarlett T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Radiant skin, boundless cellular energy, and effortless body tone maintenance."
    },
    {
        "num": 48,
        "author": "Aria N. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable reduction in oxidative stress and a brighter complexion overall."
    },
    {
        "num": 49,
        "author": "Ellie J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy standard is evident in the remarkable purity and fast results."
    },
    {
        "num": 50,
        "author": "Nora F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ repletion completely changed my daily stamina. I have energy to spare after long work days."
    },
    {
        "num": 51,
        "author": "Hazel M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin luminescence is off the charts. Glutathione is a permanent fixture in my routine now."
    },
    {
        "num": 52,
        "author": "Aurora S. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Flawless onboarding and expert support. The results on skin firmness are undeniable."
    },
    {
        "num": 53,
        "author": "Violet D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "GHK-Cu stimulated incredible hair and skin health improvements within six weeks."
    },
    {
        "num": 54,
        "author": "Savannah R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep architecture and skin healing metrics reached new personal records."
    },
    {
        "num": 55,
        "author": "Audrey K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The Athena protocol is a masterclass in comprehensive anti-aging biohacking."
    },
    {
        "num": 56,
        "author": "Brooklyn H. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Very impressed with the third-party purity testing and clinical documentation."
    },
    {
        "num": 57,
        "author": "Bella C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Melanotan II gives a gorgeous, natural glow while protecting against photoaging."
    },
    {
        "num": 58,
        "author": "Skylar W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Body composition and skin radiance both dialed in perfectly. Incredible stack."
    },
    {
        "num": 59,
        "author": "Lucy T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ and HGH synergy provides endless vitality and youthful skin tightness."
    },
    {
        "num": 60,
        "author": "Paisley P. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Smooth delivery and exceptional customer support from the VanguardBIO team."
    },
    {
        "num": 61,
        "author": "Everly B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Collagen density in my face and neck improved visibly within the first month."
    },
    {
        "num": 62,
        "author": "Anna L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione and GHK-Cu cleared my skin blemishes and brought back a youthful glow."
    },
    {
        "num": 63,
        "author": "Caroline N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The quarterly plan is seamless. Automatic shipments arrive right when needed."
    },
    {
        "num": 64,
        "author": "Nova S. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "High-end clinical grade compounds that deliver genuine anti-aging results."
    },
    {
        "num": 65,
        "author": "Genesis M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My skin feels thicker, more elastic, and intensely hydrated from within."
    },
    {
        "num": 66,
        "author": "Emilia R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth consultation was professional, thorough, and highly informative."
    },
    {
        "num": 67,
        "author": "Elena K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Oxidative stress markers dropped dramatically. I feel vibrant and look radiant."
    },
    {
        "num": 68,
        "author": "Sadie V. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Fantastic stack for maintaining skin integrity and metabolic tone effortlessly."
    },
    {
        "num": 69,
        "author": "Delilah W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 and GHK-Cu healed minor tissue wear and enhanced skin smoothness."
    },
    {
        "num": 70,
        "author": "Adalyn H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep and skin luminosity metrics have never been higher. Absolutely love Athena."
    },
    {
        "num": 71,
        "author": "Madelyn T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy standard gives absolute confidence in safety and formulation purity."
    },
    {
        "num": 72,
        "author": "Gianna C. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable smoothing of fine lines around the eyes. GHK-Cu is truly impressive."
    },
    {
        "num": 73,
        "author": "Maya S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ repletion eliminated my afternoon fatigue completely. Boundless cellular energy."
    },
    {
        "num": 74,
        "author": "Ellie B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin radiance and tone are consistently glowing week after week. Exceptional protocol."
    },
    {
        "num": 75,
        "author": "Harper P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional medical oversight made starting my peptide journey comfortable and secure."
    },
    {
        "num": 76,
        "author": "Camila D. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Melanotan II provides an even, beautiful photoprotective tan all year round."
    },
    {
        "num": 77,
        "author": "Athena J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Living up completely to its namesake. Skin tightness, body tone, and radiance are elite."
    },
    {
        "num": 78,
        "author": "Isla M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione and NAD+ work wonders for internal cleansing and external glow."
    },
    {
        "num": 79,
        "author": "Clara W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Dermal density ultrasound scans confirmed massive collagen gains by week eight."
    },
    {
        "num": 80,
        "author": "Ruby L. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Fast delivery, gorgeous packaging, and crystal-clear protocol instructions."
    },
    {
        "num": 81,
        "author": "Sophie K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My skin elasticity and overall youthful vitality have exceeded all expectations."
    },
    {
        "num": 82,
        "author": "Alice R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation keeps my skin firm, sleep deep, and body composition lean."
    },
    {
        "num": 83,
        "author": "Eva H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "GHK-Cu is an absolute staple for anyone serious about reversing skin aging."
    },
    {
        "num": 84,
        "author": "Quinn C. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Comprehensive documentation and effortless administration make this protocol top-tier."
    },
    {
        "num": 85,
        "author": "Vivian T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Systemic inflammation plummeted, leaving my complexion crystal clear and vibrant."
    },
    {
        "num": 86,
        "author": "Rebekah S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy compounding standard guarantees immaculate product quality."
    },
    {
        "num": 87,
        "author": "Daisy M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cellular energy and skin luminosity both reached remarkable new heights."
    },
    {
        "num": 88,
        "author": "Melanie P. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Solid anti-aging results with noticeable improvements in skin texture and firmness."
    },
    {
        "num": 89,
        "author": "Juliana B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ and Glutathione synergy gave me endless stamina and a radiant complexion."
    },
    {
        "num": 90,
        "author": "Valeria W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth onboarding was thorough and expert-led. Protocol guidance is crystal clear."
    },
    {
        "num": 91,
        "author": "Josephine K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Collagen synthesis from GHK-Cu visibly firmed up fine lines around my eyes."
    },
    {
        "num": 92,
        "author": "Fiona L. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Wonderful quarterly plan that keeps my anti-aging regimen uninterrupted."
    },
    {
        "num": 93,
        "author": "Iris R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 and GHK-Cu keep my skin tissue resilient, smooth, and youthful."
    },
    {
        "num": 94,
        "author": "Lillian H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep metrics and skin radiance scores hit all-time personal bests."
    },
    {
        "num": 95,
        "author": "Adeline S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional compounding quality and exceptional customer care from VanguardBIO."
    },
    {
        "num": 96,
        "author": "Gemma T. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Melanotan II provides gorgeous photoprotection with zero sun damage."
    },
    {
        "num": 97,
        "author": "Cora C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Body tone and skin luminosity improved in tandem. Highly satisfied with Athena."
    },
    {
        "num": 98,
        "author": "Rosalie M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation and NAD+ repletion keep my skin tight and energy boundless."
    },
    {
        "num": 99,
        "author": "Beatrice V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione cleared up my skin tone completely. The radiant glow is permanent."
    },
    {
        "num": 100,
        "author": "Elise W. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Exceptional formulation for women demanding high-tier aesthetic anti-aging."
    },
    {
        "num": 101,
        "author": "Genevieve B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Dermal density ultrasound scans confirmed massive collagen gains by week eight."
    },
    {
        "num": 102,
        "author": "Antonia P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth consultation was professional, thorough, and highly informative."
    },
    {
        "num": 103,
        "author": "Helena K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Oxidative stress markers dropped dramatically. I feel vibrant and look radiant."
    },
    {
        "num": 104,
        "author": "Theodora R. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Fantastic stack for maintaining skin integrity and metabolic tone effortlessly."
    },
    {
        "num": 105,
        "author": "Matilda S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 and GHK-Cu healed minor tissue wear and enhanced skin smoothness."
    },
    {
        "num": 106,
        "author": "Josephine H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep and skin luminosity metrics have never been higher. Absolutely love Athena."
    },
    {
        "num": 107,
        "author": "Rosalind M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy standard gives absolute confidence in safety and formulation purity."
    },
    {
        "num": 108,
        "author": "Marguerite T. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Noticeable smoothing of fine lines around the eyes. GHK-Cu is truly impressive."
    },
    {
        "num": 109,
        "author": "Evangeline C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ repletion eliminated my afternoon fatigue completely. Boundless cellular energy."
    },
    {
        "num": 110,
        "author": "Beatrice B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin radiance and tone are consistently glowing week after week. Exceptional protocol."
    },
    {
        "num": 111,
        "author": "Cornelia W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional medical oversight made starting my peptide journey comfortable and secure."
    },
    {
        "num": 112,
        "author": "Wilhelmina K. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Melanotan II provides an even, beautiful photoprotective tan all year round."
    },
    {
        "num": 113,
        "author": "Florence D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Living up completely to its namesake. Skin tightness, body tone, and radiance are elite."
    },
    {
        "num": 114,
        "author": "Agnes V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione and NAD+ work wonders for internal cleansing and external glow."
    },
    {
        "num": 115,
        "author": "Mabel L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Dermal density ultrasound scans confirmed massive collagen gains by week eight."
    },
    {
        "num": 116,
        "author": "Edith R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Fast delivery, gorgeous packaging, and crystal-clear protocol instructions."
    },
    {
        "num": 117,
        "author": "Gertrude H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My skin elasticity and overall youthful vitality have exceeded all expectations."
    },
    {
        "num": 118,
        "author": "Harriet S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation keeps my skin firm, sleep deep, and body composition lean."
    },
    {
        "num": 119,
        "author": "Mildred P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "GHK-Cu is an absolute staple for anyone serious about reversing skin aging."
    },
    {
        "num": 120,
        "author": "Florence T. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Comprehensive documentation and effortless administration make this protocol top-tier."
    },
    {
        "num": 121,
        "author": "Blanche M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Systemic inflammation plummeted, leaving my complexion crystal clear and vibrant."
    },
    {
        "num": 122,
        "author": "Esther C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy compounding standard guarantees immaculate product quality."
    },
    {
        "num": 123,
        "author": "Hazel B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cellular energy and skin luminosity both reached remarkable new heights."
    },
    {
        "num": 124,
        "author": "Pearl W. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Solid anti-aging results with noticeable improvements in skin texture and firmness."
    },
    {
        "num": 125,
        "author": "Opal K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ and Glutathione synergy gave me endless stamina and a radiant complexion."
    },
    {
        "num": 126,
        "author": "Ruby V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth onboarding was thorough and expert-led. Protocol guidance is crystal clear."
    },
    {
        "num": 127,
        "author": "Stella R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Collagen synthesis from GHK-Cu visibly firmed up fine lines around my eyes."
    },
    {
        "num": 128,
        "author": "Viola D. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Wonderful quarterly plan that keeps my anti-aging regimen uninterrupted."
    },
    {
        "num": 129,
        "author": "Clara H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 and GHK-Cu keep my skin tissue resilient, smooth, and youthful."
    },
    {
        "num": 130,
        "author": "Bessie S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep metrics and skin radiance scores hit all-time personal bests."
    },
    {
        "num": 131,
        "author": "Maud T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional compounding quality and exceptional customer care from VanguardBIO."
    },
    {
        "num": 132,
        "author": "Lillian C. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Melanotan II provides gorgeous photoprotection with zero sun damage."
    },
    {
        "num": 133,
        "author": "Flora M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Body tone and skin luminosity improved in tandem. Highly satisfied with Athena."
    },
    {
        "num": 134,
        "author": "Nellie B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation and NAD+ repletion keep my skin tight and energy boundless."
    },
    {
        "num": 135,
        "author": "Lottie V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione cleared up my skin tone completely. The radiant glow is permanent."
    },
    {
        "num": 136,
        "author": "Matilda W. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Exceptional formulation for women demanding high-tier aesthetic anti-aging."
    },
    {
        "num": 137,
        "author": "Hattie K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Dermal density ultrasound scans confirmed massive collagen gains by week eight."
    },
    {
        "num": 138,
        "author": "Cora R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth consultation was professional, thorough, and highly informative."
    },
    {
        "num": 139,
        "author": "Eula D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Oxidative stress markers dropped dramatically. I feel vibrant and look radiant."
    },
    {
        "num": 140,
        "author": "Minna H. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Fantastic stack for maintaining skin integrity and metabolic tone effortlessly."
    },
    {
        "num": 141,
        "author": "Lula S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 and GHK-Cu healed minor tissue wear and enhanced skin smoothness."
    },
    {
        "num": 142,
        "author": "Lida T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep and skin luminosity metrics have never been higher. Absolutely love Athena."
    },
    {
        "num": 143,
        "author": "Nettie C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy standard gives absolute confidence in safety and formulation purity."
    },
    {
        "num": 144,
        "author": "Rosie M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable smoothing of fine lines around the eyes. GHK-Cu is truly impressive."
    },
    {
        "num": 145,
        "author": "Dora B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "NAD+ repletion eliminated my afternoon fatigue completely. Boundless cellular energy."
    },
    {
        "num": 146,
        "author": "Effie W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin radiance and tone are consistently glowing week after week. Exceptional protocol."
    },
    {
        "num": 147,
        "author": "Lola K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional medical oversight made starting my peptide journey comfortable and secure."
    },
    {
        "num": 148,
        "author": "Bessie R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Melanotan II provides an even, beautiful photoprotective tan all year round."
    },
    {
        "num": 149,
        "author": "Maggie D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Living up completely to its namesake. Skin tightness, body tone, and radiance are elite."
    },
    {
        "num": 150,
        "author": "May H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione and NAD+ work wonders for internal cleansing and external glow."
    }
]

def render_ad_image(item: dict) -> Image.Image:
    canvas = Image.new("RGB", CANVAS_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # 1. Place Logo
    current_y = 60
    if logo_img:
        logo_x = (CANVAS_SIZE[0] - logo_img.width) // 2
        canvas.paste(logo_img, (logo_x, current_y), logo_img)
        current_y += logo_img.height + 30
    else:
        current_y += 120

    # 2. Rating & Stars
    rating_text = item["rating"]
    r_bbox = draw.textbbox((0, 0), rating_text, font=font_rating)
    r_w = r_bbox[2] - r_bbox[0]
    draw.text(((CANVAS_SIZE[0] - r_w) // 2, current_y), rating_text, fill=TEXT_COLOR, font=font_rating)
    current_y += (r_bbox[3] - r_bbox[1]) + 16

    # 3. Author
    author_text = item["author"]
    a_bbox = draw.textbbox((0, 0), author_text, font=font_author)
    a_w = a_bbox[2] - a_bbox[0]
    draw.text(((CANVAS_SIZE[0] - a_w) // 2, current_y), author_text, fill=SUBTEXT_COLOR, font=font_author)
    current_y += (a_bbox[3] - a_bbox[1]) + 35

    # 4. Dynamic Quote Sizing
    # Target available vertical area between header and footer
    footer_top_y = 960
    available_height = footer_top_y - current_y - 40
    
    # Try large sizes first (54px down to 44px) so text commands the screen
    quote_text = f'“{item["quote"]}”'
    chosen_font = None
    chosen_lines = []
    line_spacing = 20

    for test_size in [54, 50, 46, 42]:
        test_font = get_font("Arial.ttf", test_size)
        lines = wrap_text_pixels(quote_text, test_font, MAX_TEXT_WIDTH, draw)
        line_height = draw.textbbox((0, 0), "Ay", font=test_font)[3]
        total_text_h = len(lines) * (line_height + line_spacing)
        if total_text_h <= available_height or test_size == 42:
            chosen_font = test_font
            chosen_lines = lines
            break

    # Center the quote vertically in the remaining space
    line_h = draw.textbbox((0, 0), "Ay", font=chosen_font)[3]
    total_quote_h = len(chosen_lines) * (line_h + line_spacing)
    start_quote_y = current_y + (available_height - total_quote_h) // 2

    for line in chosen_lines:
        line_bbox = draw.textbbox((0, 0), line, font=chosen_font)
        line_w = line_bbox[2] - line_bbox[0]
        draw.text(((CANVAS_SIZE[0] - line_w) // 2, start_quote_y), line, fill=TEXT_COLOR, font=chosen_font)
        start_quote_y += line_h + line_spacing

    # 5. Footer URL (Pinned prominently at bottom)
    footer_text = "VanguardBIO.ai"
    f_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    f_w = f_bbox[2] - f_bbox[0]
    draw.text(((CANVAS_SIZE[0] - f_w) // 2, 970), footer_text, fill=TEXT_COLOR, font=font_footer)

    return canvas

@app.get("/")
def index():
    return {
        "service": "VanguardBIO Athena Ad Batch Generator",
        "total_reviews": len(REVIEWS),
        "preview_one": "/preview/1",
        "download_all_zip": "/generate-zip"
    }

@app.get("/preview/{review_num}")
def preview_single(review_num: int):
    review = next((r for r in REVIEWS if r["num"] == review_num), None)
    if not review:
        return Response(content="Review not found", status_code=404)
    img = render_ad_image(review)
    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(72, 72))
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/generate-zip")
def generate_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in REVIEWS:
            img = render_ad_image(item)
            img_io = io.BytesIO()
            img.save(img_io, format="PNG", dpi=(72, 72))
            img_io.seek(0)
            zf.writestr(f"Athena_ad_{item['num']:03d}.png", img_io.read())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=Athena_protocol_100_ads.zip"}
    )
