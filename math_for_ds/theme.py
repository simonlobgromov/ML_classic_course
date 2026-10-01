# -*- coding: utf-8 -*-
"""Shared assets for the linear-algebra Colab lessons: the setup cell source
(dark-theme CSS, SVG/JS helpers, viz() wrapper) and notebook metadata.
Both build_lesson*.py import SETUP so the lessons stay visually consistent."""

# Source of the first code cell (#@title, collapsible in Colab). Defines CSS, JS,
# and viz(body, script) which wraps an HTML body into a self-contained dark block.
SETUP = r'''#@title Оформление и хелперы визуализации — запустите первой { display-mode: "form" }
from IPython.display import HTML, display

CSS = r"""
.vec-root{--bg:#12161c;--surface:#1a1f27;--ink:#e6e9ec;--soft:#a7b0ba;--line:#2a313b;
  --green:#5fd08a;--blue:#6ab0f3;--amber:#e0b25a;--rose:#e0757f;
  font-family:Georgia,'Times New Roman',serif;color:var(--ink);
  background:var(--bg);border-radius:14px;padding:2px 0;}
.vec-root .wrap{max-width:820px;margin:0 auto;padding:18px 22px;font-size:17px;line-height:1.65;}
.vec-root .wrap.wide{max-width:1180px;}
.vec-root h2{font-family:-apple-system,'Segoe UI',sans-serif;font-size:1.5rem;color:#fff;
  border-top:2px solid var(--line);padding-top:.5em;margin:1.4em 0 .5em;}
.vec-root h3{font-family:sans-serif;color:var(--green);font-size:1.15rem;margin:1.3em 0 .3em;}
.vec-root p{margin:.6em 0;} .vec-root b,.vec-root strong{color:#fff;}
.vec-root em{color:var(--soft);} .vec-root ul,.vec-root ol{padding-left:1.4em;} .vec-root li{margin:.28em 0;}
.vec-root .en{font-family:sans-serif;font-style:normal;color:#7f8a96;font-size:.88em;white-space:nowrap;}
.vec-root .where{font-family:sans-serif;font-size:.9rem;color:var(--soft);margin:.1em 0 .7em;}
.vec-root .where ul{margin:.3em 0;padding-left:1.3em;} .vec-root .where li{margin:.15em 0;}
.vec-root a{color:var(--green);}
.vec-root .box{border-radius:12px;padding:14px 18px;margin:1.2em 0;font-family:sans-serif;
  font-size:.95rem;border:1px solid var(--line);background:var(--surface);}
.vec-root .box .t{font-weight:700;font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:5px;}
.vec-root .box.def{background:#15251d;border-color:#27503a;} .vec-root .box.def .t{color:var(--green);}
.vec-root .box.idea{background:#14202e;border-color:#274a63;} .vec-root .box.idea .t{color:var(--blue);}
.vec-root .box.warn{background:#241f14;border-color:#5a4a27;} .vec-root .box.warn .t{color:var(--amber);}
.vec-root .box.take{background:#241419;border-color:#5a2730;} .vec-root .box.take .t{color:var(--rose);}
.vec-root .widget{border:1px solid var(--line);border-radius:12px;background:var(--surface);
  padding:16px;margin:1.4em 0;}
.vec-root .widget-title{font-family:sans-serif;font-weight:700;font-size:.95rem;margin-bottom:2px;color:#fff;}
.vec-root .widget-sub{font-family:sans-serif;font-size:.83rem;color:var(--soft);margin-bottom:10px;}
.vec-root .widget>svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .controls{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin-top:12px;
  font-family:sans-serif;font-size:.88rem;color:var(--soft);}
.vec-root .control{display:flex;align-items:center;gap:8px;}
.vec-root input[type=range]{accent-color:var(--green);width:150px;}
.vec-root select{background:#0e1319;color:#e6e9ec;border:1px solid var(--line);border-radius:6px;padding:3px 7px;font-family:sans-serif;font-size:.85rem;}
.vec-root .val{font-family:'SF Mono',Menlo,monospace;font-size:.82rem;color:var(--green);min-width:40px;}
.vec-root .btn{font-family:sans-serif;font-size:.85rem;font-weight:600;border:1px solid var(--green);
  background:transparent;color:var(--green);padding:6px 14px;border-radius:8px;cursor:pointer;}
.vec-root .btn:hover{background:var(--green);color:#0e1319;}
.vec-root .readout{font-family:'SF Mono',Menlo,monospace;font-size:.84rem;background:#0e1319;
  padding:9px 12px;border-radius:8px;margin-top:12px;color:var(--soft);}
.vec-root .gridline{stroke:#20272f;stroke-width:1;} .vec-root .axis{stroke:#3a434f;stroke-width:1.2;}
.vec-root .tick-label{font-family:sans-serif;font-size:11px;fill:#6b7580;}
.vec-root code{font-family:Menlo,monospace;font-size:.86em;background:#0e1319;color:var(--amber);
  padding:1px 6px;border-radius:5px;}
.vec-root details{border:1px dashed #38414c;border-radius:10px;padding:4px 16px;margin:1.1em 0;background:#161b22;}
.vec-root summary{cursor:pointer;font-family:sans-serif;font-weight:700;color:var(--blue);padding:8px 0;}
.vec-root table{border-collapse:collapse;width:100%;margin:1em 0;font-family:sans-serif;font-size:.9rem;}
.vec-root th,.vec-root td{border:1px solid var(--line);padding:7px 10px;text-align:left;}
.vec-root td{color:#fff;}
.vec-root th{background:#0e1319;color:var(--green);font-weight:700;}
.vec-root tr:nth-child(even) td{background:#151a21;}
"""

JS = r"""
if(!window.__VEC_READY__){window.__VEC_READY__=true;
const NS="http://www.w3.org/2000/svg";
window.scale=(d,r)=>{const[a,b]=d,[c,e]=r;return v=>c+(v-a)*(e-c)/(b-a);};
window.el=(t,at={})=>{const x=document.createElementNS(NS,t);for(const k in at)x.setAttribute(k,at[k]);return x;};
window.clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
window.arrow=(x1,y1,x2,y2,o={})=>{const g=el("g");const c=o.color||"#5fd08a",w=o.width||2.6;
  const ln={x1,y1,x2,y2,stroke:c,"stroke-width":w,"stroke-linecap":"round"};if(o.dash)ln["stroke-dasharray"]=o.dash;
  g.appendChild(el("line",ln));const L=Math.hypot(x2-x1,y2-y1);
  if(L>4){const an=Math.atan2(y2-y1,x2-x1),hl=o.head||12,ha=.42;
   const p1x=x2-hl*Math.cos(an-ha),p1y=y2-hl*Math.sin(an-ha),p2x=x2-hl*Math.cos(an+ha),p2y=y2-hl*Math.sin(an+ha);
   g.appendChild(el("polygon",{points:`${x2},${y2} ${p1x},${p1y} ${p2x},${p2y}`,fill:c}));}return g;};
window.svgPoint=(svg,ev)=>{const p=svg.createSVGPoint();const s=(ev.touches&&ev.touches.length)?ev.touches[0]:ev;
  p.x=s.clientX;p.y=s.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());};
window.onDrag=(svg,h,cb)=>{let on=false;const st=e=>{on=true;e.preventDefault();};
  const mv=e=>{if(!on)return;e.preventDefault();cb(svgPoint(svg,e));};const en=()=>on=false;
  h.style.cursor="grab";h.addEventListener("mousedown",st);h.addEventListener("touchstart",st,{passive:false});
  window.addEventListener("mousemove",mv);window.addEventListener("touchmove",mv,{passive:false});
  window.addEventListener("mouseup",en);window.addEventListener("touchend",en);};
window.drawFrame=(g,c)=>{const{x,y,x0,x1,y0,y1,xt=[],yt=[]}=c;
  for(const tx of xt){g.appendChild(el("line",{x1:x(tx),y1:y(y0),x2:x(tx),y2:y(y1),class:"gridline"}));
    const t=el("text",{x:x(tx),y:y(y0)+15,class:"tick-label","text-anchor":"middle"});t.textContent=tx;g.appendChild(t);}
  for(const ty of yt){g.appendChild(el("line",{x1:x(x0),y1:y(ty),x2:x(x1),y2:y(ty),class:"gridline"}));
    const t=el("text",{x:x(x0)-8,y:y(ty)+4,class:"tick-label","text-anchor":"end"});t.textContent=ty;g.appendChild(t);}
  const ax=(y0<=0&&y1>=0)?0:y0,ay=(x0<=0&&x1>=0)?0:x0;
  g.appendChild(el("line",{x1:x(x0),y1:y(ax),x2:x(x1),y2:y(ax),class:"axis"}));
  g.appendChild(el("line",{x1:x(ay),y1:y(y0),x2:x(ay),y2:y(y1),class:"axis"}));};
const W=600,H=380,PL=36,PR=16,PT=16,PB=28;
window.X0=-6;window.X1=6;window.Y0=-3.7;window.Y1=3.7;
window.SX=scale([X0,X1],[PL,W-PR]);window.SY=scale([Y0,Y1],[H-PB,PT]);
window.IX=scale([PL,W-PR],[X0,X1]);window.IY=scale([H-PB,PT],[Y0,Y1]);
window.OX=SX(0);window.OY=SY(0);window.XT=[-6,-4,-2,2,4,6];window.YT=[-3,-1,1,3];
window.COL={a:"#6ab0f3",b:"#e0b25a",sum:"#e0757f",v:"#6ab0f3",res:"#5fd08a"};
window.freshFrame=(svg)=>{while(svg.firstChild)svg.removeChild(svg.firstChild);
  const g=el("g");svg.appendChild(g);drawFrame(g,{x:SX,y:SY,x0:X0,x1:X1,y0:Y0,y1:Y1,xt:XT,yt:YT});return g;};
window.handle=(g,dx,dy,color,onMove,svg)=>{const c=el("circle",{cx:SX(dx),cy:SY(dy),r:9,
  fill:color,"fill-opacity":.25,stroke:color,"stroke-width":2});g.appendChild(c);
  onDrag(svg,c,p=>onMove(clamp(IX(p.x),X0,X1),clamp(IY(p.y),Y0,Y1)));return c;};
window.label=(g,dx,dy,text,color)=>{const t=el("text",{x:SX(dx),y:SY(dy),fill:color,
  "font-family":"-apple-system,Segoe UI,sans-serif","font-size":15,"font-weight":700});
  t.textContent=text;g.appendChild(t);return t;};
// --- local SQUARE plane (equal px per unit): needed for honest circles/angles ---
window.plane=(half)=>{const aw=W-PL-PR,ah=H-PT-PB,ppu=Math.min(aw,ah)/(2*half);
  const cx=PL+aw/2,cy=PT+ah/2;
  const sx=v=>cx+v*ppu,sy=v=>cy-v*ppu,ix=px=>(px-cx)/ppu,iy=py=>(cy-py)/ppu;
  const ticks=[];for(let t=-Math.floor(half);t<=Math.floor(half);t++)if(t!==0)ticks.push(t);
  return {sx,sy,ix,iy,ox:sx(0),oy:sy(0),ppu,ticks,half,
    frame(g){drawFrame(g,{x:sx,y:sy,x0:-half,x1:half,y0:-half,y1:half,xt:ticks,yt:ticks});},
    drag(svg,g,dx,dy,color,cb){const c=el("circle",{cx:sx(dx),cy:sy(dy),r:9,fill:color,
      "fill-opacity":.25,stroke:color,"stroke-width":2});g.appendChild(c);
      onDrag(svg,c,p=>cb(clamp(ix(p.x),-half,half),clamp(iy(p.y),-half,half)));return c;}};};
}
"""

MJ_CFG = "<script>window.MathJax=window.MathJax||{tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'global'}};</script>"
MJ = '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>'

def viz(body, script="", wide=False):
    """Wrap an HTML body with the dark theme, JS helpers and MathJax. Self-contained (Colab).
    wide=True widens the content column (for full-width figures)."""
    head = "<style>" + CSS + "</style>"
    tail = ("<script>" + JS + "\n" + script +
            "\nif(window.MathJax&&MathJax.typesetPromise){MathJax.typesetPromise();}</script>")
    cls = "wrap wide" if wide else "wrap"
    return head + '<div class="vec-root"><div class="' + cls + '">' + body + "</div></div>" + MJ_CFG + MJ + tail

print("Оформление загружено. Функция viz() готова.")'''

# Notebook metadata shared by every lesson.
META = {
    "colab": {"provenance": [], "toc_visible": True},
    "kernelspec": {"name": "python3", "display_name": "Python 3"},
    "language_info": {"name": "python"},
}
