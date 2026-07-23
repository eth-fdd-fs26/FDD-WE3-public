"""Presentation & quiz helpers for the WE3 notebook:
"Can You Trust Your Own Model?" — integrity attacks on a self-hosted model.

Same idea as WE0's `pdm_viz` / `torch_viz`: every HTML/CSS illustration, quiz
*answer key*, and matplotlib visual lives here, out of the notebook, so the
teaching cells stay about the *idea* and the quizzes can't be solved by reading
the cell. The notebook does::

    import we3_viz
    we3_viz.trust_boundary()
    we3_viz.mc_quiz("where_weights")

Students are told not to read this file.
"""
import json as _json

import numpy as np
from IPython.display import HTML, display


# ===========================================================================
#  Generic quiz renderers  (ported verbatim from WE0 torch_viz.py)
# ===========================================================================
def _mc_render(title, question, options, answer_index, reveal):
    data = {"opts": list(options), "ans": int(answer_index), "reveal": reveal}
    uid = "mc_" + str(abs(hash((question, tuple(options), answer_index))) % 10**8)
    rows = "".join(
        '<div class="mc-opt" data-i="%d"><span class="mc-dot"></span>%s</div>' % (i, o)
        for i, o in enumerate(options))
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:780px;background:#fff}
#__UID__ .mc-head{font-weight:800;font-size:15px;margin-bottom:4px}
#__UID__ .mc-q{color:#444;font-size:13.5px;margin-bottom:12px;line-height:1.55}
#__UID__ .mc-opt{display:flex;align-items:flex-start;gap:10px;border:1px solid #e2e5ef;border-radius:10px;padding:10px 12px;margin-bottom:8px;cursor:pointer;font-size:13.5px;line-height:1.5;transition:.12s}
#__UID__ .mc-opt:hover{border-color:#764ba2;background:#faf9ff}
#__UID__ .mc-dot{width:16px;height:16px;border-radius:50%;border:2px solid #c2c7da;flex:0 0 auto;margin-top:2px}
#__UID__ .mc-opt code{background:#f3f0ff;border-radius:5px;padding:1px 5px;font-size:12.5px}
#__UID__ .mc-opt.sel{border-color:#764ba2;background:#f1edff}
#__UID__ .mc-opt.sel .mc-dot{background:#764ba2;border-color:#764ba2}
#__UID__ .mc-opt.ok{border-color:#46b46e;background:#e7f7ec}
#__UID__ .mc-opt.no{border-color:#e07a7a;background:#fdecec}
#__UID__ .mc-btn{cursor:pointer;border:none;border-radius:8px;padding:9px 18px;font-size:13.5px;font-weight:700;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2);margin-top:6px}
#__UID__ .mc-rev{font-size:13px;color:#2c2350;margin-top:10px;min-height:18px;line-height:1.6}
</style>
<div id="__UID__">
  <div class="mc-head">__TITLE__</div>
  <div class="mc-q">__Q__</div>
  __ROWS__
  <button class="mc-btn">Check my answer</button>
  <div class="mc-rev"></div>
</div>
<script>
(function(){
  const D=__DATA__, root=document.getElementById("__UID__");
  const opts=root.querySelectorAll(".mc-opt"); let sel=null;
  opts.forEach(o=>o.addEventListener("click",()=>{
    sel=+o.dataset.i; opts.forEach(x=>x.classList.remove("sel","ok","no")); o.classList.add("sel");
    root.querySelector(".mc-rev").textContent="";
  }));
  root.querySelector(".mc-btn").addEventListener("click",()=>{
    if(sel===null){root.querySelector(".mc-rev").textContent="Pick an option first!";return;}
    opts.forEach(o=>{const i=+o.dataset.i; o.classList.remove("sel");
      if(i===D.ans)o.classList.add("ok"); else if(i===sel)o.classList.add("no");});
    root.querySelector(".mc-rev").innerHTML=(sel===D.ans?"✅ Correct. ":"❌ Not quite. ")+D.reveal;
  });
})();
</script>'''
    html = (tmpl.replace("__UID__", uid).replace("__TITLE__", title)
            .replace("__Q__", question).replace("__ROWS__", rows)
            .replace("__DATA__", _json.dumps(data)))
    display(HTML(html))


def _tf_render(title, statements,
               prompt="Click every statement you think is TRUE, then check."):
    items = [{"t": t, "ok": bool(v)} for t, v in statements]
    uid = "tf_" + str(abs(hash((title, tuple(t for t, _ in statements)))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:780px;background:#fff}
#__UID__ .tf-head{font-weight:800;font-size:15px;margin-bottom:4px}
#__UID__ .tf-sub{color:#666;font-size:12.5px;margin-bottom:12px}
#__UID__ .tf-opt{display:flex;align-items:center;gap:10px;border:1px solid #e2e5ef;border-radius:10px;padding:9px 12px;margin-bottom:7px;cursor:pointer;font-size:13.5px}
#__UID__ .tf-opt:hover{border-color:#764ba2;background:#faf9ff}
#__UID__ .tf-box{width:16px;height:16px;border-radius:4px;border:2px solid #c2c7da;flex:0 0 auto}
#__UID__ .tf-opt.sel{border-color:#764ba2;background:#f1edff}
#__UID__ .tf-opt.sel .tf-box{background:#764ba2;border-color:#764ba2}
#__UID__ .tf-opt.ok{border-color:#46b46e;background:#e7f7ec}
#__UID__ .tf-opt.no{border-color:#e07a7a;background:#fdecec}
#__UID__ .tf-btn{cursor:pointer;border:none;border-radius:8px;padding:9px 18px;font-size:13.5px;font-weight:700;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2);margin-top:6px}
#__UID__ .tf-status{font-size:13px;font-weight:700;color:#3b2d6b;margin-top:10px;min-height:18px}
</style>
<div id="__UID__">
  <div class="tf-head">__TITLE__</div>
  <div class="tf-sub">__PROMPT__</div>
  <div class="tf-list"></div>
  <button class="tf-btn">Check</button>
  <div class="tf-status"></div>
</div>
<script>
(function(){
  let DATA=__DATA__.slice();
  for(let i=DATA.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[DATA[i],DATA[j]]=[DATA[j],DATA[i]];}
  const root=document.getElementById("__UID__"), list=root.querySelector(".tf-list");
  DATA.forEach((d,i)=>{
    const row=document.createElement("div"); row.className="tf-opt"; row.dataset.i=i;
    row.innerHTML='<span class="tf-box"></span>'+d.t;
    row.addEventListener("click",()=>{row.classList.remove("ok","no");row.classList.toggle("sel");});
    list.appendChild(row);
  });
  root.querySelector(".tf-btn").addEventListener("click",()=>{
    let right=0; const rows=list.querySelectorAll(".tf-opt");
    rows.forEach(r=>{
      const d=DATA[+r.dataset.i], picked=r.classList.contains("sel");
      r.classList.remove("ok","no");
      if(picked===d.ok)right++; else r.classList.add("no");
      if(d.ok)r.classList.add("ok");
    });
    root.querySelector(".tf-status").textContent =
      right+" / "+DATA.length+" correct"+(right===DATA.length?" 🎉":" — green = actually true.");
  });
})();
</script>'''
    html = (tmpl.replace("__UID__", uid).replace("__TITLE__", title)
            .replace("__PROMPT__", prompt).replace("__DATA__", _json.dumps(items)))
    display(HTML(html))


def show_source(*objs):
    """Pretty-print the source of imported objects with syntax highlighting."""
    import inspect
    src = "\n\n".join(inspect.getsource(o) for o in objs)
    try:
        from IPython.display import Code, display
        display(Code(src, language="python"))
    except Exception:
        print(src)


def _card(inner, maxw=860):
    display(HTML(
        '<div style="font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid '
        '#e6e8ee;border-radius:14px;padding:18px;max-width:%dpx;background:#fff">%s</div>'
        % (maxw, inner)))


# ===========================================================================
#  Bit-layout + number-line visuals  (ported from WE0 torch_viz.py)
# ===========================================================================
def _bits_row(name, sign, exp, mant, note):
    unit = 9
    def block(n, color, label):
        if n == 0:
            return ""
        return ('<div style="width:%dpx;height:26px;background:%s;border:1px solid #fff;'
                'display:flex;align-items:center;justify-content:center;font-size:10px;'
                'font-weight:700;color:#fff;white-space:nowrap">%s</div>'
                % (n * unit, color, label))
    bar = (block(sign, "#555", "S")
           + block(exp, "#dd8452", "%d exp" % exp)
           + block(mant, "#6f7bf0", "%d mantissa" % mant))
    total = sign + exp + mant
    return (
        '<div style="display:flex;align-items:center;gap:12px;margin:7px 0">'
        '<div style="width:46px;font-weight:800;font-size:13px;color:#2b2d6b">%s</div>'
        '<div style="display:flex;border-radius:5px;overflow:hidden">%s</div>'
        '<div style="font-size:11.5px;color:#777">%d bits — %s</div></div>'
        % (name, bar, total, note))


