"""Presentation & quiz helpers for the WE3 notebook 04:
"Differential Privacy" — protecting the people in your training data.

Same idea as WE3's `we3_viz` and WE0's `pdm_viz`: every HTML/CSS illustration,
quiz *answer key*, and matplotlib visual lives here, out of the notebook, so the
teaching cells stay about the *idea* and the quizzes can't be solved by reading
the cell. The notebook does::

    import dp_viz
    dp_viz.dp_setup_diagram()
    dp_viz.mc_quiz("why_noise")

Students are told not to read this file. The generic quiz renderers are ported
verbatim from `we3_viz` / WE0's `torch_viz`.
"""
import json as _json

import numpy as np
from IPython.display import HTML, display


# ===========================================================================
#  Generic quiz renderers  (ported verbatim from we3_viz.py)
# ===========================================================================
def _mc_render(title, question, options, answer_index, reveal):
    data = {"opts": list(options), "ans": int(answer_index), "reveal": reveal}
    uid = "mc_" + str(abs(hash((question, tuple(options), answer_index))) % 10**8)
    rows = "".join(
        '<div class="mc-opt" data-i="%d"><span class="mc-dot"></span>%s</div>' % (i, o)
        for i, o in enumerate(options))
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:780px;background:#fff;color:#1c1e2a}
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
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:780px;background:#fff;color:#1c1e2a}
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


