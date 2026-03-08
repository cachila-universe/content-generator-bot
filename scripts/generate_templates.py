#!/usr/bin/env python3
"""Generate all updated templates for the site redesign.

Creates:
- index.html (BI-inspired homepage)
- post.html (updated with Tools nav, floating subscribe)
- niche_index.html (with article images)
- subtopic_index.html (with article images)
- tools/index.html (tools landing page)
- tools/deal-finder.html
- tools/ai-tool-finder.html
- tools/budget-calculator.html
- tools/workout-generator.html
- tools/pet-food-checker.html
- tools/smart-home.html
"""

import os
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "site" / "templates"

# ═══════════════════════════════════════════════════════════
# Shared snippets used across all templates
# ═══════════════════════════════════════════════════════════

SHARED_HEAD_FONTS = """  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">"""

SHARED_NAV = """  <!-- Header -->
  <header class="header">
    <div class="container">
      <div class="header-top">
        <a href="/" class="logo">
          <img src="/assets/logo-full-dark.svg" alt="TechLife Insights">
          <span class="logo-text">TechLife Insights</span>
        </a>
        <button class="mobile-toggle" onclick="document.getElementById('navLinks').classList.toggle('open')" aria-label="Menu">☰</button>
      </div>
      <nav class="nav-links" id="navLinks">
        <div class="nav-main">
          <a href="/" class="nav-link nav-home">Home</a>
          {% for nid, niche in niches.items() %}{% if niche.enabled %}
          <div class="nav-item">
            <a href="/{{ nid }}/" class="nav-link{% if nid == active_niche %} active{% endif %}">{{ niche.name }}</a>
            {% if niche.subtopics %}<div class="nav-dropdown">{% for sub_id, sub in niche.subtopics.items() %}<a href="/{{ nid }}/{{ sub_id }}/">{{ sub.name }}</a>{% endfor %}</div>{% endif %}
          </div>
          {% endif %}{% endfor %}
        </div>
        <div class="nav-tools">
          <div class="nav-item">
            <a href="/tools/" class="nav-link nav-tools-link">🛠️ Tools</a>
            <div class="nav-dropdown nav-dropdown-right">
              <a href="/tools/deal-finder.html">🔍 Deal Finder</a>
              <a href="/tools/ai-tool-finder.html">🤖 AI Tool Directory</a>
              <a href="/tools/budget-calculator.html">💰 Budget Calculator</a>
              <a href="/tools/workout-generator.html">💪 Workout Generator</a>
              <a href="/tools/pet-food-checker.html">🐾 Pet Food Analyzer</a>
              <a href="/tools/smart-home.html">🏠 Smart Home Hub</a>
              <a href="/travel/search.html">✈️ Travel Search</a>
              <a href="/personal_finance/markets.html">📊 Market Data</a>
            </div>
          </div>
        </div>
      </nav>
    </div>
  </header>"""

SHARED_NAV_CSS = """
    .header { position: sticky; top: 0; z-index: 50; background: #1e3a8a; }
    .header-top { display: flex; align-items: center; justify-content: space-between; padding: 16px 0 10px; }
    .logo { display: flex; align-items: center; gap: 14px; text-decoration: none; color: #fff; }
    .logo img { height: 48px; width: auto; }
    .logo-text { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; color: #fff; }
    .nav-links { display: flex; align-items: center; justify-content: space-between; padding: 0 0 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; gap: 8px; }
    .nav-main { display: flex; gap: 2px; align-items: center; flex-wrap: wrap; }
    .nav-tools { display: flex; align-items: center; margin-left: auto; padding-left: 16px; border-left: 1px solid rgba(255,255,255,0.15); }
    .nav-link { padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.75); transition: all 0.15s; white-space: nowrap; text-decoration: none; }
    .nav-link:hover, .nav-link.active { color: #fff; background: rgba(255,255,255,0.12); }
    .nav-home { font-size: 14px; font-weight: 700; color: #fff; padding: 6px 16px; }
    .nav-tools-link { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.9); }
    .nav-item { position: relative; display: inline-block; }
    .nav-item:hover .nav-dropdown { display: block; }
    .nav-dropdown { display: none; position: absolute; top: 100%; left: 0; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); min-width: 210px; padding: 6px 0; z-index: 100; }
    .nav-dropdown-right { left: auto; right: 0; }
    .nav-dropdown a { display: block; padding: 8px 16px; font-size: 13px; color: #111827; font-weight: 500; transition: background 0.1s; text-decoration: none; }
    .nav-dropdown a:hover { background: #eff6ff; color: #2563eb; }
    .mobile-toggle { display: none; background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; padding: 6px; }"""

SHARED_SUBSCRIBE_FLOAT = """  <a href="https://techlife-insights.kit.com/be266c00d5" target="_blank" rel="noopener" class="subscribe-float">📬 Subscribe</a>"""

SHARED_SUBSCRIBE_CSS = """
    .subscribe-float { position: fixed; bottom: 24px; right: 24px; z-index: 1000; background: #2563eb; color: #fff !important; padding: 14px 22px; border-radius: 50px; font-size: 14px; font-weight: 700; text-decoration: none !important; box-shadow: 0 4px 20px rgba(37,99,235,0.45); display: flex; align-items: center; gap: 8px; transition: all 0.2s; font-family: 'Inter', sans-serif; }
    .subscribe-float:hover { background: #1d4ed8; transform: translateY(-2px); box-shadow: 0 6px 24px rgba(37,99,235,0.55); color: #fff !important; }"""

SHARED_MOBILE_CSS = """
    @media (max-width: 768px) {
      .logo-text { font-size: 18px; }
      .nav-links { display: none; }
      .nav-links.open { display: flex; flex-direction: column; position: absolute; top: 100%; left: 0; right: 0; background: #1e3a8a; padding: 12px 24px; border-top: 1px solid rgba(255,255,255,0.1); gap: 4px; z-index: 200; }
      .nav-links.open .nav-main { flex-direction: column; width: 100%; }
      .nav-links.open .nav-tools { border-left: none; padding-left: 0; margin-left: 0; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; margin-top: 4px; width: 100%; }
      .nav-links.open .nav-item { display: block; }
      .nav-links.open .nav-dropdown { position: static; box-shadow: none; border: none; background: rgba(255,255,255,0.05); border-radius: 6px; margin: 4px 0; }
      .nav-links.open .nav-dropdown a { color: rgba(255,255,255,0.7); }
      .nav-links.open .nav-dropdown-right { left: 0; right: auto; }
      .mobile-toggle { display: block; }
    }"""


# ═══════════════════════════════════════════════════════════
# 1. INDEX.HTML — BI-inspired homepage
# ═══════════════════════════════════════════════════════════

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ site_title }} — {{ tagline }}</title>
  <meta name="description" content="{{ tagline }}. Expert guides on AI tools, personal finance, health, home tech, travel, fitness, pet care, and remote work.">
  <meta property="og:title" content="{{ site_title }}">
  <meta property="og:description" content="{{ tagline }}">
  <meta property="og:type" content="website">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-hover:#1d4ed8; --accent-light:#eff6ff; --border:#e5e7eb; --shadow:0 4px 12px rgba(0,0,0,0.08); --shadow-lg:0 8px 30px rgba(0,0,0,0.12); --radius:10px; --max-width:1240px; }
    *{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none;transition:color .2s}a:hover{color:var(--accent-hover)}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}img{max-width:100%}
