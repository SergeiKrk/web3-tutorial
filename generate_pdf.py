#!/usr/bin/env python3
"""web3Crypto PDF generator — A5 portrait."""
import re, hashlib, markdown
from weasyprint import HTML

WIKI = "/home/ai/DewWork/web3Crypto/wiki"
OUTPUT = "/home/ai/DewWork/web3Crypto/web3Crypto.pdf"

PAGES = [
    ("web3-фронтендер: план трудоустройства", "web3-фронтендер-план-трудоустройства.md"),
    ("Главная: дорожная карта web3", "Главная.md"),
    ("Блокчейн — как это работает", "Блокчейн-как-это-работает.md"),
    ("Словарь терминов web3", "Словарь-web3.md"),
    ("Solidity — основы синтаксиса", "Solidity-основы.md"),
    ("ERC-20: стандарт токенов", "ERC-20-стандарт-токенов.md"),
    ("ERC-721: NFT стандарт", "ERC-721-NFT-стандарт.md"),
    ("Hardhat — среда разработки", "Hardhat-среда-разработки.md"),
    ("OpenZeppelin — безопасные контракты", "OpenZeppelin-безопасные-контракты.md"),
    ("wagmi + RainbowKit — фронтенд для dApps", "wagmi-RainbowKit-фронтенд.md"),
    ("Сравнение ethers.js, viem, wagmi", "Сравнение-ethers-viem-wagmi.md"),
    ("Subgraph / The Graph — индексация", "Subgraph-The-Graph.md"),
    ("Паттерны транзакций в React", "Паттерны-транзакций-React.md"),
    ("DeFi для фронтендера", "DeFi-для-фронтендера.md"),
    ("Вопросы web3-собеседования", "Вопросы-web3-собеседование.md"),
    ("GitHub Commit Notary (пет-проект)", "GitHub-Commit-Notary.md"),
    ("Proof of Skill (пет-проект)", "Proof-of-Skill.md"),
    ("Open Source Sponsor Escrow (пет-проект)", "Open-Source-Sponsor-Escrow.md"),
]

def slugify(text):
    text = text.lower().strip()
    h = hashlib.md5(text.encode()).hexdigest()[:6]
    clean = re.sub(r'[^a-zа-яё0-9]+', '-', text).strip('-')
    return f"{clean}-{h}" if clean else f"section-{h}"

def strip_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        return parts[2].strip() if len(parts) >= 3 else text
    return text

def extract_h2_headings(md_text):
    headings = []
    for line in md_text.split("\n"):
        m = re.match(r'^##\s+(.+)$', line.strip())
        if m: headings.append((slugify(m.group(1)), m.group(1).strip()))
    return headings

def md_to_html(md_text):
    md_text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", md_text)
    html = markdown.markdown(md_text, extensions=["fenced_code", "tables", "codehilite", "nl2br"])
    return re.sub(r'<h2>([^<]+)</h2>', lambda m: f'<h2 id="{slugify(m.group(1))}">{m.group(1)}</h2>', html)

def build_toc():
    lines = []
    for chap_title, filename in PAGES:
        path = f"{WIKI}/{filename}"
        with open(path, "r") as f:
            raw = f.read()
        headings = extract_h2_headings(strip_frontmatter(raw))
        lines.append(f'<li class="toc-chapter">{chap_title}')
        if headings:
            lines.append('<ol class="toc-sections">')
            for sid, text in headings[:8]:
                lines.append(f'<li><a href="#{sid}">{text}</a></li>')
            lines.append('</ol>')
        lines.append('</li>')
    return f'<ol class="toc-top">{"".join(lines)}</ol>'

def build_html():
    sections = []
    for chap_title, filename in PAGES:
        path = f"{WIKI}/{filename}"
        with open(path, "r") as f:
            raw = f.read()
        sections.append(f'<section class="chapter"><h2 class="chapter-title">{chap_title}</h2>{md_to_html(strip_frontmatter(raw))}</section>')

    css = """
    @page { size: A5 portrait; margin: 2mm 3mm; }
    body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 10pt; color: #222; line-height: 1.4; }
    .cover { text-align: center; padding-top: 30mm; page-break-after: always; }
    .cover h1 { font-size: 13pt; margin-bottom: 4mm; }
    .cover .subtitle { font-size: 11pt; margin: 2mm 0; color: #555; }
    .cover .meta { font-size: 8pt; color: #888; margin-top: 15mm; }
    .toc-page { page-break-after: always; }
    .toc-page h2 { font-size: 10.5pt; margin-bottom: 3mm; }
    .toc-top { font-size: 9pt; line-height: 1.7; padding-left: 0; list-style: none; }
    .toc-chapter { font-weight: bold; margin-top: 2mm; font-size: 9.5pt; }
    .toc-sections { font-weight: normal; font-size: 8pt; line-height: 1.6; padding-left: 5mm; list-style: disc; }
    .toc-sections a { color: #222; text-decoration: none; }
    .chapter-title { font-size: 11pt; margin: 3mm 0 2mm 0; padding-bottom: 1mm; border-bottom: 0.5px solid #999; }
    h1 { font-size: 13pt; margin: 3mm 0 2mm 0; page-break-after: avoid; }
    h2 { font-size: 10.5pt; margin: 3mm 0 1.5mm 0; page-break-after: avoid; }
    h3 { font-size: 10pt; margin: 2mm 0 1mm 0; page-break-after: avoid; }
    p { margin: 1mm 0; }
    pre { background: none; border: 0.3px solid #ccc; border-left: 1.5px solid #999; padding: 1mm 2mm; font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; line-height: 1.35; white-space: pre-wrap; word-break: break-all; margin: 1mm 0; page-break-inside: avoid; }
    code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; background: none; }
    table { width: 100%; border-collapse: collapse; font-size: 7pt; margin: 1.5mm 0; page-break-inside: avoid; }
    th { background: #f0f0f0; text-align: left; padding: 1mm 1.5mm; border-bottom: 0.5px solid #999; }
    td { padding: 0.8mm 1.5mm; border-bottom: 0.3px solid #ddd; }
    ul, ol { margin: 1mm 0; padding-left: 4mm; }
    li { margin: 0.3mm 0; }
    blockquote { border-left: 1.5px solid #bbb; margin: 1mm 0; padding: 0.5mm 2mm; color: #555; font-style: italic; }
    hr { border: none; border-top: 0.3px solid #ddd; margin: 2mm 0; }
    """

    return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="cover"><h1>web3 для фронтендера</h1><p class="subtitle">Методичка для трудоустройства</p><p class="subtitle">React + блокчейн + DeFi + собеседование</p><p class="meta">Составил: Sergei Krk &amp; Hermes AI</p><p class="meta">Дата сборки: 2026-07-23</p></div>
<div class="toc-page"><h2>Содержание</h2>{build_toc()}</div>
{"".join(sections)}
</body></html>"""

def main():
    html = build_html()
    html_path = "/tmp/web3crypto.html"
    with open(html_path, "w") as f: f.write(html)
    print(f"HTML: {html_path} ({len(html)} chars)")
    HTML(filename=html_path).write_pdf(OUTPUT)
    print(f"PDF: {OUTPUT}")

if __name__ == "__main__":
    main()
