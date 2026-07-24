"""Hidden helper for the abliteration primer (00_abliteration_primer.ipynb).

Holds the interactive quizzes (with their answer keys), the live demo, the
abliteration-lab slider, the picture, the coding-task checker, and the risk
self-assessment, so the notebook cells stay clean and the answers aren't sitting
in the notebook for participants to read off.

Students: you don't need to read this file.
"""
import json as _json

import numpy as np
from IPython.display import HTML as _HTML, display as _display

# ===========================================================================
#  Shared toy model (used by the demo and the coding task)
# ===========================================================================
_W = np.array([2.0, 1.0, -0.5])                       # the model's weights
_HARMFUL = np.array([[1.0, 0.5, 0.5],
                     [1.0, 0.4, 0.6],
                     [1.0, 0.6, 0.4]])                # requests it SHOULD refuse
_HARMLESS = np.array([[0.0, 0.5, 0.5],
                      [0.0, 0.6, 0.4],
                      [0.0, 0.4, 0.6]])               # ordinary requests
_R = _HARMFUL.mean(0) - _HARMLESS.mean(0)             # difference-in-means
_R = _R / np.linalg.norm(_R)                          # the refusal lever (= feature 0)
_THR = 1.0


def _verdict(w, x):
    return "REFUSES 🚫" if float(np.asarray(w) @ np.asarray(x)) >= _THR else "complies ✅"


def toy_model():
    """Return (w, r) for the coding task. r is found from data by difference-in-means."""
    print("The model's refusal lever, found from the harmful vs harmless examples:", np.round(_R, 2))
    print("The model refuses a request when   w · request >= %.1f" % _THR)
    return _W.copy(), _R.copy()


def demo():
    """Show the one-line abliteration flip a harmful request while sparing an ordinary one."""
    harmful, ordinary = np.array([1.0, 0.2, 0.1]), np.array([0.0, 1.0, 1.0])
    sc = lambda w, x: float(w @ x)
    print("The model reads a request as 3 numbers, and its weights score it (score >= 1 -> refuse).")
    print()
    print("  model weights   w =", np.round(_W, 2))
    print("  refusal lever   r =", np.round(_R, 2), "  (the 'refuse?' direction, found from data)")
    print()
    print("  harmful request  x =", np.round(harmful, 2))
    print("     score = w · x = %.2f   ->  %s" % (sc(_W, harmful), _verdict(_W, harmful)))
    print("  ordinary request x =", np.round(ordinary, 2))
    print("     score = w · x = %.2f   ->  %s" % (sc(_W, ordinary), _verdict(_W, ordinary)))
    print()
    w_abl = _W - (_W @ _R) * _R                        # the whole attack, one line
    print("Abliteration removes the lever from the weights:")
    print("  w_new = w - (w · r) * r =", np.round(w_abl, 2), "  (the 'refuse' part is now zero)")
    print()
    print("The SAME two requests, scored with the new weights:")
    print("     harmful : score = w_new · x = %.2f   ->  %s   (guardrail gone)"
          % (sc(w_abl, harmful), _verdict(w_abl, harmful)))
    print("     ordinary: score = w_new · x = %.2f   ->  %s   (unchanged)"
          % (sc(w_abl, ordinary), _verdict(w_abl, ordinary)))


def check_guardrail(fn):
    """Run the participant's remove_guardrail(w, r) and tell them if it worked."""
    harmful, ordinary = np.array([1.0, 0.15, 0.1]), np.array([0.0, 1.0, 1.0])
    try:
        w_new = np.asarray(fn(_W.copy(), _R.copy()), dtype=float)
    except Exception as e:
        print("⚠️ Your function raised an error:", repr(e))
        return
    correct = _W - (_W @ _R) * _R
    print("harmful request BEFORE:", _verdict(_W, harmful))
    print("harmful request AFTER :", _verdict(w_new, harmful))
    if np.allclose(w_new, correct, atol=1e-6):
        print("\n✅ Exactly right. The guardrail is gone and ordinary requests behave as before.")
    elif not _verdict(w_new, harmful).startswith("REFUSES"):
        print("\n🟡 The harmful request gets through, but that's not the clean 'remove the lever' move.")
        print("   Re-read the hint: subtract (w · r) · r, nothing more.")
    else:
        print("\n⛔ Still refusing. Your line hasn't removed the lever yet. Try again.")