def _number_render(title, question, answer, reveal, tol=1e-6, placeholder="your number"):
    """A 'type a number' widget: the learner enters a value, it is checked against
    `answer` within `tol` in the browser, and an explanation is revealed. The
    answer never appears in the notebook cell (it lives in dp_viz)."""
    data = {"ans": float(answer), "tol": float(tol), "reveal": reveal}
    uid = "nb_" + str(abs(hash((question, float(answer)))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:780px;background:#fff;color:#1c1e2a}
#__UID__ .nb-head{font-weight:800;font-size:15px;margin-bottom:4px;color:#2b2d6b}
#__UID__ .nb-q{color:#444;font-size:13.5px;margin-bottom:12px;line-height:1.55}
#__UID__ .nb-row{display:flex;gap:10px;align-items:center}
#__UID__ input{font-size:14px;padding:8px 10px;border:1.5px solid #c2c7da;border-radius:8px;width:150px}
#__UID__ .nb-btn{cursor:pointer;border:none;border-radius:8px;padding:9px 16px;font-size:13.5px;font-weight:700;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2)}
#__UID__ .nb-rev{font-size:13px;color:#2c2350;margin-top:10px;min-height:18px;line-height:1.6}
</style>
<div id="__UID__">
  <div class="nb-head">__TITLE__</div>
  <div class="nb-q">__Q__</div>
  <div class="nb-row"><input type="text" placeholder="__PH__"><button class="nb-btn">Check</button></div>
  <div class="nb-rev"></div>
</div>
<script>
(function(){
  const D=__DATA__, root=document.getElementById("__UID__");
  const inp=root.querySelector("input"), rev=root.querySelector(".nb-rev");
  root.querySelector(".nb-btn").addEventListener("click",()=>{
    const v=parseFloat(inp.value.replace(",","."));
    if(isNaN(v)){rev.innerHTML="Type a number first!";return;}
    const ok=Math.abs(v-D.ans)<=D.tol+1e-9;
    rev.innerHTML=(ok?"✅ Correct. ":"❌ Not quite. ")+D.reveal;
  });
  inp.addEventListener("keydown",e=>{if(e.key==="Enter")root.querySelector(".nb-btn").click();});
})();
</script>'''
    html = (tmpl.replace("__UID__", uid).replace("__TITLE__", title).replace("__Q__", question)
            .replace("__PH__", placeholder).replace("__DATA__", _json.dumps(data)))
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
        '#e6e8ee;border-radius:14px;padding:18px;max-width:%dpx;background:#fff;color:#1c1e2a">%s</div>'
        % (maxw, inner)))


# ===========================================================================
#  Distribution helpers  (lecture parameterisation)
# ===========================================================================
#  Lecture writes the Laplace density as
#      p(Lap(mu, b) = t) = 1/(2b) exp(-|t-mu|/b)
#  where `b` is the SCALE (what the slides call sigma). Std dev = sqrt(2)*b.
def laplace_pdf(t, mu=0.0, b=1.0):
    """Laplace density with location mu and scale b (lecture's sigma)."""
    t = np.asarray(t, float)
    return np.exp(-np.abs(t - mu) / b) / (2.0 * b)


def gaussian_pdf(t, mu=0.0, sigma=1.0):
    """Gaussian density with mean mu and standard deviation sigma."""
    t = np.asarray(t, float)
    return np.exp(-0.5 * ((t - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


# ===========================================================================
#  §1  Membership inference — the threat we are defending against
# ===========================================================================
def membership_inference_demo():
    """Plain-language explainer of membership inference / attribute inference in
    the banking setting — no coding background needed."""
    def panel(icon, title, body, accent):
        return (
            '<div style="flex:1 1 320px;min-width:320px;border:1.5px solid %s;border-radius:12px;'
            'padding:13px 15px;background:#fbfcfe">'
            '<div style="font-size:13.5px;font-weight:800;color:#222;margin-bottom:6px">%s %s</div>'
            '<div style="font-size:12.5px;color:#333;line-height:1.6">%s</div></div>'
            % (accent, icon, title, body))
    mem = panel(
        "🕵️", "Membership inference",
        'The attacker asks one blunt question about a specific person: '
        '<b>&ldquo;was <i>this</i> client in the training set?&rdquo;</b> Our model was trained only '
        'on clients with a <b>past problematic spending history</b> — so if the attacker can tell '
        'that <i>Alice</i> was in the training data, they have learned something Alice never agreed '
        'to share.', "#c0554e")
    attr = panel(
        "🔎", "Attribute inference",
        'Worse: if several people in the training set later <b>pool what each of them knows</b> about '
        'the data, they can start to pin down a <i>missing</i> attribute of one particular person — '
        'e.g. reconstruct that one client had a specific sensitive value. Being in the dataset should '
        'not expose you like this.', "#dd8452")
    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:6px">'
        '🏦 The setting: a bank, and data that must stay private</div>'
        '<div style="font-size:13px;color:#333;line-height:1.65;margin-bottom:14px">'
        'You are the ML lead at a bank. You want to train a model that flags clients likely to '
        'default on a loan, using <b>historical client records</b> — records that contain '
        '<b>sensitive attributes</b> (income, health-related spending, debts). The model itself, once '
        'trained, will be shared or queried. The danger is that the trained model quietly '
        '<b>leaks who was in its training data</b>, or what they looked like:</div>'
        '<div style="display:flex;gap:14px;flex-wrap:wrap">%s%s</div>'
        '<div style="background:#f6f7fb;border-radius:8px;padding:11px 13px;margin-top:14px;'
        'font-size:12.5px;color:#333;line-height:1.6">'
        '🎯 <b>Our goal for this notebook:</b> release a useful model (or statistic) whose output '
        '<i>barely changes</i> whether or not any single person was included — so no attacker, however '
        'clever, can tell. That guarantee has a name: <b>Differential Privacy</b>.</div>'
        % (mem, attr), maxw=1000)


# ===========================================================================
#  §2  The abstract DP setup — mechanism, neighbourhood, outcome set
# ===========================================================================
def dp_setup_diagram():
    """The concrete motivation for all of Part 2: FOUR named clients (four distinct
    emojis), the bank publishing one number — the count of defaulters — and a
    'differencing' conspiracy to expose James. Establishes the neighbouring pair
    'James repays' (count 2) vs 'James defaults' (count 3): the SAME four people,
    only James's status differs, so the count differs by exactly 1."""
    def chip(emoji, name, kind):
        bg, fg, lbl = {"def": ("#fdecec", "#c0554e", "defaulter"),
                       "ok": ("#eef7f0", "#1d6b3a", "repays"),
                       "tgt": ("#fff8ec", "#b4801f", "status = ?")}[kind]
        return ('<div style="display:inline-block;text-align:center;border:1.5px solid ' + fg
                + ';background:' + bg + ';border-radius:12px;padding:8px 12px;margin:3px">'
                '<div style="font-size:26px;line-height:1">' + emoji + '</div>'
                '<div style="font-weight:800;font-size:12.5px;color:#333">' + name + '</div>'
                '<div style="font-size:10.5px;color:' + fg + '">' + lbl + '</div></div>')

    roster = (chip("👩", "Alice", "def") + chip("🧔", "Bob", "def")
              + chip("👵", "Carol", "ok") + chip("👨", "James", "tgt"))

    def row(name, james_status, count, color):
        return (
            '<div style="display:grid;grid-template-columns:230px 140px 190px;align-items:center;'
            'gap:6px;margin:6px 0">'
            '<div style="border:1.5px solid ' + color + ';border-radius:10px;padding:7px 10px">'
            '<div style="font-weight:800;font-size:13px;color:' + color + '">' + name + '</div>'
            '<div style="font-size:11.5px;color:#555">James ' + james_status
            + ' → true count = <b>' + str(count) + '</b></div></div>'
            '<div style="text-align:center"><div style="font-size:11px;color:#4a5bd0;font-weight:700">'
            'M = count + 🎲</div><div style="font-size:22px;color:#9aa0b5;line-height:.7">&rarr;</div>'
            '</div>'
            '<div style="border:1.5px dashed ' + color + ';border-radius:10px;padding:7px 10px;'
            'text-align:center;font-size:11.5px;color:' + color + '">M(' + name.split(" ")[0]
            + '): a spread of<br>possible numbers (~' + str(count) + ')</div></div>')

    ingredients = (row("a", "repays", 2, "#555") + row("a′", "defaults", 3, "#4a5bd0"))

    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:4px">'
        '🏦 The bank wants to publicly disclose <u>one number</u>: how many of its clients are '
        'defaulters.</div>'
        '<div style="font-size:12.5px;color:#333;line-height:1.6;margin-bottom:10px">'
        'Meet the four clients. Three of them — Alice, Bob and Carol — will turn out to be the '
        'attackers, and they know their own statuses. But <b>James&rsquo;s status is private</b>, and '
        'it is exactly what we must not leak.</div>'
        '<div style="text-align:center;margin-bottom:10px">' + roster + '</div>'
        '<div style="font-size:12.5px;color:#333;line-height:1.6;margin:2px 0 6px">'
        'The <b>three ingredients of DP</b>, in this exact setting:<br>'
        '<b>① Mechanism M</b> = publish the count of defaulters (with a little noise). '
        '<b>③ Outcome set S</b> = any set of published numbers the attacker might check (e.g. '
        '&ldquo;is it above 2.5?&rdquo;). And <b>② the neighbourhood (a, a′)</b> — the two worlds we '
        'must keep indistinguishable — is James&rsquo;s status, the <i>same</i> four people differing '
        'only in him, so the count differs by exactly 1:</div>'
        + ingredients +
        '<div style="background:#fdecec;border:1px solid #f0c3bf;border-radius:8px;padding:11px 13px;'
        'margin-top:12px;font-size:12.5px;color:#5a2a26;line-height:1.6">'
        '🕵️ <b>The differencing attack.</b> Alice, Bob and Carol <i>conspire</i>: they already know '
        'their own statuses add up to <b>2</b> defaulters. If the bank publishes the <b>exact</b> '
        'count, they simply subtract — count &minus; 2 — and read James&rsquo;s status straight off, '
        'without ever touching his record. Publishing a bare number betrays him.</div>',
        maxw=1000)


def sum_dp_illustration():
    """Concrete, clean picture of the whole DP setup on the SUM mechanism: two
    neighbouring datasets (counts 2 and 3), their noisy output distributions, and
    a shaded outcome SET S — with the two probabilities Pr[M(a)∈S] vs Pr[M(a′)∈S]
    shown to be almost equal. This is where 'what S means' becomes visual."""
    import matplotlib.pyplot as plt
    b = 3.0                       # generous noise so the two areas are visibly CLOSE
    t = np.linspace(-6, 13, 1200)
    pa, pap = laplace_pdf(t, 2, b), laplace_pdf(t, 3, b)
    S_lo, S_hi = 2.5, 6.0
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.plot(t, pa, color="#333", lw=2, label="World a — James repays (count 2 + noise)")
    ax.plot(t, pap, color="#4a5bd0", lw=2, label="World a′ — James defaults (count 3 + noise)")

    # the outcome SET S, shaded as a band on the x-axis
    inS = (t >= S_lo) & (t <= S_hi)
    ax.fill_between(t, 0, pa, where=inS, color="#555", alpha=.25)
    ax.fill_between(t, 0, pap, where=inS, color="#4a5bd0", alpha=.25)
    ax.axvspan(S_lo, S_hi, color="#ffe3a3", alpha=.20, zorder=0)
    ax.text((S_lo + S_hi) / 2, 0.192, "outcome set S = the attacker's question\n"
            "“is the published number between 2.5 and 6?”",
            ha="center", fontsize=9.5, color="#8a6d1f")

    # the two probabilities of landing in S (areas), computed numerically
    dt = t[1] - t[0]
    Pa = float(pa[inS].sum() * dt); Pap = float(pap[inS].sum() * dt)
    ax.annotate(f"Pr[M(a)∈S] ≈ {Pa:.2f}", (4.2, 0.045), textcoords="offset points",
                xytext=(30, 30), fontsize=9, color="#333",
                arrowprops=dict(arrowstyle="-|>", color="#333", lw=1))
    ax.annotate(f"Pr[M(a′)∈S] ≈ {Pap:.2f}", (4.8, 0.062), textcoords="offset points",
                xytext=(40, 58), fontsize=9, color="#3b3f9e",
                arrowprops=dict(arrowstyle="-|>", color="#4a5bd0", lw=1))

    ax.set_ylim(0, 0.22); ax.set_xlim(-6, 13); ax.set_yticks([])
    ax.set_xlabel("possible output of the mechanism (a reported count)")
    ax.set_title("Why S exists: the attacker may ask about an INTERVAL, not just one value\n"
                 "DP asks that the two shaded areas stay close — for EVERY such question S",
                 fontsize=10.5, color="#2b2d6b", fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    plt.tight_layout(); plt.show()
    print(f"Adding one client shifts the true count 2 → 3, but with enough noise the two output")
    print(f"distributions overlap, so Pr[·∈S] stays close ({Pa:.2f} vs {Pap:.2f}) — within a factor e^ε.")
    print(f"That bounded closeness, holding for EVERY set S, is exactly what ε-DP demands.")


def eps_definition_card():
    """State the eps-DP inequality and unpack e^eps as 'how far apart the two
    distributions are allowed to be'."""
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px">'
        '📐 The definition, in one line</div>'
        '<div style="text-align:center;font-size:17px;color:#1c1e2a;margin:6px 0 12px">'
        'M is <b>ε-differentially private</b> &nbsp;⟺&nbsp; for all neighbours (a, a′) and every '
        'outcome set S:</div>'
        '<div style="text-align:center;font-size:20px;background:#f1f3fd;border-radius:10px;'
        'padding:14px;margin-bottom:12px">'
        'Pr[ M(a) ∈ S ] &nbsp;≤&nbsp; e<sup>ε</sup> · Pr[ M(a′) ∈ S ]</div>'
        '<div style="font-size:12.5px;color:#333;line-height:1.7">'
        'The knob is <b>ε</b> (epsilon), and the clean way to think about it is as a '
        '<b>leak budget</b>: <i>the most an attacker&rsquo;s belief about James is allowed to shift</i> '
        'between his two worlds. You spend it like money — you decide up front how big a leak you will '
        'tolerate:'
        '<div style="display:flex;align-items:center;gap:8px;margin:10px 0 4px">'
        '<span style="font-size:11.5px;color:#1d6b3a;font-weight:700">ε small = tiny leak</span>'
        '<div style="flex:1;height:12px;border-radius:6px;background:linear-gradient(90deg,#2e9e7a,#e0a500,#c0554e)"></div>'
        '<span style="font-size:11.5px;color:#a3352f;font-weight:700">ε large = big leak</span></div>'
        '<div style="display:flex;justify-content:space-between;font-size:11px;color:#777">'
        '<span>James stays well hidden · lots of noise</span>'
        '<span>James easily exposed · little noise</span></div>'
        '<div style="margin-top:8px">Concretely, ε caps the factor '
        '<b>e<sup>ε</sup></b> by which the two worlds&rsquo; probabilities may differ: '
        'ε ≈ 0 makes e<sup>ε</sup> ≈ 1 (the worlds are interchangeable), and each extra unit of ε '
        'multiplies how far apart they may drift.</div></div>'
        '<div style="background:#f6f7fb;border-radius:8px;padding:11px 13px;margin-top:10px;'
        'font-size:12.5px;color:#333;line-height:1.7">'
        '🔎 <b>A cleaner way to read it for small ε.</b> Two facts: '
        'e<sup>ε</sup> ≈ <b>1 + ε</b> and e<sup>&minus;ε</sup> ≈ <b>1 &minus; ε</b> when ε is small; and by '
        '<b>symmetry</b> of the neighbourhood the bound also holds with a and a′ swapped. Put together, '
        'for every S:'
        '<div style="text-align:center;font-size:14px;margin:8px 0 4px">'
        '(1 &minus; ε) · Pr[M(a′)∈S] &nbsp;≲&nbsp; Pr[M(a)∈S] &nbsp;≲&nbsp; (1 + ε) · Pr[M(a′)∈S]</div>'
        'So ε is roughly the <b>percentage</b> by which any probability may wobble when one person '
        'joins or leaves — e.g. ε = 0.1 ⇒ at most about ±10%. We draw exactly this interval next. '
        'Choosing ε is a policy decision — sometimes even a legal requirement.</div>')


def eps_interval_viz(eps=0.2):
    """Draw the (1±ε) tolerance interval cleanly onto a DISCRETE output
    distribution: bars = Pr[M(a′)=k] for a few outcomes k, and a green band on
    each bar marking [(1−ε)p, (1+ε)p] — the window Pr[M(a)=k] is allowed to sit
    in. Makes the 'ε ≈ how many % it may wobble' idea concrete."""
    import matplotlib.pyplot as plt
    outcomes = np.array([0, 1, 2, 3, 4])
    p = np.array([0.10, 0.22, 0.34, 0.22, 0.12]); p = p / p.sum()
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.bar(outcomes, p, width=0.55, color="#c9d2f7", edgecolor="#4a5bd0",
           label="Pr[M(a′) = k]  (one neighbour)")
    lo, hi = (1 - eps) * p, (1 + eps) * p
    ax.errorbar(outcomes, p, yerr=[p - lo, hi - p], fmt="none", ecolor="#2e9e7a",
                elinewidth=9, alpha=.5, capsize=0)
    for k, pk, h in zip(outcomes, p, hi):
        ax.plot([k - 0.28, k + 0.28], [h, h], color="#1d6b3a", lw=1)
        ax.plot([k - 0.28, k + 0.28], [(1 - eps) * pk] * 2, color="#1d6b3a", lw=1)
    ax.plot([], [], color="#2e9e7a", lw=9, alpha=.5,
            label=f"allowed window for Pr[M(a)=k]:  (1±ε)·p,  ε={eps:g}")
    ax.set_xlabel("possible output k"); ax.set_ylabel("probability")
    ax.set_title(f"ε ≈ how far each probability may wobble when one person changes\n"
                 f"here ε = {eps:g}  →  each bar may move by at most about ±{eps*100:.0f}%",
                 fontsize=10.5, color="#2b2d6b")
    ax.set_ylim(0, max(hi) * 1.25); ax.legend(fontsize=9, loc="upper right")
    plt.tight_layout(); plt.show()


def neighbourhood_examples():
    """Show three neighbourhood relations from the lecture as clickable cards."""
    def ex(icon, txt):
        return ('<div style="flex:1 1 260px;min-width:260px;border:1px solid #e2e5ef;border-radius:10px;'
                'padding:11px 13px;font-size:12.5px;color:#333;line-height:1.55;background:#fbfcfe">'
                '%s %s</div>' % (icon, txt))
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:4px">'
        '👥 What counts as &ldquo;neighbouring&rdquo;? You choose it.</div>'
        '<div style="font-size:12.5px;color:#555;margin-bottom:12px;line-height:1.5">'
        'The neighbourhood defines <i>what you are hiding</i>. It is written <b>(a, a′) ∈ Neigh</b> '
        'and is usually symmetric. Three common choices:</div>'
        '<div style="display:flex;gap:12px;flex-wrap:wrap">%s%s%s</div>'
        '<div style="background:#f6f7fb;border-radius:8px;padding:10px 13px;margin-top:12px;'
        'font-size:12px;color:#555;line-height:1.6">In this notebook we mostly use the first one: '
        '<b>add or remove one person</b>. That is exactly what protects against membership '
        'inference.</div>'
        % (ex("➕➖", "<b>Add / remove one person:</b> a′ is a with one individual added or removed. "
              "Protects <i>membership</i> — were you in the data at all?"),
           ex("✏️", "<b>Change one person's features:</b> a′ swaps one individual's record for a "
              "different one — e.g. edit <i>one client's</i> income field. Protects the "
              "<i>contents</i> of any single record."),
           ex("📏", "<b>Bounded distance:</b> a′ is any dataset with ‖a − a′‖<sub>p</sub> &lt; R — "
              "e.g. two client profiles (income, age, debt) that differ by less than R. We want the "
              "release to look the same for any two <i>nearby</i> profiles.")))


# ===========================================================================
#  §3  Why we must add noise — Laplace & Gaussian, and closeness in eps
# ===========================================================================
def why_noise_viz():
    """Deterministic mechanism -> James is exposed. Same James setting as the setup
    diagram: 'James repays' → count 2, 'James defaults' → count 3. Left: two clean
    spikes (labels parked off them). Right: the same after adding Laplace noise, so
    the two worlds overlap and a single number no longer decides James's status."""
    import matplotlib.pyplot as plt
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)

    # left: no noise. Spikes at 2 and 3; labels parked out to the sides with arrows.
    axL.axvline(2, color="#333", lw=3)
    axL.axvline(3, color="#4a5bd0", lw=3)
    axL.annotate("count = 2\nJames repays", (2, 0.72), textcoords="offset points",
                 xytext=(-58, 6), ha="center", fontsize=9.5, color="#333", fontweight="bold",
                 arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.2))
    axL.annotate("count = 3\nJames defaults", (3, 0.42), textcoords="offset points",
                 xytext=(60, 6), ha="center", fontsize=9.5, color="#3b3f9e", fontweight="bold",
                 arrowprops=dict(arrowstyle="-|>", color="#4a5bd0", lw=1.2))
    axL.set_ylim(0, 1.0); axL.set_xlim(-1, 6); axL.set_yticks([])
    axL.set_title("No noise: two lonely spikes\n→ subtract the 2 known defaulters → James is exposed",
                  fontsize=10, color="#a3352f")
    axL.set_xlabel("published count")

    t = np.linspace(-4, 9, 600)
    pa, pap = laplace_pdf(t, 2, 1.0), laplace_pdf(t, 3, 1.0)
    axR.plot(t, pa, color="#333", lw=2, label="James repays (2 + noise)")
    axR.plot(t, pap, color="#4a5bd0", lw=2, label="James defaults (3 + noise)")
    axR.fill_between(t, np.minimum(pa, pap), color="#8a8fae", alpha=.35)
    axR.set_ylim(0, 0.6); axR.set_xlim(-4, 9); axR.set_yticks([])
    axR.set_title("Add noise (‘count + a random draw’): the two worlds overlap\n"
                  "→ one published number no longer decides James",
                  fontsize=10, color="#1d6b3a")
    axR.set_xlabel("published count"); axR.legend(fontsize=9)
    plt.tight_layout(); plt.show()
    print("‘count + noise’ means: take the true count and add one random Laplace draw, so the")
    print("published number might be 2.3, 1.1, 3.8, … — a distribution, not a fixed giveaway.")


def observe_scenarios_viz():
    """The heart of the intuition: the attacker OBSERVES one published number (say
    2.6) and asks which world it came from. Two panels — LOW noise vs HIGH noise —
    each showing the density under 'James repays' (2) and 'James defaults' (3), the
    observed value, and the likelihood ratio between the two worlds. Low noise
    leaks (ratio far from 1); high noise hides James but can publish nonsense
    (a negative count of defaulters)."""
    import matplotlib.pyplot as plt
    obs = 2.6
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.4, 4.4))

    for ax, b, xlim, title in [
            (axL, 0.4, (-1, 6), "LOW noise (b = 0.4)"),
            (axR, 4.0, (-14, 18), "HIGH noise (b = 4)")]:
        t = np.linspace(xlim[0], xlim[1], 1200)
        p_rep, p_def = laplace_pdf(t, 2, b), laplace_pdf(t, 3, b)
        ax.plot(t, p_rep, color="#333", lw=2, label="James repays (true count 2)")
        ax.plot(t, p_def, color="#4a5bd0", lw=2, label="James defaults (true count 3)")
        d_rep, d_def = laplace_pdf(obs, 2, b), laplace_pdf(obs, 3, b)
        ax.axvline(obs, ls="--", color="#c0554e", lw=1.6)
        ax.plot([obs], [d_rep], "o", color="#333"); ax.plot([obs], [d_def], "o", color="#4a5bd0")
        ratio = d_def / d_rep
        ax.set_title(f"{title}\nsee {obs}: 'defaults' is {ratio:.1f}× as likely as 'repays'",
                     fontsize=10, color="#2b2d6b")
        ax.set_xlim(*xlim); ax.set_yticks([]); ax.set_xlabel("published number")
        ax.legend(fontsize=8, loc="upper left")
        peak = laplace_pdf(0, 0, b)
        ax.set_ylim(0, peak * 1.15)
        ax.annotate(f"observed = {obs}", (obs, peak * 0.9), textcoords="offset points",
                    xytext=(8, 0), fontsize=8.5, color="#a3352f")
        if b >= 4:
            # mark that impossible values (a negative count) now carry real probability
            ax.axvspan(xlim[0], 0, color="#c0554e", alpha=.08)
            pneg = 0.5 * np.exp(-2 / b)   # P(release < 0 | true count 2) for Laplace(2, b)
            ax.text(xlim[0] + 0.5, peak * 0.55,
                    f"a published count below 0\nhappens ~{pneg*100:.0f}% of the time —\n"
                    "e.g. “−8 defaulters” (nonsense!)",
                    fontsize=8, color="#a3352f")
    plt.tight_layout(); plt.show()
    print("Low noise: the observed number leans toward one world → James leaks.")
    print("High noise: the two worlds are almost equally likely → James is hidden — but the")
    print("published figure can come out negative, i.e. an impossible count of defaulters.")
    print()
    print("⚠️ And crucially: the bank does NOT get to 're-roll'. You run the mechanism ONCE and")
    print("publish whatever it draws — even a −8. If you rejected ugly draws and re-sampled, some")
    print("outputs would never appear, the two worlds would stop overlapping there, and the privacy")
    print("guarantee would break. A DP mechanism must be sampled fairly, exactly as defined.")
    print()
    print("Somewhere between too little and too much noise is the sweet spot. The dial is ε (next).")


def laplace_gaussian_shapes():
    """Two panels: Laplace at several scales, Gaussian at several std devs, so the
    'sharp peak / heavy tails' vs 'bell' contrast is visible."""
    import matplotlib.pyplot as plt
    t = np.linspace(-14, 14, 800)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.2))
    for b, c in [(1, "#c0554e"), (2, "#333"), (4, "#4a5bd0")]:
        axL.plot(t, laplace_pdf(t, 0, b), color=c, lw=2, label=f"scale b={b}")
    # highlight the heavy tail of the widest one: big, even nonsensical values are possible
    tail = t >= 8
    axL.fill_between(t, 0, laplace_pdf(t, 0, 4), where=tail, color="#4a5bd0", alpha=.25)
    axL.annotate("heavy tail: with b=4, the noise alone\ncan be +10 — so a true count of 2 might\n"
                 "be reported as 12 (or as −8: negative!)",
                 (10, laplace_pdf(10, 0, 4)), textcoords="offset points", xytext=(-150, 70),
                 fontsize=8.5, color="#3b3f9e",
                 arrowprops=dict(arrowstyle="-|>", color="#4a5bd0", lw=1.1))
    axL.set_title("Laplace  —  p(t) = 1/(2b)·exp(−|t|/b)\nsharp peak, heavy tails",
                  fontsize=10.5, color="#2b2d6b")
    axL.set_xlabel("noise value t"); axL.set_ylabel("density"); axL.legend(fontsize=9)
    axL.set_ylim(0, 0.55)

    for s, c in [(1, "#c0554e"), (2, "#333"), (4, "#4a5bd0")]:
        axR.plot(t, gaussian_pdf(t, 0, s), color=c, lw=2, label=f"std σ={s}")
    axR.set_title("Gaussian  —  the familiar bell curve\nrounder peak, lighter tails",
                  fontsize=10.5, color="#2b2d6b")
    axR.set_xlabel("noise value t"); axR.set_ylabel("density"); axR.legend(fontsize=9)
    axR.set_ylim(0, 0.45)
    plt.tight_layout(); plt.show()
    print("Bigger scale/σ → wider, flatter noise → more privacy, but a fuzzier answer.")
    print("And the tails never vanish: the published number can land far from the truth — even at")
    print("impossible values (a negative count) — which is the price of hiding any single person.")


def eps_closeness_viz(eps, sensitivity=1.0):
    """For a given eps, draw the two Laplace worlds — 'James repays' (centred at 2)
    and 'James defaults' (centred at 3) — with noise scale b = Δ/ε. A FIXED x-axis
    across calls lets students compare directly how far the two worlds sit apart:
    a small ε (lots of noise, wide curves) hides James; a large ε (little noise,
    peaky curves) exposes him."""
    import matplotlib.pyplot as plt
    b = sensitivity / eps
    t = np.linspace(-8, 13, 1000)             # FIXED range, so different ε are comparable
    pa, pap = laplace_pdf(t, 2, b), laplace_pdf(t, 3, b)
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    ax.plot(t, pa, color="#333", lw=2, label="James repays (count 2)")
    ax.plot(t, pap, color="#4a5bd0", lw=2, label="James defaults (count 3)")
    ax.fill_between(t, np.minimum(pa, pap), color="#8a8fae", alpha=.30)
    verdict = "little noise → James easy to spot" if eps >= 1 else "lots of noise → James well hidden"
    ax.set_title(f"ε = {eps:g}  (leak budget)   →   noise scale b = Δ/ε = {b:g}\n{verdict}",
                 fontsize=10.5, color="#2b2d6b", fontweight="bold")
    ax.set_xlim(-8, 13); ax.set_yticks([]); ax.set_xlabel("published number")
    ax.set_ylabel("density"); ax.legend(fontsize=9, loc="upper right")
    plt.tight_layout(); plt.show()


# ===========================================================================
#  §4  Rare-disease sum mechanism  (lecture slide 11-12)
# ===========================================================================
def sum_mechanism_table():
    """The rare-disease table and the sum mechanism, as a styled card."""
    rows = "".join(
        '<tr><td style="padding:5px 16px;border-bottom:1px solid #eee">%s</td>'
        '<td style="padding:5px 16px;border-bottom:1px solid #eee;text-align:center;font-weight:700;'
        'color:%s">%s</td></tr>' % (n, "#c0554e" if v else "#7a8092", v)
        for n, v in [("Jane", 1), ("John", 1), ("Richard", 0)])
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px">'
        '🏥 A warm-up everyone can follow: counting a rare disease</div>'
        '<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start">'
        '<div><table style="border-collapse:collapse;font-size:13px">'
        '<tr><th style="padding:5px 16px;text-align:left;border-bottom:2px solid #ccc">Name</th>'
        '<th style="padding:5px 16px;border-bottom:2px solid #ccc">Has disease (aᵢ)</th></tr>'
        '%s</table></div>'
        '<div style="flex:1;min-width:280px;font-size:12.5px;color:#333;line-height:1.7">'
        'We publish <b>how many patients have the disease</b>. The honest answer is a plain sum:'
        '<div style="text-align:center;font-size:16px;background:#f1f3fd;border-radius:8px;'
        'padding:10px;margin:8px 0">M(a) = (Σ aᵢ) + Lap(0, 1/ε)</div>'
        '<b>Neighbourhood:</b> (a, a′) ∈ Neigh ⟺ ‖a − a′‖₀ ≤ 1 &nbsp;(one person changes).<br>'
        '<b>What we protect:</b> the <i>identity of the members</i> — nobody should learn whether '
        '<i>Richard</i> specifically has the disease from the published number.</div></div>'
        % rows, maxw=980)


def pointwise_equivalence_card():
    """State the set-vs-pointwise equivalence theorem in words."""
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px">'
        '🔑 From &ldquo;one observed value&rdquo; to &ldquo;any question S&rdquo;</div>'
        '<div style="font-size:12.5px;color:#333;line-height:1.7">'
        'Just now we reasoned <b>pointwise</b>: we compared the two worlds at a <i>single</i> observed '
        'value (2.6). But a real attacker can also ask about a whole <b>set</b> — '
        '&ldquo;is the published number <i>between</i> 2 and 5?&rdquo; That set is the <b>outcome set '
        'S</b>, and the definition must hold for <i>every</i> such S — infinitely many. Luckily, for '
        'mechanisms with a density, the two views are equivalent:'
        '<div style="text-align:center;font-size:14px;background:#f1f3fd;border-radius:8px;'
        'padding:12px;margin:10px 0;line-height:1.9">'
        '&forall; single points b: &nbsp; p(M(a)=b) ≤ e<sup>ε</sup> p(M(a′)=b)<br>'
        '⟺&nbsp; &forall; sets S: &nbsp; Pr[M(a)∈S] ≤ e<sup>ε</sup> Pr[M(a′)∈S]</div>'
        'In words: <b>if the two density curves stay within a factor e<sup>ε</sup> at every single '
        'point, then every interval-probability does too.</b> So checking the easy pointwise picture '
        'already covers every question S the attacker could dream up.</div>')


# ===========================================================================
#  §5  Laplace mechanism theorem + sensitivity
# ===========================================================================
def sensitivity_viz(f_label="f = count of clients with the disease",
                    values=((("a", [1, 1, 0]), 2), (("a′", [1, 0, 0]), 1))):
    """Illustrate L1 sensitivity: the largest change in f over any neighbouring
    pair. Simple bar showing f(a) vs f(a') differing by 1."""
    import matplotlib.pyplot as plt
    (la, va), (lap, vap) = ((values[0][0][0], values[0][1]),
                            (values[1][0][0], values[1][1]))
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.bar([0, 1], [va, vap], color=["#333", "#4a5bd0"], width=0.5)
    ax.set_xticks([0, 1]); ax.set_xticklabels([f"f({la})={va}", f"f({lap})={vap}"])
    ax.annotate("", xy=(1, vap), xytext=(1, va),
                arrowprops=dict(arrowstyle="<|-|>", color="#c0554e", lw=2))
    ax.text(1.08, (va + vap) / 2, f"Δ = |{va}−{vap}| = {abs(va - vap)}",
            color="#a3352f", fontsize=11, fontweight="bold", va="center")
    ax.set_title("Sensitivity Δ₁ = the LARGEST |f(a) − f(a′)| over all neighbours",
                 fontsize=10.5, color="#2b2d6b")
    ax.set_ylabel(f_label, fontsize=9)
    ax.set_ylim(0, max(va, vap) + 1.2)
    plt.tight_layout(); plt.show()
    print("For a counting query, adding/removing one person changes the count by at most 1,")
    print("so Δ₁ = 1. The Laplace theorem then says: add Lap(0, Δ₁/ε) = Lap(0, 1/ε).")


def laplace_theorem_card():
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px">'
        '📜 Theorem (Laplace mechanism)</div>'
        '<div style="text-align:center;font-size:17px;background:#eef7f0;border:1px solid #cfe8d8;'
        'border-radius:10px;padding:14px;margin-bottom:12px">'
        'f(a) + Lap(0, <b>Δ₁</b>/ε) &nbsp;is&nbsp; <b>ε-DP</b></div>'
        # --- unpack the sensitivity formula, piece by piece ---
        '<div style="text-align:center;font-size:15px;margin:2px 0 10px">'
        'Δ₁ &nbsp;=&nbsp; <span style="color:#c0554e">max<sub>(a,a′)∈Neigh</sub></span> '
        '<span style="color:#3b3f9e">‖ f(a) − f(a′) ‖₁</span></div>'
        '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px">'
        '<div style="flex:1 1 300px;min-width:300px;border:1px solid #eecfcb;border-radius:9px;'
        'padding:9px 12px;font-size:12px;color:#333;line-height:1.6">'
        '<b style="color:#c0554e">the max over the neighbourhood</b> — we look at the <i>worst</i> '
        'pair of neighbours <b>allowed by the neighbourhood we defined</b>. For a count with '
        '&ldquo;add/remove one client&rdquo;, that worst case is <i>any</i> client set, plus one more '
        'client — whoever they are, the count moves by 1. It is not tied to James specifically.</div>'
        '<div style="flex:1 1 300px;min-width:300px;border:1px solid #cfd4ee;border-radius:9px;'
        'padding:9px 12px;font-size:12px;color:#333;line-height:1.6">'
        '<b style="color:#3b3f9e">the L1 norm ‖·‖₁</b> — the sum of the absolute differences, one per '
        'output dimension. When the output is a <b>single number</b> (as here), there is only one '
        'dimension, so this is just the plain <b>|f(a) − f(a′)|</b>.</div></div>'
        # --- worked example: average height ---
        '<div style="background:#f6f7fb;border-radius:8px;padding:11px 13px;font-size:12.5px;'
        'color:#333;line-height:1.7">'
        '📏 <b>A worked example — publishing an average.</b> Say we release the <b>average height</b> '
        'of our N clients, and heights are known to lie between <b>140 cm and 220 cm</b>. The '
        'neighbourhood is &ldquo;change one client&rsquo;s height&rdquo;. How far can <i>one</i> person '
        'move the average? At most from the bottom of the range to the top, spread over N people:'
        '<div style="text-align:center;font-size:15px;margin:6px 0">'
        'Δ₁ = (220 − 140) / N = 80 / N</div>'
        'Two lessons fall straight out of the formula for the noise scale <b>Δ₁/ε</b>:<br>'
        '• a <b>wider possible range</b> (say heights could span 0–300 instead of 140–220) makes Δ₁ '
        'bigger → <b>more noise</b>. One person can do more damage, so you must hide more.<br>'
        '• a <b>smaller leak budget ε</b> divides into Δ₁ → <b>more noise</b>. Tighter privacy always '
        'costs utility.</div>'
        '<div style="background:#fff8ec;border:1px solid #f0d9a8;border-radius:8px;padding:10px 13px;'
        'margin-top:10px;font-size:12px;color:#5a4a2a;line-height:1.6">'
        '⭐ <b>Optional proof sketch.</b> Write the ratio of the two Laplace densities at a point b. '
        'The exponent is (−|b−f(a)| + |b−f(a′)|)/(Δ₁/ε). By the reverse triangle inequality that '
        'numerator is at most |f(a)−f(a′)| ≤ Δ₁, so the whole exponent is ≤ ε — i.e. the ratio is ≤ '
        'e<sup>ε</sup>. Pointwise ≤ e<sup>ε</sup> ⇒ ε-DP by the pointwise equivalence. ∎</div>')


# ===========================================================================
#  §7  Limits of eps-DP  ->  (eps, delta)-DP
# ===========================================================================
def eps_limit_viz():
    """Show the failure mode: if M(a) can output something M(a') never can (a
    'hole' of zero density), the ratio blows up and pure eps-DP is impossible.
    (eps,delta)-DP tolerates a delta-sized hole."""
    import matplotlib.pyplot as plt
    t = np.linspace(-6, 8, 700)
    pa = gaussian_pdf(t, 1.0, 1.0)
    pap = gaussian_pdf(t, 0.0, 1.0)
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ax.plot(t, pa, color="#333", lw=2, label="M(a)")
    ax.plot(t, pap, color="#4a5bd0", lw=2, label="M(a′)")
    ax.fill_between(t, 0, pa, where=(t > 4.2), color="#c0554e", alpha=.5)
    ax.annotate("far in the tail, M(a) still has mass\nbut M(a′) is ~0 → ratio explodes",
                (5.0, gaussian_pdf(5.0, 1.0, 1.0)), textcoords="offset points",
                xytext=(-40, 60), fontsize=9, color="#a3352f",
                arrowprops=dict(arrowstyle="-|>", color="#a3352f", lw=1.2))
    ax.set_title("Why pure ε-DP is fragile: no point may have zero density where the other has mass\n"
                 "(ε,δ)-DP forgives this — up to a total slack of δ",
                 fontsize=10, color="#2b2d6b")
    ax.set_xlabel("output value"); ax.set_yticks([]); ax.legend(fontsize=9)
    plt.tight_layout(); plt.show()


def eps_delta_card():
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px">'
        '📐 Generalisation: (ε, δ)-DP</div>'
        '<div style="text-align:center;font-size:18px;background:#f1f3fd;border-radius:10px;'
        'padding:14px;margin-bottom:10px">'
        'Pr[M(a)∈S] ≤ e<sup>ε</sup> · Pr[M(a′)∈S] &nbsp;<b>+ δ</b></div>'
        '<div style="font-size:12.5px;color:#333;line-height:1.7">'
        'The extra <b>δ</b> is an <b>absolute</b> slack added to the probability (the ε factor was a '
        '<i>relative</i> one). Two things it buys us:<br>'
        '• it <b>allows the supports to differ</b> — the distributions can have small regions the '
        'other never reaches, as long as their total mass is ≤ δ;<br>'
        '• it lets us use lighter-tailed noise like the <b>Gaussian</b>.<br>'
        'Think of δ as a small &ldquo;probability of an embarrassing leak&rdquo; — you want it tiny, '
        'e.g. δ = 10<sup>−5</sup>, typically far smaller than 1/(number of people).</div>')


# ===========================================================================
#  §8  Gaussian mechanism
# ===========================================================================
def gaussian_theorem_card():
    _card(
        '<div style="font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:8px">'
        '📜 Theorem (Gaussian mechanism)</div>'
        '<div style="text-align:center;font-size:16px;background:#eef7f0;border:1px solid #cfe8d8;'
        'border-radius:10px;padding:14px;margin-bottom:10px">'
        'f(a) + 𝒩(0, σ²I) &nbsp;is&nbsp; <b>(ε, δ)-DP</b> &nbsp;&nbsp;for&nbsp;&nbsp; '
        'σ = √(2 ln(1.25/δ)) · Δ₂ / ε</div>'
        '<div style="font-size:12.5px;color:#333;line-height:1.7">'
        'Now the sensitivity is measured in the <b>L2</b> norm, '
        'Δ₂ = max<sub>(a,a′)∈Neigh</sub> ‖f(a) − f(a′)‖₂. The recipe is the same as Laplace — '
        '<b>bound the sensitivity, then set the noise scale from it</b> — but the formula also folds '
        'in δ (through the √(2 ln(1.25/δ)) factor) and ε. Smaller ε or smaller δ ⇒ bigger σ ⇒ more '
        'noise. The Gaussian is the workhorse for machine learning, because gradients are vectors and '
        'L2 is their natural norm.</div>')


def gaussian_noise_scale_viz(delta=1e-5, sensitivity=1.0):
    """Plot the Gaussian sigma needed as a function of eps, to make the
    privacy/noise trade-off concrete."""
    import matplotlib.pyplot as plt
    eps = np.linspace(0.1, 5, 200)
    sigma = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / eps
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.plot(eps, sigma, color="#4a5bd0", lw=2.5)
    for e in [0.5, 1, 2]:
        s = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / e
        ax.plot([e], [s], "o", color="#c0554e")
        ax.annotate(f"ε={e}: σ={s:.1f}", (e, s), textcoords="offset points",
                    xytext=(8, 6), fontsize=9, color="#a3352f")
    ax.set_xlabel("privacy budget ε"); ax.set_ylabel("required noise σ")
    ax.set_title(f"More privacy (smaller ε) needs more noise  (δ={delta:g}, Δ₂={sensitivity:g})",
                 fontsize=10.5, color="#2b2d6b")
    plt.tight_layout(); plt.show()


# ===========================================================================
#  §9  Composability — post-processing & composition
# ===========================================================================
def composition_diagram():
    """Two side-by-side cards: post-processing (free) and composition (budgets add)."""
    post = (
        '<div style="flex:1 1 320px;min-width:320px;border:2px solid #2e9e7a;border-radius:12px;'
        'padding:13px 15px">'
        '<div style="font-weight:800;font-size:14px;color:#1d6b3a;margin-bottom:6px">'
        '♻️ Post-processing is free</div>'
        '<div style="text-align:center;font-size:14px;background:#eef7f0;border-radius:8px;'
        'padding:9px;margin-bottom:8px">M is (ε,δ)-DP &nbsp;⇒&nbsp; f∘M is (ε,δ)-DP</div>'
        '<div style="font-size:12px;color:#333;line-height:1.6"><b>Intuition:</b> f gets to see only '
        'the already-noisy output, never the data. Any f can only <b>blur the two worlds together '
        'further</b> — it can never pull them <i>further apart</i>, because it has no new information '
        'about James to work with. So rounding, thresholding, plotting, or feeding the result to '
        'another model is all free — even against unbounded computation.</div></div>')
    comp = (
        '<div style="flex:1 1 320px;min-width:320px;border:2px solid #4a5bd0;border-radius:12px;'
        'padding:13px 15px">'
        '<div style="font-weight:800;font-size:14px;color:#3b3f9e;margin-bottom:6px">'
        '➕ Composition: budgets add up</div>'
        '<div style="text-align:center;font-size:13px;background:#f1f3fd;border-radius:8px;'
        'padding:9px;margin-bottom:8px">M₁:(ε₁,δ₁) &amp; M₂:(ε₂,δ₂) &nbsp;⇒&nbsp; '
        '(M₁,M₂):(ε₁+ε₂, δ₁+δ₂)</div>'
        '<div style="font-size:12px;color:#333;line-height:1.6"><b>Intuition:</b> imagine releasing '
        'the noisy count <i>twice</i>. Now the attacker can average the two draws and land closer to '
        'the truth. Release it again and again and the noise averages away — they can '
        '<b>reconstruct the true f(a)</b>, and James is exposed. Each release hands over more, so the '
        'budgets <b>add</b>. This is why training — <i>thousands</i> of noisy steps — is the hard '
        'case.</div></div>')
    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:10px">'
        '🧮 Two rules that let you build big private algorithms from small ones</div>'
        '<div style="display:flex;gap:14px;flex-wrap:wrap">%s%s</div>' % (post, comp), maxw=1000)


def composition_illustration(seed=0):
    """Interactive slider: drag the NUMBER OF QUERIES up and watch each noisy
    release land as a dot that fills in a histogram. With few queries the picture
    is noise; with many, the histogram traces out the true distribution and its
    centre (the true f(a)) becomes obvious. That reconstruction is exactly why
    every extra release spends privacy budget."""
    rng = np.random.default_rng(seed)
    center, b = 3.0, 2.0
    samples = np.round(rng.laplace(center, b, size=500), 3).tolist()
    data = {"s": samples, "c": center, "b": b, "xlo": -8.0, "xhi": 14.0, "nb": 44}
    uid = "comp_" + str(abs(hash(tuple(samples[:8]))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:14px;padding:16px;max-width:620px;background:#fff;color:#1c1e2a}
#__UID__ .c-head{font-weight:800;font-size:15px;color:#2b2d6b;margin-bottom:6px}
#__UID__ .c-row{display:flex;align-items:center;gap:10px;margin-top:8px}
#__UID__ input[type=range]{flex:1}
#__UID__ .c-lab{font-size:12.5px;font-weight:700;color:#3b2d6b;width:120px}
#__UID__ .c-cap{font-size:12px;color:#444;margin-top:8px;line-height:1.5;min-height:34px}
</style>
<div id="__UID__">
  <div class="c-head">🔁 More queries → the attacker rebuilds the whole distribution</div>
  <svg width="600" height="360"></svg>
  <div class="c-row">
    <span class="c-lab">queries: <span class="c-n">1</span></span>
    <input type="range" min="1" max="500" value="1">
  </div>
  <div class="c-cap"></div>
</div>
<script>
(function(){
  const D=__DATA__, root=document.getElementById("__UID__");
  const svg=root.querySelector("svg"), NS="http://www.w3.org/2000/svg";
  const ML=48, MR=16, MT=28, MB=58, W=600-ML-MR, H=360-MT-MB, y0=MT+H;
  const bw=(D.xhi-D.xlo)/D.nb;
  const peak=1/(2*D.b), yMax=peak*1.25;
  const sx=x=>ML+(x-D.xlo)/(D.xhi-D.xlo)*W;
  const sy=d=>y0-Math.min(d,yMax)/yMax*H;
  function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
  const rng=root.querySelector("input"), cap=root.querySelector(".c-cap"), nlab=root.querySelector(".c-n");
  function dens(x){return 1/(2*D.b)*Math.exp(-Math.abs(x-D.c)/D.b);}
  function draw(k){
    while(svg.firstChild)svg.removeChild(svg.firstChild);
    svg.appendChild(el("rect",{x:ML,y:MT,width:W,height:H,fill:"#fff",stroke:"#e4e7ef"}));
    // histogram of the first k samples
    const counts=new Array(D.nb).fill(0); let sum=0;
    for(let i=0;i<k;i++){const v=D.s[i]; sum+=v;
      let j=Math.floor((v-D.xlo)/bw); if(j>=0&&j<D.nb)counts[j]++;}
    for(let j=0;j<D.nb;j++){
      const dv=counts[j]/(k*bw);            // empirical density
      const x0=sx(D.xlo+j*bw), x1=sx(D.xlo+(j+1)*bw);
      svg.appendChild(el("rect",{x:x0+0.5,y:sy(dv),width:x1-x0-1,height:y0-sy(dv),
        fill:"#c9d2f7",stroke:"#a9b6ef"}));
    }
    // the true density curve the attacker is converging to
    let pts=""; for(let x=D.xlo;x<=D.xhi;x+=0.2){pts+=sx(x)+","+sy(dens(x))+" ";}
    svg.appendChild(el("polyline",{points:pts,fill:"none",stroke:"#4a5bd0","stroke-width":2}));
    // ONE red dot per query, on the axis under the bucket it landed in (a 'rug')
    for(let i=0;i<k;i++){
      svg.appendChild(el("circle",{cx:sx(D.s[i]),cy:y0+7,r:2.4,fill:"#c0554e","fill-opacity":0.35}));
    }
    // true centre (the secret f(a)) and the attacker's running estimate
    svg.appendChild(el("line",{x1:sx(D.c),y1:MT,x2:sx(D.c),y2:y0,stroke:"#c0554e",
      "stroke-width":2,"stroke-dasharray":"5 4"}));
    let tt=el("text",{x:sx(D.c),y:MT-6,"text-anchor":"middle","font-size":11,fill:"#a3352f","font-weight":700});
    tt.textContent="true f(a)="+D.c; svg.appendChild(tt);
    const est=sum/k;
    svg.appendChild(el("line",{x1:sx(est),y1:MT,x2:sx(est),y2:y0,stroke:"#1d6b3a","stroke-width":2}));
    let et=el("text",{x:ML+6,y:MT+14,"font-size":11,fill:"#1d6b3a","font-weight":700});
    et.textContent="estimate = "+est.toFixed(2); svg.appendChild(et);
    // axis labels
    let xl=el("text",{x:ML+W/2,y:y0+42,"text-anchor":"middle","font-size":11.5,fill:"#444"});
    xl.textContent="published number  (each ● = one query)"; svg.appendChild(xl);
    const yc=MT+H/2;
    let yl=el("text",{x:15,y:yc,"text-anchor":"middle","font-size":11.5,fill:"#444",
      transform:"rotate(-90 15 "+yc+")"});
    yl.textContent="how often observed (density)"; svg.appendChild(yl);
    nlab.textContent=k;
    cap.innerHTML = k<8
      ? "A handful of queries is just noise — the attacker can barely guess where the centre is."
      : (k<60
        ? "The histogram is taking shape; the estimate ("+est.toFixed(2)+") is closing in on the truth."
        : "With "+k+" queries the histogram traces the true distribution and the estimate ("+est.toFixed(2)+") ≈ the secret f(a). Privacy has leaked away.");
  }
  rng.addEventListener("input",()=>draw(+rng.value));
  draw(1);
})();
</script>'''
    html = tmpl.replace("__UID__", uid).replace("__DATA__", _json.dumps(data))
    display(HTML(html))


# ===========================================================================
#  §11  DP-SGD
# ===========================================================================
def logreg_recap(w=(1.0, 1.0), b=0.0):
    """Recap of the notebook-03 logistic regression, re-dressed for THIS notebook's
    setting: a bank classifier predicting whether a client will DEFAULT on a loan.
    Left: the sigmoid turning a score into P(default). Right: the two loan features
    split by a straight boundary into default / repay."""
    import matplotlib.pyplot as plt
    w = np.asarray(w, float)
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.4))

    # left: the sigmoid — z = 0 maps to exactly 0.5 (the boundary)
    z = np.linspace(-6, 6, 300)
    axL.plot(z, 1 / (1 + np.exp(-z)), color="#4a5bd0", lw=2.5)
    axL.axhline(0.5, ls="--", color="#c0554e", lw=1.2)
    axL.axvline(0, ls=":", color="#9aa0b5", lw=1)
    axL.plot([0], [0.5], marker="o", ms=9, color="#c0554e", zorder=5)
    axL.annotate(r"$\sigma(0)=0.5$" "\nexactly on the boundary", (0, 0.5),
                 textcoords="offset points", xytext=(10, -34), fontsize=9, color="#a3352f")
    axL.text(2.0, 0.83, "score > 0 → predict DEFAULT", fontsize=9.5, color="#a3352f")
    axL.text(-5.8, 0.12, "score < 0 → predict REPAY", fontsize=9.5, color="#1d6b3a")
    axL.set_title(r"Step 1: squash a score into a probability" "\n"
                  r"$\sigma(z)=\dfrac{1}{1+e^{-z}}$", fontsize=10.5, color="#2b2d6b")
    axL.set_xlabel("score  z = w·x + b"); axL.set_ylabel("P(default)")
    axL.set_ylim(-0.05, 1.05)

    # right: the 2-D decision regions (red = default side, green = repay side)
    lo, hi = -2.0, 2.5
    gx, gy = np.meshgrid(np.linspace(lo, hi, 240), np.linspace(lo, hi, 240))
    score = w[0] * gx + w[1] * gy + b
    axR.contourf(gx, gy, (score >= 0).astype(int), levels=[-0.5, 0.5, 1.5],
                 colors=["#e3f4ea", "#fbe3e0"], alpha=.9)
    xs = np.linspace(lo, hi, 50)
    if abs(w[1]) > 1e-9:
        axR.plot(xs, -(w[0] * xs + b) / w[1], color="#333", lw=2)
    axR.annotate(r"boundary:  $w_1x_1 + w_2x_2 + b = 0$   ($\sigma=0.5$)",
                 (0.02, 0.02), xycoords="axes fraction", fontsize=9, color="#333")

    # place DEFAULT / REPAY labels by stepping along the weight normal from a
    # central boundary point, so they always land on the correct side.
    wn = w / (np.linalg.norm(w) + 1e-9)
    pc = np.array([0.25, -(w[0] * 0.25 + b) / w[1]]) if abs(w[1]) > 1e-9 else np.array([-b / w[0], 0.25])
    dft, rep = pc + wn * 1.5, pc - wn * 1.5
    axR.text(dft[0], dft[1], "DEFAULT", fontsize=11, fontweight="bold", color="#a3352f",
             ha="center", va="center")
    axR.text(rep[0], rep[1], "REPAY", fontsize=11, fontweight="bold", color="#1d6b3a",
             ha="center", va="center")

    # a worked point ON the boundary, with drops to each axis so w1/w2 are concrete
    xp = 1.0
    yp = -(w[0] * xp + b) / w[1] if abs(w[1]) > 1e-9 else 0.0
    axR.plot([xp], [yp], marker="X", ms=13, color="#333", zorder=6)
    axR.plot([xp, xp], [0, yp], ls=":", color="#666", lw=1)
    axR.plot([0, xp], [yp, yp], ls=":", color="#666", lw=1)
    axR.axhline(0, color="#cfd4e4", lw=1); axR.axvline(0, color="#cfd4e4", lw=1)
    axR.annotate(f"client on the boundary ({xp:g}, {yp:g})\n"
                 f"score = {w[0]:g}·({xp:g}) + {w[1]:g}·({yp:g}) + {b:g} = 0\n→ σ(0) = 0.5",
                 (xp, yp), textcoords="offset points", xytext=(12, 14), fontsize=8.5, color="#333")
    axR.set_title("Step 2: the boundary  $w_1x_1 + w_2x_2 + b = 0$  splits\n"
                  "the two client features into default / repay",
                  fontsize=10.5, color="#2b2d6b")
    axR.set_xlabel("feature $x_1$  (debt-to-income ratio)")
    axR.set_ylabel("feature $x_2$  (missed payments, past year)")
    axR.set_xlim(lo, hi); axR.set_ylim(lo, hi)
    plt.tight_layout(); plt.show()


