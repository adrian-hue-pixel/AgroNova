"""All visual design for AgroNova: light "Meadow" theme (default), dark theme, large-text and low-data modes,
the Novi mascot and small HTML components.

Pure functions that return HTML/CSS strings (no Streamlit import), so they are easy to test.
EVERY piece of user-supplied text that is put into HTML goes through html.escape().
"""
import html
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
    "farm": '<path d="M3 21V10l9-6 9 6v11z"/><path d="M9 21v-6h6v6"/>',
    "ask": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3M9 21h6"/>',
    "doctor": '<path d="M12 21c-5 0-8-3-8-8 5 0 8 3 8 8z"/><path d="M12 21c0-5 3-8 8-8 0 5-3 8-8 8z"/><path d="M12 3v6M9 6h6"/>',
    "forecast": '<path d="M7 18a4 4 0 010-8 5 5 0 019.6 1A3.5 3.5 0 0116.5 18z"/><path d="M12 3v2M5 6l1.5 1.5M19 6l-1.5 1.5"/>',
    "calendar": '<rect x="4" y="5" width="16" height="16" rx="3"/><path d="M4 10h16M9 3v4M15 3v4"/><path d="M9 15l2 2 4-4"/>',
    "market": '<path d="M5 20v-8M12 20V5M19 20v-5"/><path d="M3 20h18"/>',
    "journal": '<path d="M6 3h11a2 2 0 012 2v16H8a2 2 0 01-2-2z"/><path d="M6 19a2 2 0 012-2h11M10 8h6M10 12h6"/>',
    "guides": '<path d="M3 5c3-1 6-1 9 1 3-2 6-2 9-1v14c-3-1-6-1-9 1-3-2-6-2-9-1z"/><path d="M12 6v14"/>',
}


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def icon(key: str) -> str:
    """Line icon (SF-Symbols style) that draws itself in when it appears."""
    body = _ICONS.get(key, _ICONS["home"])
    for tag in ("<path ", "<circle ", "<rect "):
        body = body.replace(tag, tag + 'pathLength="1" ')
    return (f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


BUBBLES = {
    "home": "Hi, I'm Novi. Let's grow something good.", "dashboard": "Here is your farm today.",
    "crop": "Let's find what suits your land.", "pest": "Tell me what you see. I'll help work it out.",
    "weather": "Describe the sky and I'll plan around it.", "soil": "Healthy soil, healthy harvest.",
    "sustainable": "Small steps, lasting impact.", "lab": "Let's test the prompts carefully.",
    "about": "Always double-check with a local expert.", "farm": "Tell me once. I'll remember.",
    "ask": "Just speak. I'm listening.", "doctor": "Show me the leaf. Let's look together.",
    "forecast": "I check the sky so you can plan.", "calendar": "What to do next, and when.",
    "market": "Know your prices before you plant.", "journal": "Write it down. Your farm remembers.",
    "guides": "These work even with no internet.",
}

# ---------------------------------------------------------------- colour tokens
_DARK = ("--bg:#0B0C0E;--text:#F5F5F7;--muted:#A1A1A8;--card:rgba(255,255,255,.055);--card2:rgba(255,255,255,.085);"
         "--border:rgba(255,255,255,.10);--fborder:rgba(255,255,255,.16);--field:rgba(255,255,255,.07);--pop:#17181B;"
         "--side:rgba(14,15,18,.78);--accent:#7BD3A0;--accent-soft:rgba(123,211,160,.16);--btn-text:#06150C;"
         "--star:#FFFFFF;--star2:rgba(255,255,255,.5);--shadow:0 1px 0 rgba(255,255,255,.04) inset,0 12px 40px rgba(0,0,0,.45);"
         "--blob1:rgba(123,211,160,.11);--blob2:rgba(110,150,255,.10);--hover:rgba(255,255,255,.07);--twop:.65;"
         "--warm:#F2B84B;--warm-soft:rgba(242,184,75,.15);--sky:#7FB8F0;--sky-soft:rgba(127,184,240,.15);"
         "--danger:#FF9A7A;--danger-soft:rgba(255,154,122,.14);--good:#7BD3A0;--good-soft:rgba(123,211,160,.14);"
         "--wx:linear-gradient(135deg,rgba(127,184,240,.16),rgba(242,184,75,.12));--head:rgba(255,255,255,.055);")
_LIGHT = ("--bg:#F3F7F1;--text:#14231A;--muted:#52625A;--card:#FFFFFF;--card2:#FFFFFF;--border:#DDE6D9;--fborder:#BFCDBA;"
          "--field:#FFFFFF;--pop:#FFFFFF;--side:#FFFFFF;--accent:#17734A;--accent-soft:rgba(23,115,74,.10);--btn-text:#FFFFFF;"
          "--star:#C9A23F;--star2:rgba(201,162,63,.5);--shadow:0 1px 2px rgba(20,50,30,.05),0 10px 28px rgba(20,50,30,.07);"
          "--blob1:rgba(255,214,120,.38);--blob2:rgba(23,115,74,.13);--hover:rgba(23,115,74,.07);--twop:.0;"
          "--warm:#9A5B00;--warm-soft:#FFF3DA;--sky:#17619E;--sky-soft:#E7F1FB;--danger:#A8321A;--danger-soft:#FCEBE5;"
          "--good:#17734A;--good-soft:#E5F4EA;"
          "--wx:linear-gradient(135deg,#E6F2FC 0%,#FFF6E0 100%);--head:linear-gradient(135deg,#FFFFFF 0%,#EEF7F0 100%);")

_FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');"

_CSS = """
@property --n{syntax:"<integer>";inherits:false;initial-value:0}
.stApp,.stApp *{font-family:Inter,-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Noto Sans","Noto Sans Tamil","Noto Sans Devanagari",sans-serif;-webkit-font-smoothing:antialiased;}
[data-testid="stIconMaterial"],[data-testid="stIconMaterial"] *,.stApp span[class*="material-symbols"],.stApp span[class*="material-icons"]{font-family:"Material Symbols Rounded","Material Icons"!important;}
.stApp{background:var(--bg);color:var(--text);}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"],[data-testid="stBottom"]{background:transparent!important;}
footer{visibility:hidden;}
.block-container{position:relative;z-index:1;padding-top:2rem;padding-bottom:4rem;max-width:1080px;}
.element-container:has(.bg-fx),[data-testid="stElementContainer"]:has(.bg-fx){position:absolute;height:0;margin:0;overflow:visible;}
.stApp,.stApp p,.stApp li,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp span,.stApp summary,.stApp [data-testid="stMarkdownContainer"]{color:var(--text);}
.stApp small,.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{color:var(--muted);}
.stApp h2,.stApp h3{font-weight:700;letter-spacing:-.02em;}
.stApp hr{border-color:var(--border);}
.stApp a{color:var(--accent);}
.stApp code{color:var(--accent);background:var(--accent-soft);border-radius:6px;}
.stApp [data-testid="stWidgetLabel"] p,.stApp [data-testid="stWidgetLabel"] label{font-weight:600;font-size:.93rem;}
.stApp .gt{background:linear-gradient(100deg,var(--text) 0%,var(--accent) 45%,var(--text) 90%);background-size:220% auto;-webkit-background-clip:text;background-clip:text;color:transparent!important;-webkit-text-fill-color:transparent;animation:shine 9s linear infinite;}
@keyframes shine{to{background-position:-220% center}}
@keyframes riseIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes blurIn{from{opacity:0;filter:blur(12px);transform:translateY(8px) scale(.98)}to{opacity:1;filter:none;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.8)}100%{opacity:1;transform:scale(1)}}
@keyframes flipUp{from{opacity:0;transform:perspective(900px) rotateX(12deg) translateY(26px)}to{opacity:1;transform:none}}
@keyframes slideL{from{opacity:0;transform:translateX(-22px)}to{opacity:1;transform:none}}
@keyframes slideR{from{opacity:0;transform:translateX(22px)}to{opacity:1;transform:none}}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes count{from{--n:0}}
@keyframes breathe{0%,100%{transform:scale(1);opacity:.55}50%{transform:scale(1.14);opacity:.9}}
@keyframes grow{to{width:48px}}
@keyframes fillbar{from{width:0}}
/* ---------- ambient background ---------- */
.bg-fx{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden;}
.blob{position:absolute;width:60vmax;height:60vmax;border-radius:50%;filter:blur(80px);animation:drift 40s ease-in-out infinite alternate;}
.b1{background:radial-gradient(circle,var(--blob1),transparent 65%);top:-26vmax;right:-18vmax;}
.b2{background:radial-gradient(circle,var(--blob2),transparent 65%);bottom:-26vmax;left:-18vmax;animation-duration:52s;}
@keyframes drift{to{transform:translate(-6vmax,5vmax) scale(1.1)}}
.leafpat{position:absolute;inset:0;opacity:.05;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cpath d='M20 80C20 50 40 30 70 28 70 58 50 78 20 80z' fill='%2317734A'/%3E%3Cpath d='M82 112C82 96 92 86 108 85 108 101 98 111 82 112z' fill='%2317734A'/%3E%3C/svg%3E");}
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
[data-testid="stSidebar"] label[data-baseweb="radio"]{width:100%;margin:0;padding:.55rem .8rem;border-radius:12px;transition:background .2s,transform .25s;animation:slideL .5s both;}
[data-testid="stSidebar"] label[data-baseweb="radio"]>div:first-child{display:none;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{background:var(--hover);transform:translateX(3px);}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){background:var(--accent-soft);font-weight:700;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) *{color:var(--accent);}
.navlabel{font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:.9rem 0 .2rem .3rem;}
/* ---------- hero + headers ---------- */
.hero{position:relative;text-align:center;padding:1.2rem 0 1.4rem;display:flex;flex-direction:column;align-items:center;}
.hero .mwrap{position:relative;margin-bottom:.8rem;}
.halo{position:absolute;left:50%;top:58%;width:230px;height:230px;margin:-115px 0 0 -115px;border-radius:50%;background:radial-gradient(circle,var(--accent-soft),transparent 68%);animation:breathe 5s ease-in-out infinite;z-index:-1;}
.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);animation:fade 1s .2s both;display:inline-block;}
.hero-title{font-size:clamp(2.3rem,6vw,4.2rem);line-height:1.04;font-weight:800;margin:.6rem 0 1rem;letter-spacing:-.04em;animation:blurIn 1.1s .25s cubic-bezier(.2,.8,.2,1) both;}
.hero p{margin:0 auto;color:var(--muted);font-size:1.15rem;line-height:1.55;max-width:36rem;animation:riseIn .9s .5s both;}
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:.45rem;margin-top:1.4rem;}
.chips span{padding:.32rem .9rem;border-radius:999px;background:var(--card);border:1px solid var(--border);font-size:.83rem;font-weight:500;color:var(--muted);box-shadow:0 1px 2px rgba(20,50,30,.04);animation:pop .6s cubic-bezier(.34,1.56,.64,1) both;}
.chips span:nth-child(1){animation-delay:.7s}.chips span:nth-child(2){animation-delay:.8s}.chips span:nth-child(3){animation-delay:.9s}.chips span:nth-child(4){animation-delay:1s}.chips span:nth-child(5){animation-delay:1.1s}
.pagehead{position:relative;display:flex;align-items:center;justify-content:space-between;gap:1.5rem;padding:1.3rem 1.8rem;margin-bottom:1.3rem;background:var(--head);border:1px solid var(--border);border-radius:26px;box-shadow:var(--shadow);animation:riseIn .8s cubic-bezier(.2,.8,.2,1) both;}
.pagehead .ptitle{display:flex;align-items:center;gap:1rem;}
.pagehead .ptile{flex:0 0 auto;width:56px;height:56px;border-radius:17px;display:flex;align-items:center;justify-content:center;color:var(--accent);background:var(--accent-soft);animation:pop .7s .2s cubic-bezier(.34,1.56,.64,1) both;}
.pagehead h1{font-size:clamp(1.5rem,3vw,2.05rem);margin:.1rem 0 0;font-weight:800;letter-spacing:-.03em;padding:0;line-height:1.1;animation:blurIn .8s .15s both;}
.pagehead p{margin:.3rem 0 0;color:var(--muted);font-size:1rem;line-height:1.45;max-width:34rem;animation:riseIn .8s .3s both;}
.mwrap{display:flex;flex-direction:column;align-items:center;flex-shrink:0;}
.bubble{position:relative;max-width:210px;text-align:center;padding:.5rem .9rem;margin-bottom:.6rem;border-radius:14px;background:var(--card2);border:1px solid var(--border);font-size:.8rem;color:var(--muted);box-shadow:0 1px 2px rgba(20,50,30,.05);animation:pop .7s .6s cubic-bezier(.34,1.56,.64,1) both;}
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
[class*="fcard_"]{position:relative;overflow:hidden;background:var(--card);border:1px solid var(--border);border-radius:22px;padding:1.3rem 1.3rem .9rem;box-shadow:var(--shadow);transition:transform .45s cubic-bezier(.2,.8,.2,1),border-color .3s,box-shadow .3s;animation:flipUp .9s cubic-bezier(.2,.8,.2,1) both;}
[class*="fcard_"]::after{content:"";position:absolute;inset:0;background:radial-gradient(420px circle at 80% -10%,var(--accent-soft),transparent 60%);opacity:0;transition:opacity .4s;pointer-events:none;}
[class*="fcard_"]:hover{transform:translateY(-4px);border-color:var(--accent);}
[class*="fcard_"]:hover::after{opacity:1;}
.ficon{display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:14px;color:var(--accent);background:var(--accent-soft);transition:transform .5s cubic-bezier(.34,1.56,.64,1);}
[class*="fcard_"]:hover .ficon{transform:scale(1.1) rotate(-6deg);}
.ico{width:26px;height:26px;}
.ico *{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.3s .35s cubic-bezier(.4,0,.2,1) forwards;}
.ftitle{font-weight:700;font-size:1.05rem;margin:.85rem 0 .25rem;letter-spacing:-.015em;}
.ftag{color:var(--muted);font-size:.9rem;line-height:1.45;min-height:2.6rem;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:1.1rem 1rem;text-align:center;box-shadow:var(--shadow);animation:pop .8s cubic-bezier(.34,1.56,.64,1) both;}
.stat b{display:block;font-size:2.1rem;font-weight:800;letter-spacing:-.04em;}
.cnt{counter-reset:n var(--n);animation:count 1.6s .3s cubic-bezier(.2,.8,.2,1) both;}
.cnt::after{content:counter(n);}
.stat span{color:var(--muted);font-size:.84rem;font-weight:500;}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1.2rem;margin:2rem 0 2rem;}
.step{padding:1rem 0 0;border-top:1px solid var(--border);position:relative;animation:riseIn .9s both;}
.step::before{content:"";position:absolute;top:-1px;left:0;height:2px;width:0;background:var(--accent);animation:grow 1.2s .5s cubic-bezier(.2,.8,.2,1) forwards;}
.step:nth-child(2){animation-delay:.15s}.step:nth-child(3){animation-delay:.3s}
.step i{display:block;font-style:normal;font-size:.76rem;font-weight:700;letter-spacing:.09em;color:var(--accent);margin-bottom:.35rem;}
.step b{display:block;font-weight:700;letter-spacing:-.01em;font-size:1.05rem;}.step span{color:var(--muted);font-size:.92rem;}
.h2{font-size:1.55rem;font-weight:800;letter-spacing:-.03em;margin:1.4rem 0 .8rem;animation:slideL .8s both;}
.sec-title{font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--accent);margin-bottom:.5rem;}
[class*="st-key-sec_"]{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:1.1rem 1.4rem;margin-bottom:.8rem;box-shadow:var(--shadow);animation:slideL .8s cubic-bezier(.2,.8,.2,1) both;}
.st-key-aside{position:sticky;top:3.5rem;align-self:flex-start;background:var(--card);border:1px solid var(--border);border-radius:22px;padding:1.2rem 1.3rem;box-shadow:var(--shadow);animation:slideR .9s .2s cubic-bezier(.2,.8,.2,1) both;}
.aside h4{margin:0 0 .6rem;font-size:1rem;font-weight:700;letter-spacing:-.01em;}
.aside li{color:var(--muted);font-size:.9rem;line-height:1.5;margin-bottom:.45rem;animation:fade .8s both;}
.aside ul{padding-left:1.1rem;margin:0;}
.loader{display:flex;flex-direction:column;align-items:center;padding:1.6rem;margin:1rem 0;border-radius:22px;background:var(--card);border:1px solid var(--border);box-shadow:var(--shadow);animation:pop .5s both;}
.bar{width:160px;height:4px;border-radius:4px;background:var(--accent-soft);overflow:hidden;margin-top:.6rem;}
.bar::after{content:"";display:block;width:40%;height:100%;border-radius:4px;background:var(--accent);animation:slide 1.4s ease-in-out infinite;}
@keyframes slide{0%{transform:translateX(-100%)}100%{transform:translateX(260%)}}
.lmsg{position:relative;height:1.4rem;width:100%;text-align:center;font-size:.9rem;color:var(--muted);margin-top:.7rem;}
.lmsg span{position:absolute;left:0;right:0;opacity:0;animation:lmsg 9s infinite;}
.lmsg span:nth-child(2){animation-delay:3s}.lmsg span:nth-child(3){animation-delay:6s}
@keyframes lmsg{0%{opacity:0}6%,30%{opacity:1}36%,100%{opacity:0}}
/* ---------- weather ---------- */
.wx-hero{display:flex;flex-wrap:wrap;align-items:center;gap:1.4rem;padding:1.4rem 1.7rem;margin-bottom:1rem;border-radius:24px;background:var(--wx);border:1px solid var(--border);box-shadow:var(--shadow);animation:riseIn .8s both;}
.wx-hero .wx-ico{width:84px;height:84px;flex:0 0 auto;}
.wx-hero .wx-main{flex:1 1 220px;}
.wx-place{font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);}
.wx-temp{font-size:3.3rem;font-weight:800;letter-spacing:-.05em;line-height:1.05;}
.wx-desc{font-size:1.05rem;color:var(--muted);font-weight:500;}
.wx-facts{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.7rem;}
.wx-facts span{padding:.28rem .75rem;border-radius:999px;background:var(--card);border:1px solid var(--border);font-size:.84rem;font-weight:600;}
.wx-upd{font-size:.78rem;color:var(--muted);margin-top:.6rem;}
.wx-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:.6rem;margin:.2rem 0 1rem;}
.wx-day{text-align:center;padding:.8rem .5rem;border-radius:18px;background:var(--card);border:1px solid var(--border);box-shadow:var(--shadow);animation:pop .6s both;}
.wx-day.today{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft);}
.wx-day b{display:block;font-size:.85rem;font-weight:700;}
.wx-day svg{width:38px;height:38px;margin:.2rem 0;}
.wx-day .hi{font-weight:800;font-size:1.05rem;}.wx-day .lo{color:var(--muted);font-size:.85rem;}
.wx-day .rn{color:var(--sky);font-size:.8rem;font-weight:600;margin-top:.15rem;}
.al-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:.7rem;margin:.4rem 0 1rem;}
.al{display:flex;gap:.7rem;padding:.85rem 1rem;border-radius:16px;border:1px solid var(--border);animation:riseIn .6s both;}
.al i{flex:0 0 auto;width:10px;height:10px;border-radius:50%;margin-top:.4rem;}
.al b{display:block;font-size:.96rem;margin-bottom:.1rem;}.al span{font-size:.88rem;color:var(--muted);line-height:1.45;}
.al-warn{background:var(--warm-soft);}.al-warn i{background:var(--warm);}
.al-good{background:var(--good-soft);}.al-good i{background:var(--good);}
.al-info{background:var(--sky-soft);}.al-info i{background:var(--sky);}
.attrib{font-size:.76rem;color:var(--muted);}
/* ---------- crops, tasks, journal, sources ---------- */
.crop-row{padding:1rem 1.2rem;margin-bottom:.7rem;border-radius:18px;background:var(--card);border:1px solid var(--border);box-shadow:var(--shadow);animation:riseIn .7s both;}
.crop-row .top{display:flex;justify-content:space-between;gap:.6rem;align-items:baseline;flex-wrap:wrap;}
.crop-row b{font-size:1.05rem;}.crop-row .stg{color:var(--accent);font-weight:600;font-size:.88rem;}
.crop-row .sub{color:var(--muted);font-size:.84rem;margin-top:.15rem;}
.prog{height:9px;border-radius:9px;background:var(--accent-soft);margin-top:.6rem;overflow:hidden;}
.prog i{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,#4FB27E,var(--accent));animation:fillbar 1.2s cubic-bezier(.2,.8,.2,1) both;}
.badge{display:inline-block;padding:.18rem .65rem;border-radius:999px;font-size:.76rem;font-weight:700;background:var(--accent-soft);color:var(--accent);}
.badge.warn{background:var(--warm-soft);color:var(--warm);}.badge.bad{background:var(--danger-soft);color:var(--danger);}.badge.sky{background:var(--sky-soft);color:var(--sky);}
.group-h{font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;margin:1.1rem 0 .4rem;color:var(--muted);}
.group-h.bad{color:var(--danger);}.group-h.today{color:var(--accent);}
.jr{display:flex;gap:1rem;padding:.9rem 1.1rem;margin-bottom:.6rem;border-radius:18px;background:var(--card);border:1px solid var(--border);box-shadow:var(--shadow);animation:riseIn .6s both;}
.jr .jd{flex:0 0 74px;text-align:center;}.jr .jd b{display:block;font-size:1.5rem;line-height:1;font-weight:800;}.jr .jd span{font-size:.74rem;color:var(--muted);font-weight:600;text-transform:uppercase;}
.jr .jb{flex:1;min-width:0;}.jr .jb p{margin:.25rem 0 0;font-size:.93rem;overflow-wrap:anywhere;}.jr .jm{font-size:.82rem;color:var(--muted);margin-top:.2rem;}
.srcs{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:.6rem;margin:.3rem 0;}
.srcs a{display:block;padding:.7rem .9rem;border-radius:14px;background:var(--card);border:1px solid var(--border);text-decoration:none;transition:border-color .2s,transform .2s;}
.srcs a:hover{border-color:var(--accent);transform:translateY(-2px);}
.srcs a b{display:block;color:var(--accent);font-size:.9rem;}.srcs a span{color:var(--muted);font-size:.8rem;}
.empty{text-align:center;padding:1.6rem 1rem;border:2px dashed var(--fborder);border-radius:20px;color:var(--muted);background:var(--card);}
.empty b{display:block;color:var(--text);font-size:1.02rem;margin-bottom:.2rem;}
.advrow{padding:.8rem 1rem;margin-bottom:.5rem;border-radius:16px;background:var(--card);border:1px solid var(--border);}
.advrow b{display:block;font-size:.96rem;}.advrow span{font-size:.8rem;color:var(--muted);}
.callout{padding:.9rem 1.1rem;border-radius:16px;background:var(--warm-soft);color:var(--text);font-size:.92rem;border:1px solid var(--border);}
.qcard{padding:.2rem 0 .1rem;}
/* ---------- native widgets ---------- */
[data-testid="stForm"]{background:var(--card);border:1px solid var(--border);border-radius:22px;padding:1.4rem 1.5rem;box-shadow:var(--shadow);animation:riseIn .9s .1s cubic-bezier(.2,.8,.2,1) both;}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"],[data-baseweb="select"]>div{background:var(--field)!important;border-color:var(--fborder)!important;border-radius:12px!important;transition:box-shadow .25s,border-color .25s;}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]:focus-within>div{border-color:var(--accent)!important;box-shadow:0 0 0 4px var(--accent-soft)!important;}
.stApp input,.stApp textarea,.stApp [data-baseweb="select"] *{color:var(--text)!important;-webkit-text-fill-color:var(--text);}
.stApp ::placeholder{color:var(--muted)!important;-webkit-text-fill-color:var(--muted)!important;opacity:.85;}
.stApp [data-baseweb="select"] svg{fill:var(--muted);}
[data-baseweb="tag"]{background:var(--accent-soft)!important;border-radius:999px!important;}
[data-baseweb="tag"] *{color:var(--accent)!important;}
[data-baseweb="popover"] [data-baseweb="menu"],[data-baseweb="popover"] ul{background:var(--pop)!important;border:1px solid var(--border);border-radius:14px;}
[data-baseweb="popover"] li,[data-baseweb="popover"] li *{color:var(--text)!important;}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:var(--accent-soft)!important;}
.stApp button{position:relative;overflow:hidden;border-radius:999px;font-weight:600;min-height:2.7rem;border:1px solid var(--fborder);background:var(--card2);transition:background .2s,transform .25s cubic-bezier(.34,1.56,.64,1),box-shadow .25s,border-color .2s;}
.stApp button *{color:var(--text);}
.stApp button[data-testid^="stBaseButton-primary"],.stApp button[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--accent)!important;border:0!important;color:var(--btn-text)!important;box-shadow:0 6px 16px var(--accent-soft);}
.stApp button[data-testid^="stBaseButton-primary"] *{color:var(--btn-text)!important;}
.stApp button[data-testid^="stBaseButton-primary"]::after{content:"";position:absolute;top:0;left:-70%;width:50%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.35),transparent);transform:skewX(-20deg);transition:left .7s;}
.stApp button[data-testid^="stBaseButton-primary"]:hover::after{left:130%;}
.stApp button[data-testid^="stBaseButton"]:hover{transform:translateY(-2px);border-color:var(--accent);}
.stApp button[data-testid^="stBaseButton"]:active{transform:scale(.97);}
.stApp button:focus-visible,.stApp a:focus-visible,.stApp input:focus-visible{outline:3px solid var(--accent);outline-offset:2px;}
.st-key-cta_dash,.st-key-cta_lab{display:flex;animation:riseIn .8s 1.2s both;}.st-key-cta_dash{justify-content:flex-end;}.st-key-cta_lab{justify-content:flex-start;animation-delay:1.3s;}
[data-testid="stExpander"]{background:var(--card);border:1px solid var(--border)!important;border-radius:16px;}
[data-testid="stExpander"] summary:hover{color:var(--accent);}
[data-testid="stCode"] pre,[data-testid="stCode"] code{background:var(--accent-soft)!important;border-radius:12px;}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--border)!important;border-radius:18px;background:var(--card);}
[data-testid="stFileUploaderDropzone"],[data-testid="stAudioInput"],[data-testid="stCameraInput"]{background:var(--field)!important;border:1.5px dashed var(--fborder)!important;border-radius:16px!important;}
[data-testid="stFileUploaderDropzone"] *,[data-testid="stAudioInput"] *{color:var(--text);}
[data-testid="stTabs"] [role="tablist"]{gap:.3rem;border-bottom:1px solid var(--border);}
[data-testid="stTabs"] button[role="tab"]{border-radius:12px 12px 0 0;border:0;background:transparent;min-height:2.6rem;font-weight:600;}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] *{color:var(--accent);}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:.7rem 1rem;box-shadow:var(--shadow);}
[data-testid="stProgress"] > div > div{background:var(--accent-soft)!important;}
[data-testid="stImage"] img{border-radius:14px;}
::-webkit-scrollbar{width:8px;height:8px;}::-webkit-scrollbar-thumb{background:var(--fborder);border-radius:8px;}
@media (max-width:700px){.block-container{padding-left:1rem;padding-right:1rem;}.pagehead{flex-direction:column;text-align:center;padding:1.1rem;}.pagehead .ptitle{flex-direction:column;}.st-key-aside{position:static;}.wx-temp{font-size:2.7rem;}.jr .jd{flex-basis:56px;}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-iteration-count:1!important;animation-delay:0s!important;}}
"""

# dark mode only: tint native alerts/tables to match (in light mode Streamlit's own alert colours already look right)
_DARK_ONLY = """
[data-testid="stAlert"]{background:var(--card)!important;border:1px solid var(--border);border-radius:16px;}
[data-testid="stAlert"] *{color:var(--text)!important;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{filter:invert(.9) hue-rotate(180deg);border-radius:12px;}
"""
_LIGHT_ONLY = """
[data-testid="stAlert"]{border-radius:16px;animation:riseIn .6s both;}
"""
_LARGE = (".stApp{font-size:1.18rem;}.stApp p,.stApp li,.stApp label,.stApp input,.stApp textarea,.stApp [data-baseweb=\"select\"] *,"
          ".stApp button,.stApp [data-testid=\"stMarkdownContainer\"] p{font-size:1.18rem!important;}"
          ".stApp [data-testid=\"stWidgetLabel\"] p{font-size:1.1rem!important;}.stApp button{min-height:3.2rem;}")
_LOW_DATA = ("*{animation:none!important;transition:none!important;}.ico *{stroke-dashoffset:0!important;}"
             ".cnt{counter-reset:none;}.stApp *{backdrop-filter:none!important;-webkit-backdrop-filter:none!important;}"
             "[class*=\"fcard_\"],[class*=\"st-key-sec_\"],.pagehead,.wx-day{opacity:1!important;}.gt{animation:none!important;}")


def _min(s: str) -> str:
    """Collapse whitespace so Streamlit's Markdown parser never mistakes our HTML for a code block."""
    return " ".join(s.split())


def global_css(dark: bool = False, large_text: bool = False, low_data: bool = False) -> str:
    extra = [f'[class*="st-key-sec_{i}"]{{animation-delay:{i * .12:.2f}s;}}' for i in range(5)]
    for i, k in enumerate(FEATURE_ORDER):
        extra.append(f'[class*="fcard_{k}"],[class*="fcard_h_{k}"]{{animation-delay:{.25 + i * .12:.2f}s;}}')
    extra += [f'[data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child({i}){{animation-delay:{i * .03:.2f}s}}'
              for i in range(1, 20)]
    extra.append(_DARK_ONLY if dark else _LIGHT_ONLY)
    if large_text:
        extra.append(_LARGE)
    if low_data:
        extra.append(_LOW_DATA)
    root = f".stApp{{{_DARK if dark else _LIGHT}color-scheme:{'dark' if dark else 'light'};}}"
    font = "" if low_data else _FONT_IMPORT   # low-data mode downloads no web font
    return f"<style>{_min(font + root + _CSS + ''.join(extra))}</style>"


def background_fx(dark: bool = False, seed: int = 7, low_data: bool = False) -> str:
    """Light: soft sun-glow and a faint leaf pattern. Dark: aurora, twinkling stars, rare shooting stars. (CSS only.)"""
    if low_data:
        return ""
    rnd = random.Random(seed)
    parts = ['<div class="bg-fx"><div class="blob b1"></div><div class="blob b2"></div>']
    if dark:
        for _ in range(30):
            s = rnd.choice([1, 1, 1, 2])
            parts.append(f'<i class="tw" style="left:{rnd.randint(0, 99)}%;top:{rnd.randint(0, 99)}%;width:{s}px;height:{s}px;'
                         f'--d:{rnd.uniform(4, 9):.1f}s;--dl:-{rnd.uniform(0, 9):.1f}s"></i>')
        for i in range(4):
            parts.append(f'<i class="shoot" style="--t:{rnd.randint(-5, 40)}%;--l:{rnd.randint(40, 100)}%;'
                         f'--d:{rnd.randint(14, 22)}s;--dl:{i * 4.5:.1f}s"></i>')
    else:
        parts.append('<div class="leafpat"></div>')
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
    chips = "".join(f"<span>{c}</span>" for c in ("Live weather", "Photo diagnosis", "Voice in your language",
                                                  f"{language_count} languages", "Works on weak internet"))
    return _min(f"""<div class="hero"><div class="mwrap"><div class="halo"></div><div class="bubble">{BUBBLES['home']}</div>{mascot(120)}</div>
<span class="eyebrow">{esc(greeting)}</span>
<div class="hero-title">Farming advice,<br><span class="gt">beautifully simple.</span></div>
<p>AgroNova turns simple questions about crops, soil, pests and weather into clear, local guidance, in your own language, by voice or photo.</p>
<div class="chips">{chips}</div></div>""")


def page_header(page: str, icon_unused: str, title: str, tagline: str, bubble: str = "") -> str:
    return _min(f"""<div class="pagehead"><div class="ptitle"><div class="ptile">{icon(page)}</div><div><span class="eyebrow">AgroNova</span>
<h1>{esc(title)}</h1><p>{esc(tagline)}</p></div></div><div class="mwrap"><div class="bubble">{esc(bubble or BUBBLES.get(page, ''))}</div>{mascot(72)}</div></div>""")


def steps_html() -> str:
    items = [("Tell us about your farm", "Save it once: place, crops, soil and water."),
             ("Get clear advice", "Weather-aware actions, reasons and safety warnings."),
             ("Track and improve", "Calendar, journal and feedback keep your farm on course.")]
    return _min('<div class="steps">' + "".join(f"<div class='step'><i>STEP {n}</i><b>{t}</b><span>{d}</span></div>"
                                                for n, (t, d) in enumerate(items, 1)) + "</div>")


def feature_card_html(key: str, title: str, tagline: str) -> str:
    return _min(f"<div class='ficon'>{icon(key)}</div><div class='ftitle'>{esc(title)}</div><div class='ftag'>{esc(tagline)}</div>")


def stat_html(value, label: str, icon_unused: str = "", delay: float = 0) -> str:
    num = f"<b class='cnt' style='--n:{value}'></b>" if isinstance(value, int) else f"<b>{esc(value)}</b>"
    return _min(f"<div class='stat' style='animation-delay:{delay}s'>{num}<span>{esc(label)}</span></div>")


def heading(text: str) -> str:
    return f"<div class='h2'>{esc(text)}</div>"


def nav_label(text: str) -> str:
    return f"<div class='navlabel'>{esc(text)}</div>"


def aside_html(language: str, tips=None) -> str:
    tips = tips or ["Fields marked with * are required.", f"Your advice will be written in {language}.",
                    "Be as specific as you can; details improve the answer.",
                    "AgroNova gives general guidance. Confirm important decisions with a local agricultural officer."]
    return _min("<div class='aside'><h4>Before you start</h4><ul>" + "".join(f"<li>{esc(t)}</li>" for t in tips) + "</ul></div>")


def section_title(icon_unused: str, title: str) -> str:
    return f"<div class='sec-title'>{esc(title)}</div>"


def loader_html(messages: tuple) -> str:
    spans = "".join(f"<span>{esc(m)}</span>" for m in messages[:3])
    return _min(f"<div class='loader'>{mascot(70, 'think')}<div class='bar'></div><div class='lmsg'>{spans}</div></div>")


def sidebar_brand() -> str:
    return _min(f"<div class='brand'>{mascot(38)}<b>AgroNova</b></div>")


# ---------------------------------------------------------------- weather components
_WX = {
    "sun": '<circle cx="32" cy="32" r="11" fill="#F6B93B"/><g stroke="#F6B93B" stroke-width="4" stroke-linecap="round"><path d="M32 8v6M32 50v6M8 32h6M50 32h6M15 15l4 4M45 45l4 4M49 15l-4 4M19 45l-4 4"/></g>',
    "partly": '<circle cx="24" cy="24" r="9" fill="#F6B93B"/><g stroke="#F6B93B" stroke-width="3.5" stroke-linecap="round"><path d="M24 7v4M8 24h4M12 12l3 3M36 12l-3 3"/></g><path d="M20 50a9 9 0 010-18 12 12 0 0123 3 7.5 7.5 0 010 15z" fill="#B8C7D6"/>',
    "cloud": '<path d="M18 48a10 10 0 010-20 14 14 0 0126 3 8.5 8.5 0 010 17z" fill="#A9B8C7"/>',
    "rain": '<path d="M18 40a10 10 0 010-20 14 14 0 0126 3 8.5 8.5 0 010 17z" fill="#9FB1C4"/><g stroke="#3B8FD6" stroke-width="4" stroke-linecap="round"><path d="M22 48l-3 7M32 48l-3 7M42 48l-3 7"/></g>',
    "storm": '<path d="M18 38a10 10 0 010-20 14 14 0 0126 3 8.5 8.5 0 010 17z" fill="#8797AA"/><path d="M34 40l-8 12h7l-3 9 12-14h-8z" fill="#F6B93B"/>',
    "snow": '<path d="M18 38a10 10 0 010-20 14 14 0 0126 3 8.5 8.5 0 010 17z" fill="#B8C7D6"/><g fill="#7FB8F0"><circle cx="22" cy="50" r="3"/><circle cx="32" cy="55" r="3"/><circle cx="42" cy="50" r="3"/></g>',
    "fog": '<g stroke="#A9B8C7" stroke-width="5" stroke-linecap="round"><path d="M12 24h40M8 34h40M14 44h40"/></g>',
}


def wx_icon(key: str, cls: str = "") -> str:
    body = _WX.get(key, _WX["cloud"])
    return f'<svg class="{cls}" viewBox="0 0 64 64" aria-hidden="true">{body}</svg>'


def weather_hero_html(place: str, temp: str, desc: str, icon_key: str, facts: list, updated: str) -> str:
    chips = "".join(f"<span>{esc(f)}</span>" for f in facts)
    return _min(f"""<div class="wx-hero">{wx_icon(icon_key, 'wx-ico')}<div class="wx-main"><div class="wx-place">{esc(place)}</div>
<div class="wx-temp">{esc(temp)}</div><div class="wx-desc">{esc(desc)}</div><div class="wx-facts">{chips}</div>
<div class="wx-upd">{esc(updated)}</div></div></div>""")


def forecast_strip_html(days: list) -> str:
    """days: [{'label','icon','hi','lo','rain','prob'}] - all values already formatted for the farmer's units."""
    cells = "".join(
        f"<div class='wx-day{' today' if i == 0 else ''}' style='animation-delay:{i * .05:.2f}s'><b>{esc(d['label'])}</b>"
        f"{wx_icon(d['icon'])}<div class='hi'>{esc(d['hi'])}</div><div class='lo'>{esc(d['lo'])}</div>"
        f"<div class='rn'>{esc(d['rain'])} · {esc(d['prob'])}</div></div>" for i, d in enumerate(days))
    return _min(f"<div class='wx-strip'>{cells}</div>")


def alerts_html(alerts: list) -> str:
    cells = "".join(f"<div class='al al-{esc(a['level'])}' style='animation-delay:{i * .06:.2f}s'><i></i><div><b>{esc(a['title'])}</b>"
                    f"<span>{esc(a['text'])}</span></div></div>" for i, a in enumerate(alerts))
    return _min(f"<div class='al-grid'>{cells}</div>")


# ---------------------------------------------------------------- farm components
def crop_progress_html(name: str, stage: str, pct: int, sub: str, badge: str = "") -> str:
    b = f"<span class='badge'>{esc(badge)}</span>" if badge else ""
    return _min(f"""<div class="crop-row"><div class="top"><b>{esc(name)}</b><span class="stg">{esc(stage)}</span>{b}</div>
<div class="sub">{esc(sub)}</div><div class="prog"><i style="width:{max(0, min(100, int(pct)))}%"></i></div></div>""")


def group_heading(text: str, kind: str = "") -> str:
    return f"<div class='group-h {esc(kind)}'>{esc(text)}</div>"


def badge_html(text: str, kind: str = "") -> str:
    return f"<span class='badge {esc(kind)}'>{esc(text)}</span>"


def sources_html(links: list, title: str = "") -> str:
    cells = "".join(f"<a href='{esc(l['url'])}' target='_blank' rel='noopener noreferrer'><b>{esc(l.get('name') or l.get('title') or l['url'])}</b>"
                    f"<span>{esc(l.get('why', ''))}</span></a>" for l in links if str(l.get("url", "")).startswith("http"))
    head = f"<div class='sec-title'>{esc(title)}</div>" if title else ""
    return _min(f"{head}<div class='srcs'>{cells}</div>")


def empty_html(title: str, text: str) -> str:
    return _min(f"<div class='empty'><b>{esc(title)}</b>{esc(text)}</div>")


def advice_row_html(title: str, when: str, lang: str) -> str:
    return _min(f"<div class='advrow'><b>{esc(title)}</b><span>{esc(when)} · {esc(lang)}</span></div>")


def journal_item_html(day: str, month: str, kind: str, crop: str, note: str, meta: str) -> str:
    return _min(f"""<div class="jr"><div class="jd"><b>{esc(day)}</b><span>{esc(month)}</span></div><div class="jb">
<div>{badge_html(kind)} <b>{esc(crop)}</b></div><p>{esc(note)}</p><div class="jm">{esc(meta)}</div></div></div>""")


def callout_html(text: str) -> str:
    return f"<div class='callout'>{esc(text)}</div>"