# ===========================================================================
#  Theme-aware widget styling + renderers
# ===========================================================================
_CSS = """<style>
.wig{font-family:system-ui,Segoe UI,Roboto,sans-serif;border:1px solid #e4e6ee;border-radius:14px;padding:16px 18px;max-width:760px;margin:10px 0;background:#fff;color:#1f2430}
.wig h4{margin:0 0 8px;font-size:15px}
.wig .q{font-size:14px;margin-bottom:6px;line-height:1.5}
.wig .opt{border:1px solid #e2e5ef;border-radius:10px;padding:9px 12px;margin:6px 0;cursor:pointer;font-size:13.5px;line-height:1.45;transition:.12s}
.wig .opt:hover{border-color:#7a5cd0;background:#f6f3ff}
.wig .opt.sel{border-color:#7a5cd0;background:#efeaff}
.wig .opt.ok{border-color:#3fa564;background:#e7f7ec}
.wig .opt.no{border-color:#d9736e;background:#fdeceb}
.wig .btn{border:none;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:700;color:#fff;background:linear-gradient(135deg,#6f7bf0,#7a5cd0);cursor:pointer;margin-top:8px}
.wig .fb{font-size:13px;margin-top:10px;min-height:18px;line-height:1.55}
.wig select{width:100%;padding:8px 10px;border-radius:8px;border:1px solid #cfd3e2;font-size:13px;margin-top:4px;background:#fff;color:#1f2430}
.wig .bar{height:26px;border-radius:6px;background:#e9ecf5;position:relative;overflow:hidden;margin:4px 0}
.wig .fill{height:100%;width:0%}
.wig .thr{position:absolute;top:-4px;bottom:-4px;width:2px;background:#c0554e}
.wig .badge{font-weight:700;font-size:13px}
.wig code{background:#f0eefb;border-radius:5px;padding:1px 5px}
@media (prefers-color-scheme: dark){
 .wig{background:#1e2028;color:#e7e9f0;border-color:#3a3d4a}
 .wig .opt{border-color:#3a3d4a;background:#262933}
 .wig .opt:hover{background:#2f2a45;border-color:#9a86e6}
 .wig .opt.sel{background:#332a55;border-color:#9a86e6}
 .wig .opt.ok{background:#1f3a2a;border-color:#3fa564}
 .wig .opt.no{background:#3a2422;border-color:#d9736e}
 .wig select{background:#262933;color:#e7e9f0;border-color:#3a3d4a}
 .wig .bar{background:#2b2e39}
 .wig code{background:#2f2a45}
}
</style>"""

_MC = """<div class="wig" id="__UID__"><div class="q">__Q__</div>__OPTS__<button class="btn">Check</button><div class="fb"></div></div>
<script>(function(){var D=__DATA__,root=document.getElementById("__UID__"),opts=root.querySelectorAll(".opt"),sel=null;
opts.forEach(function(o){o.onclick=function(){sel=+o.dataset.i;opts.forEach(function(x){x.classList.remove("sel","ok","no");});o.classList.add("sel");root.querySelector(".fb").innerHTML="";};});
root.querySelector(".btn").onclick=function(){if(sel===null){root.querySelector(".fb").innerHTML="Pick an option first.";return;}
opts.forEach(function(o){var i=+o.dataset.i;o.classList.remove("sel");if(i===D.a)o.classList.add("ok");else if(i===sel)o.classList.add("no");});
root.querySelector(".fb").innerHTML=(sel===D.a?"✅ Correct. ":"❌ Not quite. ")+D.e;};})();</script>"""