""" + SHARED_NAV_CSS + """
    .hero-featured{padding:32px 0 0}.hero-card{display:grid;grid-template-columns:1.3fr 1fr;gap:32px;align-items:center;text-decoration:none;color:var(--text);border-radius:var(--radius);overflow:hidden}.hero-card:hover{color:var(--text)}.hero-card:hover .hero-title{color:var(--accent)}.hero-img{border-radius:var(--radius);overflow:hidden;aspect-ratio:16/9}.hero-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s}.hero-card:hover .hero-img img{transform:scale(1.03)}.hero-content{padding:8px 0}.hero-badge{display:inline-block;background:var(--accent);color:#fff;padding:4px 12px;border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:14px}.hero-title{font-size:32px;font-weight:800;line-height:1.2;letter-spacing:-.02em;margin-bottom:14px;transition:color .2s}.hero-meta{font-size:13px;color:var(--text-secondary);display:flex;gap:8px}
    .section{padding:40px 0}.section-heading{font-size:22px;font-weight:800;margin-bottom:24px;padding-bottom:10px;border-bottom:3px solid var(--text);display:inline-block;letter-spacing:-.01em}
    .articles-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}.article-card{display:flex;flex-direction:column;text-decoration:none;color:var(--text);border-radius:var(--radius);overflow:hidden;transition:transform .2s,box-shadow .2s;border:1px solid var(--border)}.article-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg);color:var(--text)}.article-card:hover .card-title{color:var(--accent)}.card-img{aspect-ratio:16/10;overflow:hidden;background:var(--surface)}.card-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .35s}.article-card:hover .card-img img{transform:scale(1.05)}.card-body{padding:16px 18px 18px;flex:1;display:flex;flex-direction:column}.card-badge{display:inline-block;font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px}.card-title{font-size:16px;font-weight:700;line-height:1.35;margin-bottom:10px;transition:color .2s;flex:1}.card-meta{font-size:12px;color:var(--text-secondary);display:flex;gap:6px;margin-top:auto}
    .trending-bar{background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:14px 0;margin:0}.trending-inner{display:flex;align-items:center;gap:20px;overflow-x:auto}.trending-label{font-size:12px;font-weight:800;color:var(--accent);text-transform:uppercase;letter-spacing:.08em;white-space:nowrap}.trending-inner a{font-size:13px;color:var(--text);font-weight:500;white-space:nowrap}.trending-inner a:hover{color:var(--accent)}
    .tools-section{background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border)}.tools-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.tool-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:24px 20px;text-decoration:none;color:var(--text);transition:all .2s;text-align:center}.tool-card:hover{border-color:var(--accent);box-shadow:var(--shadow);transform:translateY(-3px);color:var(--text)}.tool-icon{font-size:32px;margin-bottom:10px}.tool-card h3{font-size:15px;font-weight:700;margin-bottom:6px}.tool-card p{font-size:13px;color:var(--text-secondary);line-height:1.5}
    .niche-section{border-top:1px solid var(--border)}.niche-row{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.niche-row .article-card{border:none;border-bottom:1px solid var(--border);border-radius:0}.niche-row .article-card:hover{transform:none;box-shadow:none}.section-header-row{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:20px}.see-all{font-size:13px;font-weight:600;color:var(--accent)}.see-all:hover{text-decoration:underline}
    .bestof-cta{background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);border-radius:14px;padding:36px 40px;text-align:center;color:#fff;margin:8px 0 40px}.bestof-cta h3{font-size:20px;font-weight:800;margin-bottom:8px}.bestof-cta p{font-size:14px;opacity:.85;margin-bottom:20px}.bestof-pills{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}.bestof-pills a{background:rgba(255,255,255,.15);color:#fff;padding:7px 16px;border-radius:8px;font-size:13px;font-weight:600;border:1px solid rgba(255,255,255,.2);transition:all .15s}.bestof-pills a:hover{background:rgba(255,255,255,.3);color:#fff}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:48px 0 32px;font-size:14px}.footer a{color:rgba(255,255,255,.7)}.footer a:hover{color:#fff}.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px;margin-bottom:36px}.footer-brand{font-size:14px;line-height:1.7}.footer-brand strong{color:#fff;font-size:17px;display:block;margin-bottom:8px}.footer-col h4{color:#fff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:14px}.footer-col ul{list-style:none}.footer-col li{margin-bottom:8px}.footer-col li a{font-size:14px}.footer-bottom{border-top:1px solid rgba(255,255,255,.1);padding-top:24px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:rgba(255,255,255,.45)}
    .empty-state{text-align:center;padding:100px 24px}.empty-state h2{font-size:28px;font-weight:800;margin-bottom:10px}.empty-state p{font-size:16px;color:var(--text-secondary);max-width:480px;margin:0 auto}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:1024px){.articles-grid{grid-template-columns:repeat(2,1fr)}.tools-grid{grid-template-columns:repeat(2,1fr)}.niche-row{grid-template-columns:repeat(2,1fr)}.footer-grid{grid-template-columns:1fr 1fr}}
    @media(max-width:768px){.hero-card{grid-template-columns:1fr}.hero-title{font-size:24px}.articles-grid,.niche-row{grid-template-columns:1fr}.tools-grid{grid-template-columns:1fr 1fr}.footer-grid{grid-template-columns:1fr}.footer-bottom{flex-direction:column;gap:8px;text-align:center}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>

""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  {%- if posts|length > 0 %}
  <div class="trending-bar"><div class="container"><div class="trending-inner"><span class="trending-label">📈 Trending</span>{% for post in posts[:5] %}<a href="{{ post.url }}">{{ post.title | truncate(50) }}</a>{% endfor %}</div></div></div>

  <!-- Hero -->
  <section class="hero-featured"><div class="container">
    {% set featured = posts[0] %}
    <a href="{{ featured.url }}" class="hero-card">
      <div class="hero-img"><img src="{{ featured.image_url if featured.image_url else 'https://picsum.photos/seed/' ~ featured.slug ~ '/1200/630' }}" alt="{{ featured.title }}"></div>
      <div class="hero-content">
        <span class="hero-badge">{{ featured.niche_name }}</span>
        <h1 class="hero-title">{{ featured.title }}</h1>
        <div class="hero-meta"><span>{{ featured.published_at[:10] if featured.published_at else '' }}</span><span>·</span>{% set rm = ((featured.word_count or 0) / 200) | int %}<span>{{ rm if rm > 0 else 1 }} min read</span></div>
      </div>
    </a>
  </div></section>

  {%- if posts|length > 1 %}
  <section class="section"><div class="container">
    <h2 class="section-heading">Latest</h2>
    <div class="articles-grid">
      {% for post in posts[1:] %}
      <a href="{{ post.url }}" class="article-card">
        <div class="card-img"><img src="{{ post.image_url if post.image_url else 'https://picsum.photos/seed/' ~ post.slug ~ '/600/380' }}" alt="{{ post.title }}" loading="lazy"></div>
        <div class="card-body">
          <span class="card-badge">{{ post.niche_name }}</span>
          <h3 class="card-title">{{ post.title }}</h3>
          <div class="card-meta"><span>{{ post.published_at[:10] if post.published_at else '' }}</span><span>·</span>{% set rm = ((post.word_count or 0) / 200) | int %}<span>{{ rm if rm > 0 else 1 }} min read</span></div>
        </div>
      </a>
      {% endfor %}
    </div>
  </div></section>
  {%- endif %}

  {%- else %}
  <section class="empty-state"><h2>🚀 Fresh Content Coming Soon</h2><p>We're putting the finishing touches on expert guides across AI, finance, health, tech and more. Subscribe to get notified!</p></section>
  {%- endif %}

  <!-- Tools -->
  <section class="section tools-section"><div class="container">
    <h2 class="section-heading">Tools &amp; Resources</h2>
    <div class="tools-grid">
      <a href="/tools/deal-finder.html" class="tool-card"><div class="tool-icon">🔍</div><h3>Deal Finder</h3><p>Search across top retailers for the best product deals</p></a>
      <a href="/tools/ai-tool-finder.html" class="tool-card"><div class="tool-icon">🤖</div><h3>AI Tool Directory</h3><p>Find the perfect AI tool for any task</p></a>
      <a href="/tools/budget-calculator.html" class="tool-card"><div class="tool-icon">💰</div><h3>Budget Calculator</h3><p>Plan your monthly budget and savings goals</p></a>
      <a href="/tools/workout-generator.html" class="tool-card"><div class="tool-icon">💪</div><h3>Workout Generator</h3><p>Custom workout plans for your goals</p></a>
      <a href="/tools/pet-food-checker.html" class="tool-card"><div class="tool-icon">🐾</div><h3>Pet Food Analyzer</h3><p>Check your pet's food ingredient quality</p></a>
      <a href="/tools/smart-home.html" class="tool-card"><div class="tool-icon">🏠</div><h3>Smart Home Hub</h3><p>Device compatibility checker</p></a>
      <a href="/travel/search.html" class="tool-card"><div class="tool-icon">✈️</div><h3>Travel Search</h3><p>Compare flights, hotels &amp; car rentals</p></a>
      <a href="/personal_finance/markets.html" class="tool-card"><div class="tool-icon">📊</div><h3>Market Data</h3><p>Live stock, crypto &amp; commodity data</p></a>
    </div>
  </div></section>

  <!-- Per-niche sections -->
  {%- if posts|length > 0 %}
  {% set icons = {'ai_tools':'🤖','personal_finance':'💰','health_biohacking':'🧬','home_tech':'🏠','travel':'✈️','pet_care':'🐾','fitness_wellness':'🏋️','remote_work':'💻'} %}
  {% set seen = [] %}
  {% for post in posts %}{% if post.niche_id not in seen and seen.append(post.niche_id) is none %}
  {% set niche_posts = [] %}{% for p in posts if p.niche_id == post.niche_id %}{% if niche_posts.append(p) is none %}{% endif %}{% endfor %}
  {% if niche_posts|length > 0 %}
  <section class="section niche-section"><div class="container">
    <div class="section-header-row"><h2 class="section-heading">{{ icons.get(post.niche_id,'📌') }} {{ post.niche_name }}</h2><a href="/{{ post.niche_id }}/" class="see-all">See all →</a></div>
    <div class="niche-row">{% for p in niche_posts[:3] %}<a href="{{ p.url }}" class="article-card"><div class="card-img"><img src="{{ p.image_url if p.image_url else 'https://picsum.photos/seed/' ~ p.slug ~ '/600/380' }}" alt="{{ p.title }}" loading="lazy"></div><div class="card-body"><h3 class="card-title">{{ p.title }}</h3><div class="card-meta"><span>{{ p.published_at[:10] if p.published_at else '' }}</span><span>·</span>{% set rm = ((p.word_count or 0) / 200) | int %}<span>{{ rm if rm > 0 else 1 }} min read</span></div></div></a>{% endfor %}</div>
  </div></section>
  {% endif %}{% endif %}{% endfor %}
  {%- endif %}

  <!-- Best-of CTA -->
  <div class="container" style="padding-top:16px"><div class="bestof-cta">
    <h3>🏆 Explore Our Top Picks</h3><p>Curated best-of lists across every topic we cover</p>
    <div class="bestof-pills">{% set icons = {'ai_tools':'🤖','personal_finance':'💰','health_biohacking':'🧬','home_tech':'🏠','travel':'✈️','pet_care':'🐾','fitness_wellness':'🏋️','remote_work':'💻'} %}{% for nid, niche in niches.items() %}{% if niche.enabled %}<a href="/{{ nid }}/best-of.html">{{ icons.get(nid,'📌') }} {{ niche.name }}</a>{% endif %}{% endfor %}</div>
  </div></div>

  <!-- Footer -->
  <footer class="footer"><div class="container">
    <div class="footer-grid">
      <div class="footer-brand"><strong>{{ site_title }}</strong>{{ tagline }}. Expert guides, reviews, and insights to help you make smarter decisions.</div>
      <div class="footer-col"><h4>Topics</h4><ul>{% for nid, niche in niches.items() %}{% if niche.enabled %}<li><a href="/{{ nid }}/">{{ niche.name }}</a></li>{% endif %}{% endfor %}</ul></div>
      <div class="footer-col"><h4>Tools</h4><ul><li><a href="/tools/deal-finder.html">Deal Finder</a></li><li><a href="/tools/ai-tool-finder.html">AI Tool Directory</a></li><li><a href="/tools/budget-calculator.html">Budget Calculator</a></li><li><a href="/travel/search.html">Travel Search</a></li><li><a href="/personal_finance/markets.html">Market Data</a></li></ul></div>
      <div class="footer-col"><h4>Company</h4><ul><li><a href="/about.html">About</a></li><li><a href="/contact.html">Contact</a></li><li><a href="/privacy.html">Privacy</a></li><li><a href="/disclaimer.html">Disclaimer</a></li></ul><h4 style="margin-top:20px">Follow Us</h4><ul><li><a href="https://www.youtube.com/@tech-life-insights" target="_blank" rel="noopener">▶ YouTube</a></li><li><a href="https://www.instagram.com/techlife_insights/" target="_blank" rel="noopener">📸 Instagram</a></li><li><a href="https://www.tiktok.com/@techlife_insights" target="_blank" rel="noopener">🎵 TikTok</a></li><li><a href="https://x.com/techlifeinsight" target="_blank" rel="noopener">𝕏 Twitter</a></li></ul></div>
    </div>
    <div class="footer-bottom"><span>&copy; 2026 {{ site_title }}. All rights reserved.</span><span><strong>Disclosure:</strong> Some links are affiliate links. We may earn a commission at no extra cost to you.</span></div>
  </div></footer>

""" + SHARED_SUBSCRIBE_FLOAT + """
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 2. NICHE_INDEX.HTML — With article images
# ═══════════════════════════════════════════════════════════

NICHE_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ niche_name }} — {{ site_title }}</title>
  <meta name="description" content="Expert guides and reviews about {{ niche_name }}. {{ tagline }}">
  <meta property="og:title" content="{{ niche_name }} — {{ site_title }}">
  <link rel="canonical" href="{{ site_url }}/{{ niche_id }}/">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-hover:#1d4ed8; --accent-light:#eff6ff; --border:#e5e7eb; --shadow:0 4px 12px rgba(0,0,0,0.08); --radius:10px; --max-width:1240px; }
    *{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none;transition:color .2s}a:hover{color:var(--accent-hover)}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}img{max-width:100%}
""" + SHARED_NAV_CSS + """
    .breadcrumb{padding:16px 0;font-size:14px;color:var(--text-secondary)}.breadcrumb a{color:var(--text-secondary)}.breadcrumb a:hover{color:var(--accent)}.breadcrumb span{margin:0 6px}
    .page-header{padding:32px 0 24px;border-bottom:1px solid var(--border);margin-bottom:24px}.page-icon{font-size:48px;margin-bottom:12px}.page-header h1{font-size:34px;font-weight:800;line-height:1.2;letter-spacing:-.02em;margin-bottom:6px}.page-header p{font-size:16px;color:var(--text-secondary)}.page-stats{display:flex;gap:20px;margin-top:12px;font-size:14px;color:var(--text-secondary)}.page-stats strong{color:var(--text);font-weight:600}
    .subtopic-bar{display:flex;flex-wrap:wrap;gap:6px;padding:16px 0;border-bottom:1px solid var(--border);margin-bottom:24px}.subtopic-tab{padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);font-size:13px;font-weight:500;font-family:inherit;transition:all .15s;text-decoration:none;display:inline-block}.subtopic-tab:hover,.subtopic-tab.active{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}
    .two-col{display:grid;grid-template-columns:1fr 300px;gap:40px}
    .articles-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;padding-bottom:48px}
    .article-card{display:flex;flex-direction:column;text-decoration:none;color:var(--text);border-radius:var(--radius);overflow:hidden;transition:transform .2s,box-shadow .2s;border:1px solid var(--border)}.article-card:hover{transform:translateY(-3px);box-shadow:var(--shadow);color:var(--text)}.article-card:hover .card-title{color:var(--accent)}.card-img{aspect-ratio:16/10;overflow:hidden;background:var(--surface)}.card-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .3s}.article-card:hover .card-img img{transform:scale(1.04)}.card-body{padding:14px 16px 16px;flex:1;display:flex;flex-direction:column}.card-badge{display:inline-block;font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}.card-title{font-size:15px;font-weight:700;line-height:1.35;margin-bottom:8px;transition:color .2s;flex:1}.card-meta{font-size:12px;color:var(--text-secondary);display:flex;gap:6px;margin-top:auto}
    .sidebar-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:16px}.sidebar-card h3{font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--text-secondary);margin-bottom:12px}.sidebar-card ul{list-style:none}.sidebar-card li{margin-bottom:6px}.sidebar-card li a{font-size:14px;color:var(--text)}.sidebar-card li a:hover{color:var(--accent)}
    .empty-state{text-align:center;padding:80px 24px;color:var(--text-secondary)}.empty-state h2{font-size:24px;color:var(--text);margin-bottom:8px}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:900px){.two-col{grid-template-columns:1fr}.sidebar-card{display:none}}
    @media(max-width:768px){.page-header h1{font-size:26px}.articles-grid{grid-template-columns:1fr}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if nid == niche_id %}") + """

  <div class="container"><div class="breadcrumb"><a href="/">Home</a><span>›</span>{{ niche_name }}</div></div>

  <div class="container">
    <div class="page-header">
      {% set icons = {'ai_tools':'🤖','personal_finance':'💰','health_biohacking':'🧬','home_tech':'🏠','travel':'✈️','pet_care':'🐾','fitness_wellness':'🏋️','remote_work':'💻'} %}
      <div class="page-icon">{{ icons.get(niche_id,'📌') }}</div>
      <h1>{{ niche_name }}</h1>
      <p>Expert guides, reviews, and insights about {{ niche_name | lower }}.</p>
      <div class="page-stats"><span><strong>{{ posts|length }}</strong> article{{ 's' if posts|length != 1 else '' }}</span></div>
    </div>
    {% set current_niche = niches.get(niche_id, {}) %}
    {% if current_niche.subtopics %}
    <div class="subtopic-bar">
      <a href="/{{ niche_id }}/" class="subtopic-tab active">All</a>
      {% for sub_id, sub in current_niche.subtopics.items() %}<a href="/{{ niche_id }}/{{ sub_id }}/" class="subtopic-tab">{{ sub.name }}</a>{% endfor %}
    </div>
    {% endif %}
  </div>

  <div class="container">
    <div class="two-col">
      <main>
        {% if posts|length > 0 %}
        <div class="articles-grid">
          {% for post in posts %}
          <a href="{{ post.url }}" class="article-card">
            <div class="card-img"><img src="{{ post.image_url if post.image_url else 'https://picsum.photos/seed/' ~ post.slug ~ '/600/380' }}" alt="{{ post.title }}" loading="lazy"></div>
            <div class="card-body">
              {% if post.subtopic_id %}<span class="card-badge">{{ post.subtopic_id | replace('_',' ') | title }}</span>{% endif %}
              <h3 class="card-title">{{ post.title }}</h3>
              <div class="card-meta"><span>{{ post.published_at[:10] if post.published_at else '' }}</span><span>·</span>{% set rm = ((post.word_count or 0) / 200) | int %}<span>{{ rm if rm > 0 else 1 }} min read</span></div>
            </div>
          </a>
          {% endfor %}
        </div>
        {% else %}
        <div class="empty-state"><h2>🚀 Articles Coming Soon</h2><p>Expert guides on {{ niche_name | lower }} publish regularly — check back soon!</p></div>
        {% endif %}
      </main>
      <aside>
        <div class="sidebar-card"><h3>⭐ Best Of</h3><ul><li><a href="/{{ niche_id }}/best-of.html">Best of {{ niche_name }}</a></li></ul></div>
        <div class="sidebar-card"><h3>🛠️ Tools</h3><ul><li><a href="/tools/deal-finder.html">🔍 Deal Finder</a></li><li><a href="/tools/ai-tool-finder.html">🤖 AI Tool Directory</a></li><li><a href="/tools/budget-calculator.html">💰 Budget Calculator</a></li></ul></div>
        <div class="sidebar-card"><h3>Other Topics</h3><ul>{% set icons = {'ai_tools':'🤖','personal_finance':'💰','health_biohacking':'🧬','home_tech':'🏠','travel':'✈️','pet_care':'🐾','fitness_wellness':'🏋️','remote_work':'💻'} %}{% for nid, niche in niches.items() %}{% if niche.enabled and nid != niche_id %}<li><a href="/{{ nid }}/">{{ icons.get(nid,'📌') }} {{ niche.name }}</a></li>{% endif %}{% endfor %}</ul></div>
      </aside>
    </div>
  </div>

  <footer class="footer"><div class="container"><span>&copy; 2026 {{ site_title }}.</span> · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/contact.html">Contact</a><div style="margin-top:8px;font-size:12px;color:rgba(255,255,255,.4)"><strong>Disclosure:</strong> Some links are affiliate links. We may earn a commission at no extra cost to you.</div></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 3. SUBTOPIC_INDEX.HTML — With article images
