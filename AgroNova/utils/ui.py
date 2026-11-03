"""All visual design for AgroNova: themes, animated background, the Novi mascot and small HTML components.

Pure functions that return HTML/CSS strings (no Streamlit import), so they are easy to test.
"""
import random

FEATURE_ORDER = ("crop", "pest", "weather", "soil", "sustainable")
_ICONS = {
    "home": '<path d="M4 11l8-7 8 7v9H4z"/>',
    "dashboard": '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
    "crop": '<path d="M12 21V11"/><path d="M12 11C12 7 9 5 5 5c0 4 2 6 7 6z"/><path d="M12 15c0-3 2-5 6-5 0 4-2 6-6 6z"/>',
    "pest": '<path d="M9 9a3 3 0 016 0v6a3 3 0 01-6 0z"/><path d="M12 9v9M5 8l3 2M19 8l-3 2M4 14h4M20 14h-4M6 20l3-2M18 20l-3-2M10 5L9 3M14 5l1-2"/>',
    "weather": '<path d="M7 18a4 4 0 010-8 5 5 0 019.6 1A3.5 3.5 0 0116.5 18z"/><path d="M12 3v2M5 6l1.5 1.5M19 6l-1.5 1.5"/>',
    "soil": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12.5l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
    "sustainable": '<path d="M5 19C5 10 10 5 20 4c0 10-5 15-13 15"/><path d="M5 19c3-5 6-8 10-10"/>',
    "lab": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3"/><path d="M8 15h8"/>',
    "about": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
}


