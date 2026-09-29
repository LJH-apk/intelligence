#!/usr/bin/env python3
import html
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparser

LOCAL_TZ = timezone(timedelta(hours=8))
NOW = datetime.now(timezone.utc)
SINCE = NOW - timedelta(hours=36)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 AI-Brief/1.0"
}

PRIMARY_LABELS = {"OPENAI", "ANTHROPIC", "GOOGLE", "XAI", "META"}

SOURCES = [
    {"label":"OPENAI","url":"https://help.openai.com/en/articles/6825453-chatgpt-release-notes","mode":"changelog","priority":40},
    {"label":"OPENAI","url":"https://platform.openai.com/docs/deprecations","mode":"changelog","priority":44},
    {"label":"OPENAI","url":"https://openai.com/news/","mode":"index","priority":38},
    {"label":"ANTHROPIC","url":"https://www.anthropic.com/news","mode":"index","priority":38},
    {"label":"GOOGLE","url":"https://deepmind.google/blog/","mode":"index","priority":38},
    {"label":"XAI","url":"https://x.ai/news","mode":"index","priority":38},
    {"label":"META","url":"https://ai.meta.com/blog/","mode":"index","priority":34},
    {"label":"DEEPSEEK","url":"https://api-docs.deepseek.com/updates/","mode":"changelog","priority":25},
    {"label":"QWEN","url":"https://qwenlm.github.io/blog/","mode":"index","priority":25},
    {"label":"GLM","url":"https://z.ai/blog","mode":"index","priority":25},
    {"label":"KIMI","url":"https://www.kimi.com/en/blog","mode":"index","priority":24},
    {"label":"MISTRAL","url":"https://mistral.ai/news/","mode":"index","priority":24},
]

HIGH_SIGNAL = (
    "release","released","launch","launched","introducing","model","api",
    "deprecat","shutdown","sunset","retire","reset","quota","limit",
    "default model","relaunch","restructure","codex","claude","gemini",
    "grok","llama","qwen","deepseek","glm","kimi","mistral",
    "agent","multimodal","vision","audio","reasoning"
)

OPENAI_EXTRA = (
    "reset","quota","limit","banked","default model","shutdown",
    "deprecat","retire","relaunch","restructure","rollout","codex"
)

DATE_PATTERNS = [
    r"\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b",
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(20\d{2})\b",
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(20\d{2})\b",
]

def fetch(url, timeout=20):
    r = requests.get(url, timeout=timeout, headers=HEADERS)
    r.raise_for_status()
    return r.text

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()

def parse_date_text(text):
    text = clean(text)
    for pat in DATE_PATTERNS:
        m = re.search(pat, text, flags=re.I)
        if not m:
            continue
        try:
            return dtparser.parse(m.group(0), fuzzy=True).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return None

def parse_page_date(soup):
    for attr, key in [
        ("property","article:published_time"),("name","date"),("name","pubdate"),
        ("name","publish_date"),("itemprop","datePublished"),
    ]:
        tag = soup.find("meta", attrs={attr:key})
        if tag and tag.get("content"):
            try:
                d = dtparser.parse(tag["content"])
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone.utc)
                return d.astimezone(timezone.utc)
            except Exception:
                pass
    t = soup.find("time")
    if t:
        raw = t.get("datetime") or t.get_text(" ", strip=True)
        try:
            d = dtparser.parse(raw)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc)
        except Exception:
            pass
    return parse_date_text(soup.get_text(" ", strip=True)[:3500])

def same_site(base, url):
    try:
        b = urlparse(base).netloc.lower().removeprefix("www.")
        u = urlparse(url).netloc.lower().removeprefix("www.")
        return u == b or u.endswith("." + b) or b.endswith("." + u)
    except Exception:
        return False

def interesting(text, label):
    t = clean(text).lower()
    if label == "OPENAI" and any(k in t for k in OPENAI_EXTRA):
        return True
    return any(k in t for k in HIGH_SIGNAL)

def description_from_page(soup):
    for attrs in ({"name":"description"},{"property":"og:description"}):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return clean(tag["content"])[:420]
    paras = []
    for p in soup.find_all("p"):
        txt = clean(p.get_text(" ", strip=True))
        if len(txt) >= 70:
            paras.append(txt)
        if len(" ".join(paras)) > 420:
            break
    return clean(" ".join(paras))[:420]