# ═══════════════════════════════════════════════════════════

SUBTOPIC_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ subtopic_name }} — {{ niche_name }} | {{ site_title }}</title>
  <meta name="description" content="Expert {{ subtopic_name | lower }} guides and articles. {{ tagline }}">
  <link rel="canonical" href="{{ site_url }}/{{ niche_id }}/{{ subtopic_id }}/">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-hover:#1d4ed8; --accent-light:#eff6ff; --border:#e5e7eb; --shadow:0 4px 12px rgba(0,0,0,0.08); --radius:10px; --max-width:1240px; }
    *{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none;transition:color .2s}a:hover{color:var(--accent-hover)}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}img{max-width:100%}
""" + SHARED_NAV_CSS + """
    .breadcrumb{padding:16px 0;font-size:14px;color:var(--text-secondary)}.breadcrumb a{color:var(--text-secondary)}.breadcrumb a:hover{color:var(--accent)}.breadcrumb span{margin:0 6px}
    .page-header{padding:32px 0 24px;border-bottom:1px solid var(--border);margin-bottom:24px}.page-header h1{font-size:32px;font-weight:800;line-height:1.2;letter-spacing:-.02em;margin-bottom:6px}.page-header p{font-size:16px;color:var(--text-secondary)}
    .subtopic-bar{display:flex;flex-wrap:wrap;gap:6px;padding:16px 0;border-bottom:1px solid var(--border);margin-bottom:24px}.subtopic-tab{padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);font-size:13px;font-weight:500;font-family:inherit;transition:all .15s;text-decoration:none;display:inline-block}.subtopic-tab:hover,.subtopic-tab.active{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}
    .articles-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;padding-bottom:48px}
    .article-card{display:flex;flex-direction:column;text-decoration:none;color:var(--text);border-radius:var(--radius);overflow:hidden;transition:transform .2s,box-shadow .2s;border:1px solid var(--border)}.article-card:hover{transform:translateY(-3px);box-shadow:var(--shadow);color:var(--text)}.article-card:hover .card-title{color:var(--accent)}.card-img{aspect-ratio:16/10;overflow:hidden;background:var(--surface)}.card-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .3s}.article-card:hover .card-img img{transform:scale(1.04)}.card-body{padding:14px 16px 16px;flex:1;display:flex;flex-direction:column}.card-title{font-size:15px;font-weight:700;line-height:1.35;margin-bottom:8px;transition:color .2s;flex:1}.card-meta{font-size:12px;color:var(--text-secondary);display:flex;gap:6px;margin-top:auto}
    .empty-state{text-align:center;padding:80px 24px;color:var(--text-secondary)}.empty-state h2{font-size:24px;color:var(--text);margin-bottom:8px}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.page-header h1{font-size:24px}.articles-grid{grid-template-columns:1fr}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if nid == niche_id %}") + """

  <div class="container"><div class="breadcrumb"><a href="/">Home</a><span>›</span><a href="/{{ niche_id }}/">{{ niche_name }}</a><span>›</span>{{ subtopic_name }}</div></div>

  <div class="container">
    <div class="page-header">
      {% set icons = {'ai_tools':'🤖','personal_finance':'💰','health_biohacking':'🧬','home_tech':'🏠','travel':'✈️','pet_care':'🐾','fitness_wellness':'🏋️','remote_work':'💻'} %}
      <div style="font-size:36px;margin-bottom:12px">{{ icons.get(niche_id,'📌') }}</div>
      <h1>{{ subtopic_name }}</h1>
      <p>{{ posts|length }} article{{ 's' if posts|length != 1 else '' }} about {{ subtopic_name | lower }}</p>
    </div>
    {% set current_niche = niches.get(niche_id, {}) %}
    {% if current_niche.subtopics %}
    <div class="subtopic-bar">
      <a href="/{{ niche_id }}/" class="subtopic-tab">All {{ niche_name }}</a>
      {% for sub_id, sub in current_niche.subtopics.items() %}<a href="/{{ niche_id }}/{{ sub_id }}/" class="subtopic-tab{% if sub_id == subtopic_id %} active{% endif %}">{{ sub.name }}</a>{% endfor %}
    </div>
    {% endif %}
  </div>

  <div class="container">
    {% if posts|length > 0 %}
    <div class="articles-grid">
      {% for post in posts %}
      <a href="{{ post.url }}" class="article-card">
        <div class="card-img"><img src="{{ post.image_url if post.image_url else 'https://picsum.photos/seed/' ~ post.slug ~ '/600/380' }}" alt="{{ post.title }}" loading="lazy"></div>
        <div class="card-body">
          <h3 class="card-title">{{ post.title }}</h3>
          <div class="card-meta"><span>{{ post.published_at[:10] if post.published_at else '' }}</span><span>·</span>{% set rm = ((post.word_count or 0) / 200) | int %}<span>{{ rm if rm > 0 else 1 }} min read</span></div>
        </div>
      </a>
      {% endfor %}
    </div>
    {% else %}
    <div class="empty-state"><h2>🚀 Articles Coming Soon</h2><p>Expert guides about {{ subtopic_name | lower }} coming soon!</p></div>
    {% endif %}
  </div>

  <footer class="footer"><div class="container"><span>&copy; 2026 {{ site_title }}.</span> · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/contact.html">Contact</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 4. POST.HTML — Updated with Tools nav, floating subscribe
# ═══════════════════════════════════════════════════════════

POST_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {{ article.meta_html | safe }}
  {{ article.schema_markup | safe }}
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Merriweather:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#18181b; --text-muted:#71717a; --accent:#2563eb; --accent-light:#eff6ff; --green:#059669; --green-bg:#ecfdf5; --amber:#92400e; --amber-bg:#fffbeb; --amber-border:#fde68a; --border:#e4e4e7; --max-width:760px; --radius:12px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Merriweather',Georgia,serif;font-size:17px;line-height:1.8;-webkit-font-smoothing:antialiased}a{color:var(--accent)}a:hover{text-decoration:underline}img{max-width:100%}

    .nav{position:sticky;top:0;z-index:50;backdrop-filter:blur(16px);background:#1e3a8a;border-bottom:1px solid rgba(255,255,255,.1);font-family:'Inter',sans-serif}
    .nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:12px 24px}
    .nav-logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--text);font-weight:800;font-size:18px}
    .nav-links{display:flex;gap:2px;align-items:center}
    .nav-link{padding:6px 11px;border-radius:6px;font-size:13px;font-weight:500;color:rgba(255,255,255,.75);text-decoration:none;transition:all .15s;white-space:nowrap}
    .nav-link:hover,.nav-link.active{color:#fff;background:rgba(255,255,255,.12);text-decoration:none}
    .nav-item{position:relative;display:inline-block}
    .nav-item:hover .nav-dropdown{display:block}
    .nav-dropdown{display:none;position:absolute;top:100%;left:0;background:#fff;border:1px solid #e5e7eb;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.12);min-width:210px;padding:6px 0;z-index:100}
    .nav-dropdown a{display:block;padding:8px 16px;font-size:13px;color:#18181b;font-weight:500;transition:background .1s;text-decoration:none}
    .nav-dropdown a:hover{background:#eff6ff;color:#2563eb}
    .mobile-toggle{display:none;background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:6px}

    .ftc-banner{background:var(--amber-bg);border-bottom:1px solid var(--amber-border);padding:10px 24px;text-align:center;font-family:'Inter',sans-serif;font-size:13px;color:var(--amber)}
    .container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
    .article-header{padding:48px 0 36px}
    .article-meta{display:flex;align-items:center;gap:12px;margin-bottom:16px;font-family:'Inter',sans-serif;font-size:13px;color:var(--text-muted)}
    .niche-badge{display:inline-block;background:var(--accent-light);color:var(--accent);padding:4px 12px;border-radius:20px;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
    .article-title{font-size:2.4em;line-height:1.2;font-weight:700;color:var(--text);letter-spacing:-.02em}
    .article-body{padding-bottom:48px}
    .article-body h1{font-size:1.8em;margin:40px 0 16px;letter-spacing:-.01em}
    .article-body h2{font-size:1.4em;margin:40px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--border);letter-spacing:-.01em}
    .article-body h3{font-size:1.2em;margin:32px 0 10px}
    .article-body p{margin-bottom:22px}
    .article-body ul,.article-body ol{margin:16px 0 22px 28px}
    .article-body li{margin-bottom:8px}
    .article-body code{background:var(--surface);padding:2px 6px;border-radius:4px;font-size:.88em;font-family:'SFMono-Regular',Consolas,monospace;border:1px solid var(--border)}
    .article-body strong{font-weight:700}
    .article-body blockquote{border-left:4px solid var(--accent);padding:12px 20px;margin:24px 0;background:var(--accent-light);border-radius:0 var(--radius) var(--radius) 0;font-style:italic;color:var(--text-muted)}
    .article-body .ftc-disclosure{background:var(--amber-bg);border:1px solid var(--amber-border);padding:14px 18px;border-radius:var(--radius);margin:24px 0;font-size:.85em;font-family:'Inter',sans-serif;color:var(--amber)}
    .article-body .faq-question{font-weight:700;margin-top:24px;margin-bottom:6px;font-family:'Inter',sans-serif}
    .article-body .faq-answer{margin-bottom:20px;margin-left:16px}
    .article-body a[rel~="nofollow"]{color:var(--accent);font-weight:600;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px}
    .article-body a[rel~="nofollow"]:hover{text-decoration-style:solid}
    .related{margin:48px 0 60px}.related h3{font-family:'Inter',sans-serif;font-size:20px;font-weight:800;margin-bottom:20px}
    .related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
    .related-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px;text-decoration:none;color:var(--text);transition:all .2s;display:block}
    .related-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.06);text-decoration:none}
    .related-card-niche{font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;font-family:'Inter',sans-serif}
    .related-card-title{font-size:14px;font-weight:600;line-height:1.4;font-family:'Inter',sans-serif}
    .footer{background:var(--surface);border-top:1px solid var(--border);padding:40px 24px;margin-top:40px;font-family:'Inter',sans-serif;font-size:13px;color:var(--text-muted);text-align:center}
    .footer-disclaimer{max-width:600px;margin:0 auto;line-height:1.7}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){
      .nav-links{display:none}
      .nav-links.open{display:flex;flex-direction:column;position:absolute;top:100%;left:0;right:0;background:#1e3a8a;padding:12px 24px;border-top:1px solid rgba(255,255,255,.1);gap:4px;z-index:200}
      .nav-links.open .nav-item{display:block}
      .nav-links.open .nav-dropdown{position:static;box-shadow:none;border:none;background:rgba(255,255,255,.05);border-radius:6px;margin:4px 0}
      .nav-links.open .nav-dropdown a{color:rgba(255,255,255,.7)}
      .mobile-toggle{display:block}
    }
    @media(max-width:640px){.article-title{font-size:1.6em}.container{padding:0 16px}.related-grid{grid-template-columns:1fr}.article-header{padding:32px 0 24px}}
  </style>
</head>
<body>

  <nav class="nav">
    <div class="nav-inner">
      <a href="/" class="nav-logo"><img src="/assets/logo-full-dark.svg" alt="TechLife Insights" style="height:44px;width:auto;"></a>
      <div class="nav-links" id="navLinks">
        <a href="/" class="nav-link">Home</a>
        {% if niches %}{% for nid, niche in niches.items() %}{% if niche.enabled %}
        <div class="nav-item">
          <a href="/{{ nid }}/" class="nav-link{% if nid == niche_id %} active{% endif %}">{{ niche.name }}</a>
          {% if niche.subtopics %}<div class="nav-dropdown">{% for sub_id, sub in niche.subtopics.items() %}<a href="/{{ nid }}/{{ sub_id }}/">{{ sub.name }}</a>{% endfor %}</div>{% endif %}
        </div>
        {% endif %}{% endfor %}{% endif %}
        <div class="nav-item">
          <a href="/tools/" class="nav-link">🛠️ Tools</a>
          <div class="nav-dropdown">
            <a href="/tools/deal-finder.html">🔍 Deal Finder</a>
            <a href="/tools/ai-tool-finder.html">🤖 AI Tool Directory</a>
            <a href="/tools/budget-calculator.html">💰 Budget Calculator</a>
            <a href="/tools/workout-generator.html">💪 Workout Generator</a>
            <a href="/tools/pet-food-checker.html">🐾 Pet Food Analyzer</a>
            <a href="/tools/smart-home.html">🏠 Smart Home Hub</a>
            <a href="/travel/search.html">✈️ Travel Search</a>
            <a href="/personal_finance/markets.html">📊 Market Data</a>
          </div>
        </div>
      </div>
      <button class="mobile-toggle" onclick="document.getElementById('navLinks').classList.toggle('open')" aria-label="Menu">☰</button>
    </div>
  </nav>

  <div class="ftc-banner">⚠️ <strong>Disclosure:</strong> This article contains affiliate links. We may earn a commission at no extra cost to you.</div>

  <div class="container">
    <header class="article-header">
      <div class="article-meta">
        <span class="niche-badge">{{ niche_name }}</span>
        {% if article.subtopic_id and niches and niches[niche_id] and niches[niche_id].subtopics and article.subtopic_id in niches[niche_id].subtopics %}
        <span style="font-size:12px;color:var(--text-muted)">›</span>
        <a href="/{{ niche_id }}/{{ article.subtopic_id }}/" style="font-size:12px;font-weight:600;color:var(--accent);text-decoration:none">{{ niches[niche_id].subtopics[article.subtopic_id].name }}</a>
        {% endif %}
        <span>{{ published_at[:10] if published_at else '' }}</span>
      </div>
      <h1 class="article-title">{{ article.title }}</h1>
    </header>

    {% if article.image_url %}
    <div style="margin:0 0 40px"><img src="{{ article.image_url }}" alt="{{ article.title }}" loading="lazy" style="width:100%;border-radius:var(--radius);max-height:420px;object-fit:cover;display:block"></div>
    {% endif %}

    <article class="article-body">{{ article.html_content | safe }}</article>

    <div style="background:var(--accent-light);border:1px solid #bfdbfe;border-radius:var(--radius);padding:24px 28px;margin:40px 0;font-family:'Inter',sans-serif;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
      <div><div style="font-weight:700;font-size:15px;color:var(--accent);margin-bottom:4px">📚 Explore More {{ niche_name }} Guides</div><div style="font-size:14px;color:#3b5fb5">Browse all articles in this category</div></div>
      <a href="/{{ niche_id }}/" style="background:var(--accent);color:#fff;text-decoration:none;padding:10px 20px;border-radius:8px;font-size:14px;font-weight:600;white-space:nowrap">Browse {{ niche_name }} →</a>
    </div>

    {% if related_posts %}
    <section class="related">
      <h3>You might also like</h3>
      <div class="related-grid">
        {% for post in related_posts[:6] %}
        <a href="{{ post.url }}" class="related-card">
          <div class="related-card-niche">{{ post.niche_name }}</div>
          <div class="related-card-title">{{ post.title }}</div>
        </a>
        {% endfor %}
      </div>
    </section>
    {% endif %}
  </div>

  <footer class="footer">
    <div class="footer-disclaimer"><strong>Affiliate Disclosure:</strong> We participate in various affiliate programs and may earn commissions when you purchase through our links. This does not affect our editorial independence or your purchase price.</div>
    {% if niches %}<div style="margin-top:16px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap">{% for nid, niche in niches.items() %}{% if niche.enabled %}<a href="/{{ nid }}/" class="nav-link" style="font-size:13px;color:var(--text-muted)">{{ niche.name }}</a>{% endif %}{% endfor %}</div>{% endif %}
    <div style="margin-top:12px;display:flex;gap:12px;justify-content:center;font-size:13px"><a href="/privacy.html" style="color:var(--text-muted)">Privacy</a><span style="color:var(--text-muted)">·</span><a href="/about.html" style="color:var(--text-muted)">About</a><span style="color:var(--text-muted)">·</span><a href="/contact.html" style="color:var(--text-muted)">Contact</a><span style="color:var(--text-muted)">·</span><a href="https://www.youtube.com/@tech-life-insights" target="_blank" rel="noopener" style="color:var(--text-muted)">▶ YouTube</a><span style="color:var(--text-muted)">·</span><a href="https://www.instagram.com/techlife_insights/" target="_blank" rel="noopener" style="color:var(--text-muted)">📸 Instagram</a><span style="color:var(--text-muted)">·</span><a href="https://www.tiktok.com/@techlife_insights" target="_blank" rel="noopener" style="color:var(--text-muted)">🎵 TikTok</a><span style="color:var(--text-muted)">·</span><a href="https://x.com/techlifeinsight" target="_blank" rel="noopener" style="color:var(--text-muted)">𝕏 Twitter</a></div>
    <p style="margin-top:16px">&copy; 2026 {{ settings.site.title if settings and settings.site else 'TechLife Insights' }}. All rights reserved.</p>
  </footer>

""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  (function(){
    var affiliateDomains=['amazon.com','amzn.to','shareasale.com','anrdoezrs.net','tkqlhce.com','jdoqocy.com','dpbolvw.net','kqzyfj.com','commission-junction.com'];
    var slug='{{ article.slug | default("") }}';var niche='{{ niche_id | default("") }}';
    document.addEventListener('click',function(e){var link=e.target.closest('a[href]');if(!link)return;var href=link.getAttribute('href')||'';if(!href.startsWith('http'))return;var isAffiliate=link.getAttribute('rel')&&link.getAttribute('rel').indexOf('nofollow')!==-1;if(!isAffiliate){for(var i=0;i<affiliateDomains.length;i++){if(href.indexOf(affiliateDomains[i])!==-1){isAffiliate=true;break}}}if(isAffiliate){var img=new Image();img.src='/track?url='+encodeURIComponent(href)+'&slug='+encodeURIComponent(slug)+'&niche='+encodeURIComponent(niche);if(navigator.sendBeacon){navigator.sendBeacon('/track?url='+encodeURIComponent(href)+'&slug='+encodeURIComponent(slug)+'&niche='+encodeURIComponent(niche))}}});
  })();
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 5. TOOLS INDEX
# ═══════════════════════════════════════════════════════════

TOOLS_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Free Tools & Resources — {{ site_title }}</title>
  <meta name="description" content="Free tools to help you save money, stay healthy, and make smarter decisions. Deal finder, AI tool directory, budget calculator, and more.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-hover:#1d4ed8; --accent-light:#eff6ff; --border:#e5e7eb; --shadow:0 4px 12px rgba(0,0,0,0.08); --radius:10px; --max-width:1240px; }
    *{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
""" + SHARED_NAV_CSS + """
    .page-hero{background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);color:#fff;padding:56px 0;text-align:center}
    .page-hero h1{font-size:36px;font-weight:900;margin-bottom:10px;letter-spacing:-.02em}
    .page-hero p{font-size:18px;opacity:.85;max-width:560px;margin:0 auto}
    .tools-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:48px 0}
    .tool-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:32px 24px;text-decoration:none;color:var(--text);transition:all .25s;text-align:center;display:block}
    .tool-card:hover{border-color:var(--accent);box-shadow:0 8px 30px rgba(37,99,235,.15);transform:translateY(-4px);color:var(--text)}
    .tool-icon{font-size:48px;margin-bottom:16px}
    .tool-card h2{font-size:18px;font-weight:700;margin-bottom:8px}
    .tool-card p{font-size:14px;color:var(--text-secondary);line-height:1.6}
    .tool-tag{display:inline-block;background:var(--accent-light);color:var(--accent);padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;margin-top:12px}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.tools-grid{grid-template-columns:1fr}.page-hero h1{font-size:28px}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="page-hero"><div class="container">
    <h1>🛠️ Free Tools & Resources</h1>
    <p>Powerful tools to help you save money, stay productive, and make smarter decisions — completely free.</p>
  </div></div>

  <div class="container">
    <div class="tools-grid">
      <a href="/tools/deal-finder.html" class="tool-card"><div class="tool-icon">🔍</div><h2>Deal Finder</h2><p>Search across Amazon, Best Buy, Walmart, and more to find the best deals on any product.</p><span class="tool-tag">Shopping</span></a>
      <a href="/tools/ai-tool-finder.html" class="tool-card"><div class="tool-icon">🤖</div><h2>AI Tool Directory</h2><p>Browse 60+ AI tools organized by category — writing, images, code, video, and more.</p><span class="tool-tag">AI & Tech</span></a>
      <a href="/tools/budget-calculator.html" class="tool-card"><div class="tool-icon">💰</div><h2>Budget Calculator</h2><p>Plan your monthly budget with the 50/30/20 rule and track your savings goals.</p><span class="tool-tag">Finance</span></a>
      <a href="/tools/workout-generator.html" class="tool-card"><div class="tool-icon">💪</div><h2>Workout Generator</h2><p>Generate custom workout plans based on your fitness goals, equipment, and available time.</p><span class="tool-tag">Fitness</span></a>
      <a href="/tools/pet-food-checker.html" class="tool-card"><div class="tool-icon">🐾</div><h2>Pet Food Analyzer</h2><p>Check ingredient quality and get safety ratings for your pet's food.</p><span class="tool-tag">Pet Care</span></a>
      <a href="/tools/smart-home.html" class="tool-card"><div class="tool-icon">🏠</div><h2>Smart Home Hub</h2><p>Check device compatibility across Alexa, Google Home, and Apple HomeKit ecosystems.</p><span class="tool-tag">Home Tech</span></a>
      <a href="/travel/search.html" class="tool-card"><div class="tool-icon">✈️</div><h2>Travel Search</h2><p>Compare flights, hotels, and car rentals from top travel booking platforms.</p><span class="tool-tag">Travel</span></a>
      <a href="/personal_finance/markets.html" class="tool-card"><div class="tool-icon">📊</div><h2>Market Data</h2><p>Real-time stock market, cryptocurrency, and commodity price data.</p><span class="tool-tag">Finance</span></a>
    </div>
  </div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/contact.html">Contact</a><br><span style="font-size:11px;color:rgba(255,255,255,.35)">Some links are affiliate links. We may earn a commission at no extra cost to you.</span></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 6. DEAL FINDER TOOL
