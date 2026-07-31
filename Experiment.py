# ============================================================
#  RWC - Streamlit Animation Showcase (DEPLOYED)
#  11 animations: Easy / Medium / Complex, for your team's app.
#  requirements: streamlit streamlit-lottie requests pandas pydeck
#  Run locally:  py -m streamlit run app.py
# ============================================================
import time
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Animation Showcase", page_icon="🎬", layout="centered")
st.title("🎬 Streamlit Animation Showcase")
st.write("Easy → Medium → Complex. Match the animation to the moment in your app.")

# ============================================================
#  EASY
# ============================================================
st.header("🟢 Easy")

st.subheader("1. Balloons / Snow : celebrate a win")
c1, c2 = st.columns(2)
if c1.button("🎈 Balloons"):
    st.balloons()
if c2.button("❄️ Snow"):
    st.snow()

st.subheader("2. Spinner : make a wait feel intentional")
if st.button("Analyze"):
    with st.spinner("Analyzing your results..."):
        time.sleep(2)
    st.success("Done!")

st.subheader("3. Toast : quick slide-in confirmation")
if st.button("Save"):
    st.toast("Saved to your profile!", icon="✅")

st.divider()

# ============================================================
#  MEDIUM
# ============================================================
st.header("🟡 Medium")

st.subheader("4. Count-up number : reveal a score")
if st.button("Reveal my score"):
    spot = st.empty()
    target = 82
    for n in range(0, target + 1, 2):
        spot.metric("Heart Health Score", n)
        time.sleep(0.02)
    spot.metric("Heart Health Score", target)

st.subheader("5. CSS pulse alert : pull the eye to something urgent")
st.markdown(
    """
    <style>
    @keyframes pulseRed {0%,100%{opacity:1;}50%{opacity:.45;}}
    .alert{background:#ffe5e5;color:#b00020;border:2px solid #b00020;
    padding:.8rem 1rem;border-radius:10px;font-weight:700;text-align:center;
    animation:pulseRed 1s ease-in-out infinite;}
    </style>
    <div class="alert">⚠️ Contains peanuts</div>
    """,
    unsafe_allow_html=True,
)

st.subheader("6. Typing effect : AI text that streams")
def stream_words(text):
    for w in text.split():
        yield w + " "
        time.sleep(0.05)
if st.button("Get recommendation"):
    st.write_stream(stream_words(
        "Based on your answers, here is our recommendation for you..."
    ))

st.divider()

# ============================================================
#  COMPLEX
# ============================================================
st.header("🔴 Complex")

st.subheader("7. Lottie : a themed animation (loader / hero)")
try:
    from streamlit_lottie import st_lottie
    LOTTIE_URL = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"  # swap from lottiefiles.com
    st_lottie(requests.get(LOTTIE_URL, timeout=5).json(), height=220, key="lottie")
except Exception:
    st.info("Lottie needs streamlit-lottie + a valid URL from lottiefiles.com.")

st.subheader("8. Animated chart : data that draws itself")
if st.button("Play the trend"):
    spot = st.empty()
    data = []
    for v in [12, 25, 33, 30, 48, 61, 80]:
        data.append(v)
        spot.line_chart(pd.DataFrame({"value": data}))
        time.sleep(0.15)

st.subheader("9. 3D spinning model : show off a product / mascot")
st.caption("Auto-rotates, drag to spin. Swap the .glb for your own (PureStream: your filter!).")
components.html(
    """
    <script type="module"
      src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer
      src="https://modelviewer.dev/shared-assets/models/Astronaut.glb"
      alt="A 3D model" auto-rotate camera-controls
      rotation-per-second="30deg" shadow-intensity="1"
      style="width:100%;height:320px;background:#f5f5f5;border-radius:12px;">
    </model-viewer>
    """,
    height=340,
)
st.subheader("10. Animated gauge : click to play / replay")
score = 82
circ = 339                      # circumference of r=54 circle
offset = circ * (1 - score / 100)
components.html(f"""
<style>
  body {{ margin:0; font-family:sans-serif; text-align:center; }}
  .wrap {{ position:relative; width:170px; margin:8px auto; }}
  .svg {{ transform:rotate(-90deg); }}
  .bg {{ fill:none; stroke:#eee; stroke-width:14; }}
  .fg {{ fill:none; stroke:#b00020; stroke-width:14; stroke-linecap:round;
         stroke-dasharray:{circ}; stroke-dashoffset:{circ}; }}
  @keyframes ringfill {{ from {{ stroke-dashoffset:{circ}; }} to {{ stroke-dashoffset:{offset}; }} }}
  .num {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
          font-size:2.4rem; font-weight:800; color:#b00020; }}
  .lbl {{ color:#666; font-size:.9rem; }}
  .btn {{ margin-top:10px; padding:.5rem 1.2rem; border:none; border-radius:8px;
          background:#b00020; color:white; font-weight:700; cursor:pointer; }}
</style>
<div class="wrap">
  <svg class="svg" width="170" height="170" viewBox="0 0 120 120">
    <circle class="bg" cx="60" cy="60" r="54"></circle>
    <circle class="fg" id="fg" cx="60" cy="60" r="54"></circle>
  </svg>
  <div class="num" id="num">0</div>
</div>
<div class="lbl">Heart Health Score</div>
<button class="btn" onclick="playGauge()">▶️ Play</button>
<script>
  const SCORE = {score};
  const EMPTY = {circ};
  function playGauge() {{
    const fg = document.getElementById('fg');
    const num = document.getElementById('num');
    const wrap = document.querySelector('.wrap');
    fg.style.animation = 'none';            // 1) clear any running/finished animation
    fg.style.strokeDashoffset = EMPTY;      //    reset ring to empty
    void wrap.offsetHeight;                 // 2) reflow on an HTML element (reliable)
    fg.style.animation = 'ringfill 1.4s ease-out forwards';  // 3) play from empty
    let n = 0; num.textContent = 0;         // 4) count the number up in sync
    const step = Math.max(1, Math.round(SCORE / 47));
    clearInterval(window._gaugeTimer);
    window._gaugeTimer = setInterval(() => {{
      n += step;
      if (n >= SCORE) {{ n = SCORE; clearInterval(window._gaugeTimer); }}
      num.textContent = n;
    }}, 30);
  }}
</script>
""", height=280)

st.subheader("11. Interactive 3D map : real places you can tilt and spin")
st.caption("Drag to tilt/rotate. Swap in each team's real coordinates.")
try:
    import pydeck as pdk
    spots = pd.DataFrame({"lat": [40.742, 40.735, 40.748, 40.729],
                          "lon": [-74.178, -74.169, -74.184, -74.160]})  # e.g. gyms near NJIT
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(latitude=40.742, longitude=-74.178, zoom=13, pitch=50),
        layers=[pdk.Layer("ScatterplotLayer", data=spots,
                          get_position="[lon, lat]", get_color="[176,0,32,200]", get_radius=120)]))
except Exception:
    st.info("3D map needs pydeck (in requirements.txt).")

st.divider()
st.caption("Match the animation to the moment: celebrate wins, cover waits, "
           "flag urgency, and go 3D / map / gauge where it earns its keep.")
