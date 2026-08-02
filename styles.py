"""Custom CSS injected into the Streamlit app. Strict brand palette only:
Primary #4DC49B, Secondary #488C74, Accent #21815F, Highlight #9FC35C,
Background #FFFFFF, Text #000000 (inverted tones for dark mode).
"""

LIGHT_VARS = """
    --fc-primary: #4DC49B;
    --fc-secondary: #488C74;
    --fc-accent: #21815F;
    --fc-highlight: #9FC35C;
    --fc-bg: #FFFFFF;
    --fc-text: #000000;
    --fc-card-bg: #FFFFFF;
    --fc-card-border: rgba(33,129,95,0.12);
"""

DARK_VARS = """
    --fc-primary: #4DC49B;
    --fc-secondary: #2f5b49;
    --fc-accent: #9FC35C;
    --fc-highlight: #4DC49B;
    --fc-bg: #0f1d18;
    --fc-text: #FFFFFF;
    --fc-card-bg: #16281f;
    --fc-card-border: rgba(159,195,92,0.18);
"""


def get_css(dark_mode: bool = False) -> str:
    root_vars = DARK_VARS if dark_mode else LIGHT_VARS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {{
{root_vars}
}}

html, body, [class*="css"] {{
    font-family: 'Inter', 'Poppins', sans-serif;
    color: var(--fc-text);
}}

.stApp {{
    background: var(--fc-bg);
    transition: background 0.3s ease-in-out, color 0.3s ease-in-out;
}}

/* Hide default Streamlit chrome for a cleaner branded feel */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* ---------- Typography ---------- */
h1, h2, h3 {{
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    color: var(--fc-text);
    line-height: 1.3;
}}
p, li, span, label {{
    line-height: 1.6;
}}

/* ---------- Force readable body text in BOTH modes ----------
   Streamlit ships its own default text color on many internal
   elements that otherwise ignores our palette. Pin everything
   that isn't an intentionally-colored accent (badges, the
   welcome headline) to --fc-text, which is pure black in light
   mode and white in dark mode. */
p, li, span, label,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li,
div[data-testid="stMarkdownContainer"] span,
div[data-testid="stMarkdownContainer"] strong,
div[data-testid="stMetricValue"],
div[data-testid="stMetricLabel"],
div[data-testid="stMetricDelta"],
div[data-testid="stCaptionContainer"],
.stMarkdown, .stCaption, .stText,
.stRadio label, .stRadio div, .stSelectbox label, .stTextInput label,
.stNumberInput label, .stDateInput label, .stTextArea label,
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"],
.stAlert p, .stAlert div,
.stDataFrame, .stDataFrame div,
div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] span,
div[data-testid="stPopoverBody"] label {{
    color: var(--fc-text) !important;
}}

/* ---------- Fade-in / slide-up ---------- */
@keyframes fcFadeUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fc-fade {{
    animation: fcFadeUp 0.55s ease-in-out both;
}}
.fc-fade-delay-1 {{ animation-delay: 0.08s; }}
.fc-fade-delay-2 {{ animation-delay: 0.16s; }}
.fc-fade-delay-3 {{ animation-delay: 0.24s; }}

/* ---------- Cards ---------- */
.fc-card {{
    background: var(--fc-card-bg);
    border: 1px solid var(--fc-card-border);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}}
.fc-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 16px 36px rgba(0,0,0,0.14);
}}

/* ---------- Pill buttons (Streamlit button override) ---------- */
.stButton > button {{
    background: linear-gradient(90deg, var(--fc-primary), var(--fc-secondary));
    color: #ffffff;
    border: none;
    border-radius: 999px;
    padding: 0.6em 1.6em;
    font-weight: 600;
    font-size: 0.95rem;
    transition: transform 0.2s ease-in-out, background 0.3s ease-in-out, box-shadow 0.2s ease-in-out;
    box-shadow: 0 6px 16px rgba(77,196,155,0.25);
}}
.stButton > button p {{
    color: #ffffff !important;
}}
.stButton > button:hover {{
    transform: scale(1.05);
    background: linear-gradient(90deg, var(--fc-accent), var(--fc-secondary));
}}
.stButton > button:active {{
    transform: scale(0.97);
}}

/* ---------- Inputs ----------
   These previously set text color to --fc-text (white in dark mode)
   but never gave the box itself a background, so it stayed the
   browser's native white — white text on a white box, invisible
   until some default hover/focus state tinted it gray. Giving every
   box a real themed background (--fc-card-bg, which is a dark
   grayish-green in dark mode) fixes that everywhere at once. */
