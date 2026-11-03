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
_LIGHT = ("--bg:#F7F8F3;--text:#17251D;--muted:#68766D;--card:rgba(255,255,255,.90);--card2:#FFFFFF;"
          "--border:rgba(28,75,48,.12);--field:#FFFFFF;--pop:#FFFFFF;--side:rgba(250,252,248,.88);"
          "--accent:#16734B;--accent-soft:rgba(22,115,75,.12);--btn-text:#FFFFFF;--star:#B78332;--star2:rgba(183,131,50,.5);"
          "--shadow:0 1px 2px rgba(24,55,36,.04),0 14px 38px rgba(24,55,36,.085);--blob1:rgba(48,153,99,.17);"
          "--blob2:rgba(238,184,91,.12);--hover:rgba(22,115,75,.065);--twop:.35;")

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



_LIGHT_CSS = """
/* Light-only botanical polish and consistent high-contrast Streamlit fields. */
.stApp{background:radial-gradient(ellipse at 8% 0%,rgba(111,183,128,.12),transparent 34%),radial-gradient(ellipse at 96% 12%,rgba(244,190,103,.10),transparent 30%),var(--bg);}
[data-testid="stHeader"]{background:rgba(244,247,241,.78)!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(252,254,250,.96),rgba(245,249,242,.92))!important;box-shadow:8px 0 34px rgba(30,75,46,.035);}
.block-container{padding-bottom:3rem;}.hero{padding:1.6rem 1.2rem 1.8rem;}
.hero .bubble,.pagehead .bubble{color:#52675A;background:rgba(255,255,255,.92);border-color:rgba(22,115,75,.13);box-shadow:0 8px 24px rgba(23,53,34,.07);}
.chips span{color:#426151;background:rgba(255,255,255,.78);border-color:rgba(22,115,75,.13);}
.pagehead{background:linear-gradient(115deg,rgba(255,255,255,.96),rgba(248,252,245,.88));border-color:rgba(22,115,75,.12);box-shadow:0 14px 38px rgba(25,69,42,.075);}
.pagehead .ptile,.ficon{background:linear-gradient(145deg,#E5F4E8,#F1F8E9);color:#16734B;border:1px solid rgba(22,115,75,.08);}
[class*="fcard_"],.stat,[class*="st-key-sec_"],.st-key-aside{background:linear-gradient(150deg,rgba(255,255,255,.97),rgba(249,252,247,.9));border-color:rgba(30,91,55,.12);box-shadow:0 10px 28px rgba(23,53,34,.055),0 1px 2px rgba(23,53,34,.035);}
[class*="fcard_"]:hover{box-shadow:0 18px 38px rgba(23,83,48,.12);}.stat b{color:#176B47;}
.step{border-top-color:rgba(22,115,75,.18);}.step::before{background:linear-gradient(90deg,#16734B,#A6C96C);}
.sec-title,.eyebrow{color:#16734B;}.stApp h1,.stApp h2,.stApp h3,.stApp h4{color:#17251D;}
/* Explicit nested input colours fix inherited dark-theme and white-on-white field bugs. */
.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"],.stApp [data-baseweb="textarea"],.stApp [data-baseweb="select"]>div,
.stApp [data-testid="stTextInput"] [data-baseweb="input"],.stApp [data-testid="stTextArea"] [data-baseweb="textarea"],.stApp [data-testid="stNumberInput"] [data-baseweb="input"]{background:#FFF!important;border:1px solid #D7E3D9!important;border-radius:13px!important;box-shadow:0 1px 2px rgba(25,65,39,.035);}
.stApp [data-baseweb="input"] input,.stApp [data-baseweb="base-input"] input,.stApp [data-baseweb="textarea"] textarea,.stApp [data-baseweb="select"] input,
.stApp [data-testid="stTextInput"] input,.stApp [data-testid="stTextArea"] textarea,.stApp [data-testid="stNumberInput"] input{background:transparent!important;color:#20352A!important;-webkit-text-fill-color:#20352A!important;caret-color:#16734B!important;}
.stApp [data-baseweb="select"] [role="combobox"]{color:#20352A!important;-webkit-text-fill-color:#20352A!important;}
.stApp input:disabled,.stApp textarea:disabled{background:#F0F4EF!important;color:#78877D!important;-webkit-text-fill-color:#78877D!important;}
.stApp [data-baseweb="input"]:focus-within,.stApp [data-baseweb="textarea"]:focus-within,.stApp [data-baseweb="select"]>div:focus-within{border-color:#23865A!important;box-shadow:0 0 0 3px rgba(35,134,90,.13),0 2px 8px rgba(23,83,48,.06)!important;}
.stApp input::placeholder,.stApp textarea::placeholder{color:#89968D!important;-webkit-text-fill-color:#89968D!important;opacity:1!important;}
.stApp [data-baseweb="select"] svg{color:#587365!important;fill:#587365!important;}
.stApp [data-baseweb="tag"]{background:#E7F3E8!important;border:1px solid #D4E9D8;}.stApp [data-baseweb="tag"] *{color:#176B47!important;-webkit-text-fill-color:#176B47!important;}
[data-baseweb="popover"],[data-baseweb="popover"] [data-baseweb="menu"],[data-baseweb="popover"] ul,[role="listbox"]{background:#FFF!important;color:#20352A!important;border:1px solid #DCE7DD!important;border-radius:13px!important;box-shadow:0 14px 34px rgba(24,62,38,.13)!important;}
[data-baseweb="popover"] li,[data-baseweb="popover"] li *,[role="option"],[role="option"] *{color:#20352A!important;-webkit-text-fill-color:#20352A!important;}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"],[role="option"][aria-selected="true"]{background:#EAF5EB!important;}
.stApp [data-testid="stWidgetLabel"] p,.stApp [data-testid="stWidgetLabel"] label,.stApp [data-testid="stRadio"] label,.stApp [data-testid="stCheckbox"] label,.stApp [data-testid="stToggle"] label{color:#30483A!important;}
.stApp [data-testid="stExpander"]{background:rgba(255,255,255,.84)!important;border-color:#DCE7DD!important;}
.stApp [data-testid="stAlert"]{background:#F8FBF7!important;border-color:#DCE9DD!important;}.stApp [data-testid="stAlert"] *{color:#294333!important;}
.stApp button[data-testid^="stBaseButton-primary"]{background:linear-gradient(115deg,#16734B,#23865A)!important;box-shadow:0 7px 18px rgba(22,115,75,.19)!important;}
.stApp button[data-testid^="stBaseButton"]:not([data-testid^="stBaseButton-primary"]){background:#FFF!important;border-color:#D8E4DA!important;}
.stApp button[data-testid^="stBaseButton"]:not([data-testid^="stBaseButton-primary"]) *{color:#294333!important;-webkit-text-fill-color:#294333!important;}
.stApp button[data-testid^="stBaseButton"]:hover{box-shadow:0 8px 20px rgba(22,115,75,.12);}
.stApp [data-testid="stDataFrame"]{border:1px solid #DCE7DD;border-radius:14px;overflow:hidden;}
.stApp [data-testid="stMetric"]{background:rgba(255,255,255,.75);border:1px solid rgba(22,115,75,.10);border-radius:16px;padding:.8rem 1rem;}
.stApp ::selection{background:rgba(35,134,90,.2);color:#17251D;}
@media(max-width:700px){.block-container{padding-left:1rem;padding-right:1rem;}.pagehead{padding:1.2rem;}[data-testid="stForm"]{padding:1.1rem!important;}}

/* PREMIUM LIGHT MODE FINISH — warm greenhouse palette and stronger hierarchy */
.stApp{background:radial-gradient(ellipse at 7% 4%,rgba(83,164,103,.15),transparent 34%),radial-gradient(ellipse at 94% 84%,rgba(225,180,94,.15),transparent 32%),linear-gradient(135deg,#F8FAF5 0%,#F1F6EF 52%,#F8F6EF 100%)!important;}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:transparent!important;}
[data-testid="stHeader"]{background:rgba(248,250,245,.76)!important;backdrop-filter:blur(18px);}
.block-container{max-width:1180px;padding-top:2.5rem;padding-bottom:4rem;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(251,253,248,.98),rgba(241,248,239,.97))!important;border-right:1px solid rgba(31,92,55,.12)!important;box-shadow:8px 0 34px rgba(34,75,45,.045);}
[data-testid="stSidebar"] .brand b{font-size:1.35rem;letter-spacing:-.045em;color:#173C29;}
[data-testid="stSidebar"] label[data-baseweb="radio"]{padding:.62rem .8rem!important;border:1px solid transparent;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){background:linear-gradient(100deg,rgba(27,126,77,.14),rgba(27,126,77,.055))!important;border:1px solid rgba(27,126,77,.13)!important;box-shadow:inset 3px 0 0 #218354;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) *{color:#176C43!important;}
.hero{padding:1.7rem 1.2rem 1.9rem;}
.hero .halo{width:310px;height:310px;margin:-155px 0 0 -155px;background:radial-gradient(circle,rgba(53,157,94,.21),rgba(213,177,91,.07) 48%,transparent 70%);}
.hero-title{font-size:clamp(2.9rem,6.5vw,5.1rem);line-height:.98;letter-spacing:-.062em;margin:.85rem 0 1.2rem;}
.hero .gt{background:linear-gradient(100deg,#176D43 0%,#27965D 48%,#B28A39 100%);background-size:180% auto;}
.hero p{max-width:43rem;font-size:1.15rem;color:#647168;line-height:1.6;}
.eyebrow,.sec-title{color:#26794C;letter-spacing:.14em;}
.chips{gap:.58rem;margin-top:1.6rem;}
.chips span{background:rgba(255,255,255,.84);border:1px solid rgba(33,104,62,.14);box-shadow:0 4px 14px rgba(30,70,43,.045);color:#53675A;padding:.42rem 1rem;}
.steps{gap:1rem;margin:2.5rem 0 3rem;}
.step{padding:1.15rem 1.2rem 1.35rem;background:rgba(255,255,255,.66);border:1px solid rgba(33,104,62,.11);border-radius:19px;box-shadow:0 8px 24px rgba(30,70,43,.045);}
.step::before{left:1.2rem;background:linear-gradient(90deg,#167348,#B8A05B);}
.step i{color:#287B4E;}
.step b{font-size:1.08rem;color:#20382A;}
.step span{color:#69776E;line-height:1.55;}
.h2{font-size:1.9rem;letter-spacing:-.05em;color:#1D3527;margin:2rem 0 1.1rem;}
.pagehead{background:linear-gradient(120deg,rgba(255,255,255,.96),rgba(243,249,240,.91));border:1px solid rgba(35,105,62,.14);border-radius:27px;box-shadow:0 17px 44px rgba(28,70,41,.085);}
.pagehead .ptile,.ficon{background:linear-gradient(145deg,#DFF1E3,#F5F3E4);color:#197347;border:1px solid rgba(22,115,75,.09);}
.bubble{background:#fff;color:#65736A;border-color:rgba(33,104,62,.13);box-shadow:0 7px 22px rgba(30,70,43,.055);}
.bubble::after{background:#fff;border-color:rgba(33,104,62,.13);}
[class*="fcard_"]{background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(245,250,242,.96));border:1px solid rgba(33,104,62,.13);border-radius:24px;box-shadow:0 11px 31px rgba(31,75,44,.065);}
[class*="fcard_"]:hover{box-shadow:0 19px 42px rgba(31,94,53,.13);border-color:rgba(31,126,75,.36);}
.ficon{border-radius:16px;}
.ftitle{color:#20382A;font-size:1.08rem;}
.ftag{color:#6B786F;line-height:1.55;}
.stat{background:rgba(255,255,255,.91);border:1px solid rgba(33,104,62,.13);box-shadow:0 11px 29px rgba(31,75,44,.06);}
.stat b{color:#1B7046;}
.st-key-aside,[class*="st-key-sec_"]{background:rgba(255,255,255,.82);border-color:rgba(31,105,62,.13);box-shadow:0 12px 32px rgba(31,75,44,.06);}
[data-testid="stForm"]{background:rgba(255,255,255,.88)!important;border:1px solid rgba(31,105,62,.15)!important;border-radius:24px!important;box-shadow:0 16px 42px rgba(31,75,44,.075)!important;}
/* Field fixes: explicitly style both the BaseWeb shell AND its nested editable element. */
.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"],.stApp [data-baseweb="textarea"],.stApp [data-baseweb="select"]>div{background:#FFFFFF!important;border:1px solid #D3E1D5!important;border-radius:13px!important;box-shadow:inset 0 1px 2px rgba(25,65,38,.035)!important;}
.stApp [data-baseweb="input"] input,.stApp [data-baseweb="base-input"] input,.stApp [data-baseweb="textarea"] textarea,.stApp [data-baseweb="select"] [role="combobox"],.stApp input,.stApp textarea{background:transparent!important;color:#1B2D22!important;-webkit-text-fill-color:#1B2D22!important;caret-color:#167348!important;opacity:1!important;}
.stApp [data-baseweb="select"] [role="combobox"] *{color:#1B2D22!important;-webkit-text-fill-color:#1B2D22!important;}
.stApp [data-baseweb="input"]:focus-within,.stApp [data-baseweb="textarea"]:focus-within,.stApp [data-baseweb="select"]>div:focus-within{border-color:#278454!important;box-shadow:0 0 0 3px rgba(39,132,84,.14)!important;}
.stApp input::placeholder,.stApp textarea::placeholder,.stApp ::placeholder{color:#89968C!important;-webkit-text-fill-color:#89968C!important;opacity:1!important;}
.stApp [data-baseweb="select"] svg{color:#52705C!important;fill:#52705C!important;}
.stApp [data-baseweb="popover"],.stApp [data-baseweb="menu"],.stApp [role="listbox"]{background:#FFFFFF!important;color:#1B2D22!important;border:1px solid #DCE7DC!important;box-shadow:0 16px 38px rgba(25,65,38,.14)!important;border-radius:14px!important;}
.stApp [role="option"],.stApp [role="option"] *,.stApp [data-baseweb="popover"] li,.stApp [data-baseweb="popover"] li *{background:#fff!important;color:#1B2D22!important;-webkit-text-fill-color:#1B2D22!important;}
.stApp [role="option"]:hover,.stApp [role="option"][aria-selected="true"]{background:#EAF5EC!important;}
.stApp [data-baseweb="tag"]{background:#E5F3E8!important;border:1px solid #CDE6D2!important;}
.stApp [data-baseweb="tag"] *{color:#176D43!important;-webkit-text-fill-color:#176D43!important;}
.stApp label,.stApp [data-testid="stWidgetLabel"] p{color:#314B39!important;}
.stApp button[data-testid^="stBaseButton-primary"]{background:linear-gradient(110deg,#167348,#24945E)!important;box-shadow:0 9px 22px rgba(27,119,70,.22)!important;}
.stApp button[data-testid^="stBaseButton"]:not([data-testid^="stBaseButton-primary"]){background:rgba(255,255,255,.94)!important;border:1px solid #D9E5D9!important;}
.stApp button[data-testid^="stBaseButton"]:not([data-testid^="stBaseButton-primary"]) *{color:#294333!important;-webkit-text-fill-color:#294333!important;}
.stApp [data-testid="stAlert"]{background:#F0F8F0!important;border:1px solid #D6E9D8!important;}
.stApp [data-testid="stAlert"] *{color:#294A34!important;}
.stApp [data-testid="stExpander"]{background:rgba(255,255,255,.88)!important;border:1px solid #DCE7DC!important;}
.stApp [data-testid="stDataFrame"]{border:1px solid #DCE7DC;border-radius:14px;overflow:hidden;}
.stApp hr{border-color:rgba(31,105,62,.14)!important;}
.stApp ::selection{background:rgba(39,132,84,.2);color:#173C29;}
@media(max-width:700px){.block-container{padding:1.2rem 1rem 3rem;}.hero-title{font-size:clamp(2.5rem,12vw,3.7rem);}.steps{gap:.7rem;}.step{padding:1rem;}}

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
    theme_css = _CSS if dark else _CSS + _LIGHT_CSS
    return f"<style>{_min(root + theme_css + ''.join(extra))}</style>"


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
