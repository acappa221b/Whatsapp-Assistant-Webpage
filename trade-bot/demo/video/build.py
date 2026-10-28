"""Gera o projeto HyperFrames do vídeo explicativo a partir da demo (replay.py).

Todos os números do vídeo vêm do mesmo replay, então o vídeo e o terminal concordam.
Uso: python3 demo/video/build.py <pasta-do-projeto-hyperframes>
"""

import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))

import replay  # noqa: E402
from tradebot import timemachine  # noqa: E402

W, H = 1080, 1920
GREEN, RED, AMBER, INK, MUTED, BG, PANEL, BLUE = ("#2ee59d", "#ff5470", "#ffc857", "#f4f6fb",
                                                  "#8a93a6", "#0b0f17", "#141a26", "#5b8cff")


def run_demo():
    out = os.path.join(HERE, ".demo.json")
    subprocess.run([sys.executable, os.path.join(HERE, "..", "replay.py"), "--json", out],
                   check=True, stdout=subprocess.DEVNULL)
    return json.load(open(out))


def lines_by(demo, kind, sym=None):
    return [l for l in demo["lines"] if l["kind"] == kind and (sym is None or sym in l["text"])]


# ------------------------------------------------------------------ chart geometry
CH_X, CH_Y, CH_W, CH_H = 70, 0, 940, 760
LAST_SLOT = 24                      # mostra 09:30-11:35


def scale(lo, hi):
    def sx(i):
        return CH_X + CH_W * (i + 0.5) / (LAST_SLOT + 1)

    def sy(p):
        return CH_Y + CH_H * (1 - (p - lo) / (hi - lo))
    return sx, sy


def candles_svg(bars, sx, sy, upto, idp):
    out, bw = [], CH_W / (LAST_SLOT + 1) * 0.56
    prev = bars[0][2]
    for i in range(min(upto, LAST_SLOT) + 1):
        h, l, c = bars[i]
        o = prev
        col = GREEN if c >= o else RED
        x = sx(i)
        top, bot = sy(max(o, c)), sy(min(o, c))
        out.append('<g id="%s%d" class="cdl"><line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="3"/>'
                   '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/></g>' % (
                       idp, i, x, x, sy(h), sy(l), col, x - bw / 2, top, bw, max(3, bot - top), col))
        prev = c
    return "".join(out)


def sim_paths(entry, stop, target, k, n=70):
    past, _ = replay.SCENARIOS["ACME"]
    pool, _ = timemachine.build_pool(list(past.values()))
    rng = random.Random(19)
    paths = []
    for _ in range(n):
        p, pts, outcome = entry, [(k, entry)], None
        for i in range(k + 1, LAST_SLOT + 1):
            j = min(len(pool) - 1, max(1, i + rng.randint(-2, 2)))
            _, hi, lo, c = rng.choice(pool[j])
            if p * lo <= stop:
                pts.append((i, stop)); outcome = "stop"; break
            if p * hi >= target:
                pts.append((i, target)); outcome = "target"; break
            p *= c
            pts.append((i, p))
        paths.append((pts, outcome or "open"))
    return paths


# ------------------------------------------------------------------ html helpers
def page(cid, dur, body, css, js):
    return """<template>
  <style>
    #root {{ position: absolute; inset: 0; background: {bg}; color: {ink}; font-family: Inter, sans-serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .kicker {{ font-size: 34px; letter-spacing: .18em; text-transform: uppercase; color: {muted}; font-weight: 700; }}
    {css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{w}" data-height="{h}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
""".format(bg=BG, ink=INK, muted=MUTED, css=css, cid=cid, w=W, h=H, body=body, js=js)


def fade_up(sel, at, dy=40, d=0.5):
    return '    tl.fromTo("%s", {opacity: 0, y: %d}, {opacity: 1, y: 0, duration: %s, ease: "power3.out"}, %s);\n' % (sel, dy, d, at)


def br(x):
    return ("%.2f" % x).replace(".", ",")


