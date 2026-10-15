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

# Complete Zeus Protocol Review Dataset (1 to 129)
REVIEWS = [
    {
        "num": 1,
        "author": "Marcus T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Chronic shoulder impingement resolved in 4 weeks. I’ve dealt with rotator cuff inflammation for over three years. Adding the Zeus protocol took my joint mobility from restricted to full range of motion by week four. The BPC-157 and TB-500 combination accelerated my tissue repair noticeably.",
    },
    {
        "num": 2,
        "author": "David K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Knees feel twenty years younger. Heavy squatting used to require two days of ice and NSAIDs. By week three on Zeus, systemic inflammation was practically gone. Tendon-to-bone recovery is legitimately on another level.",
    },
    {
        "num": 3,
        "author": "Elena R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Exceptional soft tissue healing. Tore a hamstring grade-1 during sprint work. My physical therapist was shocked at how rapidly the scar tissue smoothed out and tensile strength returned. High-purity compounds make a massive difference.",
    },
    {
        "num": 4,
        "author": "Brett W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Post-op recovery accelerator. Used Zeus post-meniscectomy under physician guidance. Swelling dropped faster than expected, and my tissue healing metrics outpaced normal rehabilitation timelines by at least 40%.",
    },
    {
        "num": 5,
        "author": "Garrett H. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Remarkable elbow tendonitis relief. Golfer’s elbow had plagued my pull days for months. After 21 days of daily BPC administration inside the protocol, the chronic ache completely vanished.",
    },
    {
        "num": 6,
        "author": "Samantha L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Crossfit recovery cheat code. High-volume training days no longer leave me crippled the following morning. My recovery delta between workouts has halved. Sourcing from a 503B facility gives total peace of mind.",
    },
    {
        "num": 7,
        "author": "Jason P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Achilles stiffness is completely gone. Morning heel pain and stiffness used to take 20 minutes of stretching to clear. Within two weeks of starting Zeus, my Achilles felt pliable and completely pain-free.",
    },
    {
        "num": 8,
        "author": "Christopher N. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Connective tissue support that works. I powerlift in the Masters division. The tissue remodeling from TB-500 combined with HGH has kept my pecs and bicep tendons completely resilient during peaking blocks.",
    },
    {
        "num": 9,
        "author": "Tyler B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "CRP markers dropped dramatically. My baseline high-sensitivity CRP dropped from 2.8 down to 0.6 on my 8-week lab draw. The systemic anti-inflammatory effect is measurable and undeniable.",
    },
    {
        "num": 10,
        "author": "Rachel M. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Faster muscle tear regeneration. Had a lingering calf strain that kept re-aggravating. The cellular recovery stack stabilized the area within two weeks, letting me return to full road running.",
    },
    {
        "num": 11,
        "author": "Nicholas S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "BJJ joint wear-and-tear solved. Grappling three nights a week destroys fingers, neck, and lower back. Zeus keeps the inflammation suppressed and joint fluid healthy. I wake up ready to roll.",
    },
    {
        "num": 12,
        "author": "Sean D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Ligament stability is back. Sprained my ankle badly on a trail run. The repair rate with TB-500 and BPC-157 was easily double any healing timeline I've experienced in the past.",
    },
    {
        "num": 13,
        "author": "Victor M. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Mobility index improved noticeably. Hip capsule stiffness was limiting my depth on squats. By week five, my internal rotation and hip mobility showed significant measurable improvement.",
    },
    {
        "num": 14,
        "author": "Anthony C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Lab-verified purity shows in results. I've tried research peptides from generic grey-market vendors before with zero results. VanguardBIO’s 503B pharmacy grade products are an entirely different caliber.",
    },
    {
        "num": 15,
        "author": "Lucas G. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Back spasm recovery time collapsed. Lumbar facet joint irritation used to lay me out for a week. On Zeus, localized muscular tension dissipated within 48 hours.",
    },
    {
        "num": 16,
        "author": "Daniel O. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Connective tissue density feels upgraded. Wrist pain from heavy pressing used to require wrist wraps. Now pressing bare-wristed with zero discomfort. The collagen synthesis signal is real.",
    },
    {
        "num": 17,
        "author": "Eric H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "No more morning joint creaks. Getting out of bed used to sound like bubble wrap. Week four was the tipping point—joints move effortlessly and fluidly with zero morning friction.",
    },
    {
        "num": 18,
        "author": "Travis K. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Rapid micro-tear recovery. Eccentric training blocks usually induce DOMS that last four days. On Zeus, soreness clears out completely within 24 to 36 hours.",
    },
    {
        "num": 19,
        "author": "Kyle F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Tendinopathy cleared up. Patellar tendinopathy made descending stairs painful. The tissue repair velocity of the BPC/TB duo took care of it by week six.",
    },
    {
        "num": 20,
        "author": "Jordan E. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Surgical scar tissue softened. TB-500’s actin-sequestering action noticeably reduced fibrous tension around an old surgical site on my knee. Mobility is vastly smoother.",
    },
    {
        "num": 21,
        "author": "Brandon Y. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Fast track back to training. Kept tweaking my hamstring during track intervals. Zeus stopped the cycle of recurrent micro-tears. Best recovery investment I've made.",
    },
    {
        "num": 22,
        "author": "Craig V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Systemic inflammation wiped out. Felt the systemic decline in chronic stiffness across my spine and hands within ten days. Everything just moves with less mechanical resistance.",
    },
    {
        "num": 23,
        "author": "Phil G. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "BPC-157 gastric and joint benefits. Not only did my shoulder heal, but mild reflux and gut sensitivities also disappeared. The systemic gut-joint axis benefits are tangible.",
    },
    {
        "num": 24,
        "author": "Trevor N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Exceptional cellular turnaround. At 46, recovery was taking too long. This protocol restored my ability to train hard on back-to-back days without cumulative fatigue.",
    },
    {
        "num": 25,
        "author": "Austin D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Immediate reduction in soft tissue soreness. The cellular recovery vector alone justifies the monthly cost. My joints haven't felt this resilient since my early twenties.",
    },
    {
        "num": 26,
        "author": "Arthur P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Laser executive focus without caffeine jitters. Semax and Selank together are unbelievable. I manage private equity portfolios, and my ability to synthesize balance sheets under pressure with zero anxiety is unmatched.",
    },
    {
        "num": 27,
        "author": "Julian S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "High-stakes composure is next level. Selank acts like a cognitive shock absorber. During board meetings and critical negotiations, my speech latency and stress response are completely dialed.",
    },
    {
        "num": 28,
        "author": "Dominic R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Working memory and BDNF boost. Noticeable improvement in short-term recall and contextual memory retention. Reading dense technical documents feels frictionless.",
    },
    {
        "num": 29,
        "author": "Mitchell B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Crisp mental endurance through 14-hour days. Usually by 3 PM I experience heavy cognitive fatigue. With the morning Semax/Selank routine, my focus remains sharp and steady straight through dinner.",
    },
    {
        "num": 30,
        "author": "Siddharth N. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Calms the nervous system without sedation. Selank’s GABAergic modulation removes the background static of anxiety without dulling my edge. You remain calm, assertive, and hyper-focused.",
    },
    {
        "num": 31,
        "author": "Warren C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Flow state on command. As a software architect, coding complex distributed systems requires deep flow. Semax puts me in that zone within 30 minutes of dosing.",
    },
    {
        "num": 32,
        "author": "Grant K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Speech fluency and verbal recall. Found myself recalling vocabulary, names, and metrics during presentations without the usual micro-hesitations. Executive function is noticeably elevated.",
    },
    {
        "num": 33,
        "author": "Leon M. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Eliminated brain fog completely. Mid-morning brain fog has vanished. My mental bandwidth and ability to handle multi-threaded operational problems feels upgraded.",
    },
    {
        "num": 34,
        "author": "Harrison F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cortisol mitigation under stress. High-stress deadlines used to spike my heart rate and cause paralysis by analysis. The protocol keeps my physiology completely level-headed.",
    },
    {
        "num": 35,
        "author": "Vincent T. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Clean cognitive performance. No crash, no racing pulse, no appetite destruction like commercial stimulants. Just crystal-clear executive decision-making all day.",
    },
    {
        "num": 36,
        "author": "Gabriel W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Deep work capacity unlocked. My deep work hours logged per week doubled from 15 to 30. The mental stamina provided by the peptide pairing is remarkable.",
    },
    {
        "num": 37,
        "author": "Russell H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Neuroprotective and nootropic synergy. The clinical synergy between BDNF upregulation and anxiolytic modulation is evident. It's the most effective nootropic stack I've ever experienced.",
    },
    {
        "num": 38,
        "author": "Eliot J. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Decision fatigue is gone. By evening, I used to have zero bandwidth left for personal decisions. Now my cognitive battery still has 40% left at 8 PM.",
    },
    {
        "num": 39,
        "author": "Cole S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unshakable emotional regulation. Managing enterprise disputes requires patience. Selank completely flattens volatile emotional spikes under stress.",
    },
    {
        "num": 40,
        "author": "Patrick D. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Rapid task switching. Going from engineering reviews to legal contracts used to drain me. Context-switching latency is almost imperceptible now.",
    },
    {
        "num": 41,
        "author": "Nolan A. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Cognitive processing speed is up. Complex numerical calculations and mental modeling feel faster. Processing speed and visual data intake have noticeably accelerated.",
    },
    {
        "num": 42,
        "author": "Damian V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sharp morning transition. I used to take an hour and three espressos to boot up. The Zeus morning sequence has me fully operational in under ten minutes.",
    },
    {
        "num": 43,
        "author": "Stuart L. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Elevated mental acuity. The signal-to-noise ratio in strategic planning sessions has dramatically improved. My thinking feels streamlined and direct.",
    },
    {
        "num": 44,
        "author": "Bryce K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Subtle, non-stimulant brilliance. It doesn’t feel like caffeine or amphetamines. It feels like your baseline intelligence and emotional balance have simply been optimized.",
    },
    {
        "num": 45,
        "author": "Geoffrey R. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Excellent stress resilience. Handled a major regulatory audit with zero panic. My heart rate stayed low and strategic clarity stayed pristine.",
    },
    {
        "num": 46,
        "author": "Felix P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sustained attention span. Can sit through four-hour strategic review sessions without my mind wandering once. Focus and working memory are top tier.",
    },
    {
        "num": 47,
        "author": "Zachary U. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unlocked complex problem-solving. Felt an immediate boost in synthesizing disparate technical concepts. Semax’s BDNF action is tangible in complex analytical tasks.",
    },
    {
        "num": 48,
        "author": "Christian G. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Calm executive presence. Colleagues noted how composed and direct my communication became under intense pressure. Selank delivers on its promise.",
    },
    {
        "num": 49,
        "author": "Marshall B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clear thinking, zero afternoon slump. Cut my daily caffeine intake in half. The natural neurotransmitter support keeps alertness perfectly consistent.",
    },
    {
        "num": 50,
        "author": "Ian Q. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The gold standard for cognitive protocols. Having Semax and Selank sequenced with physical recovery peptides creates a total mind-body equilibrium that is hard to describe until you feel it.",
    },
    {
        "num": 51,
        "author": "Nathaniel K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Retatrutide melted visceral fat. The triple agonist mechanism of Retatrutide is unreal. Dropped 14 lbs of stubborn visceral fat in 8 weeks while maintaining all lean muscle mass.",
    },
    {
        "num": 52,
        "author": "Ross M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Stage 4 deep sleep doubled. According to my Whoop and Oura data, slow-wave deep sleep went from 42 minutes to 1 hour and 38 minutes average. Wake up feeling genuinely restored.",
    },
    {
        "num": 53,
        "author": "Derek F. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Appetite suppression without nausea. Unlike older GLP-1s that caused constant stomach upset, Retatrutide titration was smooth. Appetite noise is silenced, and metabolic rate feels elevated.",
    },
    {
        "num": 54,
        "author": "Aaron Z. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Exogenous HGH delivers real pumps and fullness. Muscles stay dense, hydrated, and full around the clock. The direct somatropin pulse bypasses pituitary fatigue completely.",
    },
    {
        "num": 55,
        "author": "Clint W. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Fasting insulin and HOMA-IR plummeted. My fasting glucose stabilized at 84 mg/dL and fasting insulin dropped from 12 to 4.2. Insulin sensitivity and metabolic flexibility are night and day.",
    },
    {
        "num": 56,
        "author": "Simon J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Skin elasticity and body recomposition. At 49, my skin tightness improved, vascularity returned across my arms and abdomen, and waist size dropped two inches in six weeks.",
    },
    {
        "num": 57,
        "author": "Braden S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Unbelievable body recomposition. In two months: lost 4.5% body fat and gained 3 pounds of lean tissue on DEXA scan. Retatrutide plus HGH creates the ultimate partitioning agent.",
    },
    {
        "num": 58,
        "author": "Kurt D. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Zero food cravings. Late-night snacking impulses were completely extinguished. I eat my planned protein and clean carbs and have zero obsessive thoughts about sugar.",
    },
    {
        "num": 59,
        "author": "Luke T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "IGF-1 in optimal high-performance range. My baseline IGF-1 was 135 ng/mL. Retested at week 8 and hit 260 ng/mL. Recovery, skin quality, and workout pumps reflect the numbers.",
    },
    {
        "num": 60,
        "author": "Dennis E. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Lipolysis you can visibly track. The glucagon receptor activation in Retatrutide genuinely increases calorie burn. Watched my lower abdominal fat fold shrink week after week.",
    },
    {
        "num": 61,
        "author": "Maxwell H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Sleep score consistently over 90. Deep REM and slow-wave sleep scores have never been this consistent. Pre-bed HGH administration dramatically improved my sleep architecture.",
    },
    {
        "num": 62,
        "author": "Trevor P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Lean mass retention in a caloric deficit. Ran a 600-calorie deficit for 8 weeks. Kept every ounce of bench press and squat strength thanks to the anabolic signaling of HGH.",
    },
    {
        "num": 63,
        "author": "Chad M. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Energy levels on Retatrutide remain high. Previous GLP-1 agonists caused lethargy. Retatrutide’s glucagon component preserves thermogenesis and daytime energy. Training output never dipped.",
    },
    {
        "num": 64,
        "author": "Gavin L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Vascularity and definition emerged. Veins across my shoulders and calves that I haven't seen in a decade showed up by week six. Fat loss has been rapid and steady.",
    },
    {
        "num": 65,
        "author": "Joel R. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Flawless titration guide. The titration schedule for Retatrutide from 2 mg upwards prevented all gastrointestinal discomfort. Telehealth medical team guided me step-by-step.",
    },
    {
        "num": 66,
        "author": "Shane O. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Restful sleep and waking readiness. Wake up feeling like an electric battery fully charged. No grogginess, no lingering fatigue, just immediate physical readiness.",
    },
    {
        "num": 67,
        "author": "Peter V. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Dropped 3 pant sizes while building delts. The body composition delta is crazy. My waist went from 36 down to 33, while my shoulders and traps filled out significantly.",
    },
    {
        "num": 68,
        "author": "Corey B. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Satiety signaling calibrated perfectly. Portion control is effortless. I feel fully satisfied on moderate portions, which made adherence to my nutrition plan 100% compliant.",
    },
    {
        "num": 69,
        "author": "Blake N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Fast recovery from intense cardio. Ran a half marathon and normally would be wrecked for three days. With Zeus, my legs felt fresh by Tuesday afternoon.",
    },
    {
        "num": 70,
        "author": "Quinton K. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Noticeable thermogenic effect. You can feel the thermogenic shift within 24 hours of the weekly Retatrutide dose. Body heat during cardio sessions is noticeably higher.",
    },
    {
        "num": 71,
        "author": "Darren Y. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Morning resting heart rate dropped. As body fat came off and sleep deepened, my resting heart rate dropped from 62 bpm down to 51 bpm over two months.",
    },
    {
        "num": 72,
        "author": "Seth C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Complete physical recomposition. This isn’t just weight loss; it’s true body reshaping. Fat falls off while muscle fibers maintain full glycogen storage and roundness.",
    },
    {
        "num": 73,
        "author": "Mitchell G. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Nails and hair grew faster. An unexpected side effect of HGH and enhanced recovery was how fast my hair and nails began growing. Overall vitality is through the roof.",
    },
    {
        "num": 74,
        "author": "Colby W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Flawless metabolic reset. My lipid panel improved: triglycerides down 45 points, HDL up 8 points. Retatrutide works miracles on systemic metabolic parameters.",
    },
    {
        "num": 75,
        "author": "Adam T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The most complete physique enhancement tool. Combining cellular repair, cognitive sharpness, growth hormone, and triple-receptor fat loss in one box is pure genius. Nothing else compares.",
    },
    {
        "num": 76,
        "author": "Dr. Robert M., MD — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "503B pharmacy grade standards are legitimate. As an internal medicine physician, I refused to touch overseas research chemicals. VanguardBIO’s 503B sourcing and transparent Certificates of Analysis meet true clinical standards.",
    },
    {
        "num": 77,
        "author": "Kent S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Fast, temperature-controlled delivery. Arrived in insulated packaging with cold packs still frozen 48 hours after dispatch. Lyophilized peptides were pristine with zero degradation.",
    },
    {
        "num": 78,
        "author": "Dean J. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "The reconstitution guide made it foolproof. Was slightly intimidated by reconstituting with bacteriostatic water. The step-by-step PDF instructions and video breakdown made it simple in 90 seconds.",
    },
    {
        "num": 79,
        "author": "Gregory L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Telehealth consultation was thorough. The medical provider actually reviewed my comprehensive metabolic panel and previous medical history before prescribing. Extremely professional clinical intake.",
    },
    {
        "num": 80,
        "author": "Tobias C. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Auto-refill arrived before I ran out. Subscription timing is dialed in. Month two arrived four business days before my current supply expired. Zero protocol interruption.",
    },
    {
        "num": 81,
        "author": "Lance B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Painless subcutaneous administration. The 29-gauge 0.5-inch insulin syringes make injections completely painless. You don't even feel it entering the abdomen or thigh.",
    },
    {
        "num": 82,
        "author": "Franklin D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Pristine HPLC lab testing. Requested the HPLC purity sheet for my lot number and support provided it in two hours. Over 99% verified purity. That's real accountability.",
    },
    {
        "num": 83,
        "author": "Wade E. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Clear labeling and dosing cards. Every vial is color-coded with exact unit markings on the syringe cheat sheet. Impossible to mess up dosing calculations.",
    },
    {
        "num": 84,
        "author": "Howard P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clean member dashboard. Logging injection sites and monitoring weekly biomarker trends inside the VanguardBIO member portal makes staying compliant seamless.",
    },
    {
        "num": 85,
        "author": "Brent R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Customer concierge responded in 10 minutes. Had a question regarding Selank timing with morning coffee. The clinical support desk replied promptly with exact pharmacology recommendations.",
    },
    {
        "num": 86,
        "author": "Leonidas K. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Elite packaging and presentation. Unboxing feels like receiving medical equipment from the future. Heavy vials, vacuum-sealed seals, clean bacteriostatic water vials.",
    },
    {
        "num": 87,
        "author": "Sean W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "No sketchy grey-market mystery powder. Peace of mind knowing this is made in an FDA-inspected 503B facility cannot be overstated. You know exactly what’s going into your body.",
    },
    {
        "num": 88,
        "author": "Keith G. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Smooth subscription management. Pause, skip, or modify is available right in the portal. No predatory cancellation roadblocks. A top-tier professional company.",
    },
    {
        "num": 89,
        "author": "Malcolm S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Complete onboarding ecosystem. From the doctor call to the delivery box and injection walkthrough, the user experience is effortless for beginners.",
    },
    {
        "num": 90,
        "author": "Timothy H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Doctor spent 20 minutes explaining mechanisms. My telehealth intake doctor didn't just rubber-stamp the script; he walked through the synergy of Selank, Semax, and GH in detail.",
    },
    {
        "num": 91,
        "author": "Scott B. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Medical grade reconstitution supplies. The included alcohol prep pads, mixing syringes, and needles are sterile hospital-grade supplies. No need to order external equipment.",
    },
    {
        "num": 92,
        "author": "Perry T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Reliable shipping notifications. Dispatched within 24 hours of physician clearance with real-time tracking updates. Packaging was completely discreet.",
    },
    {
        "num": 93,
        "author": "Jarrett V. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Accurate dosing concentrations. Volume calculations match the peptide mass down to the microgram. Solution clears instantly upon reconstitution with zero residue.",
    },
    {
        "num": 94,
        "author": "Owen N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "High-end clinical support. Needed an adjustment on my Retatrutide titration schedule at week six. The medical provider responded within hours with updated guidelines.",
    },
    {
        "num": 95,
        "author": "Byron M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Worth every penny of the $549. Trying to source six separate 503B-grade compounds individually with physician visits would cost well over $1,200/month. The pricing is unbeatable.",
    },
    {
        "num": 96,
        "author": "Carl F. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Zero injection site irritation. Because the compounds are ultra-pure and pH-balanced properly, there's zero stinging, welts, or post-injection redness.",
    },
    {
        "num": 97,
        "author": "Roger K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Seamless 12-week review. My 12-week telehealth review looked at real biomarker deltas. We adjusted dosing based on data, not guesswork.",
    },
    {
        "num": 98,
        "author": "Warren T. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Straightforward protocol schedule. Morning: Semax/Selank/BPC. Evening: HGH. Twice weekly: TB-500. Weekly: Retatrutide. It becomes second nature in three days.",
    },
    {
        "num": 99,
        "author": "Zack L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Transparent operations. Every batch number matches the COA provided upon request. True medical standard from end to end.",
    },
    {
        "num": 100,
        "author": "Neil D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Exemplary pharmaceutical logistics. Living on the West Coast, delivery was here in two days. Cold integrity was completely intact. 10/10 execution.",
    },
    {
        "num": 101,
        "author": "Alexander G. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Total system upgrade across every metric. At 12 weeks, my body fat is at 10.5%, sleep average is 8.5 hours, my knee tendonitis is cured, and my mental focus is sharper than ever. Zeus is the real deal.",
    },
    {
        "num": 102,
        "author": "Brian J. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Synergistic design works better than individual peptides. I took BPC-157 alone in the past. Having it integrated with TB-500, HGH, and nootropics produces a compounding effect that single compounds can't match.",
    },
    {
        "num": 103,
        "author": "Christian R. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Replaced multiple standalone supplements. Canceled three different nootropic subscriptions, joint powders, and fat burners. The Zeus protocol covers every vector with clinical efficacy.",
    },
    {
        "num": 104,
        "author": "Devon S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Transformed my executive output. Operating as a startup CEO, you need stamina, cognitive clarity, and physical resilience. This protocol gives me the biological bandwidth to work 70 hours a week.",
    },
    {
        "num": 105,
        "author": "Evan H. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Biomarkers speak for themselves. Blood pressure dropped to 116/74, resting heart rate down to 49, fasting glucose down to 82, and free testosterone/IGF-1 ratio optimized.",
    },
    {
        "num": 106,
        "author": "Felix W. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "8 weeks in: absolute physical transformation. Lost 16 lbs on the scale, but gained noticeable muscle fullness. My bench press climbed 20 lbs while my waist shrank 3 inches.",
    },
    {
        "num": 107,
        "author": "Gideon M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The mental and physical interplay is incredible. When your body doesn't hurt and your sleep is deep, your brain operates at 100%. The synergy between the 4 vectors is mathematically dialed in.",
    },
    {
        "num": 108,
        "author": "Hugh C. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Consistent performance every single day. Eliminated the good day / bad day swings. My training output, cognitive focus, and mood remain rock-solid seven days a week.",
    },
    {
        "num": 109,
        "author": "Isaac K. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Peak biohacking executed properly. I've spent a decade experimenting with longevity protocols. VanguardBIO has created the definitive integrated human performance package.",
    },
    {
        "num": 110,
        "author": "Jonah T. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Zero burnout under heavy workload. Between marathon prep and managing corporate litigation, I should have crashed. Zeus keeps my cellular energy and recovery baseline elevated.",
    },
    {
        "num": 111,
        "author": "Kieran B. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "True biological age reduction. My biological age methylation test showed a 3.2-year reversal after 90 days on Zeus. The epigenetic and recovery benefits are very real.",
    },
    {
        "num": 112,
        "author": "Leland P. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "The confidence of complete recovery. I can go all-out in the gym knowing my connective tissue and muscle fibers will be completely repaired by the next morning.",
    },
    {
        "num": 113,
        "author": "Micah D. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "The ultimate anti-aging stack for men over 40. Turning 45 felt like hitting a wall. Zeus flipped the switch back. Lean mass, fast recovery, and sharp cognition returned immediately.",
    },
    {
        "num": 114,
        "author": "Nico S. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "High-stress lifestyle solution. Living on red-eye flights and high-stakes meetings usually destroys your physiology. Zeus keeps my immune system, gut, and brain locked in.",
    },
    {
        "num": 115,
        "author": "Orson F. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Pristine energy curve throughout the day. No erratic spikes or crashes. Steady, calm, clean output from 6:00 AM to 10:30 PM, followed by deep restorative sleep.",
    },
    {
        "num": 116,
        "author": "Pierce V. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Joint durability during heavy squats. Squatting 405 lbs at age 52 without knee wraps or lingering hip pain is proof enough. The cellular recovery vector works wonders.",
    },
    {
        "num": 117,
        "author": "Quincy R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Phenomenal muscle retention on cuts. Dropping body fat used to make me flat and weak. With Retatrutide paired with HGH, I stayed full, vascular, and strong throughout the cut.",
    },
    {
        "num": 118,
        "author": "Reid W. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Brain fog and fatigue completely gone. I haven't felt this lucid, sharp, and physically capable since college. It clears out all the physiological drag slowing you down.",
    },
    {
        "num": 119,
        "author": "Sterling H. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clinical excellence delivered monthly. The auto-refill, telehealth oversight, and 503B pharmacy quality make this the most streamlined medical wellness protocol on the market.",
    },
    {
        "num": 120,
        "author": "Tanner M. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Complete physical overhaul. Noticeable fat loss across my midsection, veins showing on my lower abs, and zero tendinitis in my elbows. Best shape of my life.",
    },
    {
        "num": 121,
        "author": "Ulysses K. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "High compliance due to simple routine. The 90-second daily routine is so fast and pain-free that staying 100% compliant for 90 days was effortless.",
    },
    {
        "num": 122,
        "author": "Vance L. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Restored athletic explosiveness. Sprint times and vertical jump height both increased. The tendon stiffness and cellular recovery allow for true athletic power output.",
    },
    {
        "num": 123,
        "author": "Wyatt C. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "My wife noticed the change immediately. Better mood, calmer temperament under pressure, leaner physique, and deeper sleep. The positive changes are obvious to everyone around me.",
    },
    {
        "num": 124,
        "author": "Xander B. — Verified Buyer",
        "rating": "★★★★☆ (4.9 / 5)",
        "quote": "Deep restorative rest every night. The HGH somatropin pulse before bed produces vivid dreams and heavy slow-wave recovery. I wake up energized before my alarm rings.",
    },
    {
        "num": 125,
        "author": "York T. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Clean metabolic shift. My fasting glucose dropped from 104 to 86 in 30 days. Retatrutide’s glucagon activation is the future of metabolic medicine.",
    },
    {
        "num": 126,
        "author": "Zane D. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Superior to all competitors. Other peptide clinics charge double and send unregulated vials. VanguardBIO’s 503B sourcing and clinical sequencing put them in a class of their own.",
    },
    {
        "num": 127,
        "author": "Harrison E. — Verified Buyer",
        "rating": "★★★★☆ (4.8 / 5)",
        "quote": "Accelerated workout adaptation. I can handle 20 hard sets of pressing and show up two days later ready to hit shoulders again. My recovery ceiling has reset entirely.",
    },
    {
        "num": 128,
        "author": "Callum R. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Peak cognitive and physical synergy. Having Semax and Selank sharpen my brain while BPC, TB-500, HGH, and Retatrutide repair my body is the ultimate high-performance stack.",
    },
    {
        "num": 129,
        "author": "Gregory N. — Verified Buyer",
        "rating": "★★★★★ (5.0 / 5)",
        "quote": "Life-changing 90-day protocol. Completed my first 90 days and just renewed for another cycle. Body fat down from 22% to 12%, joint pain eradicated, and mental clarity operating at peak level. Unquestionably worth the investment.",
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
        "service": "VanguardBIO Zeus Ad Batch Generator",
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
            zf.writestr(f"zeus_ad_{item['num']:03d}.png", img_io.read())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=zeus_protocol_100_ads.zip"}
    )
