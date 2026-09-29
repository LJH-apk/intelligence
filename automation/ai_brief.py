#!/usr/bin/env python3
import html
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

import requests

TZ = ZoneInfo("Asia/Shanghai")
NOW = datetime.now(timezone.utc)
SINCE = NOW - timedelta(hours=30)

QUERIES = [
    ("OPENAI", "OpenAI model API ChatGPT Codex reset deprecation site:openai.com OR site:help.openai.com"),
    ("ANTHROPIC", "Anthropic Claude model API release site:anthropic.com"),
    ("GOOGLE", "Google DeepMind Gemini model API release site:deepmind.google OR site:blog.google"),
    ("XAI", "xAI Grok model API release site:x.ai"),
    ("META", "Meta Llama AI model release site:ai.meta.com"),
    ("QWEN", "Qwen model release site:qwenlm.github.io OR site:github.com/QwenLM"),
    ("DEEPSEEK", "DeepSeek model release site:deepseek.com OR site:github.com/deepseek-ai"),
    ("GLM", "GLM model release site:z.ai OR site:github.com/THUDM"),
    ("KIMI", "Kimi Moonshot AI model release site:moonshot.cn OR site:kimi.com"),
    ("MISTRAL", "Mistral model release site:mistral.ai"),
]

TRUSTED_DOMAINS = (
    "openai.com","help.openai.com","anthropic.com","deepmind.google","blog.google",
    "x.ai","ai.meta.com","qwenlm.github.io","github.com","deepseek.com","z.ai",
    "moonshot.cn","kimi.com","mistral.ai","reuters.com","techcrunch.com","theverge.com"
)

KEYWORDS = (
    "release","released","launch","launched","model","api","deprecat","shutdown","reset",
    "relaunch","restructure","default","limit","quota","codex","claude","gemini","grok",
    "llama","qwen","deepseek","glm","kimi","mistral","agent","multimodal"
)