_TF = """<div class="wig" id="__UID__"><h4>__T__</h4><div class="q">Click every statement that is <b>TRUE</b>, then check.</div>__OPTS__<button class="btn">Check</button><div class="fb"></div></div>
<script>(function(){var D=__DATA__,root=document.getElementById("__UID__"),opts=root.querySelectorAll(".opt");
opts.forEach(function(o){o.onclick=function(){o.classList.remove("ok","no");o.classList.toggle("sel");};});
root.querySelector(".btn").onclick=function(){var right=0;opts.forEach(function(o){var i=+o.dataset.i,picked=o.classList.contains("sel");o.classList.remove("ok","no");
if(picked===D[i].ok)right++;if(D[i].ok)o.classList.add("ok");else if(picked)o.classList.add("no");});
root.querySelector(".fb").innerHTML=right+" / "+D.length+" correct. Green = actually true.";};})();</script>"""

_LAB = """<div class="wig" id="lab_abl"><h4>🔧 Abliteration lab</h4>
<div class="q">Drag to remove more of the model's <b>refusal lever</b>. Watch the <b>weights</b> change, and a <b>harmful</b> request flip while an <b>ordinary</b> one stays put.</div>
<label style="font-size:13px">Refusal lever removed: <b><span class="pct">0</span>%</b></label>
<input type="range" min="0" max="100" value="0" class="sl" style="width:100%">
<div style="font-family:ui-monospace,Menlo,monospace;font-size:12.5px;margin-top:10px;line-height:1.8">
refusal lever &nbsp;&nbsp;r = <span class="rv"></span><br>
model weights &nbsp;w = <span class="wv"></span> &nbsp;<span style="opacity:.7">(the 'refuse' part shrinks as you drag)</span></div>
<div style="margin-top:12px;font-size:13px">Harmful request &nbsp;x = <code>[1, 0.2, 0.1]</code> &nbsp; <span class="hb badge"></span></div>
<div class="bar"><div class="fill hf" style="background:linear-gradient(90deg,#6f7bf0,#7a5cd0)"></div><div class="thr hthr"></div></div>
<div style="margin-top:8px;font-size:13px">Ordinary request &nbsp;x = <code>[0, 1, 1]</code> &nbsp; <span class="ob badge"></span></div>
<div class="bar"><div class="fill of" style="background:#8a93a8"></div><div class="thr othr"></div></div>
<div class="fb"></div></div>
<script>(function(){var root=document.getElementById("lab_abl"),sl=root.querySelector(".sl");
var W=[2,1,-0.5],R=[1,0,0],XH=[1,0.2,0.1],XO=[0,1,1],THR=1.0,SCALE=2.2;
function dot(a,b){var s=0;for(var i=0;i<a.length;i++){s+=a[i]*b[i];}return s;}
function vec(a){return "["+a.map(function(v){return v.toFixed(2);}).join(", ")+"]";}
function upd(){var t=+sl.value/100,wr=dot(W,R);
var wt=[W[0]-t*wr*R[0],W[1]-t*wr*R[1],W[2]-t*wr*R[2]];
var h=dot(wt,XH),o=dot(wt,XO);
root.querySelector(".pct").textContent=Math.round(t*100);
root.querySelector(".rv").textContent=vec(R);
root.querySelector(".wv").textContent=vec(wt);
root.querySelector(".hf").style.width=Math.max(0,Math.min(100,h/SCALE*100))+"%";
root.querySelector(".of").style.width=Math.max(0,Math.min(100,o/SCALE*100))+"%";
root.querySelector(".hthr").style.left=(THR/SCALE*100)+"%";root.querySelector(".othr").style.left=(THR/SCALE*100)+"%";
root.querySelector(".hb").innerHTML="score w·x = "+h.toFixed(2)+(h>=THR?" -> REFUSES 🚫":" -> complies ✅");
root.querySelector(".ob").innerHTML="score w·x = "+o.toFixed(2)+(o>=THR?" -> REFUSES 🚫":" -> complies ✅");
root.querySelector(".fb").innerHTML=h>=THR?"The guardrail still holds. Keep removing.":"💥 Guardrail gone: the harmful request gets through, while the ordinary request never budged.";}
sl.oninput=upd;upd();})();</script>"""