def dpsgd_diagram():
    """The DP-SGD loop as a labelled flow: per-example gradient -> clip (bound
    sensitivity) -> sum -> add Gaussian noise -> update."""
    steps = [
        ("1", "Per-example gradient", "gᵢ = ∇L(θ, xᵢ)", "one gradient per person", "#6f7bf0"),
        ("2", "Clip to norm C", "gᵢ ← gᵢ / max(1, ‖gᵢ‖₂/C)", "bounds the sensitivity → Δ₂ = C", "#dd8452"),
        ("3", "Sum", "ḡ = Σ gᵢ", "aggregate the batch", "#6f7bf0"),
        ("4", "Add Gaussian noise", "g̃ = ḡ + 𝒩(0, σ²I)", "Gaussian mechanism → (ε,δ)-DP", "#2e9e7a"),
        ("5", "Update", "θ ← θ − η·g̃/L", "ordinary SGD step", "#6f7bf0"),
    ]
    body = "".join(
        '<div style="display:flex;align-items:flex-start;gap:12px;margin:7px 0">'
        '<div style="flex:0 0 26px;height:26px;border-radius:50%%;background:%s;color:#fff;'
        'font-weight:800;display:flex;align-items:center;justify-content:center;font-size:13px">%s</div>'
        '<div><div style="font-weight:700;font-size:13px;color:#222">%s &nbsp;'
        '<code style="background:#f3f0ff;border-radius:4px;padding:1px 6px;font-size:12px">%s</code></div>'
        '<div style="font-size:11.5px;color:#777">%s</div></div></div>'
        % (c, n, title, formula.replace("<", "&lt;"), note)
        for (n, title, formula, note, c) in steps)
    _card(
        '<div style="font-weight:800;font-size:16px;color:#2b2d6b;margin-bottom:4px">'
        '🔁 DP-SGD — one training step, made private</div>'
        '<div style="font-size:12.5px;color:#555;margin-bottom:10px;line-height:1.5">'
        'The whole notebook was building to this. Steps 2 &amp; 4 are the only new bits vs ordinary '
        'SGD — <b>clip</b> to bound how much one person moves the gradient, then <b>add Gaussian '
        'noise</b> sized to that bound:</div>'
        '%s'
        '<div style="background:#eef7f0;border:1px solid #cfe8d8;border-radius:8px;padding:11px 13px;'
        'margin-top:10px;font-size:12px;color:#234;line-height:1.6">'
        '🧩 <b>It is just the pieces you already have:</b> clipping is the <i>sensitivity bound</i>; '
        'the noise is the <i>Gaussian mechanism</i>; each step is one release, so <i>composition</i> '
        'sums the budget over all T steps; and using the trained model for predictions afterwards is '
        '<i>post-processing</i> — free.</div>' % body, maxw=1000)