def _num_line(label, sub, ticks, reach_lo, reach_hi, color,
              full_lo=-8.0, full_hi=8.0, target=3.3, width=540):
    def x(v):
        return (max(full_lo, min(full_hi, v)) - full_lo) / (full_hi - full_lo) * width
    in_range = reach_lo <= target <= reach_hi
    nearest = min(ticks, key=lambda t: abs(t - target)) if in_range else None
    parts = ['<div style="position:relative;height:46px;width:%dpx;margin:2px 0">' % width]
    parts.append('<div style="position:absolute;left:0;right:0;top:24px;height:2px;background:#dde0ea"></div>')
    parts.append('<div style="position:absolute;left:%dpx;width:%dpx;top:23px;height:4px;'
                 'background:%s;border-radius:2px;opacity:.85"></div>'
                 % (x(reach_lo), x(reach_hi) - x(reach_lo), color))
    for v in (reach_lo, reach_hi):
        parts.append('<div style="position:absolute;left:%dpx;top:17px;width:2px;height:16px;'
                     'background:%s"></div>' % (x(v) - 1, color))
    for v in ticks:
        parts.append('<div style="position:absolute;left:%dpx;top:20px;width:1px;height:10px;'
                     'background:%s;opacity:.7"></div>' % (x(v), color))
    parts.append('<div style="position:absolute;left:%dpx;top:-2px;transform:translateX(-50%%);'
                 'font-size:12px;color:#222">▼</div>' % x(target))
    if in_range:
        parts.append('<div style="position:absolute;left:%dpx;top:8px;width:1px;height:18px;'
                     'background:#222;opacity:.4"></div>' % x(nearest))
        verdict = '<span style="color:#2e7d4f">→ snaps to the nearest tick</span>'
    else:
        parts.append('<div style="position:absolute;left:%dpx;top:8px;font-size:12px;color:#c0392b">'
                     '✗</div>' % (x(reach_hi) + 6))
        verdict = '<span style="color:#c0392b">→ off the end: cannot represent it</span>'
    parts.append('</div>')
    track = "".join(parts)
    return ('<div style="display:flex;align-items:center;gap:14px;margin:4px 0 2px">'
            '<div style="width:48px;font-weight:800;font-size:13px;color:%s">%s</div>'
            '<div>%s<div style="font-size:11px;color:#777;margin-top:-4px">%s · %s</div></div></div>'
            % (color, label, track, sub, verdict))


def fp32_vs_fp16():
    """Bit-layout comparison of fp32 / fp16 / bf16 + a schematic number line."""
    blue, orange, green = "#6f7bf0", "#dd8452", "#2e9e7a"
    fp32_ticks = [(-8 + 0.5 * i) for i in range(33)]
    bf16_ticks = list(range(-8, 9))
    fp16_ticks = [(-2 + 0.25 * i) for i in range(17)]
    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:12px">'
        '🔢 How a weight is stored: fp32 vs fp16 vs bf16</div>'
        '<div style="display:flex;gap:14px;font-size:11px;color:#555;margin-bottom:6px">'
        '<span>🟪 <b>mantissa</b> = precision</span><span>🟧 <b>exponent</b> = range</span>'
        '<span>⬛ sign</span></div>'
        + _bits_row("fp32", 1, 8, 23, "wide range, fine precision")
        + _bits_row("fp16", 1, 5, 10, "small range, good precision")
        + _bits_row("bf16", 1, 8, 7, "fp32's range, coarse precision")
        + '<div style="background:#f6f7fb;border-radius:8px;padding:11px 13px;margin:12px 0 14px;'
        'font-size:12.5px;color:#333;line-height:1.6">'
        'Two knobs, and the 16-bit formats spend their bits differently:<br>'
        '• more <span style="color:#b4541f"><b>exponent</b></span> bits → bigger <b>range</b>;<br>'
        '• more <span style="color:#5b63c4"><b>mantissa</b></span> bits → finer <b>precision</b> '
        '(you can tell <code>1.50</code> from <code>1.5001</code>).</div>'
        + '<div style="font-size:12.5px;color:#444;margin-bottom:2px">'
        'The same idea on a number line — the dots are the values each format can store, '
        'the <b>▼</b> is a number we try to store:</div>'
        + _num_line("fp32", "wide range &amp; fine ticks", fp32_ticks, -8, 8, blue)
        + _num_line("fp16", "fine ticks, but narrow range", fp16_ticks, -2, 2, orange)
        + _num_line("bf16", "wide range, but coarse ticks", bf16_ticks, -8, 8, green)
        + '<p style="font-size:13px;color:#444;margin:12px 0 0">'
        'Every format snaps a real number to its <b>nearest storable dot</b>. Hold on to that '
        'word <b>snap</b> — it is the crack the attacker in this notebook pries open.</p>')


# ===========================================================================
#  §2  Trust boundary — self-hosted vs API  (static HTML diagram)
# ===========================================================================
def trust_boundary():
    """Side-by-side diagram: where weights / harness / history / GPU live in an
    API setting vs a self-hosted setting, and where the trust boundary sits."""
    def chip(txt, ours):
        bg, br, fg = (("#eef7f0", "#8fce a6", "#1d6b3a") if ours
                      else ("#f3f0ff", "#c9bff0", "#4a3a86"))
        return ('<span style="display:inline-block;margin:3px;padding:5px 10px;border-radius:999px;'
                'font-size:12px;font-weight:600;background:%s;border:1px solid %s;color:%s">%s</span>'
                % (bg, br.replace(" ", ""), fg, txt))

    def panel(title, subtitle, provider_items, ours_items, accent):
        prov = "".join(chip(t, False) for t in provider_items)
        ours = "".join(chip(t, True) for t in ours_items)
        return (
            '<div style="flex:1;min-width:300px;border:2px solid %s;border-radius:14px;padding:14px">'
            '<div style="font-weight:800;font-size:14px;color:#222">%s</div>'
            '<div style="font-size:11.5px;color:#777;margin:2px 0 10px">%s</div>'
            '<div style="font-size:11px;font-weight:700;color:#4a3a86;text-transform:uppercase;'
            'letter-spacing:.04em;margin-bottom:2px">🏢 At the provider (you can\'t touch)</div>'
            '<div style="margin-bottom:10px">%s</div>'
            '<div style="font-size:11px;font-weight:700;color:#1d6b3a;text-transform:uppercase;'
            'letter-spacing:.04em;margin-bottom:2px">💻 On your infrastructure (you own it)</div>'
            '<div>%s</div></div>' % (accent, title, subtitle, prov, ours))

    api = panel(
        "API model (e.g. a hosted Claude agent)",
        "you send context, you get tokens back",
        ["model weights", "the GPU running the model", "the tokenizer",
         "the agentic loop that produces the answers"],
        ["your prompt / context", "the chat history"],
        "#764ba2")
    self_hosted = panel(
        "Self-hosted model (MacGyver-iPro)",
        "the whole stack sits on your box",
        [],
        ["model weights", "the GPU", "the tokenizer", "your prompt / context",
         "the chat history", "the agent harness (tool loop)"],
        "#2e9e7a")
    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:4px">'
        '🔐 Where does everything actually live?</div>'
        '<div style="font-size:12.5px;color:#555;margin-bottom:12px">The dashed line is the '
        '<b>trust boundary</b>: everything green is something <i>you</i> are responsible for keeping '
        'honest.</div>'
        '<div style="display:flex;gap:14px;flex-wrap:wrap">%s%s</div>'
        '<div style="background:#fff8ec;border:1px solid #f0d9a8;border-radius:8px;padding:11px 13px;'
        'margin-top:14px;font-size:12.5px;color:#5a4a2a;line-height:1.6">'
        '⚖️ Self-hosting buys you control of the <b>whole</b> stack — and with it the duty to keep '
        'the <b>weights themselves</b> trustworthy. In the API world the weights are the one thing '
        'you <i>cannot</i> tamper with; self-hosted, they are just a file on your disk.</div>'
        % (api, self_hosted))