def clean_text(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""

def resolve_url(url: str) -> str:
    """Resolve news-aggregator redirect URLs to the publisher when possible."""
    try:
        d = domain(url)
        if d in ("bing.com", "www.bing.com", "news.google.com"):
            r = requests.get(
                url,
                timeout=12,
                allow_redirects=True,
                headers={"User-Agent":"Mozilla/5.0 AI-Brief/1.0"},
                stream=True,
            )
            return r.url or url
    except Exception:
        pass
    return url

def parse_date(s: str):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None

def fetch_rss(label: str, query: str):
    url = "https://www.bing.com/news/search?" + urllib.parse.urlencode({
        "q": query,
        "format": "RSS",
        "setlang": "en-US",
    })
    r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0 AI-Brief/1.0"})
    r.raise_for_status()
    root = ET.fromstring(r.text)
    out = []
    for item in root.findall(".//item"):
        title = clean_text(item.findtext("title"))
        link = clean_text(item.findtext("link"))
        desc = clean_text(item.findtext("description"))
        pub = parse_date(item.findtext("pubDate"))
        if not title or not link:
            continue
        resolved = resolve_url(link)
        d = domain(resolved)
        if not any(d == td or d.endswith("." + td) for td in TRUSTED_DOMAINS):
            continue
        link = resolved
        if pub and pub < SINCE:
            continue
        text = f"{title} {desc}".lower()
        if not any(k in text for k in KEYWORDS):
            continue
        official = any(d == od or d.endswith("." + od) for od in (
            "openai.com","help.openai.com","anthropic.com","deepmind.google","blog.google",
            "x.ai","ai.meta.com","qwenlm.github.io","deepseek.com","z.ai","moonshot.cn",
            "kimi.com","mistral.ai","github.com"
        ))
        score = 20 if official else 8
        if label in ("OPENAI","ANTHROPIC","GOOGLE","XAI","META"):
            score += 12
        if any(k in text for k in ("released","release","launch","model","api","reset","deprecat","shutdown","default","quota","limit")):
            score += 8
        if pub:
            age_h = max(0, (NOW - pub).total_seconds()/3600)
            score += max(0, 12 - age_h/2)
        out.append({
            "label": label, "title": title, "link": link, "desc": desc,
            "pub": pub, "domain": d, "score": score, "official": official,
        })
    return out

def normalize_title(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def dedupe(items):
    seen = []
    out = []
    for x in sorted(items, key=lambda z: z["score"], reverse=True):
        n = normalize_title(x["title"])
        if any(n in s or s in n for s in seen if len(n) > 12 and len(s) > 12):
            continue
        seen.append(n)
        out.append(x)
    return out

def why_it_matters(item):
    t = (item["title"] + " " + item["desc"]).lower()
    if any(k in t for k in ("reset","quota","limit","shutdown","deprecat","default","relaunch")):
        return "这类变化会直接影响现有用户或开发者的可用额度、兼容性与工作流，需要及时确认迁移或使用策略。"
    if "api" in t:
        return "API 变化通常会直接影响集成方式、模型选择与调用成本，对现有应用的兼容性尤其重要。"
    if any(k in t for k in ("agent","tool","computer use","coding")):
        return "这反映了大模型竞争继续从单纯对话转向真实任务执行与 Agent 工作流，对开发和自动化场景更直接。"
    if any(k in t for k in ("multimodal","vision","audio","video")):
        return "多模态能力的变化会扩大模型可处理的信息类型，并直接影响产品形态与应用边界。"
    return "这是近期模型能力或产品路线的重要变化，可能影响模型选择、成本、开发方式或后续生态演进。"

def summarize(item):
    desc = item["desc"]
    if not desc:
        return item["title"]
    if len(desc) > 220:
        desc = desc[:217].rstrip() + "..."
    return desc

def choose(items):
    items = dedupe(items)
    primary = [x for x in items if x["label"] in ("OPENAI","ANTHROPIC","GOOGLE","XAI","META")]
    secondary = [x for x in items if x["label"] not in ("OPENAI","ANTHROPIC","GOOGLE","XAI","META")]
    chosen = primary[:5]
    if len(chosen) < 3:
        chosen.extend(secondary[: 5-len(chosen)])
    return chosen[:5]

def build_html(items, date_str):
    cards = []
    for x in items:
        src = html.escape(x["link"], quote=True)
        cards.append(f"""
        <div style="padding:20px 0;border-bottom:1px solid #eef1f4">
          <div style="display:inline-block;font-size:11px;letter-spacing:.08em;color:#5f6670;background:#f1f3f5;border-radius:6px;padding:4px 7px;margin-bottom:10px">{html.escape(x['label'])}</div>
          <div style="font-size:20px;font-weight:700;line-height:1.45;margin-bottom:8px">{html.escape(x['title'])}</div>
          <div style="font-size:15px;line-height:1.8;color:#606770">{html.escape(summarize(x))}</div>
          <div style="font-size:14px;line-height:1.75;color:#4f5660;margin-top:9px"><b>为什么重要：</b>{html.escape(why_it_matters(x))}</div>
          <div style="margin-top:12px"><a href="{src}" style="font-size:14px;color:#3157d5;text-decoration:none">Source →</a></div>
        </div>""")
    return f"""<!doctype html>
<html><body style="margin:0;background:#f6f7f9;padding:28px 12px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif;color:#20242a">
<div style="max-width:680px;margin:0 auto;background:#fff;border:1px solid #eceff3;border-radius:14px;padding:34px 32px">
  <div style="font-size:13px;color:#58606b;margin-bottom:20px"><span style="display:inline-block;width:7px;height:7px;background:#20242a;border-radius:50%;margin-right:8px;vertical-align:1px"></span>AI Brief</div>
  <div style="font-size:32px;line-height:1.2;font-weight:700;letter-spacing:-0.02em;margin-bottom:8px">AI Brief · {date_str}</div>
  <div style="font-size:14px;color:#8c929b;margin-bottom:24px">OpenAI / Anthropic / Google / Open Source</div>
  <div style="border-top:1px solid #eceff3;margin-bottom:10px"></div>
  {''.join(cards)}
  <div style="margin-top:22px;font-size:12px;color:#979da6">Sent from daily@liujiahang.icu</div>
</div></body></html>"""

def build_text(items, date_str):
    lines = [f"AI Brief · {date_str}", "", "OpenAI / Anthropic / Google / Open Source", ""]
    for x in items:
        lines += [x["label"], x["title"], summarize(x), "为什么重要：" + why_it_matters(x), "Source → " + x["link"], ""]
    lines += ["Sent from daily@liujiahang.icu"]
    return "\n".join(lines)

def send_email(subject, text_body, html_body):
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        raise RuntimeError("Missing RESEND_API_KEY")
    payload = {
        "from": "AI Daily <daily@liujiahang.icu>",
        "to": ["Liu18701059325@qq.com"],
        "subject": subject,
        "text": text_body,
        "html": html_body,
    }
    r = requests.post(
        "https://api.resend.com/emails",
        json=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type":"application/json"},
        timeout=30,
    )
    if r.status_code >= 300:
        raise RuntimeError(f"Resend error {r.status_code}: {r.text}")
    print("sent:", r.text)

def main():
    items = []
    for label, q in QUERIES:
        try:
            items.extend(fetch_rss(label, q))
        except Exception as e:
            print(f"warning: {label}: {e}", file=sys.stderr)
        time.sleep(0.4)

    chosen = choose(items)
    date_str = datetime.now(TZ).strftime("%Y.%m.%d")
    subject = f"AI Brief · {date_str}"

    if not chosen:
        text_body = (
            f"AI Brief · {date_str}\n\n"
            "OpenAI / Anthropic / Google / Open Source\n\n"
            "过去约 24 小时内，没有检索到足够可信且足够新的重大模型更新。"
            "今天不为了凑数加入旧闻。\n\n"
            "Sent from daily@liujiahang.icu"
        )
        html_body = f"""<!doctype html><html><body style="margin:0;background:#f6f7f9;padding:28px 12px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif;color:#20242a">
<div style="max-width:680px;margin:0 auto;background:#fff;border:1px solid #eceff3;border-radius:14px;padding:34px 32px">
<div style="font-size:13px;color:#58606b;margin-bottom:20px">● AI Brief</div>
<div style="font-size:32px;font-weight:700;margin-bottom:8px">AI Brief · {date_str}</div>
<div style="font-size:14px;color:#8c929b;margin-bottom:24px">OpenAI / Anthropic / Google / Open Source</div>
<div style="border-top:1px solid #eceff3;margin-bottom:24px"></div>
<div style="font-size:15px;line-height:1.9;color:#606770">过去约 24 小时内，没有检索到足够可信且足够新的重大模型更新。今天不为了凑数加入旧闻。</div>
<div style="margin-top:26px;font-size:12px;color:#979da6">Sent from daily@liujiahang.icu</div>
</div></body></html>"""
    else:
        text_body = build_text(chosen, date_str)
        html_body = build_html(chosen, date_str)

    send_email(subject, text_body, html_body)

if __name__ == "__main__":
    main()