def _toy_bank_data(n=240, seed=0):
    """A small 2-feature banking dataset: predict 'will default' from
    (debt_ratio, months_since_last_late_payment)-style features. Linearly-ish
    separable so a logistic boundary is meaningful."""
    rng = np.random.default_rng(seed)
    n0 = n // 2
    X0 = rng.normal([-1.0, -0.6], [0.9, 0.9], size=(n0, 2))     # repays
    X1 = rng.normal([1.1, 0.7], [0.9, 0.9], size=(n - n0, 2))   # defaults
    X = np.vstack([X0, X1])
    y = np.concatenate([np.zeros(n0), np.ones(n - n0)])
    idx = rng.permutation(n)
    return X[idx], y[idx]


def _train_logreg(X, y, epochs=300, lr=0.3, clip=None, noise_sigma=0.0, seed=0):
    """Full-batch logistic-regression training. If clip/noise_sigma are set, it
    runs the DP-SGD-style private update (per-example clip + Gaussian noise)."""
    rng = np.random.default_rng(seed)
    n, d = X.shape
    w = np.zeros(d); b = 0.0
    for _ in range(epochs):
        z = X @ w + b
        p = 1 / (1 + np.exp(-z))
        # per-example gradients of BCE w.r.t (w, b)
        gw = (p - y)[:, None] * X                 # (n, d)
        gb = (p - y)                              # (n,)
        if clip is not None:
            g = np.concatenate([gw, gb[:, None]], axis=1)
            norms = np.linalg.norm(g, axis=1, keepdims=True)
            g = g / np.maximum(1.0, norms / clip)
            gw, gb = g[:, :d], g[:, d]
        gw_sum = gw.sum(0); gb_sum = gb.sum()
        if noise_sigma > 0:
            gw_sum = gw_sum + rng.normal(0, noise_sigma, size=d)
            gb_sum = gb_sum + rng.normal(0, noise_sigma)
        w -= lr * gw_sum / n
        b -= lr * gb_sum / n
    return w, b