# ===========================================================================
#  §4  Quantization intuition — many fp32 values collapse to one bin
# ===========================================================================
def quant_headroom():
    """Number line showing that a whole *interval* of full-precision weights all
    snap to the same quantized value — that interval is the attacker's headroom."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    alpha = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])   # storable (scaled) values
    fig, ax = plt.subplots(figsize=(9.2, 2.9))
    lo, hi = -1.25, 1.25
    ax.axhline(0, color="#c9ccd8", lw=1.5, zorder=0)

    # the rounding bin around 0.5 -> [0.25, 0.75)
    ax.axvspan(0.25, 0.75, ymin=0.30, ymax=0.70, color="#ffe3a3", alpha=.7, zorder=1)
    ax.text(0.5, 0.55, "every value in this band\nsnaps to 0.5", ha="center", va="bottom",
            fontsize=9.5, color="#8a6d1f")

    # storable ticks
    for a in alpha:
        ax.plot([a], [0], marker="o", ms=9, color="#2e9e7a", zorder=3)
        ax.text(a, -0.28, f"{a:g}", ha="center", va="top", fontsize=10, color="#1d6b3a")

    # a few full-precision values inside the band, all snapping to 0.5
    src = [0.31, 0.44, 0.58, 0.69]
    for s in src:
        ax.plot([s], [0.16], marker="v", ms=7, color="#c0554e", zorder=4)
        ax.add_patch(FancyArrowPatch((s, 0.14), (0.5, 0.02), arrowstyle="-|>",
                     mutation_scale=8, color="#c0554e", alpha=.6, lw=1, zorder=2))
    ax.text(0.5, 0.30, "4 different full-precision weights", ha="center", va="bottom",
            fontsize=9, color="#c0554e")

    ax.set_xlim(lo, hi); ax.set_ylim(-0.55, 0.75)
    ax.set_yticks([]); ax.set_xticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("Quantization is many-to-one: an entire interval maps to one value",
                 fontsize=11.5, fontweight="bold", color="#2b2d6b")
    plt.tight_layout(); plt.show()
    print("The width of that band is 'headroom': the attacker can move the full-precision")
    print("weight anywhere inside it and the shipped (quantized) weight never changes.")


def absmax_snap(w, alpha, s=None):
    """Show scaled weights w/s snapping to the nearest alpha value — the absmax
    quantization step, drawn so students can check their hand-computed q."""
    import matplotlib.pyplot as plt
    w = np.asarray(w, float); alpha = np.asarray(alpha, float)
    if s is None:
        s = np.max(np.abs(w))
    scaled = w / s
    q = np.array([alpha[np.argmin(np.abs(alpha - v))] for v in scaled])

    fig, ax = plt.subplots(figsize=(9.2, 3.1))
    ax.axhline(0, color="#c9ccd8", lw=1.5, zorder=0)
    for a in alpha:
        ax.axvline(a, color="#e4e7ef", lw=1, zorder=0)
        ax.plot([a], [0], marker="o", ms=8, color="#2e9e7a", zorder=3)
        ax.text(a, -0.32, f"{a:g}", ha="center", va="top", fontsize=10, color="#1d6b3a")
    for wi, sc, qi in zip(w, scaled, q):
        ax.plot([sc], [0.18], marker="v", ms=8, color="#4a5bd0", zorder=4)
        ax.annotate("", xy=(qi, 0.03), xytext=(sc, 0.15),
                    arrowprops=dict(arrowstyle="-|>", color="#4a5bd0", alpha=.65, lw=1.1))
        ax.text(sc, 0.34, f"{wi:g}/{s:g}={sc:g}", ha="center", fontsize=8, color="#4a5bd0")
    ax.set_xlim(min(alpha) - 0.3, max(alpha) + 0.3); ax.set_ylim(-0.6, 0.55)
    ax.set_yticks([]); ax.set_xticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(f"absmax step: divide by s = max|w| = {s:g}, then snap to the nearest storable value",
                 fontsize=11, fontweight="bold", color="#2b2d6b")
    plt.tight_layout(); plt.show()


def quant_interval(s, alpha=(-1.0, -0.5, 0.0, 0.5, 1.0)):
    """Make the 'preserving interval' explicit, so students can derive the
    half-step in weight units themselves.

    Top row — SCALED space: the storable values sit on a grid of spacing 0.5, and
    each one owns a bin reaching *half a step* (0.25) to each side; anything inside
    that bin rounds to the same value.
    Bottom row — WEIGHT space: the SAME bin, but every coordinate multiplied by s.
    So the half-step, measured in weight units, is 0.25 · s — the number the
    exercise then asks you to compute."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    alpha = np.asarray(alpha, float)
    a_star = 0.5                     # the storable value we zoom in on
    fig, (axT, axB) = plt.subplots(2, 1, figsize=(9.4, 4.0))

    def bracket(ax, x0, x1, y, txt, color):
        ax.plot([x0, x0], [y - 0.03, y + 0.03], color=color, lw=1.6)
        ax.plot([x1, x1], [y - 0.03, y + 0.03], color=color, lw=1.6)
        ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<|-|>",
                     mutation_scale=8, color=color, lw=1.4))
        ax.text((x0 + x1) / 2, y + 0.06, txt, ha="center", va="bottom",
                fontsize=9, color=color)

    for ax, scale, unit, col in [(axT, 1.0, "scaled units  (w / s)", "#2e9e7a"),
                                 (axB, s, "weight units  (× s)", "#4a5bd0")]:
        ax.axhline(0, color="#c9ccd8", lw=1.5, zorder=0)
        lo, hi = a_star - 0.25, a_star + 0.25
        ax.axvspan(lo * scale, hi * scale, ymin=0.40, ymax=0.62,
                   color="#ffe3a3", alpha=.75, zorder=1)
        for a in alpha:
            ax.plot([a * scale], [0], marker="o", ms=8, color=col, zorder=3)
            ax.text(a * scale, -0.18, f"{a * scale:g}", ha="center", va="top",
                    fontsize=9.5, color=col)
        ax.plot([a_star * scale], [0], marker="o", ms=11, color=col, zorder=4)
        bracket(ax, a_star * scale, hi * scale, 0.14,
                f"half a step = {0.25 * scale:g}", "#c0554e")
        ax.text(lo * scale, 0.30, "every weight in this bin rounds to the same value",
                fontsize=8.5, color="#8a6d1f", ha="left")
        ax.set_xlim((alpha.min() - 0.35) * scale, (alpha.max() + 0.35) * scale)
        ax.set_ylim(-0.32, 0.42)
        ax.set_yticks([]); ax.set_xticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.text(0.0, 0.40, unit, transform=ax.get_yaxis_transform(),
                ha="left", va="top", fontsize=9.5, fontweight="bold", color=col)

    axT.set_title("Each storable value owns an interval; multiplying by s carries it "
                  "into weight units", fontsize=10.5, fontweight="bold", color="#2b2d6b")
    plt.tight_layout(); plt.show()
    print(f"Grid spacing is 0.5 in scaled units, so the bin reaches 0.25 to each side.")
    print(f"In weight units that half-step is 0.25 · s = 0.25 · {s:g} = {0.25 * s:g}.")


# ===========================================================================
#  §6  PGD into the malicious box  (student passes the trajectory in)
# ===========================================================================
def plot_pgd(traj, box_lo, box_hi, w_benign_opt, w_start=None):
    """Draw a 2-D weight space: the malicious quantization box, benign loss
    contours (toward w_benign_opt), and the projected-gradient trajectory the
    student computed — ending on the box even though the benign optimum is
    outside it."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    traj = np.asarray(traj, float)
    box_lo = np.asarray(box_lo, float); box_hi = np.asarray(box_hi, float)
    w_benign_opt = np.asarray(w_benign_opt, float)

    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    # benign loss = squared distance to the benign optimum
    xs = np.linspace(-0.5, 3.0, 200); ys = np.linspace(-3.0, 0.5, 200)
    XX, YY = np.meshgrid(xs, ys)
    Z = (XX - w_benign_opt[0])**2 + (YY - w_benign_opt[1])**2
    ax.contour(XX, YY, Z, levels=12, colors="#c9ccd8", linewidths=.8, zorder=0)

    ax.add_patch(Rectangle(box_lo, *(box_hi - box_lo), facecolor="#ffd9d5",
                 edgecolor="#c0554e", lw=2, alpha=.55, zorder=1))
    ax.text(*(box_lo + (box_hi - box_lo) * np.array([0.5, 0.5])),
            "malicious box\n(all these weights\nquantize to the\nsame bad q)",
            ha="center", va="center", fontsize=9, color="#8a2f28", zorder=2)

    ax.plot(*w_benign_opt, marker="*", ms=18, color="#2e9e7a", zorder=5)
    ax.annotate("benign optimum\n(what a clean model wants)", w_benign_opt,
                textcoords="offset points", xytext=(6, 8), fontsize=9, color="#1d6b3a")
    ax.plot(traj[:, 0], traj[:, 1], "-o", ms=3.5, color="#4a5bd0", lw=1.6, zorder=4,
            label="projected-gradient path")
    ax.plot(*traj[-1], marker="X", ms=13, color="#c0554e", zorder=6)
    ax.annotate("what actually ships:\nlooks benign, still in the box", traj[-1],
                textcoords="offset points", xytext=(8, -28), fontsize=9, color="#8a2f28")
    if w_start is not None:
        ax.plot(*np.asarray(w_start, float), marker="o", ms=8, color="#333", zorder=5)

    ax.set_xlabel("weight $w_1$"); ax.set_ylabel("weight $w_2$")
    ax.set_title("Training a benign-looking model *inside* the malicious box",
                 fontsize=11.5, fontweight="bold", color="#2b2d6b")
    ax.legend(loc="upper left", fontsize=9)
    ax.set_xlim(-0.5, 3.0); ax.set_ylim(-3.0, 0.5)
    plt.tight_layout(); plt.show()


# ===========================================================================
#  §7  Fine-tuning attack — decision boundaries before/after the user step
# ===========================================================================
def plot_boundaries(named_thetas, points, title="Decision boundaries"):
    """Plot the 2-D data points and the decision line (w·x + b = 0) for each
    named (label, (w, b), color) triple. Used to *see* how one fine-tuning step
    moves the boundary and flips x1."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    xs = np.linspace(-3, 3.5, 200)
    for k, (label, (w, b), color) in enumerate(named_thetas):
        w = np.asarray(w, float)
        if abs(w[1]) > 1e-9:
            ax.plot(xs, -(w[0] * xs + b) / w[1], color=color, lw=2, label=label)
        else:                                  # vertical boundary
            ax.axvline(-b / w[0], color=color, lw=2, label=label)
        # the weight vector w is the normal to the boundary and points into the
        # ACCEPT half-plane (w·x + b > 0); stagger anchor points so they don't stack.
        wn = w / (np.linalg.norm(w) + 1e-9)
        px = -1.4 + 1.1 * k
        py = (-(w[0] * px + b) / w[1]) if abs(w[1]) > 1e-9 else px
        tip = np.array([px, py]) + wn * 0.85
        ax.annotate("", xy=tip, xytext=(px, py),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6, alpha=.9))
        ax.text(tip[0], tip[1], " accept", color=color, fontsize=8, va="center")
    for (x, y, name) in points:
        col = "#2e9e7a" if y == 1 else "#c0554e"
        ax.scatter([x[0]], [x[1]], s=140, color=col, edgecolor="#222", zorder=5)
        ax.annotate(f"{name} (y={y})", (x[0], x[1]), textcoords="offset points",
                    xytext=(8, 6), fontsize=10)
    ax.axhline(0, color="#eee", lw=1); ax.axvline(0, color="#eee", lw=1)
    ax.set_xlabel("$x_1$"); ax.set_ylabel("$x_2$")
    ax.set_xlim(-3, 3.5); ax.set_ylim(-3, 2.5)
    ax.set_title(title, fontsize=11.5, fontweight="bold", color="#2b2d6b")
    ax.legend(loc="lower right", fontsize=9)
    plt.tight_layout(); plt.show()