_RISK = """<div class="wig" id="risk_sc"><h4>Where does your team stand?</h4>
<div class="q">Answer two quick questions about one place you use AI, then get your read instantly.</div>
<label style="font-size:13px;display:block;margin-top:8px">1 &middot; How do you run the model?</label>
<select class="dep"><option value="">(pick one)</option>
<option value="api">We call a vendor's API (we never hold the model files)</option>
<option value="self">We self-host it, open-weight (the files are on our systems)</option>
<option value="unsure">Not sure</option></select>
<label style="font-size:13px;display:block;margin-top:12px">2 &middot; Is there a safety control OUTSIDE the model? (input/output filter, monitoring, human sign-off)</label>
<select class="ctl"><option value="">(pick one)</option>
<option value="yes">Yes</option><option value="no">No</option><option value="unsure">Not sure</option></select>
<div><button class="btn">See where I stand</button></div>
<div class="res" style="display:none;margin-top:12px;padding:12px 14px;border-radius:10px;color:#20242e"></div></div>
<script>(function(){var root=document.getElementById("risk_sc");
root.querySelector(".btn").onclick=function(){
var dep=root.querySelector(".dep").value,ctl=root.querySelector(".ctl").value,res=root.querySelector(".res");
function show(bg,bd,html){res.style.display="block";res.style.background=bg;res.style.border="1px solid "+bd;res.innerHTML=html;}
if(!dep){show("#fff5e6","#e0a94e","Pick how you run the model first.");return;}
if(dep==="api"){show("#e7f7ec","#3fa564","<b>Low exposure to abliteration.</b> You never hold the weights, so no one on your side can strip the guardrail. The provider owns that control. Still worth doing: confirm it in the contract, and make sure there's no open-weight copy floating around.");return;}
if(dep==="unsure"){show("#fff5e6","#e0a94e","<b>Find this out first.</b> Ask whether the model is called through a vendor API (weights not yours) or self-hosted / open-weight (weights on your systems). That one fact decides your exposure.");return;}
if(ctl==="yes"){show("#fff5e6","#e0a94e","<b>Exposed, but you have a backstop.</b> The model's own refusal can be removed, but your outside control would still catch it. Keep that control monitored, and actually test it now and then.");return;}
if(ctl==="no"){show("#fdeceb","#d9736e","<b>Highest risk.</b> The safety is removable <i>and</i> there's no outside net. This is exactly the gap to raise: add an external control (filter, monitoring, or human sign-off) and lock down who can read the model files.");return;}
show("#fdeceb","#d9736e","<b>Probably a gap.</b> If you're not sure there's an outside control, assume there isn't, and go find out. If there really isn't one, that's your priority.");
};})();</script>"""


def _mc(question, options, answer, explain=""):
    uid = "mc" + str(abs(hash((question, tuple(options)))) % 10**8)
    opts = "".join('<div class="opt" data-i="%d">%s</div>' % (i, o) for i, o in enumerate(options))
    _display(_HTML(_CSS + _MC.replace("__UID__", uid).replace("__Q__", question)
                   .replace("__OPTS__", opts).replace("__DATA__", _json.dumps({"a": answer, "e": explain}))))


def _tf(title, statements):
    uid = "tf" + str(abs(hash((title, tuple(t for t, _ in statements)))) % 10**8)
    opts = "".join('<div class="opt" data-i="%d">%s</div>' % (i, t) for i, (t, _) in enumerate(statements))
    data = _json.dumps([{"ok": bool(v)} for _, v in statements])
    _display(_HTML(_CSS + _TF.replace("__UID__", uid).replace("__T__", title)
                   .replace("__OPTS__", opts).replace("__DATA__", data)))


def abliteration_lab():
    """Interactive slider: remove the refusal lever and watch the model flip."""
    _display(_HTML(_CSS + _LAB))


def risk_self_check():
    """Interactive self-assessment: pick how you run AI + whether you have an outside control."""
    _display(_HTML(_CSS + _RISK))