def dpsgd_boundary_viz(seed=0):
    """Compare the decision boundary of a normally-trained model vs a DP-SGD model
    on the toy bank data — same shape, DP one is a bit noisier."""
    import matplotlib.pyplot as plt
    X, y = _toy_bank_data(seed=seed)
    w_plain, b_plain = _train_logreg(X, y)
    w_dp, b_dp = _train_logreg(X, y, clip=1.0, noise_sigma=6.0, seed=seed + 1)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, (w, b, ttl) in zip(axes, [(w_plain, b_plain, "Ordinary training (no privacy)"),
                                       (w_dp, b_dp, "DP-SGD (clipped + noisy)")]):
        ax.scatter(X[y == 0, 0], X[y == 0, 1], s=18, color="#2e9e7a", alpha=.6, label="repays")
        ax.scatter(X[y == 1, 0], X[y == 1, 1], s=18, color="#c0554e", alpha=.6, label="defaults")
        xs = np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 50)
        if abs(w[1]) > 1e-9:
            ax.plot(xs, -(w[0] * xs + b) / w[1], color="#333", lw=2)
        ax.set_title(ttl, fontsize=10.5, color="#2b2d6b")
        ax.set_xlabel("feature 1"); ax.set_ylabel("feature 2"); ax.legend(fontsize=8, loc="upper left")
    plt.tight_layout(); plt.show()
    print("Same task, same data. The private model's boundary is close but perturbed —")
    print("that perturbation is the price that hides any single client.")