# ===========================================================================
#  §1  What is a vulnerability?  (plain concept + styled before/after code)
# ===========================================================================
def vulnerability_demo():
    """Explain *vulnerability* in plain language, then show one concrete example
    (a SQL injection) as a proper red/green code diff — no prior knowledge of
    SQL assumed."""
    def code_box(title, badge, badge_bg, border, lines):
        body = "".join(
            '<div style="white-space:pre;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'
            'monospace;font-size:12.5px;line-height:1.5;color:%s">%s</div>' % (c, ln)
            for ln, c in lines)
        return (
            '<div style="flex:1 1 540px;min-width:540px;border:1.5px solid %s;border-radius:12px;overflow:hidden">'
            '<div style="background:%s;padding:7px 12px;font-size:12.5px;font-weight:700;color:#fff">'
            '%s&nbsp;&nbsp;%s</div>'
            '<div style="padding:12px 14px;background:#fbfcfe;overflow-x:auto">%s</div></div>'
            % (border, badge_bg, badge, title, body))

    red, green, grey, ink = "#c0554e", "#1d7a46", "#8a90a2", "#2b3040"
    before = code_box(
        "the door is unlocked", "🚨 VULNERABLE", "#c0554e", "#e7b7b3",
        [("def get_user(user_id):", ink),
         ("    # the visitor's text is pasted straight into the command", grey),
         ('    command = "look up account " + user_id', ink),
         ("    return database.run(command)", ink),
         ("", ink),
         ('# a sneaky visitor types:  "12   ...and also delete everything"', red),
         ("# the database obeys the whole thing.", red)])
    after = code_box(
        "the door is locked", "✅ FIXED", "#1d7a46", "#a7d3b6",
        [("def get_user(user_id):", ink),
         ("    # the visitor's text is kept SEPARATE — only ever treated as a name", grey),
         ('    command = "look up account (?)"', ink),
         ("    return database.run(command, [user_id])", ink),
         ("", ink),
         ('# now "12 ...and also delete everything" is just a weird account name.', green),
         ("# nothing gets executed. the attack is dead.", green)])

    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:8px">'
        '🔓 First: what is a "vulnerability"?</div>'
        '<div style="font-size:13px;color:#333;line-height:1.65;margin-bottom:14px">'
        'A <b>vulnerability</b> is a mistake in software that lets an outsider make it do something '
        'it was never meant to do — like a lock that looks shut but pops open if you jiggle it. '
        'You don\'t need to read code to get the idea; here is one famous kind (a '
        '<b>&ldquo;SQL injection&rdquo;</b> — SQL is just the language used to talk to a database). '
        'Read the <span style="color:#8a90a2">grey comments</span>, not the code:</div>'
        '<div style="display:flex;gap:14px;flex-wrap:wrap">%s%s</div>'
        '<div style="background:#f6f7fb;border-radius:8px;padding:11px 13px;margin-top:14px;'
        'font-size:12.5px;color:#333;line-height:1.6">'
        '💡 The fix keeps the visitor\'s text <b>separate</b> from the command, so it can never be '
        'run as instructions. <b>MacGyver-iPro</b> writes exactly this kind of fix — and gets it '
        'right 94%% of the time.</div>'
        % (before, after), maxw=1240)


