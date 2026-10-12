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

# Complete Apollo Protocol Review Dataset (1 to 100)
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
    {
        "num": 4,
        "author": "Kevin P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "I’ve been running the Apollo stack for three months now. My systemic inflammation markers (hsCRP) dropped dramatically on my latest blood panel. VanguardBIO delivers clinical-grade excellence right to your door.",
    },
    {
        "num": 5,
        "author": "Danielle M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unreal results. The combination of MOTS-c for metabolic longevity and Glutathione for cellular detoxification gives you a clean, sustained vitality that you can feel every single day. Exceptional formulation.",
    },
    {
        "num": 6,
        "author": "Thomas W. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Solid 4.9. The recovery speed of connective tissue paired with the gut-immune reset made this protocol worth every penny. My digestion handles any meal effortlessly now, and daily brain fog is completely gone.",
    },
    {
        "num": 7,
        "author": "Rachel K. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "The ultimate longevity and gut health foundation. The step-by-step PDF protocol and video walkthrough made getting started completely stress-free. Refills arrive like clockwork.",
    },
    {
        "num": 8,
        "author": "Michael B. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "An exceptionally well-thought-out stack. Thymosin Alpha-1 and KPV work in tandem to create an impenetrable shield against daily stressors and immune fatigue. Highly recommend.",
    },
    {
        "num": 9,
        "author": "Jennifer S. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Six powerful compounds working in total synergy. My gut permeability markers have normalized, and my overall physical resilience has reached an entirely new tier.",
    },
    {
        "num": 10,
        "author": "David C. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Flawless execution from VanguardBIO. The 503B purity testing and transparent quality control give me complete confidence in what I'm putting into my body.",
    },
    {
        "num": 11,
        "author": "Brian T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "If you want to optimize your biological baseline, the Apollo Protocol is the gold standard. The cellular repair and gut restoration in weeks 1 through 4 were immediately noticeable.",
    },
    {
        "num": 12,
        "author": "Amanda G. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Five stars. The quality of the packaging, the speed of delivery, and the sheer effectiveness of the KPV and BPC-157 gut-healing matrix are peerless.",
    },
    {
        "num": 13,
        "author": "Eric J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My gut health was the missing link in my performance regimen. Apollo solved it completely. Digestion is smooth, inflammation is down, and daily stamina is through the roof.",
    },
    {
        "num": 14,
        "author": "Jessica F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The inclusion of MOTS-c and Glutathione provides unmatched metabolic and antioxidant support. I feel younger, sharper, and deeply restored.",
    },
    {
        "num": 15,
        "author": "Ryan D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clean energy, pristine digestion, and elite immune support. VanguardBIO delivers white-glove wellness protocol management.",
    },
    {
        "num": 16,
        "author": "Nicholas V. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "4.8 stars because dialing in a six-compound daily routine took a few days to memorize, but the health benefits make it entirely worth it. My longevity biomarkers have never looked better.",
    },
    {
        "num": 17,
        "author": "Megan T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Stunning results by month two. Joint recovery is faster, gut irritation is non-existent, and my overall vitality feels completely rebooted.",
    },
    {
        "num": 18,
        "author": "Justin R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Solid formulation backed by serious science. The combination of Thymosin Alpha-1 and TB-500 is an absolute powerhouse for immune and tissue repair.",
    },
    {
        "num": 19,
        "author": "Kimberly N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Very impressed with the medical oversight and individual health expert consultation. The shipments arrive pristine and cold-packed every single month.",
    },
    {
        "num": 20,
        "author": "Tyler K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The ultimate longevity stack. From gut restoration to cellular mitochondrial support via MOTS-c, every vector performs exactly as promised.",
    },
    {
        "num": 21,
        "author": "Jordan E. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Absolute perfection. Pairing master antioxidants with targeted gut-healing peptides has completely transformed my daily wellness and recovery.",
    },
    {
        "num": 22,
        "author": "Stephanie C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Five stars! My digestion is harmonious, my immune system is robust, and my energy is steady all day long. Worth every dollar.",
    },
    {
        "num": 23,
        "author": "Brandon Z. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "VanguardBIO’s Apollo Protocol is revolutionary. The gut-immune-longevity triad is the smartest approach to health optimization on the market.",
    },
    {
        "num": 24,
        "author": "Heather B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Noticeably reduced systemic inflammation and vastly improved gut tolerance. Highly recommend to anyone seeking deep biological restoration.",
    },
    {
        "num": 25,
        "author": "Christopher M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional guidance, immaculate pharmacy-grade quality, and phenomenal health outcomes. Couldn't ask for a better protocol.",
    },
    {
        "num": 26,
        "author": "Sean V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Total gut and immune reboot. Worth every penny.",
    },
    {
        "num": 27,
        "author": "Melissa W. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Exceptional tissue repair and digestive comfort.",
    },
    {
        "num": 28,
        "author": "Patrick Y. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The KPV and BPC-157 combination is a lifesaver for gut health.",
    },
    {
        "num": 29,
        "author": "Ashley Z. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Immune resilience and daily energy have never been higher.",
    },
    {
        "num": 30,
        "author": "Jason B. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Great protocol, fantastic customer support.",
    },
    {
        "num": 31,
        "author": "Laura C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "MOTS-c repletion cleared my fatigue and boosted metabolic stamina.",
    },
    {
        "num": 32,
        "author": "Timothy D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Pristine 503B pharmacy quality. Highly professional.",
    },
    {
        "num": 33,
        "author": "Gregory E. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Best longevity investment on the market today.",
    },
    {
        "num": 34,
        "author": "Crystal F. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Noticeable reduction in joint stiffness and gut bloating.",
    },
    {
        "num": 35,
        "author": "Steven G. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Transformed my digestive health and vitality in 8 weeks.",
    },
    {
        "num": 36,
        "author": "Karen H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The monthly auto-refill is seamless and reliable.",
    },
    {
        "num": 37,
        "author": "Adam J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Incredible sleep architecture and immune stability.",
    },
    {
        "num": 38,
        "author": "Natalie K. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Solid 4.8. Impeccable packaging and fast delivery.",
    },
    {
        "num": 39,
        "author": "Scott L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Thymosin Alpha-1 provides elite immune defense.",
    },
    {
        "num": 40,
        "author": "Rebecca M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My physician was impressed by my improved inflammatory markers.",
    },
    {
        "num": 41,
        "author": "Mark N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Visceral reduction in oxidative stress. Brilliant stack.",
    },
    {
        "num": 42,
        "author": "Paul P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Pharmacy-grade purity you can genuinely trust.",
    },
    {
        "num": 43,
        "author": "Erin R. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Fantastic results for gut integrity and overall wellness.",
    },
    {
        "num": 44,
        "author": "Dana S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cellular recovery and mucosal repair speed are remarkable.",
    },
    {
        "num": 45,
        "author": "Jonathan T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clear instructions and wonderful expert consultation.",
    },
    {
        "num": 46,
        "author": "Kelly V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Effortless digestive comfort and vibrant daily energy.",
    },
    {
        "num": 47,
        "author": "Travis W. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Very satisfied with the comprehensive formula.",
    },
    {
        "num": 48,
        "author": "Angela Y. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Multi-vector gut and longevity optimization at its finest.",
    },
    {
        "num": 49,
        "author": "Brett Z. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Superior energy, immune defense, and gut resilience.",
    },
    {
        "num": 50,
        "author": "Haley A. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cleanest longevity peptide protocol available.",
    },
    {
        "num": 51,
        "author": "Trevor B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Blood panels proved the dramatic drop in systemic inflammation.",
    },
    {
        "num": 52,
        "author": "Courtney C. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Exceptional customer support and prompt 3-day shipping.",
    },
    {
        "num": 53,
        "author": "Kyle D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Gut feels completely healed and deeply nourished.",
    },
    {
        "num": 54,
        "author": "Whitney E. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The Apollo Protocol is worth every dollar.",
    },
    {
        "num": 55,
        "author": "Zachary F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unbelievable stamina and digestive ease.",
    },
    {
        "num": 56,
        "author": "Allison G. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Top-grade compounds and expert medical oversight.",
    },
    {
        "num": 57,
        "author": "Bradley H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Transformed my body's resilience against stress.",
    },
    {
        "num": 58,
        "author": "Chelsea J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Oxidative stress is gone. Gut clarity is unmatched.",
    },
    {
        "num": 59,
        "author": "Austin K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "MOTS-c and Glutathione are an unbeatable metabolic duo.",
    },
    {
        "num": 60,
        "author": "Shelby L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Delivers deep, restorative cellular repair day after day.",
    },
    {
        "num": 61,
        "author": "Garrett M. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Solid protocol with clear, actionable documentation.",
    },
    {
        "num": 62,
        "author": "Marissa N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Elite gut, immune, and longevity stack.",
    },
    {
        "num": 63,
        "author": "Logan P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Eliminated chronic gut sensitivity completely.",
    },
    {
        "num": 64,
        "author": "Paige R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional medical consultation gave me complete confidence.",
    },
    {
        "num": 65,
        "author": "Dillon S. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Great product, premium presentation.",
    },
    {
        "num": 66,
        "author": "Cassidy T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The gold standard for modern biological optimization.",
    },
    {
        "num": 67,
        "author": "Cole V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cellular renewal speed is phenomenal on this stack.",
    },
    {
        "num": 68,
        "author": "Sydney W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unreal results in just 8 weeks of administration.",
    },
    {
        "num": 69,
        "author": "Hunter Y. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Digestive discomfort softened and disappeared entirely.",
    },
    {
        "num": 70,
        "author": "Morgan Z. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cleanest pharmacy-grade ingredients on the market.",
    },
    {
        "num": 71,
        "author": "Luke A. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Outstanding formulation and white-glove support.",
    },
    {
        "num": 72,
        "author": "Rachel B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My immune defense hit a brand new peak.",
    },
    {
        "num": 73,
        "author": "Zane C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The TB-500 and BPC-157 combo is magical for tissue repair.",
    },
    {
        "num": 74,
        "author": "Vanessa D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Seamless auto-refill and lightning-fast delivery.",
    },
    {
        "num": 75,
        "author": "Seth E. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Exceeded all expectations across every health metric.",
    },
    {
        "num": 76,
        "author": "Chloe F. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Very impressed with the detailed clinical research dossiers.",
    },
    {
        "num": 77,
        "author": "Ian G. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unrivaled gut restoration and immune-modulating power.",
    },
    {
        "num": 78,
        "author": "Maya H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My daily energy and digestive comfort are through the roof.",
    },
    {
        "num": 79,
        "author": "Connor J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Glutathione and KPV levels optimized; body feels pristine.",
    },
    {
        "num": 80,
        "author": "Paige K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Absolute 5/5 stars. Continuing my subscription indefinitely.",
    },
    {
        "num": 81,
        "author": "Wyatt L. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "Brilliant synchronization of six powerful longevity vectors.",
    },
    {
        "num": 82,
        "author": "Skylar M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Slept better and recovered faster than ever before.",
    },
    {
        "num": 83,
        "author": "Nolan N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Top-tier execution and quality control by VanguardBIO.",
    },
    {
        "num": 84,
        "author": "Hailey P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Mitochondrial energy and gut resilience are phenomenal.",
    },
    {
        "num": 85,
        "author": "Garrett R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Professional, reliable, and exceptionally effective.",
    },
    {
        "num": 86,
        "author": "Brooke S. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Great stack, excellent digestive results.",
    },
    {
        "num": 87,
        "author": "Carter T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The ultimate protocol for foundational health and longevity.",
    },
    {
        "num": 88,
        "author": "Delaney V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Incredible vitality and reduced systemic inflammation.",
    },
    {
        "num": 89,
        "author": "Mason W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "No side effects, just steady, thriving biological progress.",
    },
    {
        "num": 90,
        "author": "Trinity Y. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The pre-enrollment consultation was thorough and reassuring.",
    },
    {
        "num": 91,
        "author": "Gavin Z. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Transformed my internal health and physical energy completely.",
    },
    {
        "num": 92,
        "author": "Zoe A. — Verified Buyer",
        "rating": "★★★★★ (4.9 / 5)",
        "quote": "High-grade 503B sourcing makes all the difference.",
    },
    {
        "num": 93,
        "author": "Reid B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unbeatable synergy between KPV, BPC-157, and MOTS-c.",
    },
    {
        "num": 94,
        "author": "Kennedy C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cellular turnover and gut repair are rapid and complete.",
    },
    {
        "num": 95,
        "author": "Spencer D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Purity and potency are 100% verified and reliable.",
    },
    {
        "num": 96,
        "author": "Sadie E. — Verified Buyer",
        "rating": "★★★★★ (4.8 / 5)",
        "quote": "Solid 4.8 stars. Exceptional health-span boost.",
    },
    {
        "num": 97,
        "author": "Parker F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clear instructions and incredible systemic outcomes.",
    },
    {
        "num": 98,
        "author": "Delaney G. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Best investment in foundational health I've ever made.",
    },
    {
        "num": 99,
        "author": "Graham H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Elite formulation. Highly recommend to anyone serious about longevity.",
    },
    {
        "num": 100,
        "author": "Reese J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Flawless protocol from start to finish. 5/5 stars.",
    },
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
        "service": "VanguardBIO Apollo Ad Batch Generator",
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
            zf.writestr(f"apollo_ad_{item['num']:03d}.png", img_io.read())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=apollo_protocol_100_ads.zip"}
    )
