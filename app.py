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

# Complete achilles Protocol Review Dataset (1 to 129)
REVIEWS = [
    {
        "num": 1,
        "author": "Marcus T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Chronic shoulder impingement resolved in 4 weeks. I’ve dealt with rotator cuff inflammation for over three years. Adding the Achilles protocol took my joint mobility from restricted to full range of motion by week four. The HGH and TB-500 combination accelerated my tissue repair noticeably."
    },
    {
        "num": 2,
        "author": "Julian R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The Achilles Protocol completely transformed my recovery metrics. Sleep architecture improved dramatically within the first ten days, and my tendonitis flare-ups after heavy pulling sessions disappeared entirely. Seamless telehealth onboarding and professional-grade packaging."
    },
    {
        "num": 3,
        "author": "Dr. Ethan K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "As someone who evaluates protocols professionally, the precision of the peptide stack here is exceptional. Rapid muscle recovery and a noticeable drop in systemic inflammation markers by week six. Highly recommend for high-performance physical optimization."
    },
    {
        "num": 4,
        "author": "Damon W. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Remarkable body recomposition and accelerated healing from a lingering knee issue. The documentation and protocol clarity made self-administration straightforward. Noticeable gains in overall joint resilience and sustained daily energy."
    },
    {
        "num": 5,
        "author": "Lucas V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide combined with HGH is an absolute game-changer. Stripped stubborn visceral fat while packing on clean mass. DEXA scan at week 8 showed a massive shift in my body fat percentage."
    },
    {
        "num": 6,
        "author": "Brandon C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The inclusion of KPV cleared up digestive issues I've battled for years. Better nutrient absorption has directly improved my training output and daily vitality."
    },
    {
        "num": 7,
        "author": "Garrett M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 worked wonders on my chronic elbow pain. Back to pressing heavy without any nagging discomfort. The 503B pharmacy quality gives complete peace of mind."
    },
    {
        "num": 8,
        "author": "Spencer H. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Deep sleep quality skyrocketed in week one thanks to the HGH component. Waking up fully rested and ready to attack heavy compound lifts."
    },
    {
        "num": 9,
        "author": "Travis L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unreal metabolic shift. Retatrutide curbs appetite effortlessly while keeping energy levels completely stable throughout intense training blocks."
    },
    {
        "num": 10,
        "author": "Nate P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The entire onboarding and health expert review process was seamless. The Achilles stack is built for serious lifters who don't want to compromise."
    },
    {
        "num": 11,
        "author": "Derek B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Noticed a substantial reduction in systemic inflammation markers by week six. My joints feel lubricated and resilient even after brutal leg days."
    },
    {
        "num": 12,
        "author": "Kyle S. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Cleanest physical recomposition stack I've ever run. Lean mass went up while waistline dropped steadily month over month."
    },
    {
        "num": 13,
        "author": "Zachary M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional packaging, rapid delivery, and crystal-clear protocol documentation. VanguardBIO sets the gold standard for peptide therapeutics."
    },
    {
        "num": 14,
        "author": "Evan T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My recovery time between heavy squat sessions was cut in half. The synergistic effect of HGH and TB-500 is palpable."
    },
    {
        "num": 15,
        "author": "Logan K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health was always my bottleneck. KPV completely resolved my post-meal bloating and enhanced my overall nutrient partitioning."
    },
    {
        "num": 16,
        "author": "Caleb J. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Exceptional results on body fat loss. Retatrutide is lightyears ahead of older generation compounds."
    },
    {
        "num": 17,
        "author": "Tyler R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "At 46 years old, this protocol brought back my physical capacity from a decade ago. Energy, recovery, and body composition are all dialed in."
    },
    {
        "num": 18,
        "author": "Austin F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The third-party HPLC testing reports gave me total confidence before starting. Results on bloodwork and body composition have been stellar."
    },
    {
        "num": 19,
        "author": "Cole H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Zero joint creakiness left in my knees. TB-500 and HGH are an unstoppable recovery pairing for heavy athletes."
    },
    {
        "num": 20,
        "author": "Jared D. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "A bit of an investment, but the return on physical performance and body composition makes every dollar worth it."
    },
    {
        "num": 21,
        "author": "Blake W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The multi-vector approach of Achilles covers every base: growth, repair, gut health, and fat loss. Absolute masterclass in stack design."
    },
    {
        "num": 22,
        "author": "Sean M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Rapid delivery right to my doorstep and automated refills mean I never miss a dose. Fantastic customer support and clinical oversight."
    },
    {
        "num": 23,
        "author": "Trevor P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My IGF-1 levels moved right into the optimal anabolic window. Lean mass gains have been steady and clean."
    },
    {
        "num": 24,
        "author": "Brody L. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Noticeably faster healing on soft tissue niggles. I used to nurse pulled hamstrings for weeks; now turnaround time is minimal."
    },
    {
        "num": 25,
        "author": "Gavin N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide keeps cravings completely silent. Combined with HGH, my physique has leaned out dramatically without sacrificing strength."
    },
    {
        "num": 26,
        "author": "Seth B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV transformed my gut integrity. Digestion is smoother and my overall systemic inflammation plummeted."
    },
    {
        "num": 27,
        "author": "Chase V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The protocol documentation is thorough, professional, and easy to execute. High-tier service from VanguardBIO."
    },
    {
        "num": 28,
        "author": "Wyatt C. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Solid protocol for dedicated guys looking to bypass normal aging plateaus. Great results on my 60-day blood panel."
    },
    {
        "num": 29,
        "author": "Ryder K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Shoulder tendonitis that lingered for two years finally cleared up entirely. TB-500 is magic."
    },
    {
        "num": 30,
        "author": "Miles J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sleep scores on my wearable device jumped instantly. Deep sleep duration doubled within the first fortnight."
    },
    {
        "num": 31,
        "author": "Grant S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy compounding standard is evident from the first unboxing. Pure pharmaceutical grade excellence."
    },
    {
        "num": 32,
        "author": "Finn R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Incredible fat loss around the midsection while maintaining full strength on my deadlifts. Retatrutide is unmatched."
    },
    {
        "num": 33,
        "author": "Declan M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth consultation was quick, professional, and thorough. The expert tailored my titration schedule perfectly."
    },
    {
        "num": 34,
        "author": "Kade T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My recovery ceiling has doubled. I can train harder, more frequently, without hitting central nervous system burnout."
    },
    {
        "num": 35,
        "author": "Zane H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health, body fat reduction, and accelerated tendon repair all rolled into one cohesive protocol. Incredible formulation."
    },
    {
        "num": 36,
        "author": "Paxton W. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable drop in recovery downtime after heavy leg volume. Highly recommend to serious competitors."
    },
    {
        "num": 37,
        "author": "Reid B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The HGH component keeps skin texture tight and muscle fullness dialed in 24/7. Outstanding physical results."
    },
    {
        "num": 38,
        "author": "Spencer D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV solved my stubborn digestive inflammation. I feel lighter, leaner, and absorb nutrients far more efficiently."
    },
    {
        "num": 39,
        "author": "Knox L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide plus HGH is the ultimate body recomposition stack. Every single biohacking metric improved."
    },
    {
        "num": 40,
        "author": "Colt P. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Smooth onboarding process and rapid shipping. VanguardBIO delivers top-tier clinical grade compounds."
    },
    {
        "num": 41,
        "author": "Jett R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Elbow and knee inflammation completely mitigated. I'm lifting heavier at 42 than I did at 28."
    },
    {
        "num": 42,
        "author": "Rory S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The sleep enhancement alone makes the Achilles protocol worth every penny. Unbroken 8 hours every single night."
    },
    {
        "num": 43,
        "author": "Brooks K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral fat melted away while lean tissue stayed completely locked in. True clinical recomposition."
    },
    {
        "num": 44,
        "author": "Rhett M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Comprehensive documentation made execution foolproof. Great support team behind the scenes."
    },
    {
        "num": 45,
        "author": "Zander H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 healed my chronic Achilles tendinopathy. The stack lives up directly to its namesake."
    },
    {
        "num": 46,
        "author": "Dax W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Appetite suppression from Retatrutide is smooth, clean, and completely devoid of jittery side effects."
    },
    {
        "num": 47,
        "author": "Stetson B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut barrier function improved markedly. Bloating is entirely gone and training pumps are fuller."
    },
    {
        "num": 48,
        "author": "Diesel T. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Top-tier pharmaceutical quality. You can tell real clinical oversight went into formulating this stack."
    },
    {
        "num": 49,
        "author": "Maverick C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My recovery metrics across my fitness tracker have never looked this green. Outstanding stack."
    },
    {
        "num": 50,
        "author": "Cash V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The dual-vector recomposition effect of HGH and Retatrutide is unmatched by anything else on the market."
    },
    {
        "num": 51,
        "author": "Ridge F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Joint aches from heavy lifting vanished within three weeks. TB-500 is an absolute powerhouse."
    },
    {
        "num": 52,
        "author": "Flint D. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Clear instructions, fast delivery, and premium packaging. Highly satisfied with the Achilles Protocol."
    },
    {
        "num": 53,
        "author": "Boone L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sleep architecture and cognitive clarity both received massive boosts. Waking up dialed in every morning."
    },
    {
        "num": 54,
        "author": "Thad P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral adipose tissue dropped significantly on my latest scan. Retatrutide is a marvel of modern biotechnology."
    },
    {
        "num": 55,
        "author": "Briggs M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV sorted out my chronic gut inflammation. Digestion is effortless now."
    },
    {
        "num": 56,
        "author": "Hank R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Professional telehealth review and custom dosing guidance made getting started seamless."
    },
    {
        "num": 57,
        "author": "Wade S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Muscle fullness and vascularity increased noticeably while body fat peeled away effortlessly."
    },
    {
        "num": 58,
        "author": "Colter K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My nagging shoulder injury finally healed after months of stalled progress. TB-500 is incredible."
    },
    {
        "num": 59,
        "author": "Zeb H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep recovery scores reached an all-time high. HGH delivers exactly what it promises."
    },
    {
        "num": 60,
        "author": "Huck B. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Exceptional purity and professional service. VanguardBIO is heads above other suppliers."
    },
    {
        "num": 61,
        "author": "Gage W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide appetite regulation is clean and sustained. Zero energy crashes during grueling workouts."
    },
    {
        "num": 62,
        "author": "Zackary T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health optimization via KPV made my nutrient absorption skyrocket. Incredible physiological shift."
    },
    {
        "num": 63,
        "author": "Laramie N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The quarterly plan is well worth it. Consistent deliveries and unmatched physical results."
    },
    {
        "num": 64,
        "author": "Tag V. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Joint recovery speed is phenomenal. I can push high volume without paying for it the next day."
    },
    {
        "num": 65,
        "author": "Coleson J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH and Retatrutide working together is like cheating physics. Lean mass up, fat mass down."
    },
    {
        "num": 66,
        "author": "Stran P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Third-party COAs gave me total trust, and the actual results on my bloodwork confirmed every claim."
    },
    {
        "num": 67,
        "author": "Jent M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV cleared up my GI distress completely. Systemic inflammation markers dropped across the board."
    },
    {
        "num": 68,
        "author": "Crewe L. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Solid support team and fast shipping. Protocols are clearly laid out for easy self-administration."
    },
    {
        "num": 69,
        "author": "Slater H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Achilles protocol restored my connective tissue integrity after years of heavy powerlifting."
    },
    {
        "num": 70,
        "author": "Bodie K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sleep architecture is pristine. Waking up refreshed before my 5 AM training session every single day."
    },
    {
        "num": 71,
        "author": "Taggart R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral fat reduction was immediately apparent on my DEXA scans. Retatrutide is state-of-the-art."
    },
    {
        "num": 72,
        "author": "Bridger S. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Fantastic stack design. Combining repair, growth, and metabolism into one monthly order is brilliant."
    },
    {
        "num": 73,
        "author": "Colter D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "TB-500 fixed my nagging patellar tendinopathy. Full range of motion restored."
    },
    {
        "num": 74,
        "author": "Rigg M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation keeps my muscle fullness peaked and skin quality immaculate. Unbelievable compound."
    },
    {
        "num": 75,
        "author": "Onyx W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV healed my gut lining. Nutrient utilization feels noticeably more efficient."
    },
    {
        "num": 76,
        "author": "Pike V. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Professional consultation ensured my dosing was dialed right from day one. Great experience."
    },
    {
        "num": 77,
        "author": "Remington B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide suppresses cravings effortlessly while preserving full training intensity."
    },
    {
        "num": 78,
        "author": "Hays H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Recovery metrics across my Oura ring have never been higher. Deep sleep and REM sleep both doubled."
    },
    {
        "num": 79,
        "author": "Jovanny C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy compounding standard gives absolute confidence in product safety and purity."
    },
    {
        "num": 80,
        "author": "Mac K. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Phenomenal body recomposition results. Dropped 4% body fat while adding lean mass."
    },
    {
        "num": 81,
        "author": "Gideon T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Chronic elbow inflammation resolved completely. TB-500 is a mandatory addition for serious lifters."
    },
    {
        "num": 82,
        "author": "Thatcher R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health support via KPV eliminated my post-workout GI distress entirely."
    },
    {
        "num": 83,
        "author": "Sutter M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH and Retatrutide stack delivers jaw-dropping aesthetic and metabolic improvements."
    },
    {
        "num": 84,
        "author": "Calum S. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Fast shipping, pristine packaging, and clear documentation. Top-tier service."
    },
    {
        "num": 85,
        "author": "Knoxley D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My recovery time between heavy deadlift sessions is practically nonexistent now."
    },
    {
        "num": 86,
        "author": "Vance W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide is lightyears ahead of older GLP-1s. Zero fatigue, maximum fat loss."
    },
    {
        "num": 87,
        "author": "Damon H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth onboarding was seamless and professional. Health expert oversight is top quality."
    },
    {
        "num": 88,
        "author": "Corbin B. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Sleep quality and joint resilience improved dramatically within the first two weeks."
    },
    {
        "num": 89,
        "author": "Lawson V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Systemic inflammation markers dropped significantly on my quarterly bloodwork. Incomparable stack."
    },
    {
        "num": 90,
        "author": "Leopold P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Lean tissue retention while cutting body fat has never been easier. Brilliant protocol design."
    },
    {
        "num": 91,
        "author": "Abel K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV sorted out my gut permeability issues. Absorption and energy levels are through the roof."
    },
    {
        "num": 92,
        "author": "Soren M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "TB-500 healed my lingering rotator cuff strain faster than anything I've tried before."
    },
    {
        "num": 93,
        "author": "Orion R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH sleep benefits kicked in on night three. Deep sleep metrics doubled instantly."
    },
    {
        "num": 94,
        "author": "Stellan H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide appetite control is effortless. Visceral fat melted off my midsection."
    },
    {
        "num": 95,
        "author": "Magnus S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional 503B compounding standards give complete peace of mind. Outstanding results."
    },
    {
        "num": 96,
        "author": "Evander W. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Recovery ceiling is doubled. I'm training with intensity I haven't seen in a decade."
    },
    {
        "num": 97,
        "author": "Alaric C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The quarterly plan is seamless. Automatic refills arrive right on schedule."
    },
    {
        "num": 98,
        "author": "Dorian B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Joint mobility in my knees and shoulders is fully restored. TB-500 is essential."
    },
    {
        "num": 99,
        "author": "Ambrose K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health and nutrient partitioning improved dramatically thanks to KPV."
    },
    {
        "num": 100,
        "author": "Lysander M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Exceptional body recomposition stack. Lean mass up, fat mass down cleanly."
    },
    {
        "num": 101,
        "author": "Caspian T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide and HGH synergy is unmatched. DEXA scans confirm elite visceral fat loss."
    },
    {
        "num": 102,
        "author": "Thane R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth consultation was thorough and expert-led. Protocol guidance is crystal clear."
    },
    {
        "num": 103,
        "author": "Viggo S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sleep architecture and recovery metrics reached all-time personal bests."
    },
    {
        "num": 104,
        "author": "Leif H. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Nagging connective tissue issues vanished by week four. Incredible healing protocol."
    },
    {
        "num": 105,
        "author": "Ronan W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Systemic inflammation plummeted. My joints feel bulletproof during heavy sessions."
    },
    {
        "num": 106,
        "author": "Torin B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV solved my chronic gut inflammation. Digestion is smooth and effortless."
    },
    {
        "num": 107,
        "author": "Stellan M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy quality is evident in every single injection. Flawless purity."
    },
    {
        "num": 108,
        "author": "Kian C. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Appetite suppression is smooth and sustained. Retatrutide is lightyears ahead."
    },
    {
        "num": 109,
        "author": "Idris K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation keeps muscle fullness dialed in 24/7. Outstanding physical results."
    },
    {
        "num": 110,
        "author": "Eoghan V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Recovery time between heavy leg days cut in half. TB-500 is a miracle worker."
    },
    {
        "num": 111,
        "author": "Cillian R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral fat melted away while lean tissue stayed completely intact. True recomposition."
    },
    {
        "num": 112,
        "author": "Tadhg P. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Comprehensive documentation made execution foolproof. Great support team."
    },
    {
        "num": 113,
        "author": "Fionn M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep duration doubled in week one. Waking up fully restored every single morning."
    },
    {
        "num": 114,
        "author": "Darragh S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health optimization via KPV made my nutrient absorption skyrocket."
    },
    {
        "num": 115,
        "author": "Oisin H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Third-party HPLC testing reports gave me total confidence. Results on bloodwork confirmed it."
    },
    {
        "num": 116,
        "author": "Cormac B. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Solid protocol for dedicated guys looking to bypass normal aging plateaus."
    },
    {
        "num": 117,
        "author": "Declan W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Shoulder tendonitis that lingered for two years finally cleared up entirely."
    },
    {
        "num": 118,
        "author": "Ronan K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide keeps cravings completely silent while maintaining full training power."
    },
    {
        "num": 119,
        "author": "Bane V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional telehealth consultation and custom dosing guidance made getting started seamless."
    },
    {
        "num": 120,
        "author": "Alistair T. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Recovery metrics across my wearable device have never looked this green."
    },
    {
        "num": 121,
        "author": "Lachlan R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The dual-vector recomposition effect of HGH and Retatrutide is unmatched."
    },
    {
        "num": 122,
        "author": "Maddox S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Joint aches from heavy lifting vanished within three weeks. TB-500 is incredible."
    },
    {
        "num": 123,
        "author": "Zayn H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clear instructions, fast delivery, and premium packaging. Highly satisfied."
    },
    {
        "num": 124,
        "author": "Kyson B. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Sleep architecture and cognitive clarity both received massive boosts."
    },
    {
        "num": 125,
        "author": "Ryker M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral adipose tissue dropped significantly on my latest scan. Retatrutide is elite."
    },
    {
        "num": 126,
        "author": "Zion W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV sorted out my chronic gut inflammation. Digestion is effortless now."
    },
    {
        "num": 127,
        "author": "Koa K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional telehealth review and custom dosing guidance made execution smooth."
    },
    {
        "num": 128,
        "author": "Orson V. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Muscle fullness and vascularity increased noticeably while body fat peeled away."
    },
    {
        "num": 129,
        "author": "Sterling T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My nagging shoulder injury finally healed after months of stalled progress."
    },
    {
        "num": 130,
        "author": "Atlas R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep sleep recovery scores reached an all-time high. HGH delivers."
    },
    {
        "num": 131,
        "author": "Remi B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Exceptional purity and professional service. VanguardBIO is heads above the rest."
    },
    {
        "num": 132,
        "author": "Soren H. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Retatrutide appetite regulation is clean and sustained. Zero energy crashes."
    },
    {
        "num": 133,
        "author": "Titan S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut health optimization via KPV made my nutrient absorption skyrocket."
    },
    {
        "num": 134,
        "author": "Zephyr M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The quarterly plan is well worth it. Consistent deliveries and stellar results."
    },
    {
        "num": 135,
        "author": "Orion W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Joint recovery speed is phenomenal. I can push high volume without paying for it."
    },
    {
        "num": 136,
        "author": "Cyrus K. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "HGH and Retatrutide working together is like cheating physics. Lean mass up."
    },
    {
        "num": 137,
        "author": "Darius V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Third-party COAs gave me total trust, and bloodwork confirmed every claim."
    },
    {
        "num": 138,
        "author": "Cassian B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV cleared up my GI distress completely. Systemic inflammation markers dropped."
    },
    {
        "num": 139,
        "author": "Leander T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Solid support team and fast shipping. Protocols are clearly laid out."
    },
    {
        "num": 140,
        "author": "Evander R. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Achilles protocol restored my connective tissue integrity after years of heavy lifting."
    },
    {
        "num": 141,
        "author": "Perseus M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sleep architecture is pristine. Waking up refreshed before my early workouts."
    },
    {
        "num": 142,
        "author": "Theseus H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral fat reduction was immediately apparent on DEXA. Retatrutide is state-of-the-art."
    },
    {
        "num": 143,
        "author": "Leonidas W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Fantastic stack design. Combining repair, growth, and metabolism is brilliant."
    },
    {
        "num": 144,
        "author": "Orpheus S. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "TB-500 fixed my nagging patellar tendinopathy. Full range of motion restored."
    },
    {
        "num": 145,
        "author": "Valerius K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "HGH elevation keeps muscle fullness peaked and skin quality immaculate."
    },
    {
        "num": 146,
        "author": "Tiberius B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "KPV healed my gut lining. Nutrient utilization feels noticeably more efficient."
    },
    {
        "num": 147,
        "author": "Maximus V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional consultation ensured my dosing was dialed right from day one."
    },
    {
        "num": 148,
        "author": "Aurelius T. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Retatrutide suppresses cravings effortlessly while preserving full training intensity."
    },
    {
        "num": 149,
        "author": "Magnus R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Recovery metrics across my Oura ring have never been higher. Deep sleep doubled."
    },
    {
        "num": 150,
        "author": "Severin H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The 503B pharmacy compounding standard gives absolute confidence in product safety."
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
        "service": "VanguardBIO achilles Ad Batch Generator",
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
            zf.writestr(f"achilles_ad_{item['num']:03d}.png", img_io.read())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=achilles_protocol_100_ads.zip"}
    )