def utility_privacy_curve(seed=0):
    """Accuracy vs epsilon: sweep the noise, showing utility rises as privacy
    (small eps) is relaxed. A schematic but real training run per point."""
    import matplotlib.pyplot as plt
    X, y = _toy_bank_data(seed=seed)
    Xtr, ytr, Xte, yte = X[:180], y[:180], X[180:], y[180:]
    C, delta, T = 1.0, 1e-5, 300
    epsilons = np.array([0.2, 0.4, 0.7, 1.0, 1.5, 2.5, 4.0, 7.0])
    accs = []
    for eps in epsilons:
        # per-step sigma via the Gaussian-mechanism formula, budget split over T steps
        sigma = np.sqrt(2 * np.log(1.25 / delta)) * C / (eps / np.sqrt(T))
        w, b = _train_logreg(Xtr, ytr, epochs=T, clip=C, noise_sigma=sigma, seed=seed + 2)
        pred = ((Xte @ w + b) >= 0).astype(float)
        accs.append((pred == yte).mean())
    w0, b0 = _train_logreg(Xtr, ytr)
    acc0 = (((Xte @ w0 + b0) >= 0).astype(float) == yte).mean()

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.plot(epsilons, accs, "-o", color="#4a5bd0", lw=2, label="DP-SGD model")
    ax.axhline(acc0, ls="--", color="#2e9e7a", lw=1.6, label=f"no-privacy model ({acc0:.2f})")
    ax.axhline(0.5, ls=":", color="#999", lw=1.2, label="coin flip (0.50)")
    ax.set_xlabel("privacy budget ε  (→ weaker privacy)")
    ax.set_ylabel("test accuracy")
    ax.set_title("The unavoidable trade-off: more privacy (small ε) costs utility",
                 fontsize=10.5, color="#2b2d6b")
    ax.set_ylim(0.45, 1.0); ax.legend(fontsize=9, loc="lower right")
    plt.tight_layout(); plt.show()