def icon(key: str) -> str:
    """Line icon (SF-Symbols style) that draws itself in when it appears."""
    body = _ICONS.get(key, _ICONS["home"])
    for tag in ("<path ", "<circle ", "<rect "):
        body = body.replace(tag, tag + 'pathLength="1" ')
    return (f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


BUBBLES = {
    "home": "Hi, I'm Novi. Let's grow something good.", "dashboard": "What would you like help with today?",
    "crop": "Let's find what suits your land.", "pest": "Tell me what you see. I'll help work it out.",
    "weather": "Describe the sky and I'll plan around it.", "soil": "Healthy soil, healthy harvest.",
    "sustainable": "Small steps, lasting impact.", "lab": "Let's test the prompts carefully.",
    "about": "Always double-check with a local expert.",
}

_DARK = ("--bg:#0B0C0E;--text:#F5F5F7;--muted:#9A9AA1;--card:rgba(255,255,255,.045);--card2:rgba(255,255,255,.075);"
         "--border:rgba(255,255,255,.09);--field:rgba(255,255,255,.06);--pop:#17181B;--side:rgba(14,15,18,.72);"
         "--accent:#7BD3A0;--accent-soft:rgba(123,211,160,.16);--btn-text:#06150C;--star:#FFFFFF;--star2:rgba(255,255,255,.5);"
         "--shadow:0 1px 0 rgba(255,255,255,.04) inset,0 12px 40px rgba(0,0,0,.45);--blob1:rgba(123,211,160,.11);"
         "--blob2:rgba(110,150,255,.10);--hover:rgba(255,255,255,.06);--twop:.65;")
_LIGHT = ("--bg:#F5F5F7;--text:#1D1D1F;--muted:#6E6E73;--card:rgba(255,255,255,.72);--card2:rgba(255,255,255,.9);"
          "--border:rgba(0,0,0,.07);--field:rgba(255,255,255,.9);--pop:#FFFFFF;--side:rgba(255,255,255,.65);"
          "--accent:#1F7A4D;--accent-soft:rgba(31,122,77,.10);--btn-text:#FFFFFF;--star:#B8903A;--star2:rgba(184,144,58,.5);"
          "--shadow:0 1px 2px rgba(0,0,0,.04),0 10px 30px rgba(0,0,0,.06);--blob1:rgba(31,122,77,.09);"
          "--blob2:rgba(0,113,227,.07);--hover:rgba(0,0,0,.04);--twop:.45;")

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@property --n{syntax:"<integer>";inherits:false;initial-value:0}
@property --ang{syntax:"<angle>";inherits:false;initial-value:0deg}
.stApp,.stApp *{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text",Inter,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased;}
.stApp{background:var(--bg);color:var(--text);}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"],[data-testid="stBottom"]{background:transparent!important;}
footer{visibility:hidden;}
.block-container{position:relative;z-index:1;padding-top:2.2rem;max-width:1080px;}
.element-container:has(.bg-fx),[data-testid="stElementContainer"]:has(.bg-fx){position:absolute;height:0;margin:0;overflow:visible;}
.stApp,.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp span,.stApp summary,.stApp [data-testid="stMarkdownContainer"]{color:var(--text);}
.stApp small,.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{color:var(--muted);}
.stApp h2,.stApp h3{font-weight:700;letter-spacing:-.025em;}
.stApp hr{border-color:var(--border);}
.stApp code{color:var(--accent);background:var(--field);border-radius:6px;}
.stApp .gt{background:linear-gradient(100deg,var(--text) 0%,var(--accent) 45%,var(--text) 90%);background-size:220% auto;-webkit-background-clip:text;background-clip:text;color:transparent!important;-webkit-text-fill-color:transparent;animation:shine 9s linear infinite;}
@keyframes shine{to{background-position:-220% center}}
@keyframes riseIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes blurIn{from{opacity:0;filter:blur(14px);transform:translateY(10px) scale(.98)}to{opacity:1;filter:none;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.7)}100%{opacity:1;transform:scale(1)}}
@keyframes flipUp{from{opacity:0;transform:perspective(900px) rotateX(14deg) translateY(30px)}to{opacity:1;transform:none}}
@keyframes slideL{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes slideR{from{opacity:0;transform:translateX(26px)}to{opacity:1;transform:none}}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes count{from{--n:0}}
@keyframes breathe{0%,100%{transform:scale(1);opacity:.55}50%{transform:scale(1.14);opacity:.9}}
@keyframes spin{to{--ang:360deg}}
/* ---------- ambient background ---------- */
.bg-fx{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden;}
.blob{position:absolute;width:55vmax;height:55vmax;border-radius:50%;filter:blur(90px);animation:drift 40s ease-in-out infinite alternate;}
.b1{background:radial-gradient(circle,var(--blob1),transparent 65%);top:-20vmax;left:-15vmax;}
.b2{background:radial-gradient(circle,var(--blob2),transparent 65%);bottom:-22vmax;right:-14vmax;animation-duration:52s;}
@keyframes drift{to{transform:translate(8vmax,5vmax) scale(1.12)}}
.tw{position:absolute;border-radius:50%;background:var(--star);opacity:0;animation:twinkle var(--d) ease-in-out infinite;animation-delay:var(--dl);}
@keyframes twinkle{0%,100%{opacity:0}50%{opacity:var(--twop)}}
.shoot{position:absolute;top:var(--t);left:var(--l);width:120px;height:1px;background:linear-gradient(90deg,transparent,var(--star2),var(--star));opacity:0;transform:rotate(145deg);animation:shoot var(--d) linear infinite;animation-delay:var(--dl);}
@keyframes shoot{0%{opacity:0;transform:rotate(145deg) translateX(0)}2%{opacity:.8}10%{opacity:0;transform:rotate(145deg) translateX(520px)}100%{opacity:0;transform:rotate(145deg) translateX(520px)}}
/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{background:var(--side)!important;backdrop-filter:saturate(180%) blur(28px);-webkit-backdrop-filter:saturate(180%) blur(28px);border-right:1px solid var(--border);}
[data-testid="stSidebar"]>div:first-child{background:transparent!important;}
.brand{display:flex;align-items:center;gap:.6rem;padding:.2rem 0 .8rem;animation:slideL .7s both;}
.brand b{font-size:1.25rem;font-weight:700;letter-spacing:-.025em;}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.1rem;}
[data-testid="stSidebar"] label[data-baseweb="radio"]{width:100%;margin:0;padding:.5rem .75rem;border-radius:10px;transition:background .2s,transform .25s;animation:slideL .6s both;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(1){animation-delay:.05s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(2){animation-delay:.1s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(3){animation-delay:.15s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(4){animation-delay:.2s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(5){animation-delay:.25s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(6){animation-delay:.3s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(7){animation-delay:.35s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(8){animation-delay:.4s}[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(9){animation-delay:.45s}
[data-testid="stSidebar"] label[data-baseweb="radio"]>div:first-child{display:none;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{background:var(--hover);transform:translateX(4px);}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){background:var(--accent-soft);font-weight:600;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) *{color:var(--accent);}
/* ---------- hero + headers ---------- */
.hero{position:relative;text-align:center;padding:1.2rem 0 1.4rem;display:flex;flex-direction:column;align-items:center;}
.hero .mwrap{position:relative;margin-bottom:.8rem;}
.halo{position:absolute;left:50%;top:58%;width:230px;height:230px;margin:-115px 0 0 -115px;border-radius:50%;background:radial-gradient(circle,var(--accent-soft),transparent 68%);animation:breathe 5s ease-in-out infinite;z-index:-1;}
.eyebrow{font-size:.78rem;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);animation:fade 1s .2s both;display:inline-block;}
.hero-title{font-size:clamp(2.4rem,6vw,4.4rem);line-height:1.03;font-weight:700;margin:.6rem 0 1rem;letter-spacing:-.045em;animation:blurIn 1.1s .25s cubic-bezier(.2,.8,.2,1) both;}
.hero p{margin:0 auto;color:var(--muted);font-size:1.18rem;line-height:1.5;max-width:36rem;animation:riseIn .9s .5s both;}
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:.45rem;margin-top:1.4rem;}
.chips span{padding:.3rem .85rem;border-radius:999px;background:var(--card);border:1px solid var(--border);font-size:.82rem;color:var(--muted);backdrop-filter:blur(10px);animation:pop .6s cubic-bezier(.34,1.56,.64,1) both;}
.chips span:nth-child(1){animation-delay:.7s}.chips span:nth-child(2){animation-delay:.8s}.chips span:nth-child(3){animation-delay:.9s}.chips span:nth-child(4){animation-delay:1s}.chips span:nth-child(5){animation-delay:1.1s}
.pagehead{position:relative;display:flex;align-items:center;justify-content:space-between;gap:1.5rem;padding:1.3rem 1.8rem;margin-bottom:1.3rem;background:var(--card);border:1px solid var(--border);border-radius:28px;backdrop-filter:saturate(180%) blur(24px);-webkit-backdrop-filter:saturate(180%) blur(24px);box-shadow:var(--shadow);animation:riseIn .8s cubic-bezier(.2,.8,.2,1) both;}
.pagehead .ptitle{display:flex;align-items:center;gap:1rem;}
.pagehead .ptile{flex:0 0 auto;width:54px;height:54px;border-radius:16px;display:flex;align-items:center;justify-content:center;color:var(--accent);background:var(--accent-soft);animation:pop .7s .2s cubic-bezier(.34,1.56,.64,1) both;}
.pagehead h1{font-size:clamp(1.6rem,3vw,2.1rem);margin:.1rem 0 0;font-weight:700;letter-spacing:-.035em;padding:0;line-height:1.1;animation:blurIn .8s .15s both;}
.pagehead p{margin:.3rem 0 0;color:var(--muted);font-size:1rem;line-height:1.45;max-width:34rem;animation:riseIn .8s .3s both;}
.mwrap{display:flex;flex-direction:column;align-items:center;flex-shrink:0;}
.bubble{position:relative;max-width:210px;text-align:center;padding:.5rem .9rem;margin-bottom:.6rem;border-radius:14px;background:var(--card2);border:1px solid var(--border);font-size:.8rem;color:var(--muted);animation:pop .7s .6s cubic-bezier(.34,1.56,.64,1) both;}
.bubble::after{content:"";position:absolute;bottom:-5px;left:50%;margin-left:-5px;width:9px;height:9px;background:var(--card2);border-right:1px solid var(--border);border-bottom:1px solid var(--border);transform:rotate(45deg);}
/* ---------- mascot ---------- */
.novi{overflow:visible;cursor:pointer;transition:transform .5s cubic-bezier(.34,1.56,.64,1);}
.novi:hover{transform:scale(1.08) rotate(-3deg);}
.nbob{animation:bob 4.5s ease-in-out infinite;transform-origin:60px 110px;}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.nshadow{animation:shad 4.5s ease-in-out infinite;transform-origin:60px 122px;}
@keyframes shad{0%,100%{transform:scale(1);opacity:.22}50%{transform:scale(.88);opacity:.12}}
.nleafL,.nleafR{transform-box:fill-box;transform-origin:50% 100%;animation:sway 4s ease-in-out infinite;}
.nleafR{animation-delay:-2s;}
@keyframes sway{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(6deg)}}
.neyes{transform-box:fill-box;transform-origin:center;animation:blink 5s infinite;}
@keyframes blink{0%,93%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}
.narm{transform-box:fill-box;transform-origin:100% 50%;animation:wave 1.1s .9s ease-in-out 3;}
@keyframes wave{0%,100%{transform:rotate(0)}50%{transform:rotate(-28deg)}}
.nspark{animation:twinkle 3s ease-in-out infinite;}
/* ---------- cards ---------- */
[class*="fcard_"]{position:relative;overflow:hidden;background:var(--card);border:1px solid var(--border);border-radius:24px;padding:1.4rem 1.4rem 1rem;backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);box-shadow:var(--shadow);transition:transform .45s cubic-bezier(.2,.8,.2,1),border-color .3s,background .3s;animation:flipUp .9s cubic-bezier(.2,.8,.2,1) both;}
[class*="fcard_"]::after{content:"";position:absolute;inset:0;background:radial-gradient(420px circle at 80% -10%,var(--accent-soft),transparent 60%);opacity:0;transition:opacity .4s;pointer-events:none;}
[class*="fcard_"]:hover{transform:translateY(-5px);border-color:var(--accent);background:var(--card2);}
[class*="fcard_"]:hover::after{opacity:1;}
.ficon{display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:14px;color:var(--accent);background:var(--accent-soft);transition:transform .5s cubic-bezier(.34,1.56,.64,1);}
[class*="fcard_"]:hover .ficon{transform:scale(1.1) rotate(-6deg);}
.ico{width:26px;height:26px;}
.ico *{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.3s .35s cubic-bezier(.4,0,.2,1) forwards;}
.ftitle{font-weight:600;font-size:1.05rem;margin:.9rem 0 .25rem;letter-spacing:-.015em;}
.ftag{color:var(--muted);font-size:.9rem;line-height:1.45;min-height:2.7rem;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:1.2rem 1rem;text-align:center;box-shadow:var(--shadow);backdrop-filter:blur(16px);animation:pop .8s cubic-bezier(.34,1.56,.64,1) both;}
.stat b{display:block;font-size:2.3rem;font-weight:700;letter-spacing:-.04em;}
.cnt{counter-reset:n var(--n);animation:count 1.6s .3s cubic-bezier(.2,.8,.2,1) both;}
.cnt::after{content:counter(n);}
.stat span{color:var(--muted);font-size:.84rem;}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1.2rem;margin:2rem 0 2rem;}
.step{padding:1rem 0 0;border-top:1px solid var(--border);position:relative;animation:riseIn .9s both;}
.step::before{content:"";position:absolute;top:-1px;left:0;height:2px;width:0;background:var(--accent);animation:grow 1.2s .5s cubic-bezier(.2,.8,.2,1) forwards;}
@keyframes grow{to{width:48px}}
.step:nth-child(2){animation-delay:.15s}.step:nth-child(3){animation-delay:.3s}
.step i{display:block;font-style:normal;font-size:.76rem;font-weight:600;letter-spacing:.09em;color:var(--accent);margin-bottom:.35rem;}
.step b{display:block;font-weight:600;letter-spacing:-.01em;font-size:1.05rem;}.step span{color:var(--muted);font-size:.92rem;}
.h2{font-size:1.7rem;font-weight:700;letter-spacing:-.035em;margin:1.2rem 0 .8rem;animation:slideL .8s both;}
.sec-title{font-size:.78rem;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);margin-bottom:.5rem;}
[class*="st-key-sec_"]{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:1.1rem 1.4rem;margin-bottom:.8rem;box-shadow:var(--shadow);backdrop-filter:blur(18px);animation:slideL .8s cubic-bezier(.2,.8,.2,1) both;}
.st-key-aside{position:sticky;top:3.5rem;align-self:flex-start;background:var(--card);border:1px solid var(--border);border-radius:24px;padding:1.3rem 1.4rem;box-shadow:var(--shadow);backdrop-filter:blur(18px);animation:slideR .9s .2s cubic-bezier(.2,.8,.2,1) both;}
.aside h4{margin:0 0 .6rem;font-size:1rem;font-weight:600;letter-spacing:-.01em;}
.aside li{color:var(--muted);font-size:.9rem;line-height:1.5;margin-bottom:.45rem;animation:fade .8s both;}
.aside li:nth-child(1){animation-delay:.5s}.aside li:nth-child(2){animation-delay:.65s}.aside li:nth-child(3){animation-delay:.8s}.aside li:nth-child(4){animation-delay:.95s}
.aside ul{padding-left:1.1rem;margin:0;}
.loader{display:flex;flex-direction:column;align-items:center;padding:1.6rem;margin:1rem 0;border-radius:24px;background:var(--card);border:1px solid var(--border);backdrop-filter:blur(16px);animation:pop .5s both;}
.bar{width:160px;height:3px;border-radius:3px;background:var(--field);overflow:hidden;margin-top:.6rem;}
.bar::after{content:"";display:block;width:40%;height:100%;border-radius:3px;background:var(--accent);animation:slide 1.4s ease-in-out infinite;}
@keyframes slide{0%{transform:translateX(-100%)}100%{transform:translateX(260%)}}
.lmsg{position:relative;height:1.4rem;width:100%;text-align:center;font-size:.9rem;color:var(--muted);margin-top:.7rem;}
.lmsg span{position:absolute;left:0;right:0;opacity:0;animation:lmsg 9s infinite;}
.lmsg span:nth-child(2){animation-delay:3s}.lmsg span:nth-child(3){animation-delay:6s}
@keyframes lmsg{0%{opacity:0}6%,30%{opacity:1}36%,100%{opacity:0}}
/* ---------- native widgets ---------- */
[data-testid="stForm"]{background:var(--card);border:1px solid var(--border);border-radius:24px;padding:1.5rem 1.6rem;backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);box-shadow:var(--shadow);animation:riseIn .9s .1s cubic-bezier(.2,.8,.2,1) both;}
[data-testid="stForm"] [data-testid="stElementContainer"]{animation:riseIn .7s both;}
[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(1){animation-delay:.15s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(2){animation-delay:.22s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(3){animation-delay:.29s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(4){animation-delay:.36s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(5){animation-delay:.43s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(6){animation-delay:.5s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(7){animation-delay:.57s}[data-testid="stForm"] [data-testid="stElementContainer"]:nth-child(8){animation-delay:.64s}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"],[data-baseweb="select"]>div{background:var(--field)!important;border-color:var(--border)!important;border-radius:12px!important;transition:box-shadow .25s,border-color .25s;}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]:focus-within>div{border-color:var(--accent)!important;box-shadow:0 0 0 4px var(--accent-soft)!important;}
.stApp input,.stApp textarea,.stApp [data-baseweb="select"] *{color:var(--text)!important;-webkit-text-fill-color:var(--text);}
.stApp ::placeholder{color:var(--muted)!important;-webkit-text-fill-color:var(--muted)!important;opacity:.8;}
.stApp [data-baseweb="select"] svg{fill:var(--muted);}
[data-baseweb="tag"]{background:var(--accent-soft)!important;border-radius:999px!important;}
[data-baseweb="tag"] *{color:var(--accent)!important;}
[data-baseweb="popover"] [data-baseweb="menu"],[data-baseweb="popover"] ul{background:var(--pop)!important;border:1px solid var(--border);border-radius:14px;}
[data-baseweb="popover"] li,[data-baseweb="popover"] li *{color:var(--text)!important;}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:var(--accent-soft)!important;}
.stApp button{position:relative;overflow:hidden;border-radius:999px;font-weight:500;border:1px solid var(--border);background:var(--card2);transition:background .2s,transform .25s cubic-bezier(.34,1.56,.64,1),box-shadow .25s;}
.stApp button *{color:var(--text);}
.stApp button[data-testid^="stBaseButton-primary"]{background:var(--accent)!important;border:0!important;color:var(--btn-text)!important;box-shadow:0 6px 18px var(--accent-soft);}
.stApp button[data-testid^="stBaseButton-primary"] *{color:var(--btn-text)!important;}
.stApp button[data-testid^="stBaseButton-primary"]::after{content:"";position:absolute;top:0;left:-70%;width:50%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.35),transparent);transform:skewX(-20deg);transition:left .7s;}
.stApp button[data-testid^="stBaseButton-primary"]:hover::after{left:130%;}
.stApp button[data-testid^="stBaseButton"]:hover{transform:translateY(-2px) scale(1.03);border-color:var(--accent);}
.stApp button[data-testid^="stBaseButton"]:active{transform:scale(.96);}
.st-key-cta_dash,.st-key-cta_lab{display:flex;animation:riseIn .8s 1.2s both;}.st-key-cta_dash{justify-content:flex-end;}.st-key-cta_lab{justify-content:flex-start;animation-delay:1.3s;}
[data-testid="stExpander"]{background:var(--card);border:1px solid var(--border)!important;border-radius:16px;}
[data-testid="stAlert"]{background:var(--card)!important;border:1px solid var(--border);border-radius:16px;animation:riseIn .6s both;}
[data-testid="stAlert"] *{color:var(--text)!important;}
[data-testid="stCode"] pre,[data-testid="stCode"] code{background:var(--field)!important;border-radius:12px;}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--border)!important;border-radius:18px;background:var(--card);}
[data-testid="stDownloadButton"],[data-testid="stRadio"] [role="radiogroup"]{animation:fade .8s both;}
::-webkit-scrollbar{width:8px;height:8px;}::-webkit-scrollbar-thumb{background:var(--border);border-radius:8px;}
@media (max-width:700px){.pagehead{flex-direction:column;text-align:center;}.pagehead .ptitle{flex-direction:column;}.st-key-aside{position:static;}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-iteration-count:1!important;animation-delay:0s!important;}}
"""


def _min(s: str) -> str:
    """Collapse whitespace so Streamlit's Markdown parser never mistakes our HTML for a code block."""
    return " ".join(s.split())


def global_css(dark: bool) -> str:
    extra = [f'[class*="st-key-sec_{i}"]{{animation-delay:{i * .12:.2f}s;}}' for i in range(5)]
    for i, k in enumerate(FEATURE_ORDER):
        extra.append(f'[class*="fcard_{k}"],[class*="fcard_h_{k}"]{{animation-delay:{.25 + i * .12:.2f}s;}}')
    if dark:
        extra.append('[data-testid="stDataFrame"]{filter:invert(.9) hue-rotate(180deg);border-radius:12px;}')
    root = f".stApp{{{_DARK if dark else _LIGHT}color-scheme:{'dark' if dark else 'light'};}}"
    return f"<style>{_min(root + _CSS + ''.join(extra))}</style>"


def background_fx(seed: int = 7) -> str:
    """Faint aurora, a few twinkling stars and rare, subtle shooting stars (pure CSS, no scripts)."""
    rnd = random.Random(seed)
    parts = ['<div class="bg-fx"><div class="blob b1"></div><div class="blob b2"></div>']
    for _ in range(30):
        s = rnd.choice([1, 1, 1, 2])
        parts.append(f'<i class="tw" style="left:{rnd.randint(0, 99)}%;top:{rnd.randint(0, 99)}%;width:{s}px;height:{s}px;'
                     f'--d:{rnd.uniform(4, 9):.1f}s;--dl:-{rnd.uniform(0, 9):.1f}s"></i>')
    for i in range(4):
        parts.append(f'<i class="shoot" style="--t:{rnd.randint(-5, 40)}%;--l:{rnd.randint(40, 100)}%;'
                     f'--d:{rnd.randint(14, 22)}s;--dl:{i * 4.5:.1f}s"></i>')
    parts.append("</div>")
    return _min("".join(parts))


def mascot(size: int = 120, mood: str = "happy") -> str:
    """Novi, a calm sprout mascot (inline SVG): waves hello, blinks, bobs, sways; reacts on hover."""
    py = 71 if mood == "think" else 75
    mouth = ('<ellipse cx="60" cy="93" rx="3.5" ry="4.5" fill="#12261A"/>' if mood == "think"
             else '<path d="M50 90 Q60 99 70 90" stroke="#12261A" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return _min(f"""<svg class="novi" viewBox="0 0 120 130" width="{size}" height="{int(size * 130 / 120)}" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="nb" cx="36%" cy="26%"><stop offset="0" stop-color="#D3EFDB"/><stop offset=".55" stop-color="#8CCBA4"/><stop offset="1" stop-color="#4E9C73"/></radialGradient>
<linearGradient id="nl" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#3F8F66"/><stop offset="1" stop-color="#B2E0C1"/></linearGradient></defs>
<ellipse class="nshadow" cx="60" cy="122" rx="28" ry="4.5" fill="#000"/>
<g class="nbob"><g class="nleafL"><path d="M58 38 C42 36 33 23 35 11 C49 11 60 21 58 38Z" fill="url(#nl)"/></g>
<g class="nleafR"><path d="M62 38 C78 36 87 23 85 11 C71 11 60 21 62 38Z" fill="url(#nl)"/></g>
<path d="M60 44 L60 32" stroke="#3F8F66" stroke-width="4" stroke-linecap="round"/>
<g class="narm"><ellipse cx="101" cy="86" rx="9" ry="5.5" fill="#6DB48C" transform="rotate(-20 101 86)"/></g>
<ellipse cx="19" cy="88" rx="9" ry="5.5" fill="#6DB48C" transform="rotate(20 19 88)"/>
<circle cx="60" cy="80" r="37" fill="url(#nb)"/>
<path d="M30 92 A37 37 0 0 0 90 98" stroke="#2E7A55" stroke-opacity=".25" stroke-width="6" fill="none" stroke-linecap="round"/>
<ellipse cx="46" cy="59" rx="12" ry="6.5" fill="#fff" opacity=".4" transform="rotate(-25 46 59)"/>
<g class="neyes"><ellipse cx="47" cy="{py}" rx="4.2" ry="5.6" fill="#12261A"/><ellipse cx="73" cy="{py}" rx="4.2" ry="5.6" fill="#12261A"/>
<circle cx="48.4" cy="{py - 2}" r="1.4" fill="#fff"/><circle cx="74.4" cy="{py - 2}" r="1.4" fill="#fff"/></g>
<circle cx="36" cy="88" r="5.5" fill="#F4A7A0" opacity=".4"/><circle cx="84" cy="88" r="5.5" fill="#F4A7A0" opacity=".4"/>
{mouth}</g><path class="nspark" d="M104 28v8M100 32h8" stroke="#8CCBA4" stroke-width="2" stroke-linecap="round"/>
<path class="nspark" style="animation-delay:-1.5s" d="M14 38v6M11 41h6" stroke="#8CCBA4" stroke-width="2" stroke-linecap="round"/></svg>""")


def hero_html(language_count: int, greeting: str) -> str:
    chips = "".join(f"<span>{c}</span>" for c in ("India", "Ghana", "Canada", f"{language_count} languages", "Powered by Gemini"))
    return _min(f"""<div class="hero"><div class="mwrap"><div class="halo"></div><div class="bubble">{BUBBLES['home']}</div>{mascot(120)}</div>
<span class="eyebrow">{greeting}</span>
<div class="hero-title">Farming advice,<br><span class="gt">beautifully simple.</span></div>
<p>AgroNova turns simple questions about crops, soil, pests and weather into clear, region-specific guidance in your own language.</p>
<div class="chips">{chips}</div></div>""")


def page_header(page: str, icon_unused: str, title: str, tagline: str, bubble: str = "") -> str:
    return _min(f"""<div class="pagehead"><div class="ptitle"><div class="ptile">{icon(page)}</div><div><span class="eyebrow">AgroNova</span>
<h1>{title}</h1><p>{tagline}</p></div></div><div class="mwrap"><div class="bubble">{bubble or BUBBLES.get(page, '')}</div>{mascot(72)}</div></div>""")


def steps_html() -> str:
    items = [("Tell us about your farm", "Country, region, crop, soil and season."),
             ("Get clear advice", "Actions, reasons, and safety warnings."), ("Share feedback", "Rate the answer so we can improve.")]
    return _min('<div class="steps">' + "".join(f"<div class='step'><i>STEP {n}</i><b>{t}</b><span>{d}</span></div>"
                                                for n, (t, d) in enumerate(items, 1)) + "</div>")


def feature_card_html(key: str, title: str, tagline: str) -> str:
    return _min(f"<div class='ficon'>{icon(key)}</div><div class='ftitle'>{title}</div><div class='ftag'>{tagline}</div>")


def stat_html(value, label: str, icon_unused: str = "", delay: float = 0) -> str:
    num = f"<b class='cnt' style='--n:{value}'></b>" if isinstance(value, int) else f"<b>{value}</b>"
    return _min(f"<div class='stat' style='animation-delay:{delay}s'>{num}<span>{label}</span></div>")


def heading(text: str) -> str:
    return f"<div class='h2'>{text}</div>"


def aside_html(language: str) -> str:
    return _min(f"""<div class='aside'><h4>Before you start</h4><ul><li>Fields marked with * are required.</li>
<li>Your advice will be written in {language}.</li><li>Be as specific as you can; details improve the answer.</li>
<li>AgroNova gives general guidance. Confirm important decisions with a local agricultural officer.</li></ul></div>""")


def section_title(icon_unused: str, title: str) -> str:
    return f"<div class='sec-title'>{title}</div>"


def loader_html(messages: tuple) -> str:
    spans = "".join(f"<span>{m}</span>" for m in messages[:3])
    return _min(f"<div class='loader'>{mascot(70, 'think')}<div class='bar'></div><div class='lmsg'>{spans}</div></div>")


def sidebar_brand() -> str:
    return _min(f"<div class='brand'>{mascot(38)}<b>AgroNova</b></div>")