def extract_index(source):
    base, label = source["url"], source["label"]
    out = []
    try:
        soup = BeautifulSoup(fetch(base), "html.parser")
    except Exception as e:
        print(f"warning: fetch {base}: {e}", file=sys.stderr)
        return out

    seen, candidates = set(), []
    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"])
        if href in seen or not same_site(base, href):
            continue
        text = clean(a.get_text(" ", strip=True))
        if len(text) < 8:
            continue
        parent_text = clean(a.parent.get_text(" ", strip=True)) if a.parent else text
        if not interesting(f"{text} {parent_text}", label):
            continue
        seen.add(href)
        candidates.append((href, text, parent_text))

    for href, anchor_text, parent_text in candidates[:35]:
        try:
            page = BeautifulSoup(fetch(href, timeout=15), "html.parser")
            d = parse_page_date(page) or parse_date_text(parent_text)
            if not d or d < SINCE:
                continue
            h1 = page.find("h1")
            title = clean(h1.get_text(" ", strip=True)) if h1 else anchor_text
            summary = description_from_page(page)
            if not interesting(f"{title} {summary}", label):
                continue
            score = source["priority"]
            low = f"{title} {summary}".lower()
            if any(k in low for k in ("release","released","introducing","launch","model","api")):
                score += 12
            if label == "OPENAI" and any(k in low for k in OPENAI_EXTRA):
                score += 16
            age_h = max(0.0, (NOW - d).total_seconds() / 3600.0)
            score += max(0.0, 12.0 - age_h / 3.0)
            out.append({"label":label,"title":title,"summary":summary or title,"url":href,"date":d,"score":score})
        except Exception as e:
            print(f"warning: article {href}: {e}", file=sys.stderr)
        time.sleep(0.12)
    return out

def extract_changelog(source):
    url, label = source["url"], source["label"]
    out = []
    try:
        soup = BeautifulSoup(fetch(url), "html.parser")
    except Exception as e:
        print(f"warning: changelog {url}: {e}", file=sys.stderr)
        return out

    current_date = None
    for h in soup.find_all(["h1","h2","h3"]):
        txt = clean(h.get_text(" ", strip=True))
        d = parse_date_text(txt)
        if d:
            current_date = d
            continue
        if not current_date or current_date < SINCE:
            continue
        section_bits = [txt]
        node = h.find_next_sibling()
        while node and node.name not in ("h1","h2","h3"):
            section_bits.append(clean(node.get_text(" ", strip=True)))
            node = node.find_next_sibling()
            if len(" ".join(section_bits)) > 900:
                break
        blob = clean(" ".join(section_bits))
        if len(blob) < 20 or not interesting(blob, label):
            continue
        title = txt if len(txt) >= 6 else blob[:100]
        summary = blob
        if summary.lower().startswith(title.lower()):
            summary = clean(summary[len(title):])
        summary = summary[:420] or title
        score = source["priority"] + 10
        low = blob.lower()
        if label == "OPENAI" and any(k in low for k in OPENAI_EXTRA):
            score += 20
        if any(k in low for k in ("release","introducing","model","api","shutdown","deprecat")):
            score += 10
        age_h = max(0.0, (NOW - current_date).total_seconds() / 3600.0)
        score += max(0.0, 12.0 - age_h / 3.0)
        out.append({"label":label,"title":title,"summary":summary,"url":url,"date":current_date,"score":score})
    return out

def normalize_title(s):
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", s.lower())

def dedupe(items):
    out, seen = [], []
    for x in sorted(items, key=lambda z:z["score"], reverse=True):
        n = normalize_title(x["title"])
        if any(len(n) > 12 and len(s) > 12 and (n in s or s in n) for s in seen):
            continue
        seen.append(n)
        out.append(x)
    return out

def choose(items):
    items = dedupe(items)
    primary = [x for x in items if x["label"] in PRIMARY_LABELS]
    secondary = [x for x in items if x["label"] not in PRIMARY_LABELS]
    chosen = primary[:5]
    if len(chosen) < 3:
        chosen.extend(secondary[:5-len(chosen)])
    return chosen[:5]