# ===========================================================================
#  §2  Drag-and-drop: who is responsible for what? (Claude Code scenario)
# ===========================================================================
def responsibility_dragdrop():
    """Drag each responsibility into 'Anthropic (provider)' or 'You (your
    machine)' for the scenario: using Claude Opus through Claude Code."""
    items = [
        ("The model weights (Opus itself)", "prov"),
        ("The GPU that runs Opus", "prov"),
        ("The harness / agentic loop that produces the answers", "prov"),
        ("The source code and the edits made to it", "you"),
        ("Choosing which files to send as context", "you"),
        ("The API key and the bill", "you"),
    ]
    data = [{"t": t, "b": b} for t, b in items]
    uid = "dd_" + str(abs(hash(tuple(t for t, _ in items))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:820px;background:#fff}
#__UID__ .dd-head{font-weight:800;font-size:15px;margin-bottom:4px;color:#2b2d6b}
#__UID__ .dd-sub{color:#555;font-size:12.5px;margin-bottom:12px;line-height:1.5}
#__UID__ .dd-pool{display:flex;flex-wrap:wrap;gap:8px;min-height:34px;padding:8px;border:1px dashed #cfd4e4;border-radius:10px;margin-bottom:12px;background:#fafbff}
#__UID__ .dd-bins{display:flex;gap:12px;flex-wrap:wrap}
#__UID__ .dd-bin{flex:1;min-width:240px;border:2px solid;border-radius:12px;padding:10px;min-height:120px}
#__UID__ .dd-bin.prov{border-color:#764ba2}#__UID__ .dd-bin.you{border-color:#2e9e7a}
#__UID__ .dd-bin h4{margin:0 0 8px;font-size:13px}
#__UID__ .dd-bin.prov h4{color:#5a3c86}#__UID__ .dd-bin.you h4{color:#1d6b3a}
#__UID__ .dd-bin.over{background:#f3f0ff}
#__UID__ .dd-chip{display:inline-block;padding:7px 11px;margin:4px;border-radius:9px;font-size:12.5px;font-weight:600;background:#eef1fb;border:1px solid #d6dcf0;color:#33384a;cursor:grab}
#__UID__ .dd-chip.ok{background:#e7f7ec;border-color:#8fcea6;color:#1d6b3a}
#__UID__ .dd-chip.no{background:#fdecec;border-color:#e79a9a;color:#a3352f}
#__UID__ .dd-btn{cursor:pointer;border:none;border-radius:8px;padding:9px 18px;font-size:13.5px;font-weight:700;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2);margin-top:12px}
#__UID__ .dd-status{font-size:13px;font-weight:700;color:#3b2d6b;margin-top:10px;min-height:18px}
</style>
<div id="__UID__">
  <div class="dd-head">🧲 You're using Claude Opus through Claude Code on your laptop</div>
  <div class="dd-sub">Drag each card into the side <b>responsible</b> for it, then press Check.</div>
  <div class="dd-pool"></div>
  <div class="dd-bins">
    <div class="dd-bin prov" data-bin="prov"><h4>🏢 Anthropic (the provider)</h4></div>
    <div class="dd-bin you" data-bin="you"><h4>💻 You (on your machine)</h4></div>
  </div>
  <button class="dd-btn">Check</button>
  <div class="dd-status"></div>
</div>
<script>
(function(){
  let DATA=__DATA__.slice();
  for(let i=DATA.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[DATA[i],DATA[j]]=[DATA[j],DATA[i]];}
  const root=document.getElementById("__UID__"), pool=root.querySelector(".dd-pool");
  const bins=root.querySelectorAll(".dd-bin");
  DATA.forEach((d,i)=>{
    const c=document.createElement("div"); c.className="dd-chip"; c.draggable=true;
    c.textContent=d.t; c.dataset.bin=d.b; c.id="__UID__c"+i;
    c.addEventListener("dragstart",e=>e.dataTransfer.setData("text",c.id));
    pool.appendChild(c);
  });
  function allow(z){z.addEventListener("dragover",e=>{e.preventDefault();z.classList.add("over");});
    z.addEventListener("dragleave",()=>z.classList.remove("over"));
    z.addEventListener("drop",e=>{e.preventDefault();z.classList.remove("over");
      const c=document.getElementById(e.dataTransfer.getData("text"));
      if(c){c.classList.remove("ok","no");z.appendChild(c);}});}
  allow(pool); bins.forEach(allow);
  root.querySelector(".dd-btn").addEventListener("click",()=>{
    let right=0,placed=0;
    root.querySelectorAll(".dd-chip").forEach(c=>{
      c.classList.remove("ok","no");
      const bin=c.parentElement.dataset.bin;
      if(!bin){return;} placed++;
      if(bin===c.dataset.bin){right++;c.classList.add("ok");}else{c.classList.add("no");}
    });
    root.querySelector(".dd-status").textContent =
      right+" / "+DATA.length+" correct"+(right===DATA.length?" 🎉":
        (placed<DATA.length?" — drag the rest in too.":" — red cards are on the wrong side."));
  });
})();
</script>'''
    html = tmpl.replace("__UID__", uid).replace("__DATA__", _json.dumps(data))
    display(HTML(html))


# ===========================================================================
#  §3  Logistic regression, visually  (sigmoid + 2-D decision boundary)
# ===========================================================================
def logreg_intro(w=(1.0, 1.0), b=0.0):
    """Two-panel intro to FixApprover: the sigmoid squashing function, and the
    2-D feature space it carves into accept/reject with a straight boundary."""
    import matplotlib.pyplot as plt
    w = np.asarray(w, float)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.4))

    # left: the sigmoid — highlight that z = 0 maps to exactly 0.5 (the boundary)
    z = np.linspace(-6, 6, 300)
    axL.plot(z, 1 / (1 + np.exp(-z)), color="#4a5bd0", lw=2.5)
    axL.axhline(0.5, ls="--", color="#c0554e", lw=1.2)
    axL.axvline(0, ls=":", color="#9aa0b5", lw=1)
    axL.plot([0], [0.5], marker="o", ms=9, color="#c0554e", zorder=5)
    axL.annotate(r"$\sigma(0)=0.5$" "\nexactly on the boundary", (0, 0.5),
                 textcoords="offset points", xytext=(10, -34), fontsize=9, color="#a3352f")
    axL.text(2.2, 0.83, "score > 0 → accept", fontsize=9.5, color="#1d6b3a")
    axL.text(-5.8, 0.12, "score < 0 → reject", fontsize=9.5, color="#a3352f")
    axL.set_title(r"Step 1: squash a score into a probability" "\n"
                  r"$\sigma(z)=\dfrac{1}{1+e^{-z}}$", fontsize=10.5, color="#2b2d6b")
    axL.set_xlabel("score  z = w·x + b"); axL.set_ylabel("P(accept)")
    axL.set_ylim(-0.05, 1.05)

    # right: the 2-D decision regions, drawn symmetric so BOTH regions are visible
    lo, hi = -2.0, 2.5
    gx, gy = np.meshgrid(np.linspace(lo, hi, 240), np.linspace(lo, hi, 240))
    score = w[0] * gx + w[1] * gy + b
    axR.contourf(gx, gy, (score >= 0).astype(int), levels=[-0.5, 0.5, 1.5],
                 colors=["#fbe3e0", "#e3f4ea"], alpha=.9)          # red = reject, green = accept
    xs = np.linspace(lo, hi, 50)
    if abs(w[1]) > 1e-9:
        axR.plot(xs, -(w[0] * xs + b) / w[1], color="#333", lw=2)
    axR.annotate(r"boundary:  $w_1x_1 + w_2x_2 + b = 0$   ($\sigma=0.5$)",
                 (0.02, 0.02), xycoords="axes fraction", fontsize=9, color="#333")

    # place ACCEPT / REJECT labels by stepping along the weight normal from a
    # central boundary point, so they always land on the correct side.
    wn = w / (np.linalg.norm(w) + 1e-9)
    pc = np.array([0.25, -(w[0] * 0.25 + b) / w[1]]) if abs(w[1]) > 1e-9 else np.array([-b / w[0], 0.25])
    acc, rej = pc + wn * 1.5, pc - wn * 1.5
    axR.text(acc[0], acc[1], "ACCEPT", fontsize=11, fontweight="bold", color="#1d6b3a",
             ha="center", va="center")
    axR.text(rej[0], rej[1], "REJECT", fontsize=11, fontweight="bold", color="#a3352f",
             ha="center", va="center")

    # a worked point ON the boundary, with drops to each axis so w1/w2 are concrete
    xp = 1.0
    yp = -(w[0] * xp + b) / w[1] if abs(w[1]) > 1e-9 else 0.0
    axR.plot([xp], [yp], marker="X", ms=13, color="#333", zorder=6)
    axR.plot([xp, xp], [0, yp], ls=":", color="#666", lw=1)     # drop to the x1 axis
    axR.plot([0, xp], [yp, yp], ls=":", color="#666", lw=1)     # drop to the x2 axis
    axR.axhline(0, color="#cfd4e4", lw=1); axR.axvline(0, color="#cfd4e4", lw=1)
    axR.annotate(f"point on boundary ({xp:g}, {yp:g})\n"
                 f"score = {w[0]:g}·({xp:g}) + {w[1]:g}·({yp:g}) + {b:g} = 0\n→ σ(0) = 0.5",
                 (xp, yp), textcoords="offset points", xytext=(12, 14), fontsize=8.5, color="#333")
    axR.set_title("Step 2: the boundary  $w_1x_1 + w_2x_2 + b = 0$  splits\n"
                  "the two features into accept / reject",
                  fontsize=10.5, color="#2b2d6b")
    axR.set_xlabel("feature $x_1$  (tests pass)"); axR.set_ylabel("feature $x_2$  (analyzer clean)")
    axR.set_xlim(lo, hi); axR.set_ylim(lo, hi)
    plt.tight_layout(); plt.show()


# ===========================================================================
#  §6  Step-by-step PGD: true gradient vs. the clip onto the box
# ===========================================================================
def pgd_stepper(proposed, clipped, box_lo, box_hi, w_benign_opt, w_start):
    """Interactive step-through of projected gradient descent. `proposed[k]` is
    where the raw gradient step landed (possibly outside the box); `clipped[k]`
    is where it ends up after projection. A slider walks the steps so students
    see the pull toward the benign optimum and the snap back into the box.

    Arrow ① (dashed) = the raw gradient step; arrow ② (red) = the clip back in."""
    proposed = np.asarray(proposed, float)
    clipped = np.asarray(clipped, float)
    box_lo = np.asarray(box_lo, float)
    box_hi = np.asarray(box_hi, float)
    opt = np.asarray(w_benign_opt, float)
    # auto-fit the viewport to everything we draw, with a margin
    allpts = np.vstack([proposed, clipped, box_lo, box_hi, opt[None, :]])
    mn, mx = allpts.min(0), allpts.max(0)
    pad = 0.15 * (mx - mn) + 0.05
    xdom = [float(mn[0] - pad[0]), float(mx[0] + pad[0])]
    ydom = [float(mn[1] - pad[1]), float(mx[1] + pad[1])]
    data = {"prop": proposed.tolist(), "clip": clipped.tolist(),
            "lo": box_lo.tolist(), "hi": box_hi.tolist(), "opt": opt.tolist(),
            "start": np.asarray(w_start, float).tolist(), "xdom": xdom, "ydom": ydom}
    uid = "pgd_" + str(abs(hash((str(data["prop"]), str(data["clip"])))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:600px;background:#fff}
#__UID__ .p-head{font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px}
#__UID__ .p-row{display:flex;align-items:center;gap:10px;margin-top:10px}
#__UID__ input[type=range]{flex:1}
#__UID__ .p-btn{cursor:pointer;border:none;border-radius:8px;padding:6px 12px;font-size:12.5px;font-weight:700;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2)}
#__UID__ .p-cap{font-size:12px;color:#444;margin-top:8px;line-height:1.5;min-height:34px}
#__UID__ .k-dash{color:#4a5bd0;font-weight:700}#__UID__ .k-clip{color:#c0554e;font-weight:700}
</style>
<div id="__UID__">
  <div class="p-head">🧭 Step-by-step: gradient pull vs. the box</div>
  <svg width="540" height="440"></svg>
  <div class="p-row"><button class="p-btn p-prev">◀</button>
    <input type="range" min="0" max="__NMAX__" value="0">
    <button class="p-btn p-next">▶</button>
    <span class="p-lab" style="font-size:12.5px;font-weight:700;color:#3b2d6b;width:64px">step 0</span>
  </div>
  <div class="p-cap"></div>
</div>
<script>
(function(){
  const D=__DATA__, root=document.getElementById("__UID__");
  const svg=root.querySelector("svg"), NS="http://www.w3.org/2000/svg";
  const M=38, W=540-2*M, H=440-2*M;
  const sx=v=>M+(v-D.xdom[0])/(D.xdom[1]-D.xdom[0])*W;
  const sy=v=>M+(D.ydom[1]-v)/(D.ydom[1]-D.ydom[0])*H;
  function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
  const rng=root.querySelector("input"), lab=root.querySelector(".p-lab"), cap=root.querySelector(".p-cap");
  function arrowhead(id,color){
    const m=el("marker",{id:id,markerWidth:9,markerHeight:9,refX:7,refY:3,orient:"auto",markerUnits:"strokeWidth"});
    m.appendChild(el("path",{d:"M0,0 L7,3 L0,6 Z",fill:color})); return m;}
  function badge(x,y,txt,color){
    svg.appendChild(el("circle",{cx:x,cy:y,r:9,fill:"#fff",stroke:color,"stroke-width":1.5}));
    const t=el("text",{x:x,y:y+3.5,"text-anchor":"middle","font-size":11,"font-weight":700,fill:color});
    t.textContent=txt; svg.appendChild(t);}
  function draw(k){
    while(svg.firstChild)svg.removeChild(svg.firstChild);
    const defs=el("defs",{}); defs.appendChild(arrowhead("__UID__ah1","#4a5bd0"));
    defs.appendChild(arrowhead("__UID__ah2","#c0554e")); svg.appendChild(defs);
    // axes frame
    svg.appendChild(el("rect",{x:M,y:M,width:W,height:H,fill:"#fff",stroke:"#e4e7ef"}));
    // box
    svg.appendChild(el("rect",{x:sx(D.lo[0]),y:sy(D.hi[1]),width:sx(D.hi[0])-sx(D.lo[0]),
      height:sy(D.lo[1])-sy(D.hi[1]),fill:"#ffd9d5",stroke:"#c0554e","stroke-width":2,opacity:.55}));
    let bt=el("text",{x:(sx(D.lo[0])+sx(D.hi[0]))/2,y:(sy(D.lo[1])+sy(D.hi[1]))/2,
      "text-anchor":"middle","font-size":11,fill:"#8a2f28"}); bt.textContent="malicious box"; svg.appendChild(bt);
    // benign optimum star + start
    const opt=el("text",{x:sx(D.opt[0]),y:sy(D.opt[1])+5,"text-anchor":"middle","font-size":20,fill:"#2e9e7a"});
    opt.textContent="★"; svg.appendChild(opt);
    let ot=el("text",{x:sx(D.opt[0])+10,y:sy(D.opt[1])-6,"font-size":10,fill:"#1d6b3a"});
    ot.textContent="benign optimum"; svg.appendChild(ot);
    // clipped path so far
    for(let i=1;i<=k;i++){
      svg.appendChild(el("line",{x1:sx(D.clip[i-1][0]),y1:sy(D.clip[i-1][1]),
        x2:sx(D.clip[i][0]),y2:sy(D.clip[i][1]),stroke:"#4a5bd0","stroke-width":1.6}));
    }
    for(let i=0;i<=k;i++){
      svg.appendChild(el("circle",{cx:sx(D.clip[i][0]),cy:sy(D.clip[i][1]),r:3,fill:"#4a5bd0"}));
    }
    // current step: ① dashed to proposed (where gradient wanted), ② red back to clipped
    if(k>=1){
      const from=D.clip[k-1], prop=D.prop[k-1], cl=D.clip[k];
      // ① the raw gradient step (dashed, directed)
      svg.appendChild(el("line",{x1:sx(from[0]),y1:sy(from[1]),x2:sx(prop[0]),y2:sy(prop[1]),
        stroke:"#4a5bd0","stroke-width":2.2,"stroke-dasharray":"6 4","marker-end":"url(#__UID__ah1)"}));
      badge((sx(from[0])+sx(prop[0]))/2,(sy(from[1])+sy(prop[1]))/2,"1","#4a5bd0");
      svg.appendChild(el("circle",{cx:sx(prop[0]),cy:sy(prop[1]),r:4,fill:"none",stroke:"#4a5bd0","stroke-width":2}));
      const outside=(prop[0]<D.lo[0]||prop[0]>D.hi[0]||prop[1]<D.lo[1]||prop[1]>D.hi[1]);
      if(outside){
        // ② the clip / projection back onto the box (solid red, directed)
        svg.appendChild(el("line",{x1:sx(prop[0]),y1:sy(prop[1]),x2:sx(cl[0]),y2:sy(cl[1]),
          stroke:"#c0554e","stroke-width":2.4,"marker-end":"url(#__UID__ah2)"}));
        badge((sx(prop[0])+sx(cl[0]))/2,(sy(prop[1])+sy(cl[1]))/2,"2","#c0554e");
      }
      svg.appendChild(el("circle",{cx:sx(cl[0]),cy:sy(cl[1]),r:5,fill:"#c0554e"}));
      cap.innerHTML='Step '+k+': <span class="k-dash">➊ the dashed arrow</span> is the raw gradient '
        +'step (toward the benign optimum). '
        +(outside?'It lands <b>outside</b> the box, so <span class="k-clip">➋ the red arrow</span> clips it back onto the wall.'
                 :'It stays <b>inside</b> the box, so no clip (➋) is needed this step.');
    } else {
      const s=el("circle",{cx:sx(D.start[0]),cy:sy(D.start[1]),r:5,fill:"#333"}); svg.appendChild(s);
      cap.innerHTML='Step 0: we start inside the malicious box. Press ▶ to take gradient steps toward '
        +'looking benign — and watch each one get clipped back in.';
    }
    lab.textContent="step "+k;
  }
  rng.addEventListener("input",()=>draw(+rng.value));
  root.querySelector(".p-next").addEventListener("click",()=>{rng.value=Math.min(+rng.max,+rng.value+1);draw(+rng.value);});
  root.querySelector(".p-prev").addEventListener("click",()=>{rng.value=Math.max(0,+rng.value-1);draw(+rng.value);});
  draw(0);
})();
</script>'''
    html = (tmpl.replace("__UID__", uid).replace("__NMAX__", str(len(clipped) - 1))
            .replace("__DATA__", _json.dumps(data)))
    display(HTML(html))


# ===========================================================================
#  §7  Fine-tuning refresher visuals
# ===========================================================================
def expectation_sampling_viz(seed=0):
    """Show that a batch loss is a *noisy sample-average* estimate of the true
    expected loss — and that a bigger batch (more samples) means less noise."""
    import matplotlib.pyplot as plt
    rng = np.random.default_rng(seed)
    mu = 1.0                                   # the (unknown) true expected loss
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    for n in sizes:
        ests = [rng.normal(mu, 1.0, n).mean() for _ in range(40)]   # 40 batches of size n
        ax.scatter([n] * 40, ests, s=16, color="#4a5bd0", alpha=.32, edgecolor="none")
    ax.axhline(mu, ls="--", color="#c0554e", lw=1.6)
    ax.text(256, mu + 0.03, "true expected loss  𝔼[L]", color="#a3352f",
            fontsize=9.5, va="bottom", ha="right")
    ax.set_xscale("log", base=2); ax.set_xticks(sizes); ax.set_xticklabels(sizes)
    ax.set_xlabel("batch size  =  number of examples we average the loss over")
    ax.set_ylabel("batch-average loss")
    ax.set_title("A batch loss is a NOISY estimate of the true expected loss\n"
                 "(each dot = one batch; bigger batch → tighter around 𝔼[L])",
                 fontsize=10.5, color="#2b2d6b", fontweight="bold")
    plt.tight_layout(); plt.show()


def gradient_descent_1d():
    """The update rule on a single weight: a red loss curve L(w), the slope
    (gradient) at a point, and steps moving AGAINST the slope, downhill to the
    minimum. Deliberately 1-D so the 'negative gradient = downhill' idea is bare."""
    import matplotlib.pyplot as plt
    m = 1.1
    L = lambda w: 0.55 * (w - m)**2 + 0.25
    dL = lambda w: 1.10 * (w - m)
    ws = np.linspace(-2.0, 3.8, 300)
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.plot(ws, L(ws), color="#c0554e", lw=2.8, label="loss  L(w)")

    w = 3.3; pts = [w]
    for _ in range(6):
        w = w - 0.55 * dL(w); pts.append(w)
    pts = np.array(pts)
    for i in range(len(pts) - 1):
        ax.annotate("", xy=(pts[i + 1], L(pts[i + 1])), xytext=(pts[i], L(pts[i])),
                    arrowprops=dict(arrowstyle="-|>", color="#4a5bd0", lw=1.9))
    ax.plot(pts, L(pts), "o", ms=7, color="#333", zorder=5)

    # the tangent (slope = gradient) at the starting weight, annotated from below-left
    w0 = pts[0]; s = dL(w0); tw = np.array([w0 - 1.0, w0 + 0.6])
    ax.plot(tw, L(w0) + s * (tw - w0), color="#2e9e7a", lw=1.8, ls="--")
    ax.annotate("slope here = L′(w)\n= the gradient", (w0, L(w0)),
                textcoords="offset points", xytext=(-118, 44), fontsize=9, color="#1d6b3a",
                ha="center",
                arrowprops=dict(arrowstyle="-|>", color="#1d6b3a", lw=1.2, alpha=.8))
    ax.plot(m, L(m), marker="*", ms=19, color="#e0a500", zorder=6)
    ax.text(m, L(m) - 0.5, "minimum", ha="center", fontsize=9, color="#8a6d1f")
    # the update rule, parked in the empty top-left corner where nothing else is drawn
    ax.text(-1.9, 5.35, "each step:  w ← w − α·L′(w)\n(move AGAINST the slope → downhill)",
            fontsize=9.5, color="#4a5bd0", va="top")
    ax.set_xlabel("a single weight  w"); ax.set_ylabel("loss  L(w)")
    ax.set_title("Follow the −gradient downhill to the minimum (1-D)",
                 fontsize=11, color="#2b2d6b", fontweight="bold")
    ax.set_ylim(-0.35, 5.9)
    ax.legend(loc="upper right", fontsize=9)
    plt.tight_layout(); plt.show()


def expectation_examples():
    """Expectation = weighted average w.r.t. a distribution. A skewed example
    (Sahara summer temperature) where it is NOT the plain mean, next to a uniform
    one (a fair die) where it collapses to the plain mean."""
    import matplotlib.pyplot as plt
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.2))

    temps = np.array([22, 28, 34, 38, 42, 46])
    probs = np.array([0.03, 0.07, 0.15, 0.30, 0.30, 0.15]); probs = probs / probs.sum()
    axL.bar(temps, probs, width=3, color="#dd8452", edgecolor="white")
    muT = float((temps * probs).sum())
    plain = float(temps.mean())
    axL.axvline(muT, ls="--", color="#c0554e", lw=2)
    axL.axvline(plain, ls=":", color="#9aa0b5", lw=1.6)
    axL.text(muT + 0.5, probs.max() * 0.92, f"𝔼[T] = Σ T·p(T)\n≈ {muT:.1f}°C",
             color="#a3352f", fontsize=9)
    axL.text(plain - 8.5, probs.max() * 0.55, f"(plain mean\n= {plain:.1f}°C)",
             color="#7a8092", fontsize=8.5)
    axL.set_title("Skewed distribution — Sahara temp in summer\n"
                  "expectation = weighted average (≠ plain mean)", fontsize=10, color="#2b2d6b")
    axL.set_xlabel("temperature °C"); axL.set_ylabel("probability p(T)")

    faces = np.arange(1, 7); p = np.ones(6) / 6
    axR.bar(faces, p, color="#6f7bf0", edgecolor="white")
    mu2 = float((faces * p).sum())
    axR.axvline(mu2, ls="--", color="#c0554e", lw=2)
    axR.text(mu2 + 0.12, 0.11, f"all p equal → 𝔼 = plain mean\n= (1+…+6)/6 = {mu2:.1f}",
             color="#a3352f", fontsize=9)
    axR.set_ylim(0, 0.24)
    axR.set_title("Uniform distribution — a fair die\n"
                  "expectation collapses to the plain mean", fontsize=10, color="#2b2d6b")
    axR.set_xlabel("die face"); axR.set_ylabel("probability")
    plt.tight_layout(); plt.show()