.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {{
    background: var(--fc-card-bg) !important;
    border-radius: 12px !important;
    border: 1.5px solid var(--fc-card-border) !important;
    color: var(--fc-text) !important;
    transition: border 0.25s ease-in-out, box-shadow 0.25s ease-in-out, background 0.25s ease-in-out;
}}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {{
    border: 1.5px solid var(--fc-primary) !important;
    box-shadow: 0 0 0 3px rgba(77,196,155,0.25) !important;
}}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: var(--fc-text) !important;
    opacity: 0.55;
}}
.stFileUploaderDropzone, section[data-testid="stFileUploaderDropzone"] {{
    background: var(--fc-card-bg) !important;
    border: 1.5px dashed var(--fc-card-border) !important;
}}

/* ---------- Dropdown / calendar popups ----------
   Selectbox options, the multiselect tag list, and the date-picker
   calendar are rendered by Streamlit into a portal at the end of
   <body>, outside .stSelectbox/.stDateInput — so the rules above
   never reached them. They kept their native white background while
   our global "p, li, span, label" rule (below) still forced their
   text white, which is exactly the "only readable once it goes gray
   on hover" bug: the browser's own hover-highlight was the only
   thing giving the white text any contrast at all. Theming the
   popup itself, plus a real (not just-happens-to-be-lighter) hover
   color, fixes it in both states. */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
div[data-baseweb="calendar"] {{
    background: var(--fc-card-bg) !important;
    color: var(--fc-text) !important;
}}
li[role="option"],
div[data-baseweb="menu"] li,
div[data-baseweb="calendar"] * {{
    background: var(--fc-card-bg) !important;
    color: var(--fc-text) !important;
}}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {{
    background: var(--fc-primary) !important;
    color: #ffffff !important;
}}

/* ---------- Progress / highlight bars ---------- */
.stProgress > div > div {{
    background: linear-gradient(90deg, var(--fc-highlight), var(--fc-primary)) !important;
}}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: var(--fc-card-bg);
    border-right: 1px solid var(--fc-card-border);
}}

/* ---------- Why-us / feature cards grid text ---------- */
.fc-badge {{
    display: inline-block;
    background: rgba(77,196,155,0.15);
    color: var(--fc-accent) !important;
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 8px;
}}

/* ---------- Flip flashcards ---------- */
.fc-flip-container {{
    perspective: 1000px;
    height: 220px;
    width: 100%;
    margin-bottom: 10px;
}}
.fc-flip-inner {{
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.6s;
    transform-style: preserve-3d;
    cursor: pointer;
}}
.fc-flip-container.flipped .fc-flip-inner {{
    transform: rotateY(180deg);
}}
.fc-flip-front, .fc-flip-back {{
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    font-weight: 600;
    font-size: 1.05rem;
}}
.fc-flip-front {{
    background: linear-gradient(135deg, var(--fc-primary), var(--fc-secondary));
    color: #ffffff !important;
}}
.fc-flip-front p, .fc-flip-front span, .fc-flip-front div {{
    color: #ffffff !important;
}}
.fc-flip-back {{
    background: var(--fc-card-bg);
    color: var(--fc-text);
    border: 1.5px solid var(--fc-primary);
    transform: rotateY(180deg);
    font-weight: 400;
    font-size: 0.95rem;
}}

/* ---------- Logo pulse for loading/welcome ---------- */
@keyframes fcPulse {{
    0%   {{ transform: scale(1); }}
    50%  {{ transform: scale(1.06); }}
    100% {{ transform: scale(1); }}
}}
div.st-key-fc_logo_pulse {{
    animation: fcPulse 2.2s ease-in-out infinite;
    text-align: center;
}}

/* ---------- Typing cursor ---------- */
.fc-typing::after {{
    content: '|';
    animation: fcBlink 0.9s step-end infinite;
    color: var(--fc-primary);
}}
@keyframes fcBlink {{
    50% {{ opacity: 0; }}
}}

/* ---------- Top-bar icon buttons (dark mode / language / profile / hamburger) ----------
   These sit in the top bar as small circular icon buttons instead of the
   full gradient pill, and — critically — st.popover (used for the
   hamburger and language menus) renders its panel as a floating overlay
   that does NOT push the rest of the page down or add gap in the top bar. */
div[class*="st-key-fc_icon_"] .stButton > button,
div[class*="st-key-fc_icon_"] button[data-testid="stPopoverButton"] {{
    background: var(--fc-card-bg) !important;
    color: var(--fc-text) !important;
    border: 1.5px solid var(--fc-card-border) !important;
    border-radius: 50% !important;
    width: 44px;
    height: 44px;
    padding: 0 !important;
    font-size: 1.15rem;
    box-shadow: none !important;
    display: flex;
    align-items: center;
    justify-content: center;
}}
div[class*="st-key-fc_icon_"] .stButton > button p,
div[class*="st-key-fc_icon_"] button[data-testid="stPopoverButton"] p {{
    color: var(--fc-text) !important;
}}
div[class*="st-key-fc_icon_"] .stButton > button:hover,
div[class*="st-key-fc_icon_"] button[data-testid="stPopoverButton"]:hover {{
    transform: scale(1.08);
    background: linear-gradient(90deg, var(--fc-primary), var(--fc-secondary)) !important;
    border-color: transparent !important;
}}
div[class*="st-key-fc_icon_"] .stButton > button:hover p,
div[class*="st-key-fc_icon_"] button[data-testid="stPopoverButton"]:hover p {{
    color: #ffffff !important;
}}