# ===========================================================================
#  Quiz answer keys
# ===========================================================================
_MC_QUIZZES = {
    "membership": (
        "What is a membership inference attack?",
        "Our bank trained a model only on clients with a <b>past problematic spending history</b>. "
        "An attacker runs a membership inference attack against it. What are they trying to learn?",
        ["The full source code of the model",
         "How to make the model run faster",
         "Whether one specific person was in the training set",
         "The bank's total number of employees"],
        2,
        "Membership inference asks &ldquo;was <i>this</i> record used to train the model?&rdquo; "
        "Here, a &ldquo;yes&rdquo; also reveals that person had problematic spending — which is why "
        "the setting is so sensitive."),
    "why_noise": (
        "Why must a differentially private mechanism be randomised?",
        "Suppose we published the exact count of clients with the disease, with no noise. Why does "
        "that fail to be private?",
        ["A deterministic answer changes when one person is added/removed, so comparing the two "
         "answers reveals that person",
         "Deterministic code is slower than random code",
         "Random numbers are required by law",
         "Counting is not a valid mechanism"],
        0,
        "With no noise, M(a) and M(a′) are two different fixed numbers — seeing the output tells you "
        "exactly which dataset produced it. Noise makes the two output <i>distributions</i> overlap, "
        "so a single output no longer gives the person away."),
    "eps_meaning": (
        "What does a SMALLER ε give you?",
        "You can dial the privacy budget ε. What happens as you make ε smaller (say from 2 down to "
        "0.1)?",
        ["Weaker privacy and less noise",
         "Nothing — ε has no effect on privacy",
         "The mechanism stops being random",
         "Stronger privacy: the two output distributions are forced closer together, at the cost of "
         "more noise"],
        3,
        "Smaller ε ⇒ e^ε closer to 1 ⇒ M(a) and M(a′) must be nearly identical ⇒ stronger privacy. "
        "The bound is enforced by adding more noise, which is why utility drops."),
    "sensitivity": (
        "What is the sensitivity of a counting query?",
        "We report the number of clients with the disease, with neighbourhood = add/remove one "
        "person. What is the L1 sensitivity Δ₁ of this count?",
        ["1 — adding or removing one person changes the count by at most 1",
         "0 — counts never change",
         "The total number of clients",
         "It depends on ε"],
        0,
        "One person can change a count by at most 1, so Δ₁ = 1. The Laplace mechanism then adds "
        "Lap(0, Δ₁/ε) = Lap(0, 1/ε). A query one person can swing more (e.g. a sum of loan amounts) "
        "would have a larger Δ₁ and need more noise."),
    "eps_delta": (
        "What role does δ play in (ε, δ)-DP?",
        "We generalise ε-DP to (ε, δ)-DP by adding a term: Pr[M(a)∈S] ≤ e^ε·Pr[M(a′)∈S] + δ. What "
        "is δ?",
        ["A second copy of ε",
         "The number of people in the dataset",
         "A small absolute slack — roughly a tiny allowed probability that the guarantee fails — "
         "which also lets the distributions' supports differ",
         "The learning rate of the model"],
        2,
        "δ is an absolute (additive) slack, unlike the relative e^ε factor. It permits light-tailed "
        "noise like the Gaussian and small differences in support. You want δ tiny, e.g. 10⁻⁵."),
    "composition": (
        "You run two DP releases — what is the combined guarantee?",
        "The bank publishes a noisy count that is (0.5, 0)-DP, and a noisy average that is (1.0, 0)-"
        "DP, on the same data. By the composition rule, the pair of releases together is:",
        ["(1.5, 0)-DP — the ε budgets add up",
         "(0.5, 0)-DP — the smaller budget wins",
         "(0, 0)-DP — two releases cancel out",
         "still (1.0, 0)-DP — nothing changes"],
        0,
        "Composition: budgets add. (ε₁+ε₂, δ₁+δ₂) = (0.5+1.0, 0+0) = (1.5, 0)-DP. Every extra "
        "release spends more of your privacy budget."),
    "dpsgd_clip": (
        "Why does DP-SGD clip each per-example gradient?",
        "In DP-SGD we divide each person's gradient by max(1, ‖g‖₂/C) before summing. Why is this "
        "clip step necessary?",
        ["To make training faster",
         "To remove the need for noise entirely",
         "To increase the learning rate",
         "To bound the sensitivity — capping how much any single person can move the summed "
         "gradient, so we know how much noise to add"],
        3,
        "Clipping to norm C guarantees that adding/removing one person changes the summed gradient by "
        "at most C in L2 — that is the sensitivity Δ₂ the Gaussian mechanism needs. Without it, one "
        "outlier could dominate and no fixed noise level would be private."),
    "ex2_neighbourhood": (
        "Which neighbourhood protects membership?",
        "In Problem B we publish a 2-D count and we want to hide <b>whether any one client was in the "
        "dataset at all</b>. Which neighbourhood relation encodes that?",
        ["Change one client's region label",
         "Add or remove one client from the dataset",
         "Scale every client's contribution by 2",
         "Replace the whole dataset with a fresh one"],
        1,
        "&ldquo;Was this person in the data?&rdquo; is exactly the <b>add/remove one client</b> "
        "neighbourhood — the membership question. (Changing a client's features protects the "
        "<i>contents</i> of a record instead.)"),
    "full_neighbourhood": (
        "Which neighbourhood fits the full problem?",
        "The bank will release a private count of defaulters and a private count of high-risk "
        "clients. It wants to hide <b>whether any single client is in the data at all</b>. Which "
        "neighbourhood encodes that?",
        ["Change one client's region",
         "Add or remove one client",
         "Double every client's weight",
         "Swap the two released numbers"],
        1,
        "Hiding &ldquo;is this person in the data?&rdquo; is the <b>add/remove one client</b> "
        "neighbourhood &mdash; the <b>membership</b> question. (James&rsquo;s story was the other "
        "kind: the same four people, only his <i>status</i> flipped &mdash; an attribute question.)"),
    "noise_where": (
        "Where should we inject the noise to train a private classifier?",
        "Our model outputs a 0/1 decision from logits → probability → threshold. We want the trained "
        "model to be DP. Which quantity should we add noise to?",
        ["The final 0/1 decision — flip the label with some probability",
         "The probability, right before thresholding",
         "The logits (the score before the sigmoid)",
         "The gradient of each training step — treat that step as a private release"],
        3,
        "Noising the 0/1 label is crude and destroys utility; noising the probability quickly pushes "
        "it outside [0,1] and its sensitivity can be the full 0→1 swing; noising the logits needs a "
        "sensitivity bound that is very hard to get and is re-spent on <i>every</i> query. The clean "
        "place is the <b>gradient step</b> — that is where a data point actually influences the "
        "model, so we make <i>that</i> release private (clip + Gaussian noise). The model is then DP "
        "by post-processing."),
    "query_composition": (
        "You noise the logits at inference. A user queries the model 1000 times. Then…",
        "Suppose we managed to bound the logit sensitivity and add noise at prediction time. What "
        "happens to the privacy guarantee if the same user can query the model many times?",
        ["Nothing — one bound covers unlimited queries",
         "Each query is another noisy release, so by composition the budget adds up and privacy "
         "erodes with the number of queries",
         "The budget shrinks with more queries",
         "Only the first query costs budget"],
        1,
        "Inference-time noise is re-drawn (and re-spent) every query — that is composition. 1000 "
        "queries ≈ 1000× the budget, and the guarantee collapses. Training-time DP avoids this: you "
        "pay once during training, then predictions are free post-processing."),
    "dpsgd_budget": (
        "What is the total privacy budget after T DP-SGD steps?",
        "Each of the T gradient steps is a Gaussian-mechanism release costing (ε_step, δ_step). By the "
        "basic composition rule, what does the whole training run cost?",
        ["(ε_step, δ_step) — one step's cost, no matter how many steps",
         "(ε_step / T, δ_step / T) — the cost shrinks",
         "(T·ε_step, T·δ_step) — the per-step budgets add up over all T steps",
         "(0, 0) — the steps cancel out"],
        2,
        "Composition sums budgets, so T steps cost about (T·ε_step, T·δ_step). Then using the final "
        "trained model for predictions is post-processing — free. (Tighter accountants like the "
        "moments accountant give a better-than-linear bound, but linear is the honest first answer.)"),
}