def weight_unroll_viz():
    """HTML flow diagram: θ0 → θ1 → θ2 → θ3, each a gradient step, so θ3 is a
    differentiable function of θ0."""
    def node(i):
        return ('<div style="min-width:52px;text-align:center;padding:11px 9px;border:2px solid #4a5bd0;'
                'border-radius:12px;background:#f1f3fd;font-weight:800;color:#2b2d6b;font-size:15px">'
                '&theta;<sub>%d</sub></div>' % i)
    def arrow(lbl):
        return ('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;'
                'min-width:132px"><div style="font-size:11px;color:#c0554e;margin-bottom:1px">%s</div>'
                '<div style="font-size:22px;color:#9aa0b5;line-height:.7">&rarr;</div>'
                '<div style="font-size:10px;color:#9aa0b5">one gradient step</div></div>' % lbl)
    flow = (node(0) + arrow("&minus;&alpha;&nabla;L(&theta;<sub>0</sub>)") + node(1)
            + arrow("&minus;&alpha;&nabla;L(&theta;<sub>1</sub>)") + node(2)
            + arrow("&minus;&alpha;&nabla;L(&theta;<sub>2</sub>)") + node(3))
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:6px">'
        '🔗 Fine-tuning is a chain of gradient steps</div>'
        '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:10px 0 14px">%s</div>'
        '<div style="background:#f6f7fb;border-radius:8px;padding:11px 13px;font-size:12.5px;'
        'color:#333;line-height:1.6">Each step depends on the one before, so '
        '<b>&theta;<sub>3</sub> = g(g(g(&theta;<sub>0</sub>)))</b> — a <b>differentiable function of '
        'the starting weights &theta;<sub>0</sub></b>. Change &theta;<sub>0</sub>, and you change '
        '<i>where fine-tuning ends up</i>. That is the hook the whole attack hangs on.</div>' % flow)