/* Popover panel contents (hamburger nav + language picker) */
div[data-testid="stPopoverBody"] {{
    border-radius: 16px !important;
    border: 1px solid var(--fc-card-border) !important;
    background: var(--fc-card-bg) !important;
}}
div[data-testid="stPopoverBody"] .stButton > button {{
    background: transparent !important;
    color: var(--fc-text) !important;
    border: none !important;
    box-shadow: none !important;
    text-align: left;
    justify-content: flex-start;
    border-radius: 10px;
    width: 100%;
}}
div[data-testid="stPopoverBody"] .stButton > button p {{
    color: var(--fc-text) !important;
}}
div[data-testid="stPopoverBody"] .stButton > button:hover {{
    background: linear-gradient(90deg, var(--fc-primary), var(--fc-secondary)) !important;
}}
div[data-testid="stPopoverBody"] .stButton > button:hover p {{
    color: #ffffff !important;
}}

/* ---------- Top bar: logo + big "Welcome back" sit together ---------- */
.fc-topbar-brand {{
    display: flex;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
}}
.fc-topbar-logo {{
    height: 56px;
    width: auto;
    display: block;
}}
.fc-welcome-text {{
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--fc-text);
    line-height: 1.2;
}}
.fc-welcome-text b {{
    color: var(--fc-accent);
}}

/* ---------- Dashboard: circular course-completion ring ---------- */
.fc-progress-ring {{
    width: 150px;
    height: 150px;
    border-radius: 50%;
    margin: 12px auto;
    background: conic-gradient(var(--fc-primary) calc(var(--pct) * 1%), var(--fc-card-border) 0);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.6s ease-in-out;
}}
.fc-progress-ring-inner {{
    width: 112px;
    height: 112px;
    border-radius: 50%;
    background: var(--fc-card-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--fc-text);
}}

/* ---------- Dashboard: quiz points count ---------- */
.fc-points-number {{
    font-size: 3rem;
    font-weight: 800;
    color: var(--fc-accent);
    margin: 6px 0;
}}

/* ---------- Dashboard: Life Simulation CTA card ---------- */
.fc-cta-card {{
    background: linear-gradient(135deg, var(--fc-primary), var(--fc-accent));
    border-radius: 20px;
    padding: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.14);
    margin-bottom: 14px;
    min-height: 150px;
}}

/* ---------- Login / Signup page: guaranteed contrast + brand buttons ----------
   Dark mode: black background, white text, light-green buttons with
   black text. Light mode: white background, black text, dark-green
   buttons with white text. Scoped to .fc-auth-page so nothing else on
   the site is affected. */
div.st-key-fc_auth_page .stTabs [data-baseweb="tab-panel"] {{
    background: {"#000000" if dark_mode else "#FFFFFF"} !important;
    border-radius: 18px;
    padding: 22px;
}}
div.st-key-fc_auth_page .stTabs [data-baseweb="tab-panel"] p,
div.st-key-fc_auth_page .stTabs [data-baseweb="tab-panel"] label,
div.st-key-fc_auth_page .stTabs [data-baseweb="tab-panel"] span,
div.st-key-fc_auth_page .stTabs [data-baseweb="tab-panel"] div {{
    color: {"#FFFFFF" if dark_mode else "#000000"} !important;
}}
div.st-key-fc_auth_page .stTextInput input {{
    background: {"#000000" if dark_mode else "#FFFFFF"} !important;
    color: {"#FFFFFF" if dark_mode else "#000000"} !important;
    border: 1.5px solid {"#FFFFFF" if dark_mode else "#000000"} !important;
}}
div.st-key-fc_auth_page .stButton > button,
div.st-key-fc_auth_page .stFormSubmitButton > button {{
    background: {"#9FC35C" if dark_mode else "#21815F"} !important;
    color: {"#000000" if dark_mode else "#FFFFFF"} !important;
    box-shadow: none !important;
}}
div.st-key-fc_auth_page .stButton > button p,
div.st-key-fc_auth_page .stFormSubmitButton > button p {{
    color: {"#000000" if dark_mode else "#FFFFFF"} !important;
}}
div.st-key-fc_auth_page .stButton > button:hover,
div.st-key-fc_auth_page .stFormSubmitButton > button:hover {{
    background: var(--fc-primary) !important;
}}
</style>
"""