def why_it_matters(item):
    t = f"{item['title']} {item['summary']}".lower()
    if any(k in t for k in ("reset","quota","limit","shutdown","deprecat","retire","default model")):
        return "这类变化会直接影响现有用户或开发者的额度、兼容性或默认工作流，需要及时确认迁移与使用策略。"
    if "api" in t:
        return "API 变化会直接影响模型接入、兼容性、成本与生产环境调用方式。"
    if any(k in t for k in ("agent","tool use","computer use","coding")):
        return "这反映出模型竞争继续从聊天转向真实任务执行和 Agent 工作流，对开发与自动化场景更直接。"
    if any(k in t for k in ("multimodal","vision","audio","video")):
        return "多模态能力扩展会直接改变模型可处理的信息类型，并影响产品形态和应用边界。"
    return "这是近期模型能力或产品路线的重要变化，可能影响模型选择、成本、开发方式或后续生态演进。"

def build_html(items, date_str):
    if not items:
        body = '<div style="font-size:15px;line-height:1.9;color:#606770">过去约 24 小时内，没有检索到足够可信且足够新的重大模型更新。今天不为了凑数加入旧闻。</div>'
    else:
        cards = []
        for x in items:
            cards.append(f"""
            <div style="padding:20px 0;border-bottom:1px solid #eef1f4">
              <div style="display:inline-block;font-size:11px;letter-spacing:.08em;color:#5f6670;background:#f1f3f5;border-radius:6px;padding:4px 7px;margin-bottom:10px">{html.escape(x['label'])}</div>
              <div style="font-size:20px;font-weight:700;line-height:1.45;margin-bottom:8px">{html.escape(x['title'])}</div>
              <div style="font-size:15px;line-height:1.8;color:#606770">{html.escape(x['summary'])}</div>
              <div style="font-size:14px;line-height:1.75;color:#4f5660;margin-top:9px"><b>为什么重要：</b>{html.escape(why_it_matters(x))}</div>
              <div style="margin-top:12px"><a href="{html.escape(x['url'], quote=True)}" style="font-size:14px;color:#3157d5;text-decoration:none">Source →</a></div>
            </div>""")
        body = "".join(cards)
    return f"""<!doctype html><html><body style="margin:0;background:#f6f7f9;padding:28px 12px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif;color:#20242a">
<div style="max-width:680px;margin:0 auto;background:#fff;border:1px solid #eceff3;border-radius:14px;padding:34px 32px">
  <div style="font-size:13px;color:#58606b;margin-bottom:20px"><span style="display:inline-block;width:7px;height:7px;background:#20242a;border-radius:50%;margin-right:8px;vertical-align:1px"></span>AI Brief</div>
  <div style="font-size:32px;line-height:1.2;font-weight:700;letter-spacing:-0.02em;margin-bottom:8px">AI Brief · {date_str}</div>
  <div style="font-size:14px;color:#8c929b;margin-bottom:24px">OpenAI / Anthropic / Google / Open Source</div>
  <div style="border-top:1px solid #eceff3;margin-bottom:10px"></div>{body}
  <div style="margin-top:22px;font-size:12px;color:#979da6">Sent from daily@liujiahang.icu</div>
</div></body></html>"""

def build_text(items, date_str):
    lines = [f"AI Brief · {date_str}", "", "OpenAI / Anthropic / Google / Open Source", ""]
    if not items:
        lines.append("过去约 24 小时内，没有检索到足够可信且足够新的重大模型更新。今天不为了凑数加入旧闻。")
    for x in items:
        lines += [x["label"],x["title"],x["summary"],"为什么重要："+why_it_matters(x),"Source → "+x["url"],""]
    lines += ["Sent from daily@liujiahang.icu"]
    return "\n".join(lines)

def send_email(subject, text_body, html_body):
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        raise RuntimeError("Missing RESEND_API_KEY")
    r = requests.post(
        "https://api.resend.com/emails",
        json={"from":"AI Daily <daily@liujiahang.icu>","to":["Liu18701059325@qq.com"],"subject":subject,"text":text_body,"html":html_body},
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
        timeout=30,
    )
    if r.status_code >= 300:
        raise RuntimeError(f"Resend error {r.status_code}: {r.text}")
    print("sent:", r.text)

def main():
    items = []
    for source in SOURCES:
        extractor = extract_changelog if source["mode"] == "changelog" else extract_index
        found = extractor(source)
        print(f"{source['label']:10s} {source['url']} -> {len(found)} recent candidates")
        items.extend(found)
    chosen = choose(items)
    date_str = datetime.now(LOCAL_TZ).strftime("%Y.%m.%d")
    send_email(f"AI Brief · {date_str}", build_text(chosen, date_str), build_html(chosen, date_str))

if __name__ == "__main__":
    main()