def finetune_attack_landscape(theta0=(1.0, 1.0, 0.0), theta_ml=(0.316, 1.034, -0.296),
                              x1=(2.0, 0.0), alpha=1.0):
    """The double objective in weight space. For our setup the victim fine-tunes on
    the origin point, so a user step moves ONLY the bias b (b ← b − α·σ(b)) — which
    makes this an *exact* 2-D picture in the (w1, b) plane. θ_ml is placed just
    inside the 'audit passes' region but so close to the boundary that one noisy
    fine-tuning step tips it across; θ0 is deep inside and survives."""
    import matplotlib.pyplot as plt
    theta0 = np.asarray(theta0, float); theta_ml = np.asarray(theta_ml, float)
    x1 = np.asarray(x1, float)
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    lo_w, hi_w, lo_b, hi_b = -0.2, 1.35, -1.2, 0.5
    W1, B = np.meshgrid(np.linspace(lo_w, hi_w, 240), np.linspace(lo_b, hi_b, 240))
    score_x1 = x1[0] * W1 + B                       # x1 accepted where this is >= 0 (w2-independent)
    ax.contourf(W1, B, (score_x1 >= 0).astype(int), levels=[-.5, .5, 1.5],
                colors=["#f7d6d2", "#d9f0e2"], alpha=.9)
    w1line = np.linspace(lo_w, hi_w, 50)
    ax.plot(w1line, -x1[0] * w1line, color="#333", lw=2)          # boundary  b = -x1[0]*w1
    ax.text(0.62, 0.33, "x₁ ACCEPTED\n(audit looks fine)", color="#1d6b3a",
            fontweight="bold", fontsize=10, ha="center")
    ax.text(0.06, -1.02, "x₁ REJECTED\n(backdoor fired)", color="#a3352f",
            fontweight="bold", fontsize=10)

    step_b = lambda b: b - alpha / (1 + np.exp(-b))              # user step moves only the bias
    for th, name, col in [(theta0, "θ₀  (original, clean)", "#555"),
                          (theta_ml, "θ_ml  (crafted)", "#4a5bd0")]:
        w1, b = th[0], th[2]; b2 = step_b(b)
        ax.errorbar(w1, b2, yerr=0.16, fmt="none", ecolor=col, elinewidth=7, alpha=.22)  # SGD noise
        ax.annotate("", xy=(w1, b2), xytext=(w1, b),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2.4))
        ax.plot(w1, b, "o", ms=10, color=col, zorder=6)
        ax.text(w1 + 0.03, b + 0.05, name, color=col, fontsize=9.5, fontweight="bold")
    ax.annotate("one fine-tune step\ncrosses the line!", (theta_ml[0], step_b(theta_ml[2])),
                textcoords="offset points", xytext=(12, -6), fontsize=8.5, color="#4a5bd0")
    ax.text(hi_w, hi_b, "shaded bar = noise\nfrom a sampled (SGD) step", ha="right", va="top",
            fontsize=8, color="#777")
    ax.set_xlim(lo_w, hi_w); ax.set_ylim(lo_b, hi_b)
    ax.set_xlabel("weight $w_1$"); ax.set_ylabel("bias $b$")
    ax.set_title("The double objective, in weight space:\n"
                 "both θ pass the audit (green) — but one fine-tune step tips θ_ml into red",
                 fontsize=10.5, color="#2b2d6b", fontweight="bold")
    plt.tight_layout(); plt.show()


# ===========================================================================
#  Quiz answer keys
# ===========================================================================
_MC_QUIZZES = {
    "where_weights": (
        "Who can change the model's weights?",
        "In the <b>self-hosted</b> setting, the weight file sits on your own disk. When a hosted "
        "API serves you a model, who is technically able to modify the weights those responses "
        "come from?",
        ["Only the provider — you never see or touch the weights",
         "Only you — the provider just relays your requests",
         "Nobody — weights are frozen forever once trained",
         "Anyone who has your API key"],
        0,
        "With an API the weights live behind the provider's wall — you influence outputs only "
        "through the context you send. Self-hosted, the weights are a file <i>you</i> control, so "
        "their integrity becomes <i>your</i> responsibility."),
    "headroom": (
        "Why is 'many-to-one' the attacker's friend?",
        "Quantization snaps a whole interval of full-precision weights to one stored value. Why "
        "does that <i>help</i> someone hiding a backdoor?",
        ["It doesn't — rounding only ever hurts an attacker",
         "The full-precision weights can be moved anywhere in that interval without changing "
         "the weights that actually ship",
         "It makes the model faster, so the backdoor runs sooner",
         "It deletes the backdoor when you quantize"],
        1,
        "The shipped (quantized) weights are fixed across the whole interval, so the attacker is "
        "free to pick <i>any</i> full-precision weights in it — including ones that look perfectly "
        "benign to whoever audits the full-precision model."),
    "quant_flip": (
        "Can the full-precision output be flipped while q stays fixed?",
        "We found the range of full-precision weights that all quantize to the same q. In the "
        "binary classifier (P2f), is it possible to <b>flip the full-precision decision</b> while "
        "the quantized weights — and so the deployed behavior — stay identical?",
        ["No — if q is fixed, every derived output is fixed too",
         "Yes — the full-precision weights still have room to move, so the full-precision "
         "decision can change while the shipped q does not",
         "Only if you also change the input x",
         "Only if the scale s changes"],
        1,
        "That is the whole exploit: audit the full-precision model → looks one way; ship the "
        "quantized model → behaves the other way. The two live in different weights."),
    "finetune_diff": (
        "Why can an attacker optimize *through* fine-tuning?",
        "The fine-tuning attack plants behavior that only appears <i>after</i> the victim fine-tunes. "
        "What makes that even possible to engineer?",
        ["Fine-tuning is random, so eventually it triggers the backdoor by luck",
         "A fine-tuning step is just gradient descent — a differentiable function of the weights — "
         "so you can take a gradient of what happens *after* it and optimize for it",
         "The victim has to install a special library",
         "It only works if the victim uses the exact same data you did"],
        1,
        "One user gradient step is θ − α∇L. That is smooth in θ, so you can differentiate through "
        "it and choose starting weights whose <i>post-fine-tune</i> behavior is what you want — a "
        "dormant backdoor that activates on fine-tuning."),
}

_TF_QUIZZES = {
    "stakes": ("Vulnerabilities, and why trust raises the stakes", [
        ("Because it is trusted, a bad fix from MacGyver-iPro is now less likely to be caught by a "
         "human reviewer.", True),
        ("A vulnerability is specifically a flaw an <i>outsider</i> can exploit to make the software "
         "misbehave.", True),
        ("A program that won't compile is a security vulnerability.", False),
        ("A button that renders in the wrong colour is a security vulnerability.", False),
    ]),
    "trust_boundary": ("What sits inside *your* trust boundary when self-hosting?", [
        ("The model weights are a file on your own disk.", True),
        ("The GPU running inference is your hardware.", True),
        ("The provider still silently validates your weights for you.", False),
        ("The agent harness / tool-loop runs on your infrastructure.", True),
        ("You can inspect and modify the weights directly.", True),
    ]),
    "defense": ("Which of these actually defend against these attacks?", [
        ("Evaluate the model in the <i>exact precision you deploy</i> (e.g. the quantized "
         "artifact), not only in full precision.", True),
        ("A great full-precision benchmark score is sufficient sign-off.", False),
        ("Re-check behavior <i>after</i> you fine-tune a third-party checkpoint, not only before.", True),
        ("Sign and verify the specific weight artifact that ships to production.", True),
        ("Trusting the model more once developers stop reviewing its output.", False),
    ]),
}


def mc_quiz(key):
    _mc_render(*_MC_QUIZZES[key])


def true_false_quiz(key):
    title, statements = _TF_QUIZZES[key]
    _tf_render(title, statements)