_TF_QUIZZES = {
    "dp_setup": ("Differential Privacy — the setup", [
        ("A differentially private mechanism is randomised: its output is a distribution, not a "
         "single fixed value.", True),
        ("The neighbourhood relation defines which pairs of datasets we want to keep "
         "indistinguishable.", True),
        ("DP requires the attacker to have no side information about the data.", False),
        ("The guarantee must hold for every possible outcome set S, not just a convenient one.", True),
        ("DP protects a fact that is true of the whole population regardless of any one person.", False),
    ]),
    "laplace": ("The Laplace mechanism and sensitivity", [
        ("Sensitivity Δ₁ is the largest change one neighbour-swap can cause in the output.", True),
        ("A query that one person can swing more needs LESS noise for the same ε.", False),
        ("The Laplace mechanism adds noise whose scale grows with ε.", False),
        ("For a plain counting query with add/remove-one neighbourhood, Δ₁ = 1.", True),
        ("Adding Laplace noise of scale Δ₁/ε makes a query ε-DP.", True),
    ]),
    "gaussian_delta": ("(ε,δ)-DP and the Gaussian mechanism", [
        ("The δ term is an absolute slack added to the probability bound.", True),
        ("The Gaussian mechanism measures sensitivity in the L2 norm.", True),
        ("Pure ε-DP allows one distribution to have mass where the other has exactly zero.", False),
        ("A smaller δ (all else equal) requires a larger Gaussian σ.", True),
        ("The Gaussian mechanism gives pure ε-DP with δ = 0.", False),
    ]),
    "composability": ("Post-processing & composition — which is which?", [
        ("Rounding a DP-released count to the nearest integer is post-processing (no extra budget).",
         True),
        ("Publishing two separately-noised statistics about the same people is composition (budgets "
         "add).", True),
        ("Post-processing can be used to recover the noise-free answer.", False),
        ("Plotting a chart from a DP result spends additional privacy budget.", False),
        ("Answering more queries about the same data spends more privacy budget.", True),
    ]),
    "dpsgd": ("DP-SGD, and the big picture", [
        ("DP-SGD adds noise to the gradient during training, not to the final answer only.", True),
        ("Clipping the per-example gradient bounds its sensitivity.", True),
        ("Because each step is independent, running more training steps does not spend any extra "
         "privacy budget.", False),
        ("More noise gives more privacy but tends to lower the model's accuracy.", True),
        ("Once the model is trained privately, making predictions with it costs extra privacy "
         "budget.", False),
    ]),
}


_NUMBER_QUIZZES = {
    "ex1_sensitivity": (
        "🎯 Find the sensitivity Δ₁",
        "We publish the <b>average height</b> of N = 200 clients; heights lie in [140 cm, 220 cm]; "
        "the neighbourhood changes one client's height. Type the L1 sensitivity Δ₁ (in cm).",
        0.4, "Δ₁ = (220 − 140) / N = 80 / 200 = <b>0.4 cm</b>. One person moves an average of 200 "
        "by at most the full range divided by 200.", 0.01),
    "ex2_sensitivity": (
        "🎯 Find the sensitivity Δ₁",
        "We publish the 2-D count (defaulters in region A, defaulters in region B); the neighbourhood "
        "adds/removes one client. Type the L1 sensitivity Δ₁.",
        1.0, "One client lives in exactly one region, so adding/removing them changes exactly one "
        "component by 1. The L1 norm = |Δ_A| + |Δ_B| = 1 + 0 = <b>1</b>.", 1e-6),
    "gauss_l2_sensitivity": (
        "🎯 Find the L2 sensitivity Δ₂",
        "We publish a 2-D vector (total defaulters, total high-risk clients). A single "
        "<i>high-risk defaulter</i> added/removed changes <b>both</b> components by 1, i.e. by the "
        "vector (1, 1). Type the L2 sensitivity Δ₂ (2 decimals).",
        2 ** 0.5, "The trap: L2 is the <b>root of the sum of squares</b>, not the sum. "
        "Δ₂ = √(1² + 1²) = √2 ≈ <b>1.41</b> — not 2 (that would be the L1 value).", 0.02),
    "full_sensitivity": (
        "🎯 Sensitivity of each released count",
        "Both the defaulter count and the high-risk count are plain counts, under the add/remove-one "
        "neighbourhood. Type the L1 sensitivity Δ₁ that each of them has.",
        1.0, "Adding or removing one client changes a count by at most 1, so Δ₁ = <b>1</b> for each "
        "release — and each gets Laplace noise of scale 1/ε.", 1e-6),
    "full_eps2": (
        "🎯 How much budget is left for the second release?",
        "The bank set a total budget of ε = 1.5 for everything it discloses about default status, and "
        "has already spent ε₁ = 0.5 on the first release. By composition, what is the largest ε₂ it "
        "may spend on the second release?",
        1.0, "Composition adds budgets, so ε₁ + ε₂ ≤ ε_total ⇒ ε₂ = 1.5 − 0.5 = <b>1.0</b>.", 1e-6),
    "dpsgd_sum_sensitivity": (
        "🎯 Sensitivity when we noise the SUM",
        "Batch of L clients, each gradient clipped to L2 norm C = 1, then we noise the <b>sum</b> of "
        "the clipped gradients. Adding/removing one client changes that sum by at most one clipped "
        "gradient. Type the L2 sensitivity Δ₂.",
        1.0, "One client contributes at most one clipped gradient, whose norm is ≤ C = 1. So "
        "Δ₂ = C = <b>1</b> — independent of the batch size L.", 1e-6),
    "dpsgd_mean_sensitivity": (
        "🎯 Sensitivity when we noise the MEAN",
        "Same batch of L = 10 clients, clip C = 1, but now we noise the <b>mean</b> = (1/L)·Σ of the "
        "clipped gradients before the update. Type the L2 sensitivity Δ₂ of that mean.",
        0.1, "Dividing the sum by L divides its sensitivity by L too: Δ₂ = C / L = 1 / 10 = <b>0.1</b>. "
        "Averaging shrinks each person's footprint — so the mean needs proportionally less noise for "
        "the same ε.", 1e-6),
}


def mc_quiz(key):
    _mc_render(*_MC_QUIZZES[key])


def true_false_quiz(key):
    title, statements = _TF_QUIZZES[key]
    _tf_render(title, statements)


def number_box(key):
    _number_render(*_NUMBER_QUIZZES[key])


# ===========================================================================
#  Final boss — timed true/false flash quiz with lives (ported from we3_viz)
# ===========================================================================
# Balanced 24 true / 24 false, phrased so neither answer is given away by wording.
_FLASH_POOL = [
    # --- membership inference / motivation (3T / 3F) ---
    ("Membership inference asks whether a specific record was in the training set.", True),
    ("Differential privacy is a principled defence against membership inference.", True),
    ("Differential privacy hides facts that are true of the whole population.", False),
    ("Attribute inference tries to recover a missing feature of one individual.", True),
    ("Differential privacy is only needed when the training data is already public.", False),
    ("A membership inference attacker needs the model's source code to succeed.", False),
    # --- definition / neighbourhood (4T / 4F) ---
    ("A differentially private mechanism is randomised.", True),
    ("The neighbourhood relation specifies which datasets must be indistinguishable.", True),
    ("A smaller ε gives weaker privacy.", False),
    ("A larger ε pushes the two output distributions closer together.", False),
    ("Adding or removing one person is a common neighbourhood relation.", True),
    ("The DP guarantee must hold for every possible outcome set S.", True),
    ("The DP inequality only has to hold for a single convenient dataset pair.", False),
    ("Differential privacy assumes the attacker has no side information.", False),
    # --- why noise / Laplace (5T / 5F) ---
    ("A deterministic count can reveal whether one person was added or removed.", True),
    ("Adding noise makes the output distributions of neighbours overlap.", True),
    ("The Laplace density has a sharp peak and heavy tails.", True),
    ("Sensitivity is the largest output change over any neighbouring pair.", True),
    ("For the Laplace mechanism the noise scale is Δ₁/ε.", True),
    ("A query that one person can swing more needs less noise.", False),
    ("The L1 sensitivity of a plain counting query is 0.", False),
    ("A larger noise scale gives weaker privacy.", False),
    ("Sensitivity does not depend on the neighbourhood relation.", False),
    ("The Laplace noise scale grows as ε grows.", False),
    # --- (eps,delta) / Gaussian (4T / 4F) ---
    ("δ in (ε,δ)-DP is an absolute slack added to the probability bound.", True),
    ("The Gaussian mechanism measures sensitivity in the L2 norm.", True),
    ("A smaller δ requires a larger Gaussian σ, all else equal.", True),
    ("(ε,δ)-DP with δ = 0 coincides with ε-DP.", True),
    ("The Gaussian mechanism achieves pure ε-DP with δ = 0.", False),
    ("Pure ε-DP allows one distribution to be zero where the other is positive.", False),
    ("A larger δ (all else equal) requires a larger Gaussian σ.", False),
    ("You generally want δ to be close to 1.", False),
    # --- composability (3T / 3F) ---
    ("Post-processing a DP output preserves its privacy guarantee.", True),
    ("Composition adds the ε budgets of the mechanisms you run.", True),
    ("Answering more queries about the same data spends more privacy budget.", True),
    ("Post-processing can recover the original noise-free value.", False),
    ("Two DP releases together are more private than either one alone.", False),
    ("Feeding a DP result into another model costs additional privacy budget.", False),
    # --- DP-SGD / trade-off (5T / 5F) ---
    ("DP-SGD adds noise during the gradient update step.", True),
    ("Clipping the per-example gradient bounds its sensitivity.", True),
    ("DP-SGD clips each gradient to a fixed L2 norm C.", True),
    ("Over many training steps the privacy budget accumulates by composition.", True),
    ("More noise in DP-SGD tends to reduce model accuracy.", True),
    ("Making predictions with an already-private model costs extra privacy budget.", False),
    ("The utility–privacy trade-off is unique to DP-SGD.", False),
    ("Clipping gradients removes the need to add any noise.", False),
    ("DP-SGD adds noise only to the final trained weights, never during training.", False),
    ("A privacy budget of ε = 0 with useful accuracy is generally achievable.", False),
]


def flash_quiz(n_to_pass=10, lives=3, seconds=10):
    """Timed true/false 'final boss'. Ported verbatim from we3_viz.flash_quiz —
    all logic runs in the browser, so nothing here reveals answers to the cell."""
    pool = [{"t": t, "a": bool(a)} for t, a in _FLASH_POOL]
    data = {"pool": pool, "need": int(n_to_pass), "lives0": int(lives), "secs": int(seconds)}
    uid = "flash_" + str(abs(hash(tuple(t for t, _ in _FLASH_POOL))) % 10**8)
    tmpl = r'''
<style>
#__UID__{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e6e8ee;border-radius:16px;padding:20px;max-width:640px;background:#fff;color:#1c1e2a;position:relative}
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
  const stmt=()=>$(".fq-stmt"), flash=()=>$(".fq-flash");
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
      +(won?("You cleared "+correct+" questions. You understand differential privacy."):
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