def picture():
    """The 2-D 'remove the refusal component' vector picture."""
    import matplotlib.pyplot as plt
    r = np.array([1.0, 0.0])
    w = np.array([2.0, 1.0])
    w_abl = w - np.dot(w, r) * r
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.axhline(0, color="#bbb", lw=1); ax.axvline(0, color="#bbb", lw=1)
    ax.plot([-0.3, 2.6], [0, 0], "--", color="#c0554e", lw=1.6)
    ax.annotate("the 'refusal' lever  r", (2.0, 0.12), color="#c0554e", fontsize=10)
    ax.annotate("", xy=w, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#3a56d4", lw=2.4))
    ax.annotate("model  w = (2, 1)\n(refuses when needed)", w + np.array([0.03, 0.12]),
                color="#3a56d4", fontsize=10)
    ax.annotate("", xy=w_abl, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#2e9e5b", lw=2.4))
    ax.annotate("after abliteration  w_new = (0, 1)\n(can't refuse)", w_abl + np.array([-0.05, 0.12]),
                color="#2e9e5b", fontsize=10)
    ax.annotate("", xy=(w[0], 0), xytext=w, arrowprops=dict(arrowstyle="-", color="#c0554e", lw=1.4, ls=":"))
    ax.annotate("removed 'refusal' part", (w[0] * 0.5, -0.28), color="#c0554e", fontsize=9, ha="center")
    ax.set_xlim(-0.4, 2.8); ax.set_ylim(-0.5, 1.6); ax.set_aspect("equal")
    ax.set_title("Abliteration = delete the 'refusal' part, keep everything else", fontsize=11)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ["top", "right", "left", "bottom"]:
        ax.spines[s].set_visible(False)
    plt.tight_layout(); plt.show()


# ===========================================================================
#  Quizzes  (question + hidden answer key live HERE, not in the notebook)
# ===========================================================================
def quiz_jailbreak():
    _mc("You paste a clever backstory to get a chatbot to answer a banned question, and the "
        "model's files are never touched. Is that abliteration?",
        ["No. That's jailbreaking: fooling the model from the outside with words. "
         "Abliteration edits the model's files.",
         "Yes, any way of getting a banned answer counts as abliteration.",
         "Yes, as long as the trick works on the first try.",
         "No, that's quantization."],
        answer=0,
        explain="Jailbreaking attacks the <b>input</b> and works even on a hosted API. "
                "Abliteration changes the <b>weights</b> and needs the model's files.")


def quiz_true_about_abliteration():
    _tf("What's actually true about abliteration?",
        [("It removes the model's ability to refuse harmful requests.", True),
         ("It needs access to the model's files (its weights).", True),
         ("It also destroys the model's usefulness on everyday tasks.", False),
         ("It works on a closed chatbot you only reach through a web API.", False),
         ("An abliterated model still looks normal on ordinary questions.", True)])


def quiz_who_exposed():
    _mc("Your team uses a large AI model <b>only</b> through a vendor's web API, and you never "
        "download it. Are you exposed to someone abliterating that model?",
        ["No. You never hold the weights, so there's nothing on your side to abliterate. "
         "The provider controls it.",
         "Yes, any AI model can be abliterated by whoever uses it.",
         "Yes, abliteration happens automatically through the API.",
         "Only if you send it harmful prompts."],
        answer=0,
        explain="Abliteration needs the weight files. Exposure comes from running "
                "<b>open-weight / self-hosted</b> models, not from calling a closed API.")


def quiz_capstone():
    _tf("Everything at once: which of these are TRUE?",
        [("Abliteration removes a model's refusal by editing its weights.", True),
         ("A closed, hosted API can be abliterated by the customer using it.", False),
         ("An abliterated model usually still performs well on ordinary tasks.", True),
         ("Jailbreaking (clever prompts) and abliteration are the same thing.", False),
         ("For open-weight models, built-in refusal is a durable security control.", False),
         ("Real safety controls should live OUTSIDE the model (filters, monitoring, human review).", True),
         ("Abliteration needs a supercomputer and a huge dataset.", False)])