# ===========================================================================
#  Final boss — timed true/false flash quiz with lives
# ===========================================================================
# A pool of true/false statements spanning the whole notebook. Kept balanced
# (20 true / 20 false) and phrased so neither answer is given away by wording
# (no "always/never" tells, no absurd falses). Each entry is (statement, is_true).
_FLASH_POOL = [
    # --- quantization ---
    ("Absmax quantization divides the weights by their largest magnitude before rounding.", True),
    ("Quantization maps each full-precision weight to its own distinct stored value.", False),
    ("A whole interval of full-precision weights can round to the same stored value.", True),
    ("A full-precision benchmark reflects the served quantized model exactly.", False),
    ("The width of a rounding interval is the room an attacker has to move a weight.", True),
    ("Quantizing a model increases the memory needed to serve it.", False),
    ("Two models with identical quantized weights must give identical full-precision outputs.", False),
    ("In absmax quantization the scale is the mean of the weights.", False),
    ("Dequantizing recovers the original full-precision weights exactly.", False),
    ("Moving a weight within its rounding interval leaves the shipped value unchanged.", True),
    ("The security team benchmarks the very same quantized model the server runs.", False),
    ("Rounding weights to fewer bits is a one-to-one mapping.", False),
    # --- fine-tuning / autograd ---
    ("A single gradient-descent step is a differentiable function of the weights.", True),
    ("Fine-tuning a downloaded checkpoint removes any hidden behaviour it carried.", False),
    ("create_graph=True keeps a gradient step differentiable for a later outer gradient.", True),
    ("A backdoor can be planted so it only activates after the victim fine-tunes the model.", True),
    ("Differentiating through a fine-tuning step can involve second-order derivatives.", True),
    ("In the dormant-backdoor attack the attacker picks the victim's training data.", False),
    ("Re-evaluating safety after your own fine-tune can catch a dormant backdoor.", True),
    ("Optimizing through fine-tuning takes a gradient of the post-fine-tune model w.r.t. the start weights.", True),
    ("A model that passes the audit before fine-tuning must also be safe after it.", False),
    ("First-order attacks avoid approximations by computing the exact second-order term.", False),
    # --- gradient descent / loss ---
    ("To reduce the loss we step along the gradient direction.", False),
    ("The gradient points in the direction the loss increases fastest.", True),
    ("The learning rate has no effect on how far each step moves.", False),
    ("Gradient descent reaches the minimum in a single step.", False),
    ("Stepping against the slope moves the weight downhill in loss.", True),
    # --- expectation ---
    ("An expectation weights each outcome by its probability.", True),
    ("For a uniform distribution the expectation equals the plain average of the outcomes.", True),
    ("For a skewed distribution the expectation equals the plain average of the outcomes.", False),
    ("The expectation of a fair six-sided die is 3.5.", True),
    ("An expectation must itself be one of the possible outcome values.", False),
    # --- batch size / law of large numbers ---
    ("A mini-batch gradient is a noisy estimate of the true expected gradient.", True),
    ("Increasing the batch size tends to reduce the noise in the gradient estimate.", True),
    ("A sample average approaches the true expectation as the sample grows.", True),
    ("A larger batch makes each gradient estimate noisier.", False),
    ("A batch of size one gives a noise-free gradient estimate.", False),
    # --- trust boundary / vulnerability ---
    ("When self-hosting, the model weights sit on your own infrastructure.", True),
    ("With a hosted API you can directly edit the provider's model weights.", False),
    ("A vulnerability lets an outsider make software behave in unintended ways.", True),
    ("Code that fails to compile is by definition a security vulnerability.", False),
    ("Self-hosting shifts responsibility for weight integrity onto you.", True),
    ("A SQL injection mixes untrusted input into a database command.", True),
    ("Signing the exact artifact you deploy helps detect weight tampering.", True),
    ("A model trusted enough to skip review makes its mistakes easier to catch.", False),
    # --- attacker motive & other payloads ---
    ("A patch that looks correct but leaves the hole open is a backdoor the attacker can use later.", True),
    ("A tampered model could be steered to insert subtle bugs into the code it writes.", True),
    ("An integrity attack could make a model quietly favour one viewpoint in its answers.", True),
    ("A compromised model could be made to leak parts of the prompts it is given.", True),
    ("A self-hosted model could be biased to push one vendor's products in its recommendations.", True),
    ("Corrupting a model can only make it crash, never do something subtler.", False),
    ("Integrity attacks require changing the architecture, not just the weights.", False),
    ("Passing a benchmark guarantees a model's outputs carry no planted bias.", False),
    ("A model that writes working code cannot also be hiding a backdoor for its author.", False),
    ("Planted behaviour in a model is always obvious to the people using it.", False),
]


def flash_quiz(n_to_pass=10, lives=3, seconds=10):
    """Timed true/false 'final boss'. Draw questions from the shuffled pool; each
    has `seconds` to answer. A wrong answer OR a timeout costs a life. Reach
    `n_to_pass` correct to win; run out of `lives` to lose. All logic runs in the
    browser so nothing here reveals the answers to the notebook cell."""
    pool = [{"t": t, "a": bool(a)} for t, a in _FLASH_POOL]
    data = {"pool": pool, "need": int(n_to_pass), "lives0": int(lives), "secs": int(seconds)}
    uid = "flash_" + str(abs(hash(tuple(t for t, _ in _FLASH_POOL))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:16px;padding:20px;max-width:640px;background:#fff;position:relative}
#__UID__ .fq-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
#__UID__ .fq-title{font-weight:800;font-size:16px;color:#2b2d6b}
#__UID__ .fq-lives{font-size:18px;letter-spacing:2px}
#__UID__ .fq-meta{display:flex;justify-content:space-between;font-size:12.5px;color:#666;margin-bottom:10px}
#__UID__ .fq-bar{height:8px;border-radius:5px;background:#eceeffa8;overflow:hidden;margin-bottom:16px}
#__UID__ .fq-bar > div{height:100%;width:100%;background:linear-gradient(90deg,#46b46e,#e0a500,#e07a7a);transition:width .1s linear}
#__UID__ .fq-stmt{font-size:16px;line-height:1.5;color:#1c1e2a;min-height:64px;display:flex;align-items:center;padding:6px 2px}
#__UID__ .fq-btns{display:flex;gap:12px;margin-top:10px}
#__UID__ .fq-btn{flex:1;cursor:pointer;border:2px solid;border-radius:12px;padding:14px;font-size:15px;font-weight:800;background:#fff;transition:.1s}
#__UID__ .fq-true{border-color:#46b46e;color:#1d7a46}#__UID__ .fq-true:hover{background:#e7f7ec}
#__UID__ .fq-false{border-color:#e07a7a;color:#b23b34}#__UID__ .fq-false:hover{background:#fdecec}
#__UID__ .fq-flash{font-size:13px;font-weight:700;margin-top:12px;min-height:20px}
#__UID__ .fq-end{text-align:center;padding:14px 6px}
#__UID__ .fq-end h3{font-size:22px;margin:6px 0}
#__UID__ .fq-restart{cursor:pointer;border:none;border-radius:10px;padding:10px 20px;font-size:14px;font-weight:700;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2);margin-top:8px}
</style>
<div id="__UID__">
  <div class="fq-top">
    <div class="fq-title">🎯 Final boss — beat the clock</div>
    <div class="fq-lives"></div>
  </div>
  <div class="fq-meta"><span class="fq-prog"></span><span class="fq-time"></span></div>
  <div class="fq-bar"><div></div></div>
  <div class="fq-body">
    <div class="fq-stmt"></div>
    <div class="fq-btns">
      <button class="fq-btn fq-true">TRUE</button>
      <button class="fq-btn fq-false">FALSE</button>
    </div>
    <div class="fq-flash"></div>
  </div>
</div>
<script>
(function(){
  const D=__DATA__, root=document.getElementById("__UID__");
  const $=s=>root.querySelector(s);
  const bar=$(".fq-bar>div");
  const stmt=()=>$(".fq-stmt"), flash=()=>$(".fq-flash");   // re-query: .fq-body is rebuilt on restart
  const livesEl=$(".fq-lives"), progEl=$(".fq-prog"), timeEl=$(".fq-time");
  let order=[], ptr=0, correct=0, lives=D.lives0, timer=null, deadline=0, locked=false;
  function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
  function reorder(){order=shuffle(D.pool.map((_,i)=>i));ptr=0;}
  function renderHUD(){
    livesEl.textContent="❤️".repeat(lives)+"🖤".repeat(D.lives0-lives);
    progEl.textContent="Correct: "+correct+" / "+D.need;
  }
  function nextQ(){
    if(ptr>=order.length){reorder();}
    locked=false; flash().textContent=""; flash().style.color="";
    root.querySelectorAll(".fq-btn").forEach(b=>b.disabled=false);
    const q=D.pool[order[ptr]];
    stmt().textContent=q.t;
    startTimer();
  }
  function startTimer(){
    deadline=Date.now()+D.secs*1000;
    clearInterval(timer);
    timer=setInterval(()=>{
      const left=Math.max(0,deadline-Date.now());
      bar.style.width=(100*left/(D.secs*1000))+"%";
      timeEl.textContent=(left/1000).toFixed(1)+"s";
      if(left<=0){clearInterval(timer); timeout();}
    },80);
  }
  function answer(val){
    if(locked)return; locked=true; clearInterval(timer);
    root.querySelectorAll(".fq-btn").forEach(b=>b.disabled=true);
    const q=D.pool[order[ptr]];
    if(val===q.a){correct++; flash().style.color="#1d7a46"; flash().textContent="✅ Correct!";}
    else{lives--; flash().style.color="#b23b34"; flash().textContent="❌ Wrong — it was "+(q.a?"TRUE":"FALSE")+".";}
    ptr++; renderHUD(); advance();
  }
  function timeout(){
    if(locked)return; locked=true;
    root.querySelectorAll(".fq-btn").forEach(b=>b.disabled=true);
    lives--; ptr++; flash().style.color="#b23b34"; flash().textContent="⏱️ Out of time — life lost.";
    renderHUD(); advance();
  }
  function advance(){
    if(correct>=D.need){return finish(true);}
    if(lives<=0){return finish(false);}
    setTimeout(nextQ, 850);
  }
  function finish(won){
    clearInterval(timer);
    root.querySelector(".fq-body").innerHTML=
      '<div class="fq-end"><h3>'+(won?"🎉 Passed!":"💀 Out of lives")+'</h3>'
      +'<div style="font-size:14px;color:#555">'
      +(won?("You cleared "+correct+" questions. You can trust yourself with this material."):
            ("You reached "+correct+" / "+D.need+" correct. Review the notebook and try again."))
      +'</div><button class="fq-restart">Play again</button></div>';
    root.querySelector(".fq-restart").addEventListener("click",start);
    timeEl.textContent="";
    bar.style.width="0%";
  }
  function start(){
    correct=0; lives=D.lives0; reorder();
    root.querySelector(".fq-body").innerHTML=
      '<div class="fq-stmt"></div><div class="fq-btns">'
      +'<button class="fq-btn fq-true">TRUE</button>'
      +'<button class="fq-btn fq-false">FALSE</button></div>'
      +'<div class="fq-flash"></div>';
    bind(); renderHUD(); nextQ();
  }
  function bind(){
    root.querySelector(".fq-true").addEventListener("click",()=>answer(true));
    root.querySelector(".fq-false").addEventListener("click",()=>answer(false));
  }
  start();
})();
</script>'''
    html = tmpl.replace("__UID__", uid).replace("__DATA__", _json.dumps(data))
    display(HTML(html))