# ═══════════════════════════════════════════════════════════

DEAL_FINDER_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deal Finder — Search for the Best Deals | {{ site_title }}</title>
  <meta name="description" content="Search across Amazon, Best Buy, Walmart, Target and more to find the best deals on any product. Free deal comparison tool.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-hover:#1d4ed8; --accent-light:#eff6ff; --border:#e5e7eb; --radius:10px; --max-width:900px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}img{max-width:100%}
""" + SHARED_NAV_CSS + """
    .tool-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:#fff;padding:48px 0;text-align:center}
    .tool-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.tool-hero p{font-size:16px;opacity:.8;max-width:500px;margin:0 auto 28px}
    .search-box{max-width:600px;margin:0 auto;display:flex;gap:0;border-radius:50px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.3)}
    .search-box input{flex:1;padding:16px 24px;border:none;font-size:16px;font-family:inherit;outline:none}
    .search-box button{background:var(--accent);color:#fff;border:none;padding:16px 28px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:background .2s}
    .search-box button:hover{background:var(--accent-hover)}
    .results{padding:40px 0}.results h2{font-size:20px;font-weight:800;margin-bottom:20px;text-align:center}
    .retailer-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
    .retailer-card{border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center;transition:all .2s;text-decoration:none;color:var(--text);display:block}
    .retailer-card:hover{border-color:var(--accent);box-shadow:0 4px 16px rgba(37,99,235,.12);transform:translateY(-2px);color:var(--text)}
    .retailer-logo{font-size:36px;margin-bottom:8px}
    .retailer-card h3{font-size:15px;font-weight:700;margin-bottom:4px}
    .retailer-card p{font-size:12px;color:var(--text-secondary)}
    .search-btn{display:inline-block;background:var(--accent);color:#fff;padding:8px 18px;border-radius:6px;font-size:13px;font-weight:600;margin-top:10px;transition:background .2s}
    .search-btn:hover{background:var(--accent-hover);color:#fff}
    #noQuery{display:none;text-align:center;padding:20px;color:var(--text-secondary);font-size:14px}
    .categories{padding:32px 0}.categories h2{font-size:20px;font-weight:800;margin-bottom:20px}
    .cat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
    .cat-pill{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px;text-align:center;cursor:pointer;transition:all .15s;font-size:13px;font-weight:600}
    .cat-pill:hover{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
    .cat-pill span{display:block;font-size:24px;margin-bottom:4px}
    .tips{padding:32px 0;border-top:1px solid var(--border)}.tips h2{font-size:20px;font-weight:800;margin-bottom:16px}
    .tip-item{padding:12px 0;border-bottom:1px solid var(--border);font-size:14px}
    .tip-item strong{color:var(--accent)}
    .disclaimer{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-top:32px;font-size:12px;color:var(--text-secondary);line-height:1.7}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.retailer-grid{grid-template-columns:1fr 1fr}.cat-grid{grid-template-columns:1fr 1fr}.tool-hero h1{font-size:24px}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="tool-hero">
    <h1>🔍 Deal Finder</h1>
    <p>Search across top retailers to find the best deals on any product</p>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="What are you looking for? e.g. wireless headphones" autofocus>
      <button onclick="searchDeals()">Search Deals</button>
    </div>
  </div>

  <div class="container">
    <div id="noQuery"><p>Enter a product above to search across retailers</p></div>
    <div class="results" id="results" style="display:none">
      <h2>Search "<span id="queryDisplay"></span>" on these retailers:</h2>
      <div class="retailer-grid" id="retailerGrid"></div>
    </div>

    <div class="categories">
      <h2>Popular Categories</h2>
      <div class="cat-grid">
        <div class="cat-pill" onclick="quickSearch('wireless headphones')"><span>🎧</span>Headphones</div>
        <div class="cat-pill" onclick="quickSearch('laptop deals')"><span>💻</span>Laptops</div>
        <div class="cat-pill" onclick="quickSearch('smart home devices')"><span>🏠</span>Smart Home</div>
        <div class="cat-pill" onclick="quickSearch('fitness tracker')"><span>⌚</span>Fitness Tech</div>
        <div class="cat-pill" onclick="quickSearch('kitchen appliances')"><span>🍳</span>Kitchen</div>
        <div class="cat-pill" onclick="quickSearch('gaming accessories')"><span>🎮</span>Gaming</div>
        <div class="cat-pill" onclick="quickSearch('pet supplies')"><span>🐾</span>Pet Supplies</div>
        <div class="cat-pill" onclick="quickSearch('home office desk')"><span>🪑</span>Office</div>
      </div>
    </div>

    <div class="tips">
      <h2>💡 Smart Shopping Tips</h2>
      <div class="tip-item"><strong>Compare prices</strong> across at least 3 retailers before buying — prices can vary by 20-40%.</div>
      <div class="tip-item"><strong>Check for coupons</strong> — search "[retailer name] coupon code" before checkout.</div>
      <div class="tip-item"><strong>Set price alerts</strong> — tools like CamelCamelCamel (Amazon) track price history.</div>
      <div class="tip-item"><strong>Buy refurbished</strong> — certified refurbished products offer 20-50% savings with warranties.</div>
      <div class="tip-item"><strong>Time your purchases</strong> — Black Friday, Prime Day, and end-of-season sales offer the best deals.</div>
    </div>

    <div class="disclaimer">
      <strong>Affiliate Disclosure:</strong> Some retailer links on this page are affiliate links. When you click through and make a purchase, we may earn a small commission at no additional cost to you. This helps support our free tools and content. We are not affiliated with or endorsed by any of the retailers listed. Prices, availability, and deals are determined by the retailers and may change at any time.
    </div>
  </div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  var retailers = [
    { name: 'Amazon', icon: '📦', color: '#FF9900', search: 'https://www.amazon.com/s?k=QUERY&tag=techlife0ac-20', desc: 'Millions of products with Prime shipping' },
    { name: 'Best Buy', icon: '🏪', color: '#0046BE', search: 'https://www.bestbuy.com/site/searchpage.jsp?st=QUERY', desc: 'Electronics, appliances & tech deals' },
    { name: 'Walmart', icon: '🛒', color: '#0071DC', search: 'https://www.walmart.com/search?q=QUERY', desc: 'Everyday low prices on everything' },
    { name: 'Target', icon: '🎯', color: '#CC0000', search: 'https://www.target.com/s?searchTerm=QUERY', desc: 'Quality products at great prices' },
    { name: 'Newegg', icon: '💾', color: '#E76F00', search: 'https://www.newegg.com/p/pl?d=QUERY', desc: 'Tech & computer hardware specialist' },
    { name: 'eBay', icon: '🏷️', color: '#E53238', search: 'https://www.ebay.com/sch/i.html?_nkw=QUERY', desc: 'New, used & refurbished deals' },
    { name: 'B&H Photo', icon: '📷', color: '#000', search: 'https://www.bhphotovideo.com/c/search?q=QUERY', desc: 'Camera, audio & electronics pro gear' },
    { name: 'Costco', icon: '🏬', color: '#E31837', search: 'https://www.costco.com/CatalogSearch?dept=All&keyword=QUERY', desc: 'Bulk deals for members' },
    { name: 'Google Shopping', icon: '🔎', color: '#4285F4', search: 'https://www.google.com/search?tbm=shop&q=QUERY', desc: 'Compare prices across all stores' }
  ];

  function searchDeals() {
    var q = document.getElementById('searchInput').value.trim();
    if (!q) { document.getElementById('noQuery').style.display = 'block'; document.getElementById('results').style.display = 'none'; return; }
    document.getElementById('noQuery').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    document.getElementById('queryDisplay').textContent = q;
    var grid = document.getElementById('retailerGrid');
    grid.innerHTML = '';
    retailers.forEach(function(r) {
      var url = r.search.replace('QUERY', encodeURIComponent(q));
      var card = document.createElement('a');
      card.href = url; card.target = '_blank'; card.rel = 'noopener'; card.className = 'retailer-card';
      card.innerHTML = '<div class="retailer-logo">' + r.icon + '</div><h3>' + r.name + '</h3><p>' + r.desc + '</p><span class="search-btn">Search ' + r.name + ' →</span>';
      grid.appendChild(card);
    });
  }

  function quickSearch(q) {
    document.getElementById('searchInput').value = q;
    searchDeals();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  document.getElementById('searchInput').addEventListener('keypress', function(e) { if (e.key === 'Enter') searchDeals(); });
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 7. AI TOOL FINDER
# ═══════════════════════════════════════════════════════════

AI_TOOL_FINDER_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Tool Directory — Find the Best AI Tools | {{ site_title }}</title>
  <meta name="description" content="Browse 60+ AI tools organized by category. Find the perfect AI tool for writing, image generation, coding, video, and more.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-light:#eff6ff; --border:#e5e7eb; --radius:10px; --max-width:1100px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
""" + SHARED_NAV_CSS + """
    .page-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.8;max-width:500px;margin:0 auto 20px}
    .search-wrap{max-width:500px;margin:0 auto}.search-wrap input{width:100%;padding:14px 20px;border-radius:50px;border:none;font-size:15px;font-family:inherit;outline:none;box-shadow:0 4px 20px rgba(0,0,0,.3)}
    .filters{display:flex;flex-wrap:wrap;gap:8px;padding:24px 0;justify-content:center;border-bottom:1px solid var(--border)}
    .filter-btn{padding:7px 16px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
    .filter-btn:hover,.filter-btn.active{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}
    .tools-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:32px 0}
    .ai-card{border:1px solid var(--border);border-radius:var(--radius);padding:20px;transition:all .2s}
    .ai-card:hover{border-color:var(--accent);box-shadow:0 4px 16px rgba(37,99,235,.1)}
    .ai-card h3{font-size:16px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:8px}
    .ai-card .cat-tag{font-size:11px;font-weight:600;color:var(--accent);background:var(--accent-light);padding:2px 8px;border-radius:10px}
    .ai-card p{font-size:13px;color:var(--text-secondary);margin:8px 0}
    .ai-card .pricing{font-size:12px;font-weight:600;color:#059669}
    .ai-card .visit-btn{display:inline-block;margin-top:10px;background:var(--accent);color:#fff;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;transition:background .2s}
    .ai-card .visit-btn:hover{background:var(--accent-hover);color:#fff}
    .tool-count{text-align:center;padding:8px 0;font-size:13px;color:var(--text-secondary)}
    .disclaimer{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin:24px 0;font-size:12px;color:var(--text-secondary);line-height:1.7}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.tools-grid{grid-template-columns:1fr}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="page-hero">
    <h1>🤖 AI Tool Directory</h1>
    <p>Find the perfect AI tool for any task — over 60 tools organized by category</p>
    <div class="search-wrap"><input type="text" id="searchInput" placeholder="Search AI tools..." oninput="filterTools()"></div>
  </div>

  <div class="container">
    <div class="filters" id="filters"></div>
    <div class="tool-count" id="toolCount"></div>
    <div class="tools-grid" id="toolsGrid"></div>
    <div class="disclaimer"><strong>Disclaimer:</strong> This directory is curated for informational purposes. We are not affiliated with these tools unless noted. Some links may be affiliate links. Pricing and features may change — always verify on the official website. Our inclusion of a tool does not constitute an endorsement.</div>
  </div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  var aiTools = [
    {name:'ChatGPT',cat:'Writing',desc:'Conversational AI for writing, analysis, coding, and creative tasks.',pricing:'Free / $20/mo',url:'https://chat.openai.com'},
    {name:'Claude',cat:'Writing',desc:'Anthropic\'s AI assistant for thoughtful, nuanced writing and analysis.',pricing:'Free / $20/mo',url:'https://claude.ai'},
    {name:'Gemini',cat:'Writing',desc:'Google\'s multimodal AI for text, images, and code generation.',pricing:'Free / $20/mo',url:'https://gemini.google.com'},
    {name:'Jasper',cat:'Writing',desc:'AI writing platform for marketing copy, blogs, and social media.',pricing:'From $49/mo',url:'https://www.jasper.ai'},
    {name:'Copy.ai',cat:'Writing',desc:'Generate marketing copy, emails, and social posts with AI.',pricing:'Free / $49/mo',url:'https://www.copy.ai'},
    {name:'Writesonic',cat:'Writing',desc:'AI writer for SEO articles, ad copy, and product descriptions.',pricing:'Free / $16/mo',url:'https://writesonic.com'},
    {name:'Grammarly',cat:'Writing',desc:'AI writing assistant for grammar, tone, and clarity.',pricing:'Free / $12/mo',url:'https://www.grammarly.com'},
    {name:'QuillBot',cat:'Writing',desc:'AI paraphrasing and summarization tool for better writing.',pricing:'Free / $10/mo',url:'https://quillbot.com'},
    {name:'Midjourney',cat:'Images',desc:'Create stunning AI art and images from text prompts.',pricing:'From $10/mo',url:'https://www.midjourney.com'},
    {name:'DALL-E 3',cat:'Images',desc:'OpenAI\'s image generator — create art, photos, and designs.',pricing:'Included with ChatGPT Plus',url:'https://openai.com/dall-e-3'},
    {name:'Stable Diffusion',cat:'Images',desc:'Open-source AI image generation — run locally or in cloud.',pricing:'Free (open source)',url:'https://stability.ai'},
    {name:'Leonardo AI',cat:'Images',desc:'AI image generation for creative projects and game assets.',pricing:'Free / $12/mo',url:'https://leonardo.ai'},
    {name:'Canva AI',cat:'Images',desc:'AI-powered design tool for social media, presentations, and more.',pricing:'Free / $13/mo',url:'https://www.canva.com'},
    {name:'Adobe Firefly',cat:'Images',desc:'AI image generation integrated into Adobe Creative Cloud.',pricing:'Free / from $10/mo',url:'https://firefly.adobe.com'},
    {name:'Runway',cat:'Video',desc:'AI video generation, editing, and visual effects platform.',pricing:'Free / $12/mo',url:'https://runwayml.com'},
    {name:'Synthesia',cat:'Video',desc:'Create AI avatar videos for training, marketing, and education.',pricing:'From $22/mo',url:'https://www.synthesia.io'},
    {name:'Descript',cat:'Video',desc:'AI video & podcast editor — edit video by editing text.',pricing:'Free / $24/mo',url:'https://www.descript.com'},
    {name:'HeyGen',cat:'Video',desc:'AI spokesperson videos with realistic avatars and voices.',pricing:'Free / $24/mo',url:'https://www.heygen.com'},
    {name:'Luma AI',cat:'Video',desc:'3D capture and AI video generation from text and images.',pricing:'Free / $10/mo',url:'https://lumalabs.ai'},
    {name:'GitHub Copilot',cat:'Code',desc:'AI pair programmer — code suggestions right in your editor.',pricing:'Free / $10/mo',url:'https://github.com/features/copilot'},
    {name:'Cursor',cat:'Code',desc:'AI-first code editor built for AI-assisted development.',pricing:'Free / $20/mo',url:'https://cursor.sh'},
    {name:'Replit AI',cat:'Code',desc:'Cloud IDE with AI code generation and deployment.',pricing:'Free / $25/mo',url:'https://replit.com'},
    {name:'Tabnine',cat:'Code',desc:'AI code completion that runs locally for privacy.',pricing:'Free / $12/mo',url:'https://www.tabnine.com'},
    {name:'Codeium',cat:'Code',desc:'Free AI code autocomplete for 70+ programming languages.',pricing:'Free / $10/mo',url:'https://codeium.com'},
    {name:'ElevenLabs',cat:'Voice',desc:'Realistic AI voice generation and text-to-speech.',pricing:'Free / $5/mo',url:'https://elevenlabs.io'},
    {name:'Murf AI',cat:'Voice',desc:'AI voiceover studio for videos, presentations, and podcasts.',pricing:'Free / $26/mo',url:'https://murf.ai'},
    {name:'Play.ht',cat:'Voice',desc:'Ultra-realistic AI voice generation with voice cloning.',pricing:'Free / $39/mo',url:'https://play.ht'},
    {name:'Speechify',cat:'Voice',desc:'AI text-to-speech reader for documents and web pages.',pricing:'Free / $11/mo',url:'https://speechify.com'},
    {name:'Notion AI',cat:'Productivity',desc:'AI writing and organization built into Notion workspace.',pricing:'$10/mo add-on',url:'https://www.notion.so/product/ai'},
    {name:'Otter.ai',cat:'Productivity',desc:'AI meeting transcription and note-taking assistant.',pricing:'Free / $17/mo',url:'https://otter.ai'},
    {name:'Reclaim AI',cat:'Productivity',desc:'AI calendar scheduling and time management.',pricing:'Free / $10/mo',url:'https://reclaim.ai'},
    {name:'Taskade',cat:'Productivity',desc:'AI-powered project management with task automation.',pricing:'Free / $10/mo',url:'https://www.taskade.com'},
    {name:'Zapier AI',cat:'Productivity',desc:'AI-powered automation connecting 6000+ apps.',pricing:'Free / $20/mo',url:'https://zapier.com'},
    {name:'Perplexity',cat:'Research',desc:'AI-powered search engine with source citations.',pricing:'Free / $20/mo',url:'https://www.perplexity.ai'},
    {name:'Consensus',cat:'Research',desc:'AI research engine that finds answers from scientific papers.',pricing:'Free / $10/mo',url:'https://consensus.app'},
    {name:'Elicit',cat:'Research',desc:'AI research assistant for literature review and analysis.',pricing:'Free / $10/mo',url:'https://elicit.com'},
    {name:'Scite',cat:'Research',desc:'Smart citations — see how papers have been cited.',pricing:'$20/mo',url:'https://scite.ai'},
    {name:'SurferSEO',cat:'Marketing',desc:'AI content optimization for better search engine rankings.',pricing:'From $89/mo',url:'https://surferseo.com'},
    {name:'Semrush AI',cat:'Marketing',desc:'AI-powered SEO toolkit for keyword research and audits.',pricing:'From $130/mo',url:'https://www.semrush.com'},
    {name:'AdCreative AI',cat:'Marketing',desc:'Generate high-converting ad creatives with AI.',pricing:'From $29/mo',url:'https://www.adcreative.ai'},
    {name:'Pictory',cat:'Marketing',desc:'Turn text content into short marketing videos with AI.',pricing:'From $19/mo',url:'https://pictory.ai'},
    {name:'Opus Clip',cat:'Marketing',desc:'AI tool that turns long videos into viral short clips.',pricing:'Free / $15/mo',url:'https://www.opus.pro'},
    {name:'Beautiful.ai',cat:'Design',desc:'AI-powered presentations that design themselves.',pricing:'From $12/mo',url:'https://www.beautiful.ai'},
    {name:'Looka',cat:'Design',desc:'AI logo maker and brand identity generator.',pricing:'From $20 one-time',url:'https://looka.com'},
    {name:'Khroma',cat:'Design',desc:'AI color tool that learns your color preferences.',pricing:'Free',url:'https://www.khroma.co'},
    {name:'Uizard',cat:'Design',desc:'Turn sketches and screenshots into editable UI designs.',pricing:'Free / $12/mo',url:'https://uizard.io'},
    {name:'Tome',cat:'Design',desc:'AI-powered storytelling and presentation creator.',pricing:'Free / $10/mo',url:'https://tome.app'},
  ];

  var categories = ['All'];
  aiTools.forEach(function(t){ if(categories.indexOf(t.cat)===-1) categories.push(t.cat); });
  var activeFilter = 'All';

  function renderFilters(){
    var html='';
    categories.forEach(function(c){html+='<button class="filter-btn'+(c===activeFilter?' active':'')+'" onclick="setFilter(\''+c+'\')">'+c+'</button>';});
    document.getElementById('filters').innerHTML=html;
  }

  function setFilter(cat){activeFilter=cat;renderFilters();filterTools();}

  function filterTools(){
    var q=document.getElementById('searchInput').value.toLowerCase();
    var grid=document.getElementById('toolsGrid');
    var filtered=aiTools.filter(function(t){
      var matchCat=activeFilter==='All'||t.cat===activeFilter;
      var matchQ=!q||t.name.toLowerCase().indexOf(q)!==-1||t.desc.toLowerCase().indexOf(q)!==-1||t.cat.toLowerCase().indexOf(q)!==-1;
      return matchCat&&matchQ;
    });
    document.getElementById('toolCount').textContent='Showing '+filtered.length+' of '+aiTools.length+' tools';
    grid.innerHTML='';
    filtered.forEach(function(t){
      var card=document.createElement('div');card.className='ai-card';
      card.innerHTML='<h3>'+t.name+' <span class="cat-tag">'+t.cat+'</span></h3><p>'+t.desc+'</p><div class="pricing">'+t.pricing+'</div><a href="'+t.url+'" target="_blank" rel="noopener" class="visit-btn">Visit '+t.name+' →</a>';
      grid.appendChild(card);
    });
  }

  renderFilters();filterTools();
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 8. BUDGET CALCULATOR
# ═══════════════════════════════════════════════════════════

BUDGET_CALCULATOR_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Budget Calculator — Monthly Budget Planner | {{ site_title }}</title>
  <meta name="description" content="Free budget calculator using the 50/30/20 rule. Plan your monthly expenses, track savings goals, and take control of your finances.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#2563eb; --accent-light:#eff6ff; --green:#059669; --green-bg:#ecfdf5; --red:#dc2626; --red-bg:#fef2f2; --border:#e5e7eb; --radius:10px; --max-width:900px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
""" + SHARED_NAV_CSS + """
    .page-hero{background:linear-gradient(135deg,#059669 0%,#10b981 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:500px;margin:0 auto}
    .calc-section{padding:32px 0}
    .calc-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:28px;margin-bottom:20px}
    .calc-card h2{font-size:18px;font-weight:800;margin-bottom:16px;display:flex;align-items:center;gap:8px}
    .form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px}
    .form-group{display:flex;flex-direction:column;gap:4px}
    .form-group label{font-size:13px;font-weight:600;color:var(--text-secondary)}
    .form-group input{padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:15px;font-family:inherit;outline:none;transition:border .2s}
    .form-group input:focus{border-color:var(--accent)}
    .btn{background:var(--accent);color:#fff;border:none;padding:12px 24px;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:background .2s;width:100%}
    .btn:hover{background:#1d4ed8}
    .results-panel{display:none;margin-top:24px}
    .result-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
    .result-box{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center}
    .result-box.positive{background:var(--green-bg);border-color:#a7f3d0}
    .result-box.negative{background:var(--red-bg);border-color:#fecaca}
    .result-box .label{font-size:12px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
    .result-box .value{font-size:28px;font-weight:800}
    .result-box.positive .value{color:var(--green)}
    .result-box.negative .value{color:var(--red)}
    .bar-chart{margin:20px 0}.bar-row{display:flex;align-items:center;gap:12px;margin-bottom:10px}.bar-label{width:100px;font-size:13px;font-weight:600;text-align:right;flex-shrink:0}.bar-track{flex:1;background:var(--surface);border-radius:4px;height:24px;overflow:hidden}.bar-fill{height:100%;border-radius:4px;transition:width .5s}.bar-value{width:80px;font-size:13px;font-weight:600;text-align:right;flex-shrink:0}
    .rule-section{margin-top:28px;padding:24px;background:var(--accent-light);border-radius:var(--radius)}
    .rule-section h3{font-size:16px;font-weight:700;color:var(--accent);margin-bottom:12px}
    .rule-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #bfdbfe;font-size:14px}
    .rule-row:last-child{border-bottom:none}
    .rule-row .ideal{color:var(--accent);font-weight:600}
    .disclaimer{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-top:24px;font-size:12px;color:var(--text-secondary);line-height:1.7}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.form-row,.result-summary{grid-template-columns:1fr}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="page-hero"><h1>💰 Budget Calculator</h1><p>Plan your monthly budget using the 50/30/20 rule and track your savings goals</p></div>

  <div class="container"><div class="calc-section">
    <div class="calc-card">
      <h2>💵 Monthly Income</h2>
      <div class="form-row">
        <div class="form-group"><label>Take-Home Pay (after tax)</label><input type="number" id="income" placeholder="e.g. 5000" value=""></div>
        <div class="form-group"><label>Other Income</label><input type="number" id="otherIncome" placeholder="e.g. 500" value=""></div>
      </div>
    </div>

    <div class="calc-card">
      <h2>🏠 Needs (Essential Expenses)</h2>
      <div class="form-row">
        <div class="form-group"><label>Rent / Mortgage</label><input type="number" class="expense needs" placeholder="0"></div>
        <div class="form-group"><label>Utilities</label><input type="number" class="expense needs" placeholder="0"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Groceries</label><input type="number" class="expense needs" placeholder="0"></div>
        <div class="form-group"><label>Transportation</label><input type="number" class="expense needs" placeholder="0"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Insurance</label><input type="number" class="expense needs" placeholder="0"></div>
        <div class="form-group"><label>Minimum Debt Payments</label><input type="number" class="expense needs" placeholder="0"></div>
      </div>
    </div>

    <div class="calc-card">
      <h2>🎉 Wants (Lifestyle Expenses)</h2>
      <div class="form-row">
        <div class="form-group"><label>Dining Out</label><input type="number" class="expense wants" placeholder="0"></div>
        <div class="form-group"><label>Entertainment</label><input type="number" class="expense wants" placeholder="0"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Shopping</label><input type="number" class="expense wants" placeholder="0"></div>
        <div class="form-group"><label>Subscriptions</label><input type="number" class="expense wants" placeholder="0"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Hobbies</label><input type="number" class="expense wants" placeholder="0"></div>
        <div class="form-group"><label>Travel / Vacation</label><input type="number" class="expense wants" placeholder="0"></div>
      </div>
    </div>

    <div class="calc-card">
      <h2>🎯 Savings Goal</h2>
      <div class="form-row">
        <div class="form-group"><label>Monthly Savings Target</label><input type="number" id="savingsGoal" placeholder="e.g. 1000"></div>
        <div class="form-group"><label>Goal Name (optional)</label><input type="text" id="goalName" placeholder="e.g. Emergency Fund"></div>
      </div>
    </div>

    <button class="btn" onclick="calculate()">Calculate My Budget</button>

    <div class="results-panel" id="results">
      <div class="result-summary">
        <div class="result-box"><div class="label">Total Income</div><div class="value" id="rIncome">$0</div></div>
        <div class="result-box"><div class="label">Total Expenses</div><div class="value" id="rExpenses">$0</div></div>
        <div class="result-box" id="rSurplusBox"><div class="label">Surplus / Deficit</div><div class="value" id="rSurplus">$0</div></div>
      </div>
      <div class="bar-chart" id="barChart"></div>
      <div class="rule-section">
        <h3>📏 50/30/20 Rule Analysis</h3>
        <div id="ruleAnalysis"></div>
      </div>
    </div>

    <div class="disclaimer"><strong>Disclaimer:</strong> This calculator is for informational and educational purposes only. It does not constitute financial advice. Results are estimates based on the information you provide. Consult a qualified financial advisor for personalized financial planning.</div>
  </div></div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  function getVal(id){return parseFloat(document.getElementById(id).value)||0}
  function sumClass(cls){var total=0;document.querySelectorAll('.expense.'+cls).forEach(function(el){total+=parseFloat(el.value)||0});return total}
  function fmt(n){return '$'+n.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:0})}
  function calculate(){
    var income=getVal('income')+getVal('otherIncome');
    var needs=sumClass('needs');var wants=sumClass('wants');
    var totalExpenses=needs+wants;var surplus=income-totalExpenses;
    document.getElementById('rIncome').textContent=fmt(income);
    document.getElementById('rExpenses').textContent=fmt(totalExpenses);
    document.getElementById('rSurplus').textContent=fmt(surplus);
    var box=document.getElementById('rSurplusBox');
    box.className='result-box '+(surplus>=0?'positive':'negative');
    var colors=['#3b82f6','#f59e0b','#10b981','#ef4444'];
    var items=[{label:'Needs',val:needs,color:colors[0]},{label:'Wants',val:wants,color:colors[1]},{label:'Savings',val:Math.max(surplus,0),color:colors[2]}];
    if(surplus<0)items.push({label:'Deficit',val:Math.abs(surplus),color:colors[3]});
    var chartHtml='';var maxVal=Math.max(income,totalExpenses);
    items.forEach(function(it){var pct=maxVal>0?(it.val/maxVal*100):0;chartHtml+='<div class="bar-row"><div class="bar-label">'+it.label+'</div><div class="bar-track"><div class="bar-fill" style="width:'+pct+'%;background:'+it.color+'"></div></div><div class="bar-value">'+fmt(it.val)+'</div></div>'});
    document.getElementById('barChart').innerHTML=chartHtml;
    var idealNeeds=income*.5;var idealWants=income*.3;var idealSavings=income*.2;
    var ruleHtml='<div class="rule-row"><span>Needs (50%)</span><span>You: '+fmt(needs)+' / <span class="ideal">Ideal: '+fmt(idealNeeds)+'</span></span></div>';
    ruleHtml+='<div class="rule-row"><span>Wants (30%)</span><span>You: '+fmt(wants)+' / <span class="ideal">Ideal: '+fmt(idealWants)+'</span></span></div>';
    ruleHtml+='<div class="rule-row"><span>Savings (20%)</span><span>You: '+fmt(Math.max(surplus,0))+' / <span class="ideal">Ideal: '+fmt(idealSavings)+'</span></span></div>';
    document.getElementById('ruleAnalysis').innerHTML=ruleHtml;
    document.getElementById('results').style.display='block';
    document.getElementById('results').scrollIntoView({behavior:'smooth'});
  }
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 9. WORKOUT GENERATOR
# ═══════════════════════════════════════════════════════════

WORKOUT_GENERATOR_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Workout Generator — Custom Exercise Plans | {{ site_title }}</title>
  <meta name="description" content="Generate a custom workout plan based on your fitness goals, available equipment, and time. Free workout builder tool.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#7c3aed; --accent-light:#f5f3ff; --border:#e5e7eb; --radius:10px; --max-width:900px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
""" + SHARED_NAV_CSS + """
    .page-hero{background:linear-gradient(135deg,#5b21b6 0%,#7c3aed 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:500px;margin:0 auto}
    .config-section{padding:32px 0}
    .config-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:16px}
    .config-card h2{font-size:16px;font-weight:700;margin-bottom:14px}
    .option-grid{display:flex;flex-wrap:wrap;gap:8px}
    .option-btn{padding:10px 18px;border:2px solid var(--border);border-radius:8px;background:transparent;color:var(--text);font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
    .option-btn:hover{border-color:var(--accent);color:var(--accent)}
    .option-btn.selected{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
    .btn{background:var(--accent);color:#fff;border:none;padding:14px 28px;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;width:100%;margin-top:8px;transition:background .2s}
    .btn:hover{background:#5b21b6}
    .workout-result{display:none;margin-top:28px}
    .workout-header{background:var(--accent-light);border:1px solid #ddd6fe;border-radius:var(--radius);padding:20px 24px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center}
    .workout-header h2{font-size:18px;font-weight:800;color:var(--accent)}
    .workout-header .stats{font-size:13px;color:var(--text-secondary)}
    .exercise-card{border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-bottom:10px;display:flex;align-items:center;gap:16px}
    .exercise-num{width:36px;height:36px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0}
    .exercise-info h3{font-size:15px;font-weight:700;margin-bottom:2px}.exercise-info p{font-size:13px;color:var(--text-secondary)}
    .exercise-detail{display:flex;gap:12px;margin-top:4px}.exercise-detail span{font-size:12px;background:var(--surface);padding:2px 8px;border-radius:4px;font-weight:600}
    .print-btn{background:transparent;border:1px solid var(--border);color:var(--text);padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}
    .print-btn:hover{border-color:var(--accent);color:var(--accent)}
    .disclaimer{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-top:24px;font-size:12px;color:var(--text-secondary);line-height:1.7}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.workout-header{flex-direction:column;gap:8px}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
    @media print{.header,.page-hero,.config-section,.subscribe-float,.footer,.print-btn,.disclaimer{display:none!important}.workout-result{display:block!important}}
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="page-hero"><h1>💪 Workout Generator</h1><p>Get a custom workout plan based on your goals, equipment, and available time</p></div>

  <div class="container"><div class="config-section">
    <div class="config-card"><h2>🎯 Fitness Goal</h2><div class="option-grid" id="goalOptions">
      <button class="option-btn" data-val="strength" onclick="selectOption(this,'goal')">Build Strength</button>
      <button class="option-btn" data-val="muscle" onclick="selectOption(this,'goal')">Build Muscle</button>
      <button class="option-btn" data-val="cardio" onclick="selectOption(this,'goal')">Improve Cardio</button>
      <button class="option-btn" data-val="weight_loss" onclick="selectOption(this,'goal')">Lose Weight</button>
      <button class="option-btn" data-val="flexibility" onclick="selectOption(this,'goal')">Flexibility</button>
      <button class="option-btn" data-val="general" onclick="selectOption(this,'goal')">General Fitness</button>
    </div></div>
    <div class="config-card"><h2>🏋️ Equipment Available</h2><div class="option-grid" id="equipOptions">
      <button class="option-btn" data-val="none" onclick="selectOption(this,'equip')">No Equipment</button>
      <button class="option-btn" data-val="dumbbells" onclick="selectOption(this,'equip')">Dumbbells Only</button>
      <button class="option-btn" data-val="home" onclick="selectOption(this,'equip')">Home Gym (Bands, DB, Bench)</button>
      <button class="option-btn" data-val="full" onclick="selectOption(this,'equip')">Full Gym</button>
    </div></div>
    <div class="config-card"><h2>⏱️ Available Time</h2><div class="option-grid" id="timeOptions">
      <button class="option-btn" data-val="15" onclick="selectOption(this,'time')">15 min</button>
      <button class="option-btn" data-val="30" onclick="selectOption(this,'time')">30 min</button>
      <button class="option-btn" data-val="45" onclick="selectOption(this,'time')">45 min</button>
      <button class="option-btn" data-val="60" onclick="selectOption(this,'time')">60 min</button>
    </div></div>
    <div class="config-card"><h2>📊 Fitness Level</h2><div class="option-grid" id="levelOptions">
      <button class="option-btn" data-val="beginner" onclick="selectOption(this,'level')">Beginner</button>
      <button class="option-btn" data-val="intermediate" onclick="selectOption(this,'level')">Intermediate</button>
      <button class="option-btn" data-val="advanced" onclick="selectOption(this,'level')">Advanced</button>
    </div></div>
    <button class="btn" onclick="generateWorkout()">Generate My Workout</button>
  </div>

  <div class="workout-result" id="workoutResult">
    <div class="workout-header"><h2 id="workoutTitle">Your Workout</h2><div><span class="stats" id="workoutStats"></span> <button class="print-btn" onclick="window.print()">🖨️ Print</button></div></div>
    <div id="exerciseList"></div>
  </div>

  <div class="disclaimer"><strong>Disclaimer:</strong> This workout generator provides general exercise suggestions for informational purposes only. It is not a substitute for professional medical or fitness advice. Consult a doctor before starting any exercise program. Listen to your body and stop if you feel pain.</div>
  </div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  var sel={goal:'',equip:'',time:'',level:''};
  function selectOption(btn,key){
    sel[key]=btn.dataset.val;
    btn.parentElement.querySelectorAll('.option-btn').forEach(function(b){b.classList.remove('selected')});
    btn.classList.add('selected');
  }

  var exercises={
    bodyweight:{warmup:['Jumping Jacks','High Knees','Arm Circles','Leg Swings','Bodyweight Squats'],
      strength:['Push-ups','Diamond Push-ups','Pike Push-ups','Bodyweight Squats','Lunges','Glute Bridges','Plank','Side Plank','Superman','Tricep Dips (chair)','Bulgarian Split Squats','Calf Raises'],
      cardio:['Burpees','Mountain Climbers','Jump Squats','High Knees','Butt Kicks','Skaters','Tuck Jumps','Bear Crawls'],
      flexibility:['Cat-Cow Stretch','Pigeon Pose','Standing Hamstring Stretch','Quad Stretch','Child\'s Pose','Seated Twist','Hip Flexor Stretch','Shoulder Stretch']},
    dumbbells:{strength:['Dumbbell Bench Press','Dumbbell Rows','Dumbbell Shoulder Press','Goblet Squats','Romanian Deadlifts','Bicep Curls','Tricep Extensions','Lateral Raises','Dumbbell Lunges'],
      cardio:['Dumbbell Thrusters','Renegade Rows','Dumbbell Swings','Man Makers']},
    home:{strength:['Resistance Band Pull-aparts','Band-assisted Pull-ups','Incline Dumbbell Press','Dumbbell Flyes','Bent Over Rows','Step-ups','Band Squats','Floor Press'],
      cardio:['Battle Rope Waves','Box Jumps','Band Sprints']},
    full:{strength:['Barbell Bench Press','Barbell Squats','Deadlifts','Overhead Press','Pull-ups','Barbell Rows','Lat Pulldown','Leg Press','Cable Flyes','Hack Squat','T-Bar Row','Face Pulls'],
      cardio:['Rowing Machine','Assault Bike','Stairclimber Intervals','Sled Push']}
  };

  function pick(arr,n){var a=arr.slice();var r=[];for(var i=0;i<Math.min(n,a.length);i++){var idx=Math.floor(Math.random()*a.length);r.push(a.splice(idx,1)[0]);}return r;}

  function generateWorkout(){
    if(!sel.goal||!sel.equip||!sel.time||!sel.level){alert('Please select all options');return;}
    var mins=parseInt(sel.time);var numExercises=Math.max(3,Math.floor(mins/5));
    var pool=exercises.bodyweight;var equipKey=sel.equip;
    if(equipKey==='dumbbells')pool={warmup:pool.warmup,strength:pool.strength.concat(exercises.dumbbells.strength),cardio:pool.cardio.concat(exercises.dumbbells.cardio),flexibility:pool.flexibility};
    else if(equipKey==='home')pool={warmup:pool.warmup,strength:pool.strength.concat(exercises.dumbbells.strength).concat(exercises.home.strength),cardio:pool.cardio.concat(exercises.dumbbells.cardio).concat(exercises.home.cardio),flexibility:pool.flexibility};
    else if(equipKey==='full')pool={warmup:pool.warmup,strength:pool.strength.concat(exercises.full.strength),cardio:pool.cardio.concat(exercises.full.cardio),flexibility:pool.flexibility};

    var workout=[];var warmupCount=Math.min(3,Math.ceil(numExercises*.2));var cooldownCount=2;
    var mainCount=numExercises-warmupCount-cooldownCount;
    var warmups=pick(pool.warmup,warmupCount);
    var mainPool=sel.goal==='cardio'?pool.cardio:sel.goal==='flexibility'?pool.flexibility:pool.strength;
    if(sel.goal==='weight_loss'||sel.goal==='general')mainPool=pool.strength.concat(pool.cardio);
    var main=pick(mainPool,Math.max(mainCount,3));
    var cooldown=pick(pool.flexibility,cooldownCount);

    var sets=sel.level==='beginner'?2:sel.level==='intermediate'?3:4;
    var reps=sel.goal==='strength'?'6-8':sel.goal==='muscle'?'8-12':sel.goal==='cardio'?'30 sec':'15-20';

    warmups.forEach(function(e){workout.push({name:e,phase:'Warm-up',sets:1,reps:'30 sec',rest:'15 sec'})});
    main.forEach(function(e){workout.push({name:e,phase:'Main',sets:sets,reps:reps,rest:sel.goal==='cardio'?'30 sec':'60 sec'})});
    cooldown.forEach(function(e){workout.push({name:e,phase:'Cool-down',sets:1,reps:'45 sec hold',rest:'15 sec'})});

    var goalNames={strength:'Strength Building',muscle:'Muscle Hypertrophy',cardio:'Cardio Conditioning',weight_loss:'Fat Burning',flexibility:'Flexibility & Mobility',general:'General Fitness'};
    document.getElementById('workoutTitle').textContent=goalNames[sel.goal]+' Workout';
    document.getElementById('workoutStats').textContent=mins+' min · '+workout.length+' exercises · '+sel.level;

    var html='';workout.forEach(function(ex,i){
      html+='<div class="exercise-card"><div class="exercise-num">'+(i+1)+'</div><div class="exercise-info"><h3>'+ex.name+'</h3><p>'+ex.phase+'</p><div class="exercise-detail"><span>'+ex.sets+' set'+(ex.sets>1?'s':'')+'</span><span>'+ex.reps+'</span><span>Rest: '+ex.rest+'</span></div></div></div>';
    });
    document.getElementById('exerciseList').innerHTML=html;
    document.getElementById('workoutResult').style.display='block';
    document.getElementById('workoutResult').scrollIntoView({behavior:'smooth'});
  }
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 10. PET FOOD CHECKER
# ═══════════════════════════════════════════════════════════

PET_FOOD_CHECKER_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pet Food Analyzer — Check Ingredient Quality | {{ site_title }}</title>
  <meta name="description" content="Analyze your pet food ingredients for quality and safety. Get ratings and recommendations for healthier pet nutrition.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#ea580c; --accent-light:#fff7ed; --green:#059669; --yellow:#d97706; --red:#dc2626; --border:#e5e7eb; --radius:10px; --max-width:900px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
""" + SHARED_NAV_CSS + """
    .page-hero{background:linear-gradient(135deg,#c2410c 0%,#ea580c 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:500px;margin:0 auto}
    .input-section{padding:32px 0}
    .input-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:16px}
    .input-card h2{font-size:16px;font-weight:700;margin-bottom:12px}
    .pet-type{display:flex;gap:8px;margin-bottom:16px}
    .pet-btn{flex:1;padding:12px;border:2px solid var(--border);border-radius:8px;background:transparent;color:var(--text);font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s;text-align:center}
    .pet-btn:hover{border-color:var(--accent)}.pet-btn.selected{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
    .pet-btn span{display:block;font-size:28px;margin-bottom:4px}
    textarea{width:100%;padding:14px;border:1px solid var(--border);border-radius:8px;font-size:14px;font-family:inherit;resize:vertical;min-height:100px;outline:none}
    textarea:focus{border-color:var(--accent)}
    .btn{background:var(--accent);color:#fff;border:none;padding:14px 28px;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;width:100%;margin-top:12px;transition:background .2s}
    .btn:hover{background:#c2410c}
    .results{display:none;margin-top:24px}
    .score-card{text-align:center;padding:32px;border-radius:var(--radius);margin-bottom:20px}
    .score-card.good{background:#ecfdf5;border:2px solid #a7f3d0}.score-card.ok{background:#fffbeb;border:2px solid #fde68a}.score-card.bad{background:#fef2f2;border:2px solid #fecaca}
    .score-num{font-size:56px;font-weight:900}.score-card.good .score-num{color:var(--green)}.score-card.ok .score-num{color:var(--yellow)}.score-card.bad .score-num{color:var(--red)}
    .score-label{font-size:18px;font-weight:700;margin-top:4px}
    .ingredient-list{margin-top:16px}
    .ing-item{display:flex;align-items:center;gap:12px;padding:10px 14px;border:1px solid var(--border);border-radius:8px;margin-bottom:6px}
    .ing-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}.ing-dot.good{background:var(--green)}.ing-dot.ok{background:var(--yellow)}.ing-dot.bad{background:var(--red)}
    .ing-name{font-size:14px;font-weight:600;flex:1}.ing-note{font-size:12px;color:var(--text-secondary);max-width:300px}
    .tips-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-top:20px}
    .tips-card h3{font-size:15px;font-weight:700;margin-bottom:10px}.tips-card li{font-size:13px;margin-bottom:6px}
    .disclaimer{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-top:24px;font-size:12px;color:var(--text-secondary);line-height:1.7}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + SHARED_MOBILE_CSS + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="page-hero"><h1>🐾 Pet Food Analyzer</h1><p>Paste your pet food's ingredient list to get a quality analysis and health rating</p></div>

  <div class="container"><div class="input-section">
    <div class="input-card">
      <h2>Select Pet Type</h2>
      <div class="pet-type">
        <button class="pet-btn selected" onclick="selectPet(this,'dog')"><span>🐕</span>Dog</button>
        <button class="pet-btn" onclick="selectPet(this,'cat')"><span>🐱</span>Cat</button>
      </div>
      <h2>Paste Ingredient List</h2>
      <textarea id="ingredients" placeholder="Paste the ingredient list from your pet food packaging here...&#10;&#10;Example: Chicken, Brown Rice, Chicken Meal, Barley, Oatmeal, Chicken Fat, Dried Beet Pulp, Natural Flavor..."></textarea>
      <button class="btn" onclick="analyzeFood()">Analyze Ingredients</button>
    </div>

    <div class="results" id="results">
      <div class="score-card" id="scoreCard"><div class="score-num" id="scoreNum">0</div><div class="score-label" id="scoreLabel">Quality Score</div></div>
      <h3 style="margin-bottom:12px">Ingredient Breakdown</h3>
      <div class="ingredient-list" id="ingredientList"></div>
      <div class="tips-card" id="tipsCard"></div>
    </div>

    <div class="disclaimer"><strong>Disclaimer:</strong> This tool provides general informational assessments based on common pet nutrition guidelines. It is NOT a substitute for professional veterinary advice. Individual pets may have specific dietary needs, allergies, or health conditions. Always consult your veterinarian before making changes to your pet's diet.</div>
  </div></div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  var petType='dog';
  function selectPet(btn,type){petType=type;document.querySelectorAll('.pet-btn').forEach(function(b){b.classList.remove('selected')});btn.classList.add('selected')}

  var goodIngredients={dog:['chicken','beef','salmon','turkey','lamb','duck','venison','bison','brown rice','sweet potato','peas','blueberries','cranberries','spinach','carrots','pumpkin','flaxseed','fish oil','coconut oil','turmeric','probiotics','glucosamine','chondroitin','egg','sardine','herring','oatmeal','barley','quinoa','kale','broccoli','apple'],cat:['chicken','tuna','salmon','turkey','duck','rabbit','sardine','herring','egg','liver','heart','fish oil','pumpkin','cranberries','blueberries','taurine','probiotics','flaxseed']};
  var okIngredients=['chicken meal','fish meal','brewers rice','rice','corn','wheat','soybean','beet pulp','chicken fat','natural flavor','cellulose','tomato pomace','potassium chloride','salt','calcium carbonate','yeast','dried egg','pork meal','corn gluten meal'];
  var badIngredients=['by-product','by product','byproduct','artificial','BHA','BHT','ethoxyquin','propylene glycol','menadione','food coloring','red 40','blue 2','yellow 5','yellow 6','sodium nitrite','carrageenan','xylitol','propyl gallate','TBHQ','rendered fat','animal digest','sugar','corn syrup','sorbitol'];

  function analyzeFood(){
    var raw=document.getElementById('ingredients').value.trim();
    if(!raw){alert('Please paste ingredient list');return;}
    var ings=raw.split(/,|;|\n/).map(function(s){return s.trim()}).filter(function(s){return s.length>0});
    var results=[];var totalScore=0;
    ings.forEach(function(ing){
      var lower=ing.toLowerCase();var rating='ok';var note='Common ingredient';
      for(var i=0;i<goodIngredients[petType].length;i++){if(lower.indexOf(goodIngredients[petType][i])!==-1){rating='good';note='Quality protein/nutrient source';break;}}
      if(rating==='ok'){for(var i=0;i<badIngredients.length;i++){if(lower.indexOf(badIngredients[i])!==-1){rating='bad';note='Potentially harmful or low-quality';break;}}}
      if(rating==='ok'){for(var i=0;i<okIngredients.length;i++){if(lower.indexOf(okIngredients[i])!==-1){note='Acceptable filler or supplement';break;}}}
      var score=rating==='good'?10:rating==='ok'?5:0;totalScore+=score;
      results.push({name:ing,rating:rating,note:note});
    });
    var maxScore=ings.length*10;var pct=maxScore>0?Math.round(totalScore/maxScore*100):0;
    var sc=document.getElementById('scoreCard');
    sc.className='score-card '+(pct>=70?'good':pct>=40?'ok':'bad');
    document.getElementById('scoreNum').textContent=pct+'/100';
    document.getElementById('scoreLabel').textContent=pct>=70?'Good Quality':pct>=40?'Average Quality':'Below Average';
    var html='';results.forEach(function(r){html+='<div class="ing-item"><div class="ing-dot '+r.rating+'"></div><div class="ing-name">'+r.name+'</div><div class="ing-note">'+r.note+'</div></div>'});
    document.getElementById('ingredientList').innerHTML=html;
    var goodCount=results.filter(function(r){return r.rating==='good'}).length;
    var badCount=results.filter(function(r){return r.rating==='bad'}).length;
    var tips='<h3>💡 Analysis Tips</h3><ul>';
    if(goodCount>0)tips+='<li>✅ Found <strong>'+goodCount+'</strong> high-quality ingredients</li>';
    if(badCount>0)tips+='<li>⚠️ Found <strong>'+badCount+'</strong> potentially concerning ingredients</li>';
    tips+='<li>First ingredient should be a named protein (chicken, beef, salmon — not "meat")</li>';
    tips+='<li>Avoid foods with artificial colors, preservatives (BHA/BHT), or unnamed "by-products"</li>';
    tips+='<li>Look for whole foods over processed fillers in the first 5 ingredients</li>';
    tips+='</ul>';
    document.getElementById('tipsCard').innerHTML=tips;
    document.getElementById('results').style.display='block';
    document.getElementById('results').scrollIntoView({behavior:'smooth'});
  }
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# 11. SMART HOME COMPATIBILITY CHECKER
# ═══════════════════════════════════════════════════════════

SMART_HOME_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Home Hub — Device Compatibility Checker | {{ site_title }}</title>
  <meta name="description" content="Check smart home device compatibility across Alexa, Google Home, and Apple HomeKit. Plan your smart home ecosystem.">
""" + SHARED_HEAD_FONTS + """
  <style>
    :root { --bg:#fff; --surface:#f8f9fb; --text:#111827; --text-secondary:#6b7280; --accent:#0891b2; --accent-light:#ecfeff; --green:#059669; --red:#dc2626; --border:#e5e7eb; --radius:10px; --max-width:1000px; }
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
""" + SHARED_NAV_CSS + """
    .page-hero{background:linear-gradient(135deg,#0e7490 0%,#0891b2 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:560px;margin:0 auto}
    .section{padding:32px 0}
    .eco-selector{display:flex;gap:12px;margin-bottom:24px;justify-content:center;flex-wrap:wrap}
    .eco-btn{padding:14px 24px;border:2px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:all .15s;text-align:center;min-width:160px}
    .eco-btn:hover{border-color:var(--accent)}.eco-btn.selected{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
    .eco-btn span{display:block;font-size:32px;margin-bottom:4px}
    .cat-filter{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;justify-content:center}
    .cat-btn{padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
    .cat-btn:hover,.cat-btn.active{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}
    .device-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .device-card{border:1px solid var(--border);border-radius:var(--radius);padding:16px;transition:all .15s}
    .device-card:hover{border-color:var(--accent)}
    .device-card h3{font-size:14px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:8px}
    .device-card .cat-tag{font-size:10px;font-weight:600;color:var(--accent);background:var(--accent-light);padding:2px 6px;border-radius:8px}
    .device-card p{font-size:12px;color:var(--text-secondary);margin-bottom:8px}
    .compat-row{display:flex;gap:8px}
    .compat-badge{font-size:11px;padding:3px 8px;border-radius:4px;font-weight:600}
    .compat-badge.yes{background:#ecfdf5;color:var(--green)}.compat-badge.no{background:#fef2f2;color:var(--red)}.compat-badge.partial{background:#fffbeb;color:#d97706}
    .device-count{text-align:center;padding:8px 0;font-size:13px;color:var(--text-secondary);margin-bottom:8px}
    .search-wrap{max-width:400px;margin:0 auto 20px}.search-wrap input{width:100%;padding:10px 16px;border-radius:50px;border:1px solid var(--border);font-size:14px;font-family:inherit;outline:none}.search-wrap input:focus{border-color:var(--accent)}
    .disclaimer{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-top:24px;font-size:12px;color:var(--text-secondary);line-height:1.7}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
""" + SHARED_SUBSCRIBE_CSS + """
    @media(max-width:768px){.device-grid{grid-template-columns:1fr}.eco-selector{flex-direction:column;align-items:center}""" + SHARED_MOBILE_CSS.replace("@media (max-width: 768px) {","") + """
  </style>
</head>
<body>
""" + SHARED_NAV.replace("{% if nid == active_niche %}", "{% if false %}") + """

  <div class="page-hero"><h1>🏠 Smart Home Hub</h1><p>Check device compatibility across Alexa, Google Home, Apple HomeKit, and Matter ecosystems</p></div>

  <div class="container"><div class="section">
    <div class="eco-selector">
      <button class="eco-btn selected" onclick="selectEco(this,'all')"><span>🌐</span>All Ecosystems</button>
      <button class="eco-btn" onclick="selectEco(this,'alexa')"><span>🔵</span>Amazon Alexa</button>
      <button class="eco-btn" onclick="selectEco(this,'google')"><span>🔴</span>Google Home</button>
      <button class="eco-btn" onclick="selectEco(this,'homekit')"><span>⚪</span>Apple HomeKit</button>
    </div>
    <div class="search-wrap"><input type="text" id="searchInput" placeholder="Search devices..." oninput="renderDevices()"></div>
    <div class="cat-filter" id="catFilter"></div>
    <div class="device-count" id="deviceCount"></div>
    <div class="device-grid" id="deviceGrid"></div>
    <div class="disclaimer"><strong>Disclaimer:</strong> Compatibility information is based on publicly available data and may not reflect the latest firmware updates or regional variations. Always verify compatibility on the manufacturer's website before purchasing. Inclusion of a device does not constitute an endorsement. Some links may be affiliate links.</div>
  </div></div>

  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>
""" + SHARED_SUBSCRIBE_FLOAT + """

  <script>
  var devices=[
    {name:'Amazon Echo Dot',cat:'Speaker',alexa:'yes',google:'no',homekit:'no',matter:'no',desc:'Compact smart speaker with Alexa'},
    {name:'Google Nest Mini',cat:'Speaker',alexa:'no',google:'yes',homekit:'no',matter:'no',desc:'Compact smart speaker with Google Assistant'},
    {name:'Apple HomePod Mini',cat:'Speaker',alexa:'no',google:'no',homekit:'yes',matter:'yes',desc:'Compact smart speaker with Siri'},
    {name:'Sonos One',cat:'Speaker',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Premium smart speaker with multi-room audio'},
    {name:'Philips Hue Bulbs',cat:'Lighting',alexa:'yes',google:'yes',homekit:'yes',matter:'yes',desc:'Smart LED bulbs with 16 million colors'},
    {name:'LIFX Smart Bulb',cat:'Lighting',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Wi-Fi smart bulb — no hub required'},
    {name:'Nanoleaf Shapes',cat:'Lighting',alexa:'yes',google:'yes',homekit:'yes',matter:'yes',desc:'Modular smart light panels'},
    {name:'Wyze Bulb',cat:'Lighting',alexa:'yes',google:'yes',homekit:'no',matter:'no',desc:'Budget smart bulb with tunable white'},
    {name:'Ring Video Doorbell',cat:'Security',alexa:'yes',google:'no',homekit:'no',matter:'no',desc:'1080p video doorbell with motion detection'},
    {name:'Google Nest Doorbell',cat:'Security',alexa:'no',google:'yes',homekit:'no',matter:'no',desc:'Smart doorbell with 24/7 recording'},
    {name:'Arlo Pro 4',cat:'Security',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Wireless 2K security camera'},
    {name:'Eufy Security Cam',cat:'Security',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Local storage security camera — no subscription'},
    {name:'ecobee Smart Thermostat',cat:'Climate',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Smart thermostat with room sensors'},
    {name:'Google Nest Thermostat',cat:'Climate',alexa:'no',google:'yes',homekit:'no',matter:'no',desc:'Learning thermostat with energy savings'},
    {name:'Honeywell T9',cat:'Climate',alexa:'yes',google:'yes',homekit:'no',matter:'no',desc:'Smart thermostat with room sensors'},
    {name:'August Smart Lock',cat:'Locks',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Retrofit smart lock — keeps existing key'},
    {name:'Yale Assure Lock 2',cat:'Locks',alexa:'yes',google:'yes',homekit:'yes',matter:'yes',desc:'Keyless smart lock with touchscreen'},
    {name:'Schlage Encode Plus',cat:'Locks',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'Smart lock with Apple Home Key support'},
    {name:'iRobot Roomba j7+',cat:'Cleaning',alexa:'yes',google:'yes',homekit:'no',matter:'no',desc:'Self-emptying robot vacuum with obstacle avoidance'},
    {name:'Roborock S8 Pro',cat:'Cleaning',alexa:'yes',google:'yes',homekit:'no',matter:'no',desc:'Robot vacuum and mop combo'},
    {name:'TP-Link Kasa Plug',cat:'Plugs',alexa:'yes',google:'yes',homekit:'no',matter:'no',desc:'Wi-Fi smart plug with energy monitoring'},
    {name:'Meross Smart Plug',cat:'Plugs',alexa:'yes',google:'yes',homekit:'yes',matter:'yes',desc:'Compact smart plug with HomeKit support'},
    {name:'Eve Energy',cat:'Plugs',alexa:'no',google:'no',homekit:'yes',matter:'yes',desc:'Thread-enabled smart plug for Apple ecosystem'},
    {name:'Samsung SmartThings Hub',cat:'Hubs',alexa:'yes',google:'yes',homekit:'no',matter:'yes',desc:'Universal smart home hub supporting Zigbee, Z-Wave, Matter'},
    {name:'Apple TV 4K',cat:'Hubs',alexa:'no',google:'no',homekit:'yes',matter:'yes',desc:'HomeKit hub + streaming device'},
    {name:'Amazon Echo Show 10',cat:'Display',alexa:'yes',google:'no',homekit:'no',matter:'no',desc:'Smart display with rotating screen'},
    {name:'Google Nest Hub Max',cat:'Display',alexa:'no',google:'yes',homekit:'no',matter:'no',desc:'10" smart display with camera'},
    {name:'Lutron Caseta Switch',cat:'Switches',alexa:'yes',google:'yes',homekit:'yes',matter:'no',desc:'In-wall smart dimmer switch'},
    {name:'Leviton Decora Smart',cat:'Switches',alexa:'yes',google:'yes',homekit:'yes',matter:'yes',desc:'In-wall smart switch with Matter'},
  ];

  var activeEco='all';var activeCat='All';
  var categories=['All'];devices.forEach(function(d){if(categories.indexOf(d.cat)===-1)categories.push(d.cat)});

  function selectEco(btn,eco){activeEco=eco;document.querySelectorAll('.eco-btn').forEach(function(b){b.classList.remove('selected')});btn.classList.add('selected');renderDevices();}

  function renderFilters(){
    var html='';categories.forEach(function(c){html+='<button class="cat-btn'+(c===activeCat?' active':'')+'" onclick="setCat(\''+c+'\')">'+c+'</button>'});
    document.getElementById('catFilter').innerHTML=html;
  }
  function setCat(c){activeCat=c;renderFilters();renderDevices();}

  function renderDevices(){
    var q=(document.getElementById('searchInput').value||'').toLowerCase();
    var filtered=devices.filter(function(d){
      var matchCat=activeCat==='All'||d.cat===activeCat;
      var matchQ=!q||d.name.toLowerCase().indexOf(q)!==-1||d.cat.toLowerCase().indexOf(q)!==-1;
      var matchEco=activeEco==='all'||d[activeEco]==='yes';
      return matchCat&&matchQ&&matchEco;
    });
    document.getElementById('deviceCount').textContent='Showing '+filtered.length+' of '+devices.length+' devices';
    var grid=document.getElementById('deviceGrid');grid.innerHTML='';
    filtered.forEach(function(d){
      var card=document.createElement('div');card.className='device-card';
      var compat='<div class="compat-row">';
      compat+='<span class="compat-badge '+(d.alexa==='yes'?'yes':'no')+'">'+(d.alexa==='yes'?'✓':'✗')+' Alexa</span>';
      compat+='<span class="compat-badge '+(d.google==='yes'?'yes':'no')+'">'+(d.google==='yes'?'✓':'✗')+' Google</span>';
      compat+='<span class="compat-badge '+(d.homekit==='yes'?'yes':'no')+'">'+(d.homekit==='yes'?'✓':'✗')+' HomeKit</span>';
      if(d.matter==='yes')compat+='<span class="compat-badge yes">✓ Matter</span>';
      compat+='</div>';
      card.innerHTML='<h3>'+d.name+' <span class="cat-tag">'+d.cat+'</span></h3><p>'+d.desc+'</p>'+compat;
      grid.appendChild(card);
    });
  }

  renderFilters();renderDevices();
  </script>
</body></html>"""


# ═══════════════════════════════════════════════════════════
# Write all templates to disk
# ═══════════════════════════════════════════════════════════

def main():
    templates = {
        "index.html": INDEX_HTML,
        "post.html": POST_HTML,
        "niche_index.html": NICHE_INDEX_HTML,
        "subtopic_index.html": SUBTOPIC_INDEX_HTML,
        "tools_index.html": TOOLS_INDEX_HTML,
        "deal_finder.html": DEAL_FINDER_HTML,
        "ai_tool_finder.html": AI_TOOL_FINDER_HTML,
        "budget_calculator.html": BUDGET_CALCULATOR_HTML,
        "workout_generator.html": WORKOUT_GENERATOR_HTML,
        "pet_food_checker.html": PET_FOOD_CHECKER_HTML,
        "smart_home.html": SMART_HOME_HTML,
    }

    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in templates.items():
        filepath = TEMPLATES_DIR / filename
        filepath.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"✅ Written: {filepath.relative_to(TEMPLATES_DIR.parent.parent)}")

    print(f"\n✅ All {len(templates)} templates generated successfully!")


if __name__ == "__main__":
    main()