def build(dest):
    demo = run_demo()
    bars = demo["bars"]["ACME"]
    buy = next(f for f in demo["fills"] if f["symbol"] == "ACME" and f["side"] == "buy")
    sell = next(f for f in demo["fills"] if f["symbol"] == "ACME" and f["side"] == "sell")
    order_line = lines_by(demo, "ordem", "ACME")[0]["text"]
    stop = float(order_line.split("stop ")[1].split()[0])
    target = float(order_line.split("alvo ")[1].split()[0])
    sig = lines_by(demo, "sinal", "ACME")[0]
    sig_entry = float(sig["text"].split("entrada ")[1].split()[0])
    or_high = float(sig["text"].split("máxima ")[1].split()[0])
    tm_a = lines_by(demo, "tm", "ACME")[0]["text"]
    tm_b = lines_by(demo, "tm", "BRVO")[0]["text"]
    pct = lambda txt, key: txt.split(key + " ")[1].split("%")[0]  # noqa: E731
    n_cen = tm_a.split("(")[1].split(" cen")[0]
    n_preg = tm_a.split("cenários, ")[1].split(" preg")[0]
    risk_usd = buy["qty"] * (buy["price"] - stop)
    sig_slot = 4
    hit_slot = next(i for i in range(sig_slot + 1, len(bars)) if bars[i][0] >= target)

    lo = min(min(b[1] for b in bars[:LAST_SLOT + 1]), stop) - 0.25
    hi = max(max(b[0] for b in bars[:LAST_SLOT + 1]), target) + 0.25
    sx, sy = scale(lo, hi)
    or_lo = min(b[1] for b in bars[:3])
    or_hi = max(b[0] for b in bars[:3])

    os.makedirs(os.path.join(dest, "compositions"), exist_ok=True)
    scenes = []

    # ---------------- 1. intro (0-4.5)
    body = """    <div id="i-wrap" style="position:absolute;left:90px;right:90px;top:640px">
      <div id="i-k" class="kicker">trade-bot · demonstração</div>
      <h1 id="i-t" style="font-size:118px;line-height:1.02;font-weight:900;margin-top:36px;letter-spacing:-.03em">Como o robô decide<br>uma operação</h1>
      <div id="i-s" style="margin-top:48px;font-size:40px;color:%s">Pregão simulado · dados sintéticos · modo SIM</div>
    </div>""" % MUTED
    js = fade_up("#i-k", 0.2) + fade_up("#i-s", 0.8)   # título já visível no frame 0 (miniatura)
    scenes.append(("intro", 4.5, page("intro", 4.5, body, "", js)))

    # ---------------- 2. chart (4.5-24): faixa, rompimento, stop/alvo, Máquina do Tempo
    paths = sim_paths(sig_entry, stop, target, sig_slot)
    path_svg = []
    for n, (pts, oc) in enumerate(paths):
        col = GREEN if oc == "target" else RED if oc == "stop" else MUTED
        d = "M" + " L".join("%.1f %.1f" % (sx(i), sy(p)) for i, p in pts)
        path_svg.append('<path id="sp%d" class="sp" d="%s" fill="none" stroke="%s" stroke-width="3" stroke-opacity=".55"/>' % (n, d, col))
    svg = """      <svg id="c-svg" width="1080" height="800" viewBox="0 0 1080 800" style="position:absolute;left:0;top:560px" data-layout-allow-overflow>
        <rect id="c-or" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity=".14" stroke="%s" stroke-dasharray="10 8" stroke-width="2"/>
        <g id="c-candles">%s</g>
        <line id="c-stop" x1="%.1f" x2="1010" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="4" stroke-dasharray="14 10"/>
        <line id="c-tgt" x1="%.1f" x2="1010" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="4" stroke-dasharray="14 10"/>
        <g id="c-paths">%s</g>
        <circle id="c-dot" cx="%.1f" cy="%.1f" r="16" fill="none" stroke="%s" stroke-width="5"/>
      </svg>""" % (CH_X, sy(or_hi), sx(LAST_SLOT) - CH_X + 20, sy(or_lo) - sy(or_hi), BLUE, BLUE,
                  candles_svg(bars, sx, sy, sig_slot, "cc"),
                  sx(sig_slot), sy(stop), sy(stop), RED, sx(sig_slot), sy(target), sy(target), GREEN,
                  "".join(path_svg), sx(sig_slot), sy(bars[sig_slot][2]), AMBER)
    body = """    <div id="c-head" style="position:absolute;left:90px;right:90px;top:150px">
      <div class="kicker">ACME · 27/10 · candles de 5 min</div>
      <div id="c-cap1" class="cap" style="font-size:66px;font-weight:800;margin-top:28px">1. Faixa dos primeiros 15 min</div>
      <div id="c-cap2" class="cap" style="font-size:66px;font-weight:800;margin-top:28px">2. Rompeu a máxima: sinal</div>
      <div id="c-cap3" class="cap" style="font-size:66px;font-weight:800;margin-top:28px">3. Stop e alvo antes de entrar</div>
      <div id="c-cap4" class="cap" style="font-size:66px;font-weight:800;margin-top:28px">4. Máquina do Tempo</div>
    </div>
{svg}
    <div id="c-or-lab" class="mono lab" style="position:absolute;left:90px;top:{orlab}px;font-size:30px;color:{blue}">faixa {orlo} – {orhi}</div>
    <div id="c-sig-lab" class="mono lab" style="position:absolute;left:{sigx}px;top:{sigy}px;font-size:32px;color:{amber}">09:55 entrada {entry}</div>
    <div id="c-stop-lab" class="mono lab" style="position:absolute;right:70px;top:{stopy}px;font-size:32px;color:{red}">stop {stop}</div>
    <div id="c-tgt-lab" class="mono lab" style="position:absolute;right:70px;top:{tgty}px;font-size:32px;color:{green}">alvo {target}</div>
    <div id="c-tm" style="position:absolute;left:90px;right:90px;top:1360px">
      <div id="c-tm1" style="font-size:44px;color:{muted}">{ncen} futuros simulados com {npreg} pregões de histórico</div>
      <div style="display:flex;gap:28px;margin-top:34px">
        <div id="c-tm2" class="box" style="border-color:{green}"><div class="big" style="color:{green}">{pa}%</div><div class="sm">bateram o alvo</div></div>
        <div id="c-tm3" class="box" style="border-color:{red}"><div class="big" style="color:{red}">{ps}%</div><div class="sm">bateram o stop</div></div>
      </div>
      <div id="c-tm4" style="margin-top:36px;font-size:64px;font-weight:900;color:{green}">✔ APROVADO</div>
    </div>""".format(
        svg=svg, orlab=int(560 + sy(or_lo) + 14), blue=BLUE, orlo=br(or_lo), orhi=br(or_hi),
        sigx=int(sx(sig_slot) + 26), sigy=int(560 + sy(bars[sig_slot][2]) - 70), amber=AMBER, entry=br(sig_entry),
        stopy=int(560 + sy(stop) + 10), tgty=int(560 + sy(target) - 50), red=RED, green=GREEN,
        stop=br(stop), target=br(target), muted=MUTED, ncen=n_cen.replace("000", ".000"), npreg=n_preg,
        pa=pct(tm_a, "alvo"), ps=pct(tm_a, "stop"))
    css = """.box { flex: 1; border: 3px solid; border-radius: 28px; padding: 26px 32px; background: %s; }
    .big { font-size: 96px; font-weight: 900; line-height: 1; }
    .sm { font-size: 34px; color: %s; margin-top: 10px; }
    .cap, .lab, #c-tm1, #c-tm2, #c-tm3, #c-tm4, #c-stop, #c-tgt, #c-dot, .sp, .cdl { opacity: 0; }
    .cap { position: absolute; left: 0; right: 0; top: 70px; }""" % (PANEL, MUTED)
    js = ""
    js += '    tl.fromTo("#c-or", {opacity: 0}, {opacity: 1, duration: .6}, .8);\n'
    js += fade_up("#c-cap1", 0.3)
    for i in range(3):
        js += '    tl.fromTo("#cc%d", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: .35, ease: "back.out(2)"}, %.2f);\n' % (i, 0.6 + 0.35 * i)
    js += fade_up("#c-or-lab", 1.8, 20)
    js += '    tl.to("#c-cap1", {opacity: 0, duration: .3}, 3.6);\n' + fade_up("#c-cap2", 3.8)
    js += '    tl.fromTo("#cc3", {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: .35}, 4.0);\n'
    js += '    tl.fromTo("#cc4", {opacity: 0, scale: .4, transformOrigin: "50% 100%"}, {opacity: 1, scale: 1, duration: .5, ease: "back.out(3)"}, 4.6);\n'
    js += '    tl.fromTo("#c-dot", {opacity: 0, scale: 2.5, transformOrigin: "50% 50%"}, {opacity: 1, scale: 1, duration: .5, ease: "power3.out"}, 5.0);\n'
    js += fade_up("#c-sig-lab", 5.2, 20)
    js += '    tl.to("#c-cap2", {opacity: 0, duration: .3}, 7.2);\n' + fade_up("#c-cap3", 7.4)
    js += '    tl.fromTo("#c-stop", {opacity: 0, scaleX: 0, transformOrigin: "0% 50%"}, {opacity: 1, scaleX: 1, duration: .6, ease: "power2.out"}, 7.7);\n'
    js += fade_up("#c-stop-lab", 8.0, 20)
    js += '    tl.fromTo("#c-tgt", {opacity: 0, scaleX: 0, transformOrigin: "0% 50%"}, {opacity: 1, scaleX: 1, duration: .6, ease: "power2.out"}, 8.4);\n'
    js += fade_up("#c-tgt-lab", 8.7, 20)
    js += '    tl.to("#c-cap3", {opacity: 0, duration: .3}, 10.6);\n' + fade_up("#c-cap4", 10.8)
    js += '    tl.to("#c-sig-lab", {opacity: 0, duration: .3}, 10.8);\n'
    js += fade_up("#c-tm1", 11.0, 20)
    js += '    tl.fromTo(".sp", {opacity: 0}, {opacity: 1, duration: .25, stagger: 0.045}, 11.3);\n'
    js += fade_up("#c-tm2", 14.6) + fade_up("#c-tm3", 14.9)
    js += '    tl.fromTo("#c-tm4", {opacity: 0, scale: .6, transformOrigin: "0% 50%"}, {opacity: 1, scale: 1, duration: .5, ease: "back.out(2.5)"}, 16.2);\n'
    scenes.append(("chart", 19.5, page("chart", 19.5, body, css, js)))

    # ---------------- 3. ordem + risco (24-31)
    checks = ["Horário: entre 09:45 e 15:30", "Perda no stop ≤ US$ 50", "Perda do dia abaixo do limite",
              "Máx. 3 operações / 2 posições", "Retorno ≥ risco (1:1)", "Kill switch desligado"]
    rows = "".join('<div id="o-c%d" class="chk"><span style="color:%s">✔</span> %s</div>' % (i, GREEN, t) for i, t in enumerate(checks))
    body = """    <div style="position:absolute;left:90px;right:90px;top:220px">
      <div id="o-k" class="kicker">5. Tamanho e regras de risco</div>
      <div id="o-ticket" style="margin-top:40px;background:{panel};border-radius:36px;padding:52px;border:3px solid #263049">
        <div style="font-size:40px;color:{muted}">ordem bracket enviada à corretora</div>
        <div style="font-size:92px;font-weight:900;margin-top:16px">COMPRA {qty} ACME</div>
        <div class="mono" style="font-size:44px;margin-top:26px;line-height:1.6">
          entrada <b>{entry}</b><br><span style="color:{red}">stop {stop}</span> · <span style="color:{green}">alvo {target}</span><br>
          risco máximo <b style="color:{amber}">US$ {risk}</b>
        </div>
      </div>
      <div style="margin-top:56px">{rows}</div>
      <div id="o-note" data-hold style="margin-top:44px;font-size:38px;color:{muted}">Stop e alvo ficam na corretora: valem mesmo se o robô cair.</div>
    </div>""".format(panel=PANEL, muted=MUTED, qty=buy["qty"], entry=br(buy["price"]), red=RED, green=GREEN,
                     stop=br(stop), target=br(target), amber=AMBER, risk=br(risk_usd), rows=rows)
    css = ".chk { font-size: 46px; margin: 18px 0; font-weight: 600; }"
    js = fade_up("#o-k", 0.2) + '    tl.fromTo("#o-ticket", {opacity: 0, scale: .9}, {opacity: 1, scale: 1, duration: .6, ease: "back.out(1.8)"}, 0.5);\n'
    for i in range(len(checks)):
        js += fade_up("#o-c%d" % i, 1.6 + 0.4 * i, 20, 0.35)
    js += fade_up("#o-note", 3.6, 20)
    scenes.append(("ordem", 8, page("ordem", 8, body, css, js)))

    # ---------------- 4. veto (31-37)
    body = """    <div style="position:absolute;left:90px;right:90px;top:520px">
      <div id="v-k" class="kicker">Mesmo pregão, 10:10</div>
      <div id="v-t" style="font-size:96px;font-weight:900;margin-top:30px">BRVO também rompeu…</div>
      <div style="display:flex;gap:28px;margin-top:56px">
        <div id="v-a" class="box" style="border-color:{green}"><div class="big" style="color:{green}">{pa}%</div><div class="sm">alvo</div></div>
        <div id="v-b" class="box" style="border-color:{red}"><div class="big" style="color:{red}">{ps}%</div><div class="sm">stop</div></div>
      </div>
      <div id="v-x" style="margin-top:56px;font-size:110px;font-weight:900;color:{red}">✖ VETADO</div>
      <div id="v-n" style="margin-top:30px;font-size:52px;color:{muted}">Na dúvida, o robô não opera.</div>
    </div>""".format(green=GREEN, red=RED, muted=MUTED, pa=pct(tm_b, "alvo"), ps=pct(tm_b, "stop"))
    css = """.box { flex: 1; border: 3px solid; border-radius: 28px; padding: 26px 32px; background: %s; }
    .big { font-size: 110px; font-weight: 900; line-height: 1; }
    .sm { font-size: 36px; color: %s; margin-top: 10px; }""" % (PANEL, MUTED)
    js = fade_up("#v-k", 0.2) + fade_up("#v-t", 0.4) + fade_up("#v-a", 1.3) + fade_up("#v-b", 1.6)
    js += '    tl.fromTo("#v-x", {opacity: 0, scale: 1.6, transformOrigin: "0% 50%"}, {opacity: 1, scale: 1, duration: .45, ease: "power4.out"}, 2.6);\n'
    js += fade_up("#v-n", 3.4)
    scenes.append(("veto", 6, page("veto", 6, body, css, js)))

    # ---------------- 5. resultado (37-44)
    sx2, sy2 = sx, sy
    svg = """      <svg width="1080" height="800" viewBox="0 0 1080 800" style="position:absolute;left:0;top:560px">
        <line x1="%.1f" x2="1010" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="4" stroke-dasharray="14 10"/>
        <line x1="%.1f" x2="1010" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="4" stroke-dasharray="14 10"/>
        <g>%s</g>
        <circle id="r-hit" cx="%.1f" cy="%.1f" r="20" fill="none" stroke="%s" stroke-width="6"/>
      </svg>""" % (sx2(sig_slot), sy2(stop), sy2(stop), RED, sx2(sig_slot), sy2(target), sy2(target), GREEN,
                  candles_svg(bars, sx2, sy2, hit_slot, "rc"), sx2(hit_slot), sy2(target), GREEN)
    body = """    <div style="position:absolute;left:90px;right:90px;top:200px">
      <div id="r-k" class="kicker">6. Resultado</div>
      <div id="r-t" style="font-size:72px;font-weight:800;margin-top:26px">11:15 · bateu o alvo</div>
      <div id="r-p" style="font-size:150px;font-weight:900;color:{green};margin-top:10px">+US$ {pnl}</div>
    </div>
{svg}
    <div id="r-n" style="position:absolute;left:90px;right:90px;top:1460px;font-size:44px;color:{muted};line-height:1.4">
      15:55: o robô zera tudo.<br>Ninguém dorme posicionado.
    </div>""".format(green=GREEN, pnl=br(sell["pnl"]), svg=svg, muted=MUTED)
    js = fade_up("#r-k", 0.2)
    js += '    tl.fromTo(".cdl", {opacity: 0}, {opacity: 1, duration: .2, stagger: 0.08}, 0.4);\n'
    t_hit = 0.4 + 0.08 * hit_slot + 0.3
    js += '    tl.fromTo("#r-hit", {opacity: 0, scale: 2.5, transformOrigin: "50%% 50%%"}, {opacity: 1, scale: 1, duration: .5}, %.2f);\n' % t_hit
    js += fade_up("#r-t", t_hit + 0.2) + '    tl.fromTo("#r-p", {opacity: 0, scale: .7, transformOrigin: "0%% 50%%"}, {opacity: 1, scale: 1, duration: .55, ease: "back.out(2.5)"}, %.2f);\n' % (t_hit + 0.6)
    js += fade_up("#r-n", t_hit + 1.6)
    scenes.append(("resultado", 7, page("resultado", 7, body, ".cdl, #r-hit { opacity: 0; }", js)))

    # ---------------- 6. fim (44-50)
    body = """    <div style="position:absolute;left:90px;right:90px;top:600px">
      <div id="f-1" style="font-size:96px;font-weight:900;line-height:1.05">Primeiro no<br>dinheiro fictício.</div>
      <div id="f-2" style="font-size:52px;color:{muted};margin-top:44px;line-height:1.35">Dinheiro real só depois de<br>20 pregões em paper.</div>
      <div id="f-3" class="mono" style="font-size:38px;color:{amber};margin-top:70px">python3 -m tradebot run</div>
    </div>
    <div id="f-c" style="position:absolute;left:90px;right:90px;bottom:120px;font-size:30px;color:{muted}">Dados sintéticos · não é recomendação de investimento · Music: Sascha Ende, ende.app (CC BY 4.0)</div>""".format(muted=MUTED, amber=AMBER)
    js = fade_up("#f-1", 0.2, 60, 0.7) + fade_up("#f-2", 1.0) + fade_up("#f-3", 1.8) + fade_up("#f-c", 1.2, 10)
    scenes.append(("fim", 7, page("fim", 7, body, "", js)))

    # ---------------- root
    t, hosts = 0.0, []
    for i, (cid, dur, html) in enumerate(scenes):
        open(os.path.join(dest, "compositions", cid + ".html"), "w").write(html)
        hosts.append('      <div id="%s" data-composition-id="%s" data-composition-src="compositions/%s.html" data-start="%.1f" '
                     'data-duration="%.1f" data-track-index="%d" data-track-kind="graphics" data-width="%d" data-height="%d"></div>'
                     % (cid, cid, cid, t, dur, 1, W, H))
        t += dur
    total = t
    index = """<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {bg}; }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(1200px 900px at 80% 10%, #16213a 0%, {bg} 60%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.1f}" data-width="1080" data-height="1920">
      <div id="bg"></div>
{hosts}
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{total:.1f}" data-volume="0.35" data-fade-in="0.5" data-fade-out="2" data-track-index="2"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""".format(bg=BG, total=total, hosts="\n".join(hosts))
    open(os.path.join(dest, "index.html"), "w").write(index)
    print("ok: %d cenas, %.1f s" % (len(scenes), total))


if __name__ == "__main__":
    build(sys.argv[1])
