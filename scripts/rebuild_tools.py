#!/usr/bin/env python3
"""Rebuild all tool templates — v2 with fixes and major enhancements.

Fixes:
  - Smart Home: JS onclick quoting bug → uses template literals
  - AI Tool Finder: JS onclick quoting bug → uses template literals
  - Pet Food Analyzer: split regex newline bug → proper \\n
  - Workout Generator: validation UX → highlights missing selections

Enhancements:
  - Market Data: TradingView real-time widgets + CoinGecko + symbol search
  - Travel Search: airport autocomplete + multi-provider deep links in-page
  - Budget Calculator: debt payoff, savings projection, pie chart, export
  - Deal Finder: open-all button, recent searches, more retailers
  - Smart Home: Amazon buy links, build-my-setup cost estimator
  - Tools Index: updated descriptions for all tools

Run:
  python scripts/rebuild_tools.py
"""
from pathlib import Path

TMPL = Path(__file__).parent.parent / "site" / "templates"

# ─── Shared Components ────────────────────────────────────────────
HEAD_FONTS = """  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">"""

NAV_CSS = """    .header{position:sticky;top:0;z-index:50;background:#1e3a8a}
    .header .container{max-width:1200px;margin:0 auto;padding:0 24px}
    .header-inner{display:flex;align-items:center;justify-content:space-between;padding:12px 0}
    .logo img{height:44px;width:auto}
    .nav-links{display:flex;gap:2px;align-items:center;flex-wrap:wrap}
    .nav-link{padding:6px 11px;border-radius:6px;font-size:13px;font-weight:500;color:rgba(255,255,255,.75);transition:all .15s;white-space:nowrap;text-decoration:none}
    .nav-link:hover,.nav-link.active{color:#fff;background:rgba(255,255,255,.12)}
    .nav-item{position:relative;display:inline-block}
    .nav-item:hover .nav-dropdown{display:block}
    .nav-dropdown{display:none;position:absolute;top:100%;left:0;background:#fff;border:1px solid #e5e7eb;border-radius:8px;box-shadow:0 8px 30px rgba(0,0,0,.12);min-width:210px;padding:6px 0;z-index:100}
    .nav-dropdown a{display:block;padding:8px 16px;font-size:13px;color:#111827;font-weight:500;transition:background .1s;text-decoration:none}
    .nav-dropdown a:hover{background:#eff6ff;color:#2563eb}
    .mobile-toggle{display:none;background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:6px}"""

NAV_HTML = """  <header class="header">
    <div class="container">
      <div class="header-inner">
        <a href="/" class="logo"><img src="/assets/logo-full-dark.svg" alt="TechLife Insights"></a>
        <nav class="nav-links" id="navLinks">
          <a href="/" class="nav-link" style="font-weight:700;color:#fff;">Home</a>
          {% for nid, niche in niches.items() %}{% if niche.enabled %}
          <div class="nav-item">
            <a href="/{{ nid }}/" class="nav-link">{{ niche.name }}</a>
            {% if niche.subtopics %}<div class="nav-dropdown">{% for sub_id, sub in niche.subtopics.items() %}<a href="/{{ nid }}/{{ sub_id }}/">{{ sub.name }}</a>{% endfor %}</div>{% endif %}
          </div>
          {% endif %}{% endfor %}
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
        </nav>
        <button class="mobile-toggle" onclick="document.getElementById('navLinks').classList.toggle('open')" aria-label="Menu">☰</button>
      </div>
    </div>
  </header>"""

SUB_CSS = """    .subscribe-float{position:fixed;bottom:24px;right:24px;z-index:1000;background:#2563eb;color:#fff!important;padding:14px 22px;border-radius:50px;font-size:14px;font-weight:700;text-decoration:none!important;box-shadow:0 4px 20px rgba(37,99,235,.45);display:flex;align-items:center;gap:8px;transition:all .2s;font-family:'Inter',sans-serif}
    .subscribe-float:hover{background:#1d4ed8;transform:translateY(-2px);box-shadow:0 6px 24px rgba(37,99,235,.55)}"""

MOBILE_CSS = """    @media(max-width:768px){
      .nav-links{display:none}.nav-links.open{display:flex;flex-direction:column;position:absolute;top:100%;left:0;right:0;background:#1e3a8a;padding:12px 24px;border-top:1px solid rgba(255,255,255,.1);gap:4px;z-index:200}
      .nav-links.open .nav-item{display:block}.nav-links.open .nav-dropdown{position:static;box-shadow:none;border:none;background:rgba(255,255,255,.05);border-radius:6px;margin:4px 0}
      .nav-links.open .nav-dropdown a{color:rgba(255,255,255,.7)}.mobile-toggle{display:block}
    }"""

FOOTER = """  <footer class="footer"><div class="container">&copy; 2026 {{ site_title }}. · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a> · <a href="/tools/">All Tools</a></div></footer>"""
SUB_BTN = """  <a href="https://techlife-insights.kit.com/be266c00d5" target="_blank" rel="noopener" class="subscribe-float">📬 Subscribe</a>"""

SHARED_STYLE_BASE = """    :root{--bg:#fff;--surface:#f8f9fb;--text:#111827;--text-secondary:#6b7280;--accent:#2563eb;--accent-hover:#1d4ed8;--accent-light:#eff6ff;--green:#059669;--red:#dc2626;--border:#e5e7eb;--shadow:0 4px 12px rgba(0,0,0,.08);--radius:10px;--max-width:1100px}
    *{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:16px;line-height:1.6}a{color:var(--accent);text-decoration:none}.container{max-width:var(--max-width);margin:0 auto;padding:0 24px}
    .footer{background:#0f172a;color:rgba(255,255,255,.7);padding:32px 0;font-size:13px;text-align:center;margin-top:48px}.footer a{color:rgba(255,255,255,.6)}.footer a:hover{color:#fff}
    .disclaimer{background:#fffbeb;border:1px solid #fde68a;border-radius:var(--radius);padding:14px 18px;font-size:12px;color:#92400e;line-height:1.7;margin:24px 0}"""


def _head(title, meta_desc):
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            '  <meta charset="UTF-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '  <title>' + title + ' | {{ site_title }}</title>\n'
            '  <meta name="description" content="' + meta_desc + '">\n'
            + HEAD_FONTS + '\n')


def _style(extra):
    return '  <style>\n' + SHARED_STYLE_BASE + '\n' + NAV_CSS + '\n' + SUB_CSS + '\n' + extra + '\n' + MOBILE_CSS + '\n  </style>\n</head>\n<body>\n'


# ─── 1. MARKET DATA ──────────────────────────────────────────────
def market_data():
    return (_head("Market Data Center — Stocks, Crypto, Forex & More",
                  "Real-time market data powered by TradingView. Live charts for stocks, crypto, forex and commodities with search.")
    + _style("""
    .ticker-wrap{width:100%}
    .page-hero{padding:28px 0 16px}.page-hero h1{font-size:28px;font-weight:900;margin-bottom:6px}
    .page-hero p{font-size:14px;color:var(--text-secondary)}.timestamp{font-size:12px;color:var(--text-secondary);margin-top:6px}
    .quick-search{display:flex;gap:10px;margin:16px 0}.quick-search input{flex:1;padding:12px 16px;border:1px solid var(--border);border-radius:8px;font-size:15px;font-family:inherit;outline:none}
    .quick-search input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.1)}
    .quick-search button{background:var(--accent);color:#fff;border:none;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;white-space:nowrap}
    .quick-chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px}
    .chip{padding:5px 12px;border:1px solid var(--border);border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;background:var(--bg);transition:all .15s}
    .chip:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}
    .chart-box{border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-bottom:28px}
    .overview-box{border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-bottom:28px}
    .section-title{font-size:20px;font-weight:800;margin:28px 0 12px}
    .crypto-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:24px}
    .crypto-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;transition:all .15s}
    .crypto-card:hover{border-color:var(--accent);box-shadow:var(--shadow)}
    .crypto-sym{font-size:12px;font-weight:700;color:var(--text-secondary);letter-spacing:.03em}
    .crypto-name{font-size:14px;font-weight:600;margin:2px 0 8px}
    .crypto-price{font-size:22px;font-weight:800;font-family:'JetBrains Mono',monospace}
    .crypto-chg{font-size:13px;font-weight:600;margin-top:2px}.crypto-chg.up{color:var(--green)}.crypto-chg.down{color:var(--red)}
    .crypto-cap{font-size:11px;color:var(--text-secondary);margin-top:4px}
    @media(max-width:768px){.quick-search{flex-direction:column}.crypto-grid{grid-template-columns:1fr 1fr}}
""")
    + NAV_HTML + """
  <!-- TradingView Ticker Tape -->
  <div class="ticker-wrap">
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {
        "symbols": [
          {"proName":"FOREXCOM:SPXUSD","title":"S&P 500"},
          {"proName":"FOREXCOM:NSXUSD","title":"US 100"},
          {"proName":"INDEX:DJI","title":"Dow Jones"},
          {"proName":"BITSTAMP:BTCUSD","title":"Bitcoin"},
          {"proName":"BITSTAMP:ETHUSD","title":"Ethereum"},
          {"proName":"FX:EURUSD","title":"EUR/USD"},
          {"proName":"FX:GBPUSD","title":"GBP/USD"},
          {"proName":"COMEX:GC1!","title":"Gold"},
          {"proName":"NYMEX:CL1!","title":"Oil"},
          {"proName":"NASDAQ:AAPL","title":"Apple"},
          {"proName":"NASDAQ:NVDA","title":"NVIDIA"},
          {"proName":"NASDAQ:MSFT","title":"Microsoft"},
          {"proName":"NASDAQ:TSLA","title":"Tesla"}
        ],
        "showSymbolLogo":true,"colorTheme":"dark","isTransparent":false,"displayMode":"adaptive","locale":"en"
      }
      </script>
    </div>
  </div>

  <div class="container">
    <div class="page-hero">
      <h1>📊 Market Data Center</h1>
      <p>Real-time charts powered by TradingView. Search any stock, crypto, forex pair, or commodity.</p>
      <div class="timestamp">Last updated: <span id="updateTime">Loading...</span> · Prices refresh in real-time (up to 15-min delay for equities)</div>
    </div>

    <div class="quick-search">
      <input type="text" id="symbolInput" placeholder="Search any symbol — e.g. AAPL, BTCUSD, EURUSD, Gold" onkeydown="if(event.key==='Enter')loadChart()">
      <button onclick="loadChart()">📊 Load Chart</button>
    </div>
    <div class="quick-chips" id="chips"></div>

    <div class="chart-box" style="height:520px;">
      <div id="tv_chart" style="height:100%;"></div>
    </div>

    <h2 class="section-title">📈 Market Overview</h2>
    <div class="overview-box" style="height:660px;">
      <div class="tradingview-widget-container" style="height:100%;">
        <div class="tradingview-widget-container__widget" style="height:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
        {
          "colorTheme":"light","dateRange":"12M","showChart":true,"locale":"en","width":"100%","height":"100%",
          "isTransparent":false,"showSymbolLogo":true,"showFloatingTooltip":true,
          "tabs":[
            {"title":"Indices","symbols":[
              {"s":"FOREXCOM:SPXUSD","d":"S&P 500"},{"s":"FOREXCOM:NSXUSD","d":"Nasdaq 100"},
              {"s":"INDEX:DJI","d":"Dow Jones"},{"s":"INDEX:RUT","d":"Russell 2000"},
              {"s":"FOREXCOM:UKXGBP","d":"FTSE 100"},{"s":"INDEX:NI225","d":"Nikkei 225"},{"s":"INDEX:DEU40","d":"DAX"}
            ]},
            {"title":"Stocks","symbols":[
              {"s":"NASDAQ:AAPL","d":"Apple"},{"s":"NASDAQ:MSFT","d":"Microsoft"},
              {"s":"NASDAQ:GOOGL","d":"Alphabet"},{"s":"NASDAQ:AMZN","d":"Amazon"},
              {"s":"NASDAQ:NVDA","d":"NVIDIA"},{"s":"NASDAQ:TSLA","d":"Tesla"},
              {"s":"NASDAQ:META","d":"Meta"},{"s":"NYSE:JPM","d":"JPMorgan"}
            ]},
            {"title":"Crypto","symbols":[
              {"s":"BITSTAMP:BTCUSD","d":"Bitcoin"},{"s":"BITSTAMP:ETHUSD","d":"Ethereum"},
              {"s":"BINANCE:SOLUSDT","d":"Solana"},{"s":"BINANCE:BNBUSDT","d":"BNB"},
              {"s":"BINANCE:XRPUSDT","d":"XRP"},{"s":"BINANCE:ADAUSDT","d":"Cardano"},{"s":"BINANCE:DOGEUSDT","d":"Dogecoin"}
            ]},
            {"title":"Forex","symbols":[
              {"s":"FX:EURUSD","d":"EUR/USD"},{"s":"FX:GBPUSD","d":"GBP/USD"},
              {"s":"FX:USDJPY","d":"USD/JPY"},{"s":"FX:USDCHF","d":"USD/CHF"},
              {"s":"FX:AUDUSD","d":"AUD/USD"},{"s":"FX:USDCAD","d":"USD/CAD"}
            ]},
            {"title":"Commodities","symbols":[
              {"s":"COMEX:GC1!","d":"Gold"},{"s":"COMEX:SI1!","d":"Silver"},
              {"s":"NYMEX:CL1!","d":"Crude Oil"},{"s":"NYMEX:NG1!","d":"Natural Gas"}
            ]}
          ]
        }
        </script>
      </div>
    </div>

    <h2 class="section-title">🪙 Crypto Live Prices</h2>
    <p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px;">Real-time via CoinGecko API · Auto-refreshes every 60s · <span id="cryptoTime">Loading...</span></p>
    <div class="crypto-grid" id="cryptoGrid"><div style="text-align:center;padding:24px;color:var(--text-secondary);grid-column:1/-1;">Loading crypto data...</div></div>

    <div class="disclaimer"><strong>⚠️ Disclaimer:</strong> Market data is for informational purposes only and may be delayed up to 15 minutes for equities. Crypto prices are near real-time via CoinGecko. This is not financial advice. Always do your own research before making investment decisions.</div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script>
  var SYMBOLS = {
    AAPL:'NASDAQ:AAPL',MSFT:'NASDAQ:MSFT',GOOGL:'NASDAQ:GOOGL',AMZN:'NASDAQ:AMZN',NVDA:'NASDAQ:NVDA',
    TSLA:'NASDAQ:TSLA',META:'NASDAQ:META',NFLX:'NASDAQ:NFLX',AMD:'NASDAQ:AMD',INTC:'NASDAQ:INTC',
    JPM:'NYSE:JPM',V:'NYSE:V',MA:'NYSE:MA',BAC:'NYSE:BAC',WMT:'NYSE:WMT',DIS:'NYSE:DIS',
    BTC:'BITSTAMP:BTCUSD',ETH:'BITSTAMP:ETHUSD',SOL:'BINANCE:SOLUSDT',XRP:'BINANCE:XRPUSDT',
    DOGE:'BINANCE:DOGEUSDT',ADA:'BINANCE:ADAUSDT',DOT:'BINANCE:DOTUSDT',AVAX:'BINANCE:AVAXUSDT',
    GOLD:'COMEX:GC1!',SILVER:'COMEX:SI1!',OIL:'NYMEX:CL1!',GAS:'NYMEX:NG1!',
    'EUR/USD':'FX:EURUSD','GBP/USD':'FX:GBPUSD','USD/JPY':'FX:USDJPY','EUR':'FX:EURUSD','GBP':'FX:GBPUSD','JPY':'FX:USDJPY'
  };

  var QUICK = [
    {label:'AAPL',sym:'NASDAQ:AAPL'},{label:'MSFT',sym:'NASDAQ:MSFT'},{label:'GOOGL',sym:'NASDAQ:GOOGL'},
    {label:'NVDA',sym:'NASDAQ:NVDA'},{label:'TSLA',sym:'NASDAQ:TSLA'},{label:'AMZN',sym:'NASDAQ:AMZN'},
    {label:'BTC',sym:'BITSTAMP:BTCUSD'},{label:'ETH',sym:'BITSTAMP:ETHUSD'},{label:'SOL',sym:'BINANCE:SOLUSDT'},
    {label:'EUR/USD',sym:'FX:EURUSD'},{label:'Gold',sym:'COMEX:GC1!'},{label:'Oil',sym:'NYMEX:CL1!'}
  ];
  var chipsEl = document.getElementById('chips');
  QUICK.forEach(function(q){
    var s = document.createElement('span');
    s.className = 'chip';
    s.textContent = q.label;
    s.addEventListener('click', function(){ document.getElementById('symbolInput').value=q.label; initChart(q.sym); });
    chipsEl.appendChild(s);
  });

  function initChart(symbol) {
    var el = document.getElementById('tv_chart');
    el.innerHTML = '';
    new TradingView.widget({
      autosize:true, symbol:symbol||'NASDAQ:AAPL', interval:'D', timezone:'Etc/UTC',
      theme:'light', style:'1', locale:'en', toolbar_bg:'#f1f3f6',
      enable_publishing:false, allow_symbol_change:true, hide_side_toolbar:false,
      watchlist:['NASDAQ:AAPL','NASDAQ:MSFT','NASDAQ:NVDA','BITSTAMP:BTCUSD','BITSTAMP:ETHUSD','FX:EURUSD','COMEX:GC1!'],
      details:true, hotlist:true, calendar:false, container_id:'tv_chart'
    });
  }

  function loadChart() {
    var q = document.getElementById('symbolInput').value.trim().toUpperCase();
    if (!q) return;
    var resolved = SYMBOLS[q] || q;
    if (resolved.indexOf(':') === -1) resolved = 'NASDAQ:' + resolved;
    initChart(resolved);
  }

  initChart('NASDAQ:AAPL');

  function updateTime() {
    var n = new Date();
    document.getElementById('updateTime').textContent = n.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'}) + ' at ' + n.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  }
  updateTime(); setInterval(updateTime, 60000);

  var CRYPTO_IDS = 'bitcoin,ethereum,solana,binancecoin,ripple,cardano,dogecoin,polkadot,avalanche-2,chainlink';
  var CRYPTO_NAMES = {bitcoin:'Bitcoin',ethereum:'Ethereum',solana:'Solana',binancecoin:'BNB',ripple:'XRP',cardano:'Cardano',dogecoin:'Dogecoin',polkadot:'Polkadot','avalanche-2':'Avalanche',chainlink:'Chainlink'};
  var CRYPTO_SYMS = {bitcoin:'BTC',ethereum:'ETH',solana:'SOL',binancecoin:'BNB',ripple:'XRP',cardano:'ADA',dogecoin:'DOGE',polkadot:'DOT','avalanche-2':'AVAX',chainlink:'LINK'};
  function fetchCrypto() {
    fetch('https://api.coingecko.com/api/v3/simple/price?ids='+CRYPTO_IDS+'&vs_currencies=usd&include_24hr_change=true&include_market_cap=true')
    .then(function(r){return r.json()})
    .then(function(data){
      var html='';
      Object.keys(CRYPTO_NAMES).forEach(function(id){
        if(!data[id]) return;
        var d=data[id], p=d.usd, c=d.usd_24h_change||0, cap=d.usd_market_cap||0;
        var up=c>=0;
        var ps=p>=1000?p.toLocaleString('en-US',{maximumFractionDigits:0}):p<1?p.toFixed(4):p.toFixed(2);
        html+='<div class="crypto-card"><div class="crypto-sym">'+CRYPTO_SYMS[id]+'</div><div class="crypto-name">'+CRYPTO_NAMES[id]+'</div><div class="crypto-price">$'+ps+'</div><div class="crypto-chg '+(up?'up':'down')+'">'+(up?'▲ +':'▼ ')+c.toFixed(2)+'%</div><div class="crypto-cap">MCap: $'+(cap/1e9).toFixed(1)+'B</div></div>';
      });
      document.getElementById('cryptoGrid').innerHTML=html;
      document.getElementById('cryptoTime').textContent='Updated '+new Date().toLocaleTimeString();
    }).catch(function(){});
  }
  fetchCrypto(); setInterval(fetchCrypto, 60000);
  </script>
</body>
</html>
""")


# ─── 2. TRAVEL SEARCH ────────────────────────────────────────────
def travel_search():
    return (_head("Travel Search — Flights, Hotels & Cars",
                  "Search and compare flights, hotels, and car rentals across multiple providers. Smart autocomplete, deep links to booking sites.")
    + _style("""
    .page-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:560px;margin:0 auto}
    .tabs{display:flex;justify-content:center;gap:8px;margin:28px 0 24px;flex-wrap:wrap}
    .tab{padding:12px 28px;border-radius:10px;border:2px solid var(--border);background:var(--bg);color:var(--text-secondary);cursor:pointer;font-size:15px;font-weight:700;font-family:inherit;transition:all .2s;display:flex;align-items:center;gap:8px}
    .tab:hover,.tab.active{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}
    .panel{display:none;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:28px;margin-bottom:24px}
    .panel.active{display:block}
    .form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:14px}
    .form-group{display:flex;flex-direction:column;gap:5px;position:relative}
    .form-group label{font-size:12px;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.04em}
    .form-group input,.form-group select{padding:12px 16px;border:1px solid var(--border);border-radius:8px;font-size:15px;font-family:inherit;background:var(--bg);color:var(--text);outline:none}
    .form-group input:focus,.form-group select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.1)}
    .ac-dropdown{position:absolute;top:100%;left:0;right:0;background:#fff;border:1px solid var(--border);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.15);max-height:250px;overflow-y:auto;z-index:200;display:none}
    .ac-item{padding:10px 16px;cursor:pointer;font-size:14px;border-bottom:1px solid #f3f4f6;transition:background .1s}
    .ac-item:hover{background:var(--accent-light)}
    .ac-item strong{color:var(--accent)}
    .ac-item small{color:var(--text-secondary);display:block;font-size:12px}
    .trip-toggle{display:flex;gap:8px;margin-bottom:14px}
    .trip-btn{padding:8px 16px;border:1px solid var(--border);border-radius:6px;background:transparent;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
    .trip-btn.active{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
    .search-btn{width:100%;padding:14px;border:none;border-radius:10px;background:var(--accent);color:#fff;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;transition:background .2s;margin-top:8px}
    .search-btn:hover{background:var(--accent-hover)}
    .results-panel{display:none;margin:24px 0}
    .results-header{font-size:16px;font-weight:700;margin-bottom:16px;padding:16px;background:var(--accent-light);border-radius:var(--radius);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
    .provider-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
    .provider-card{border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center;text-decoration:none;color:var(--text);display:block;transition:all .2s}
    .provider-card:hover{border-color:var(--accent);box-shadow:var(--shadow);transform:translateY(-2px)}
    .provider-icon{font-size:32px;margin-bottom:8px}
    .provider-card h3{font-size:14px;font-weight:700;margin-bottom:4px}
    .provider-card p{font-size:12px;color:var(--text-secondary)}
    .provider-card .go-btn{display:inline-block;margin-top:8px;background:var(--accent);color:#fff;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600}
    .open-all{background:var(--accent);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}
    .partners{padding:28px 0;border-top:1px solid var(--border);margin-top:20px}
    .partners h2{font-size:18px;font-weight:800;margin-bottom:16px;text-align:center}
    .partner-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
    .partner-card{display:flex;flex-direction:column;align-items:center;padding:20px;border:1px solid var(--border);border-radius:var(--radius);text-decoration:none;color:var(--text);transition:all .2s}
    .partner-card:hover{border-color:var(--accent);box-shadow:var(--shadow)}
    .partner-card .p-icon{font-size:32px;margin-bottom:8px}.partner-card h3{font-size:14px;font-weight:700;margin-bottom:4px}
    .partner-card p{font-size:12px;color:var(--text-secondary);text-align:center}
    .tips{padding:24px 0;border-top:1px solid var(--border);margin-top:20px}.tips h2{font-size:18px;font-weight:800;margin-bottom:12px}
    .tip{padding:10px 0;border-bottom:1px solid var(--border);font-size:14px}.tip strong{color:var(--accent)}
    @media(max-width:768px){.form-row{grid-template-columns:1fr}.tabs{flex-direction:column;align-items:stretch}.provider-grid{grid-template-columns:1fr 1fr}}
""")
    + NAV_HTML + """
  <div class="page-hero"><h1>✈️ Travel Search Center</h1><p>Compare flights, hotels & car rentals across top providers — results shown right here</p></div>

  <div class="container">
    <div class="tabs">
      <button class="tab active" onclick="switchTab('flights',this)">✈️ Flights</button>
      <button class="tab" onclick="switchTab('hotels',this)">🏨 Hotels</button>
      <button class="tab" onclick="switchTab('cars',this)">🚗 Car Rental</button>
    </div>

    <!-- FLIGHTS -->
    <div class="panel active" id="panel-flights">
      <div class="trip-toggle"><button class="trip-btn active" onclick="setTrip('round',this)">↔ Round Trip</button><button class="trip-btn" onclick="setTrip('oneway',this)">→ One Way</button></div>
      <div class="form-row">
        <div class="form-group"><label>From</label><input type="text" id="f-from" placeholder="City or airport — e.g. New York" autocomplete="off" oninput="showAC(this,'f-from-ac')"><div class="ac-dropdown" id="f-from-ac"></div></div>
        <div class="form-group"><label>To</label><input type="text" id="f-to" placeholder="City or airport — e.g. London" autocomplete="off" oninput="showAC(this,'f-to-ac')"><div class="ac-dropdown" id="f-to-ac"></div></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Departure</label><input type="date" id="f-depart"></div>
        <div class="form-group" id="f-return-group"><label>Return</label><input type="date" id="f-return"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Passengers</label><select id="f-pax"><option value="1">1 Adult</option><option value="2" selected>2 Adults</option><option value="3">3 Adults</option><option value="4">4 Adults</option></select></div>
        <div class="form-group"><label>Class</label><select id="f-class"><option value="economy">Economy</option><option value="business">Business</option><option value="first">First</option></select></div>
      </div>
      <button class="search-btn" onclick="searchFlights()">🔍 Search All Flight Providers</button>
    </div>

    <!-- HOTELS -->
    <div class="panel" id="panel-hotels">
      <div class="form-row">
        <div class="form-group"><label>Destination</label><input type="text" id="h-dest" placeholder="City — e.g. Paris" autocomplete="off" oninput="showAC(this,'h-dest-ac')"><div class="ac-dropdown" id="h-dest-ac"></div></div>
        <div class="form-group"><label>Guests</label><select id="h-guests"><option value="1">1 Guest</option><option value="2" selected>2 Guests</option><option value="3">3 Guests</option><option value="4">4 Guests</option></select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Check-in</label><input type="date" id="h-checkin"></div>
        <div class="form-group"><label>Check-out</label><input type="date" id="h-checkout"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Rooms</label><select id="h-rooms"><option value="1">1 Room</option><option value="2">2 Rooms</option></select></div>
        <div class="form-group"></div>
      </div>
      <button class="search-btn" onclick="searchHotels()">🔍 Search All Hotel Providers</button>
    </div>

    <!-- CARS -->
    <div class="panel" id="panel-cars">
      <div class="form-row">
        <div class="form-group"><label>Pick-up Location</label><input type="text" id="c-pickup" placeholder="City or airport" autocomplete="off" oninput="showAC(this,'c-pickup-ac')"><div class="ac-dropdown" id="c-pickup-ac"></div></div>
        <div class="form-group"><label>Drop-off Location</label><input type="text" id="c-dropoff" placeholder="Same as pick-up (optional)" autocomplete="off" oninput="showAC(this,'c-drop-ac')"><div class="ac-dropdown" id="c-drop-ac"></div></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Pick-up Date</label><input type="date" id="c-pickdate"></div>
        <div class="form-group"><label>Drop-off Date</label><input type="date" id="c-dropdate"></div>
      </div>
      <button class="search-btn" onclick="searchCars()">🔍 Search All Car Rental Providers</button>
    </div>

    <!-- RESULTS -->
    <div class="results-panel" id="results">
      <div class="results-header"><span id="resultsTitle">Results</span><button class="open-all" onclick="openAll()">Open All Providers ↗</button></div>
      <div class="provider-grid" id="providerGrid"></div>
    </div>

    <div class="tips">
      <h2>💡 Smart Booking Tips</h2>
      <div class="tip"><strong>Compare across providers</strong> — prices can vary 20-40% for the same flight or hotel.</div>
      <div class="tip"><strong>Book 6-8 weeks ahead</strong> for domestic flights, 2-3 months for international.</div>
      <div class="tip"><strong>Use incognito mode</strong> — some sites raise prices based on repeated searches.</div>
      <div class="tip"><strong>Be flexible with dates</strong> — flying midweek (Tue-Thu) is often 20-30% cheaper.</div>
      <div class="tip"><strong>Check direct</strong> — after finding a deal, check the airline/hotel's own site for matching rates.</div>
    </div>

    <div class="partners">
      <h2>🤝 Trusted Booking Partners</h2>
      <div class="partner-grid">
        <a href="https://www.skyscanner.com" target="_blank" rel="noopener" class="partner-card"><div class="p-icon">✈️</div><h3>Skyscanner</h3><p>Compare 1,200+ airlines</p></a>
        <a href="https://www.booking.com" target="_blank" rel="noopener" class="partner-card"><div class="p-icon">🏨</div><h3>Booking.com</h3><p>28M+ accommodations</p></a>
        <a href="https://www.kayak.com" target="_blank" rel="noopener" class="partner-card"><div class="p-icon">🛶</div><h3>Kayak</h3><p>Flights, hotels & cars</p></a>
        <a href="https://www.hostelworld.com" target="_blank" rel="noopener" class="partner-card"><div class="p-icon">🎒</div><h3>Hostelworld</h3><p>Budget hostels worldwide</p></a>
        <a href="https://www.rentalcars.com" target="_blank" rel="noopener" class="partner-card"><div class="p-icon">🚗</div><h3>RentalCars</h3><p>900+ car rental companies</p></a>
        <a href="https://www.safetywing.com" target="_blank" rel="noopener" class="partner-card"><div class="p-icon">🛡️</div><h3>SafetyWing</h3><p>Travel medical insurance</p></a>
      </div>
    </div>

    <div class="disclaimer"><strong>⚠️ Transparency Notice:</strong> When you click a provider link, you'll be taken to their official website with your search pre-filled. We may earn a referral commission at no extra cost to you. All results come directly from the provider. Prices and availability change frequently — always verify before booking.</div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  // Airport database
  var AP = [
    {c:'JFK',city:'New York',n:'John F. Kennedy Intl',co:'US'},{c:'EWR',city:'Newark',n:'Newark Liberty Intl',co:'US'},
    {c:'LGA',city:'New York',n:'LaGuardia',co:'US'},{c:'LAX',city:'Los Angeles',n:'Los Angeles Intl',co:'US'},
    {c:'SFO',city:'San Francisco',n:'San Francisco Intl',co:'US'},{c:'ORD',city:'Chicago',n:"O'Hare Intl",co:'US'},
    {c:'ATL',city:'Atlanta',n:'Hartsfield-Jackson',co:'US'},{c:'DFW',city:'Dallas',n:'Dallas/Fort Worth Intl',co:'US'},
    {c:'DEN',city:'Denver',n:'Denver Intl',co:'US'},{c:'SEA',city:'Seattle',n:'Seattle-Tacoma Intl',co:'US'},
    {c:'MIA',city:'Miami',n:'Miami Intl',co:'US'},{c:'BOS',city:'Boston',n:'Logan Intl',co:'US'},
    {c:'IAH',city:'Houston',n:'George Bush Intercontinental',co:'US'},{c:'PHX',city:'Phoenix',n:'Phoenix Sky Harbor',co:'US'},
    {c:'LAS',city:'Las Vegas',n:'Harry Reid Intl',co:'US'},{c:'MCO',city:'Orlando',n:'Orlando Intl',co:'US'},
    {c:'DTW',city:'Detroit',n:'Detroit Metropolitan',co:'US'},{c:'MSP',city:'Minneapolis',n:'Minneapolis-Saint Paul',co:'US'},
    {c:'PHL',city:'Philadelphia',n:'Philadelphia Intl',co:'US'},{c:'IAD',city:'Washington DC',n:'Dulles Intl',co:'US'},
    {c:'SAN',city:'San Diego',n:'San Diego Intl',co:'US'},{c:'TPA',city:'Tampa',n:'Tampa Intl',co:'US'},
    {c:'HNL',city:'Honolulu',n:'Daniel K. Inouye Intl',co:'US'},{c:'AUS',city:'Austin',n:'Austin-Bergstrom',co:'US'},
    {c:'LHR',city:'London',n:'Heathrow',co:'GB'},{c:'LGW',city:'London',n:'Gatwick',co:'GB'},
    {c:'CDG',city:'Paris',n:'Charles de Gaulle',co:'FR'},{c:'AMS',city:'Amsterdam',n:'Schiphol',co:'NL'},
    {c:'FRA',city:'Frankfurt',n:'Frankfurt am Main',co:'DE'},{c:'MAD',city:'Madrid',n:'Adolfo Suarez Madrid-Barajas',co:'ES'},
    {c:'BCN',city:'Barcelona',n:'El Prat',co:'ES'},{c:'FCO',city:'Rome',n:'Leonardo da Vinci-Fiumicino',co:'IT'},
    {c:'MUC',city:'Munich',n:'Franz Josef Strauss',co:'DE'},{c:'IST',city:'Istanbul',n:'Istanbul Airport',co:'TR'},
    {c:'ZRH',city:'Zurich',n:'Zurich Airport',co:'CH'},{c:'VIE',city:'Vienna',n:'Vienna Intl',co:'AT'},
    {c:'CPH',city:'Copenhagen',n:'Copenhagen Airport',co:'DK'},{c:'DUB',city:'Dublin',n:'Dublin Airport',co:'IE'},
    {c:'LIS',city:'Lisbon',n:'Humberto Delgado',co:'PT'},{c:'ATH',city:'Athens',n:'Eleftherios Venizelos',co:'GR'},
    {c:'NRT',city:'Tokyo',n:'Narita Intl',co:'JP'},{c:'HND',city:'Tokyo',n:'Haneda',co:'JP'},
    {c:'PEK',city:'Beijing',n:'Beijing Capital Intl',co:'CN'},{c:'PVG',city:'Shanghai',n:'Pudong Intl',co:'CN'},
    {c:'HKG',city:'Hong Kong',n:'Hong Kong Intl',co:'HK'},{c:'SIN',city:'Singapore',n:'Changi Airport',co:'SG'},
    {c:'ICN',city:'Seoul',n:'Incheon Intl',co:'KR'},{c:'BKK',city:'Bangkok',n:'Suvarnabhumi',co:'TH'},
    {c:'DEL',city:'New Delhi',n:'Indira Gandhi Intl',co:'IN'},{c:'BOM',city:'Mumbai',n:'Chhatrapati Shivaji Maharaj',co:'IN'},
    {c:'DXB',city:'Dubai',n:'Dubai Intl',co:'AE'},{c:'DOH',city:'Doha',n:'Hamad Intl',co:'QA'},
    {c:'AUH',city:'Abu Dhabi',n:'Zayed Intl',co:'AE'},
    {c:'SYD',city:'Sydney',n:'Kingsford Smith',co:'AU'},{c:'MEL',city:'Melbourne',n:'Melbourne Airport',co:'AU'},
    {c:'AKL',city:'Auckland',n:'Auckland Airport',co:'NZ'},
    {c:'YYZ',city:'Toronto',n:'Pearson Intl',co:'CA'},{c:'YVR',city:'Vancouver',n:'Vancouver Intl',co:'CA'},
    {c:'MEX',city:'Mexico City',n:'Benito Juarez Intl',co:'MX'},{c:'GRU',city:'Sao Paulo',n:'Guarulhos Intl',co:'BR'},
    {c:'SCL',city:'Santiago',n:'Arturo Merino Benitez',co:'CL'},{c:'BOG',city:'Bogota',n:'El Dorado Intl',co:'CO'},
    {c:'EZE',city:'Buenos Aires',n:'Ministro Pistarini',co:'AR'},{c:'CUN',city:'Cancun',n:'Cancun Intl',co:'MX'},
    {c:'KUL',city:'Kuala Lumpur',n:'KL Intl',co:'MY'},{c:'MNL',city:'Manila',n:'Ninoy Aquino Intl',co:'PH'}
  ];

  var selectedFrom={}, selectedTo={}, tripType='round';

  function showAC(input, dropId) {
    var q = input.value.toLowerCase();
    var drop = document.getElementById(dropId);
    if (q.length < 2) { drop.style.display='none'; return; }
    var matches = AP.filter(function(a){
      return a.c.toLowerCase().indexOf(q)!==-1 || a.city.toLowerCase().indexOf(q)!==-1 || a.n.toLowerCase().indexOf(q)!==-1;
    }).slice(0, 8);
    if (!matches.length) { drop.style.display='none'; return; }
    drop.innerHTML = '';
    matches.forEach(function(a) {
      var d = document.createElement('div');
      d.className = 'ac-item';
      d.innerHTML = '<strong>' + a.c + '</strong> — ' + a.city + '<small>' + a.n + ', ' + a.co + '</small>';
      d.addEventListener('click', function() {
        input.value = a.c + ' — ' + a.city;
        input.dataset.code = a.c;
        input.dataset.city = a.city;
        drop.style.display = 'none';
      });
      drop.appendChild(d);
    });
    drop.style.display = 'block';
  }

  document.addEventListener('click', function(e) {
    document.querySelectorAll('.ac-dropdown').forEach(function(d) {
      if (!d.contains(e.target) && e.target !== d.previousElementSibling) d.style.display='none';
    });
  });

  function switchTab(tab, btn) {
    document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active')});
    document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active')});
    btn.classList.add('active');
    document.getElementById('panel-'+tab).classList.add('active');
    document.getElementById('results').style.display='none';
  }

  function setTrip(type, btn) {
    tripType = type;
    document.querySelectorAll('.trip-btn').forEach(function(b){b.classList.remove('active')});
    btn.classList.add('active');
    document.getElementById('f-return-group').style.display = type==='oneway' ? 'none' : 'flex';
  }

  // Set default dates
  (function(){
    var today=new Date(), tmrw=new Date(today), nw=new Date(today);
    tmrw.setDate(today.getDate()+1); nw.setDate(today.getDate()+8);
    var fmt=function(d){return d.toISOString().split('T')[0]};
    ['f-depart','h-checkin','c-pickdate'].forEach(function(id){document.getElementById(id).value=fmt(tmrw)});
    ['f-return','h-checkout','c-dropdate'].forEach(function(id){document.getElementById(id).value=fmt(nw)});
  })();

  var lastProviderUrls = [];
  function showResults(title, providers) {
    lastProviderUrls = providers.map(function(p){return p.url});
    document.getElementById('resultsTitle').textContent = title;
    var grid = document.getElementById('providerGrid');
    grid.innerHTML = '';
    providers.forEach(function(p) {
      var card = document.createElement('a');
      card.href = p.url; card.target='_blank'; card.rel='noopener'; card.className='provider-card';
      card.innerHTML = '<div class="provider-icon">'+p.icon+'</div><h3>'+p.name+'</h3><p>'+p.desc+'</p><span class="go-btn">Search '+p.name+' →</span>';
      grid.appendChild(card);
    });
    var rp = document.getElementById('results');
    rp.style.display = 'block';
    rp.scrollIntoView({behavior:'smooth'});
  }

  function openAll() { lastProviderUrls.forEach(function(u){window.open(u,'_blank')}); }

  function getCode(id) { var el=document.getElementById(id); return (el.dataset.code||el.value.split(' ')[0]||'').toUpperCase(); }
  function getCity(id) { var el=document.getElementById(id); return el.dataset.city||el.value.replace(/\\s*—.*$/,'').trim(); }

  function searchFlights() {
    var from=getCode('f-from'), to=getCode('f-to');
    var dep=document.getElementById('f-depart').value, ret=document.getElementById('f-return').value;
    var pax=document.getElementById('f-pax').value, cls=document.getElementById('f-class').value;
    if(!from||!to||!dep){alert('Please fill in From, To, and Departure date');return;}
    var fromCity=getCity('f-from'), toCity=getCity('f-to');
    var skyDep=dep.replace(/-/g,'').slice(2), skyRet=ret?ret.replace(/-/g,'').slice(2):'';
    var providers = [
      {name:'Google Flights',icon:'✈️',desc:'Comprehensive search across airlines',
       url:'https://www.google.com/travel/flights?q='+encodeURIComponent('flights from '+fromCity+' '+from+' to '+toCity+' '+to+' on '+dep+(ret?' return '+ret:''))},
      {name:'Skyscanner',icon:'🔍',desc:'Compare 1,200+ airlines & agents',
       url:'https://www.skyscanner.com/transport/flights/'+from.toLowerCase()+'/'+to.toLowerCase()+'/'+skyDep+'/'+(tripType==='round'?skyRet+'/?':'?')+'adults='+pax+'&cabinclass='+cls},
      {name:'Kayak',icon:'🛶',desc:'Flexible search with price alerts',
       url:'https://www.kayak.com/flights/'+from+'-'+to+'/'+dep+'/'+(tripType==='round'?ret+'/':'')+pax+'adults/'+cls+'?sort=bestflight_a'},
      {name:'Momondo',icon:'🌍',desc:'Find hidden deals & budget airlines',
       url:'https://www.momondo.com/flight-search/'+from+'-'+to+'/'+dep+'/'+(tripType==='round'?ret:'')},
      {name:'Kiwi.com',icon:'🥝',desc:'Virtual interlining for cheaper routes',
       url:'https://www.kiwi.com/en/search/results/'+from+'/'+to+'/'+dep+'/'+(tripType==='round'?ret:'')}
    ];
    showResults('✈️ Flights: '+from+' → '+to+' · '+dep+(tripType==='round'?' – '+ret:' (one way)')+' · '+pax+' pax', providers);
  }

  function searchHotels() {
    var dest=getCity('h-dest'), ci=document.getElementById('h-checkin').value, co=document.getElementById('h-checkout').value;
    var guests=document.getElementById('h-guests').value, rooms=document.getElementById('h-rooms').value;
    if(!dest||!ci||!co){alert('Please fill in destination and dates');return;}
    var ed=encodeURIComponent(dest);
    var providers = [
      {name:'Booking.com',icon:'🏨',desc:'28M+ listings, free cancellation options',
       url:'https://www.booking.com/searchresults.html?ss='+ed+'&checkin='+ci+'&checkout='+co+'&group_adults='+guests+'&no_rooms='+rooms},
      {name:'Hotels.com',icon:'🌟',desc:'Rewards program, price match guarantee',
       url:'https://www.hotels.com/search.do?q-destination='+ed+'&q-check-in='+ci+'&q-check-out='+co+'&q-rooms='+rooms+'&q-room-0-adults='+guests},
      {name:'Agoda',icon:'🏢',desc:'Best for Asia-Pacific, member deals',
       url:'https://www.agoda.com/search?q='+ed+'&checkIn='+ci+'&checkOut='+co+'&rooms='+rooms+'&adults='+guests},
      {name:'Trivago',icon:'🔎',desc:'Meta-search across 400+ booking sites',
       url:'https://www.trivago.com/en-US/srl?search='+ed},
      {name:'Hostelworld',icon:'🎒',desc:'Budget hostels in 170+ countries',
       url:'https://www.hostelworld.com/s?q='+ed+'&dateFrom='+ci+'&dateTo='+co+'&guests='+guests}
    ];
    showResults('🏨 Hotels in '+dest+' · '+ci+' to '+co+' · '+guests+' guests', providers);
  }

  function searchCars() {
    var loc=getCity('c-pickup'), pd=document.getElementById('c-pickdate').value, dd=document.getElementById('c-dropdate').value;
    if(!loc||!pd||!dd){alert('Please fill in location and dates');return;}
    var el=encodeURIComponent(loc);
    var providers = [
      {name:'Kayak Cars',icon:'🛶',desc:'Compare across major rental companies',
       url:'https://www.kayak.com/cars/'+el+'/'+pd+'/'+dd+'?sort=price_a'},
      {name:'RentalCars.com',icon:'🚗',desc:'900+ rental companies, best price guarantee',
       url:'https://www.rentalcars.com/search-results?location='+el+'&puDate='+pd+'&doDate='+dd},
      {name:'Discover Cars',icon:'🔍',desc:'Compare 500+ car rental companies',
       url:'https://www.discovercars.com/search?pick='+el+'&pdate='+pd+'&ddate='+dd},
      {name:'AutoEurope',icon:'🌍',desc:'20,000+ locations, price match',
       url:'https://www.autoeurope.com/go/searchresults.cfm?location='+el+'&puDate='+pd+'&doDate='+dd}
    ];
    showResults('🚗 Car Rental in '+loc+' · '+pd+' to '+dd, providers);
  }
  </script>
</body>
</html>
""")


# ─── 3. DEAL FINDER ──────────────────────────────────────────────
def deal_finder():
    return (_head("Deal Finder — Search for the Best Deals",
                  "Search across Amazon, Best Buy, Walmart, Target and more. Compare deals on any product with one click.")
    + _style("""
    .tool-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:#fff;padding:48px 0;text-align:center}
    .tool-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.tool-hero p{font-size:16px;opacity:.8;max-width:520px;margin:0 auto 28px}
    .search-box{max-width:620px;margin:0 auto;display:flex;gap:0;border-radius:50px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.3)}
    .search-box input{flex:1;padding:16px 24px;border:none;font-size:16px;font-family:inherit;outline:none}
    .search-box button{background:var(--accent);color:#fff;border:none;padding:16px 28px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:background .2s;white-space:nowrap}
    .search-box button:hover{background:var(--accent-hover)}
    .results{padding:32px 0;display:none}
    .results-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px}
    .results-header h2{font-size:20px;font-weight:800}
    .open-all-btn{background:var(--accent);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}
    .retailer-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
    .retailer-card{border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center;transition:all .2s;text-decoration:none;color:var(--text);display:block}
    .retailer-card:hover{border-color:var(--accent);box-shadow:var(--shadow);transform:translateY(-2px)}
    .retailer-logo{font-size:36px;margin-bottom:8px}
    .retailer-card h3{font-size:15px;font-weight:700;margin-bottom:4px}
    .retailer-card p{font-size:12px;color:var(--text-secondary)}
    .go-btn{display:inline-block;background:var(--accent);color:#fff;padding:6px 16px;border-radius:6px;font-size:12px;font-weight:600;margin-top:10px}
    .categories{padding:28px 0}.categories h2{font-size:20px;font-weight:800;margin-bottom:16px}
    .cat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
    .cat-pill{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px;text-align:center;cursor:pointer;transition:all .15s;font-size:13px;font-weight:600}
    .cat-pill:hover{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
    .cat-pill span{display:block;font-size:22px;margin-bottom:4px}
    .recent{padding:16px 0}.recent h3{font-size:14px;font-weight:700;color:var(--text-secondary);margin-bottom:8px}
    .recent-chips{display:flex;flex-wrap:wrap;gap:6px}
    .recent-chip{padding:4px 12px;border:1px solid var(--border);border-radius:20px;font-size:12px;cursor:pointer;background:var(--bg);transition:all .15s}
    .recent-chip:hover{border-color:var(--accent);color:var(--accent)}
    .tips{padding:24px 0;border-top:1px solid var(--border)}.tips h2{font-size:18px;font-weight:800;margin-bottom:12px}
    .tip-item{padding:10px 0;border-bottom:1px solid var(--border);font-size:14px}.tip-item strong{color:var(--accent)}
    @media(max-width:768px){.retailer-grid{grid-template-columns:1fr 1fr}.cat-grid{grid-template-columns:1fr 1fr}.tool-hero h1{font-size:24px}}
""")
    + NAV_HTML + """
  <div class="tool-hero">
    <h1>🔍 Deal Finder</h1>
    <p>Search any product across top retailers — compare deals with one click</p>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="e.g. wireless headphones, MacBook Pro, air fryer" autofocus>
      <button onclick="searchDeals()">Search Deals</button>
    </div>
  </div>

  <div class="container">
    <div class="recent" id="recentSection" style="display:none"><h3>Recent Searches</h3><div class="recent-chips" id="recentChips"></div></div>

    <div class="results" id="results">
      <div class="results-header"><h2>Search "<span id="queryDisplay"></span>" on:</h2><button class="open-all-btn" onclick="openAll()">🚀 Open All Retailers</button></div>
      <div class="retailer-grid" id="retailerGrid"></div>
    </div>

    <div class="categories">
      <h2>Popular Categories</h2>
      <div class="cat-grid">
        <div class="cat-pill" onclick="qSearch('wireless headphones')"><span>🎧</span>Headphones</div>
        <div class="cat-pill" onclick="qSearch('laptop deals')"><span>💻</span>Laptops</div>
        <div class="cat-pill" onclick="qSearch('smart home devices')"><span>🏠</span>Smart Home</div>
        <div class="cat-pill" onclick="qSearch('fitness tracker')"><span>⌚</span>Fitness Tech</div>
        <div class="cat-pill" onclick="qSearch('kitchen appliances')"><span>🍳</span>Kitchen</div>
        <div class="cat-pill" onclick="qSearch('gaming accessories')"><span>🎮</span>Gaming</div>
        <div class="cat-pill" onclick="qSearch('pet supplies')"><span>🐾</span>Pet Supplies</div>
        <div class="cat-pill" onclick="qSearch('home office desk')"><span>🪑</span>Office</div>
        <div class="cat-pill" onclick="qSearch('robot vacuum')"><span>🤖</span>Robot Vacuums</div>
        <div class="cat-pill" onclick="qSearch('air purifier')"><span>💨</span>Air Purifiers</div>
        <div class="cat-pill" onclick="qSearch('running shoes')"><span>👟</span>Running Shoes</div>
        <div class="cat-pill" onclick="qSearch('power tools')"><span>🔧</span>Power Tools</div>
      </div>
    </div>

    <div class="tips">
      <h2>💡 Smart Shopping Tips</h2>
      <div class="tip-item"><strong>Compare prices</strong> across at least 3 retailers — prices can vary 20-40%.</div>
      <div class="tip-item"><strong>Check for coupons</strong> — search "[retailer name] coupon code" before checkout.</div>
      <div class="tip-item"><strong>Use CamelCamelCamel</strong> to check Amazon price history before buying.</div>
      <div class="tip-item"><strong>Buy refurbished</strong> — certified refurbished products offer 20-50% savings.</div>
      <div class="tip-item"><strong>Time your purchases</strong> — Black Friday, Prime Day, end-of-season sales.</div>
    </div>

    <div class="disclaimer"><strong>Affiliate Disclosure:</strong> Some retailer links contain affiliate tags. We may earn a commission at no extra cost to you. Prices and availability are determined by retailers and may change.</div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  var retailers = [
    {name:'Amazon',icon:'📦',search:'https://www.amazon.com/s?k=QUERY&tag=techlife0ac-20',desc:'Millions of products + Prime shipping'},
    {name:'Best Buy',icon:'🏪',search:'https://www.bestbuy.com/site/searchpage.jsp?st=QUERY',desc:'Electronics, appliances & tech'},
    {name:'Walmart',icon:'🛒',search:'https://www.walmart.com/search?q=QUERY',desc:'Everyday low prices'},
    {name:'Target',icon:'🎯',search:'https://www.target.com/s?searchTerm=QUERY',desc:'Quality products, great prices'},
    {name:'Newegg',icon:'💾',search:'https://www.newegg.com/p/pl?d=QUERY',desc:'Tech & computer hardware'},
    {name:'eBay',icon:'🏷️',search:'https://www.ebay.com/sch/i.html?_nkw=QUERY',desc:'New, used & refurbished deals'},
    {name:'B&H Photo',icon:'📷',search:'https://www.bhphotovideo.com/c/search?q=QUERY',desc:'Pro gear: cameras, audio, tech'},
    {name:'Costco',icon:'🏬',search:'https://www.costco.com/CatalogSearch?dept=All&keyword=QUERY',desc:'Bulk deals for members'},
    {name:'Google Shopping',icon:'🔎',search:'https://www.google.com/search?tbm=shop&q=QUERY',desc:'Compare prices across all stores'}
  ];
  var lastUrls = [];

  function searchDeals() {
    var q = document.getElementById('searchInput').value.trim();
    if(!q) return;
    saveRecent(q);
    document.getElementById('queryDisplay').textContent = q;
    var grid = document.getElementById('retailerGrid');
    grid.innerHTML = '';
    lastUrls = [];
    retailers.forEach(function(r){
      var url = r.search.replace('QUERY', encodeURIComponent(q));
      lastUrls.push(url);
      var card = document.createElement('a');
      card.href=url; card.target='_blank'; card.rel='noopener'; card.className='retailer-card';
      card.innerHTML='<div class="retailer-logo">'+r.icon+'</div><h3>'+r.name+'</h3><p>'+r.desc+'</p><span class="go-btn">Search '+r.name+' →</span>';
      grid.appendChild(card);
    });
    document.getElementById('results').style.display='block';
    document.getElementById('results').scrollIntoView({behavior:'smooth'});
  }
  function openAll(){lastUrls.forEach(function(u){window.open(u,'_blank')})}
  function qSearch(q){document.getElementById('searchInput').value=q;searchDeals();window.scrollTo({top:0,behavior:'smooth'})}
  document.getElementById('searchInput').addEventListener('keydown',function(e){if(e.key==='Enter')searchDeals()});

  function saveRecent(q){
    var arr=JSON.parse(localStorage.getItem('dealSearches')||'[]');
    arr=arr.filter(function(s){return s!==q});
    arr.unshift(q);
    if(arr.length>8) arr=arr.slice(0,8);
    localStorage.setItem('dealSearches',JSON.stringify(arr));
    renderRecent();
  }
  function renderRecent(){
    var arr=JSON.parse(localStorage.getItem('dealSearches')||'[]');
    if(!arr.length){document.getElementById('recentSection').style.display='none';return;}
    document.getElementById('recentSection').style.display='block';
    var html='';
    arr.forEach(function(s){html+='<span class="recent-chip" onclick="qSearch(\\''+s.replace(/'/g,"\\\\'")+'\\')">'+s+'</span>'});
    document.getElementById('recentChips').innerHTML=html;
  }
  renderRecent();
  </script>
</body>
</html>
""")


# ─── 4. AI TOOL DIRECTORY (fixed JS quoting) ─────────────────────
def ai_tool_finder():
    return (_head("AI Tool Directory — Find the Best AI Tools",
                  "Browse 60+ curated AI tools organized by category. Writing, images, video, code, voice, productivity and more.")
    + _style("""
    .page-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.8;max-width:520px;margin:0 auto 20px}
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
    .ai-card .visit-btn{display:inline-block;margin-top:10px;background:var(--accent);color:#fff;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;transition:background .2s;text-decoration:none}
    .ai-card .visit-btn:hover{background:var(--accent-hover)}
    .tool-count{text-align:center;padding:8px 0;font-size:13px;color:var(--text-secondary)}
    @media(max-width:768px){.tools-grid{grid-template-columns:1fr}}
""")
    + NAV_HTML + """
  <div class="page-hero">
    <h1>🤖 AI Tool Directory</h1>
    <p>Find the perfect AI tool for any task — 60+ tools organized by category</p>
    <div class="search-wrap"><input type="text" id="searchInput" placeholder="Search AI tools..." oninput="filterTools()"></div>
  </div>
  <div class="container">
    <div class="filters" id="filters"></div>
    <div class="tool-count" id="toolCount"></div>
    <div class="tools-grid" id="toolsGrid"></div>
    <div class="disclaimer"><strong>Disclaimer:</strong> This directory is curated for informational purposes. Some links may be affiliate links. Pricing may change — verify on the official website.</div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  var aiTools = [
    {name:'ChatGPT',cat:'Writing',desc:'Conversational AI for writing, analysis, coding, and creative tasks.',pricing:'Free / $20/mo',url:'https://chat.openai.com'},
    {name:'Claude',cat:'Writing',desc:"Anthropic's AI assistant for thoughtful, nuanced writing and analysis.",pricing:'Free / $20/mo',url:'https://claude.ai'},
    {name:'Gemini',cat:'Writing',desc:"Google's multimodal AI for text, images, and code generation.",pricing:'Free / $20/mo',url:'https://gemini.google.com'},
    {name:'Jasper',cat:'Writing',desc:'AI writing platform for marketing copy, blogs, and social media.',pricing:'From $49/mo',url:'https://www.jasper.ai'},
    {name:'Copy.ai',cat:'Writing',desc:'Generate marketing copy, emails, and social posts with AI.',pricing:'Free / $49/mo',url:'https://www.copy.ai'},
    {name:'Writesonic',cat:'Writing',desc:'AI writer for SEO articles, ad copy, and product descriptions.',pricing:'Free / $16/mo',url:'https://writesonic.com'},
    {name:'Grammarly',cat:'Writing',desc:'AI writing assistant for grammar, tone, and clarity.',pricing:'Free / $12/mo',url:'https://www.grammarly.com'},
    {name:'QuillBot',cat:'Writing',desc:'AI paraphrasing and summarization tool for better writing.',pricing:'Free / $10/mo',url:'https://quillbot.com'},
    {name:'Midjourney',cat:'Images',desc:'Create stunning AI art and images from text prompts.',pricing:'From $10/mo',url:'https://www.midjourney.com'},
    {name:'DALL-E 3',cat:'Images',desc:"OpenAI's image generator for art, photos, and designs.",pricing:'Included with Plus',url:'https://openai.com/dall-e-3'},
    {name:'Stable Diffusion',cat:'Images',desc:'Open-source AI image generation — run locally or in cloud.',pricing:'Free (open source)',url:'https://stability.ai'},
    {name:'Leonardo AI',cat:'Images',desc:'AI image generation for creative projects and game assets.',pricing:'Free / $12/mo',url:'https://leonardo.ai'},
    {name:'Canva AI',cat:'Images',desc:'AI-powered design tool for social media and presentations.',pricing:'Free / $13/mo',url:'https://www.canva.com'},
    {name:'Adobe Firefly',cat:'Images',desc:'AI image generation integrated into Adobe Creative Cloud.',pricing:'Free / $10/mo',url:'https://firefly.adobe.com'},
    {name:'Runway',cat:'Video',desc:'AI video generation, editing, and visual effects platform.',pricing:'Free / $12/mo',url:'https://runwayml.com'},
    {name:'Synthesia',cat:'Video',desc:'Create AI avatar videos for training and marketing.',pricing:'From $22/mo',url:'https://www.synthesia.io'},
    {name:'Descript',cat:'Video',desc:'AI video & podcast editor — edit video by editing text.',pricing:'Free / $24/mo',url:'https://www.descript.com'},
    {name:'HeyGen',cat:'Video',desc:'AI spokesperson videos with realistic avatars and voices.',pricing:'Free / $24/mo',url:'https://www.heygen.com'},
    {name:'Luma AI',cat:'Video',desc:'3D capture and AI video generation from text and images.',pricing:'Free / $10/mo',url:'https://lumalabs.ai'},
    {name:'GitHub Copilot',cat:'Code',desc:'AI pair programmer with code suggestions in your editor.',pricing:'Free / $10/mo',url:'https://github.com/features/copilot'},
    {name:'Cursor',cat:'Code',desc:'AI-first code editor built for AI-assisted development.',pricing:'Free / $20/mo',url:'https://cursor.sh'},
    {name:'Replit AI',cat:'Code',desc:'Cloud IDE with AI code generation and deployment.',pricing:'Free / $25/mo',url:'https://replit.com'},
    {name:'Tabnine',cat:'Code',desc:'AI code completion that runs locally for privacy.',pricing:'Free / $12/mo',url:'https://www.tabnine.com'},
    {name:'Codeium',cat:'Code',desc:'Free AI code autocomplete for 70+ languages.',pricing:'Free / $10/mo',url:'https://codeium.com'},
    {name:'ElevenLabs',cat:'Voice',desc:'Realistic AI voice generation and text-to-speech.',pricing:'Free / $5/mo',url:'https://elevenlabs.io'},
    {name:'Murf AI',cat:'Voice',desc:'AI voiceover studio for videos and podcasts.',pricing:'Free / $26/mo',url:'https://murf.ai'},
    {name:'Play.ht',cat:'Voice',desc:'Ultra-realistic AI voice generation with voice cloning.',pricing:'Free / $39/mo',url:'https://play.ht'},
    {name:'Speechify',cat:'Voice',desc:'AI text-to-speech reader for documents and web pages.',pricing:'Free / $11/mo',url:'https://speechify.com'},
    {name:'Notion AI',cat:'Productivity',desc:'AI writing and organization built into Notion workspace.',pricing:'$10/mo add-on',url:'https://www.notion.so/product/ai'},
    {name:'Otter.ai',cat:'Productivity',desc:'AI meeting transcription and note-taking assistant.',pricing:'Free / $17/mo',url:'https://otter.ai'},
    {name:'Reclaim AI',cat:'Productivity',desc:'AI calendar scheduling and time management.',pricing:'Free / $10/mo',url:'https://reclaim.ai'},
    {name:'Zapier AI',cat:'Productivity',desc:'AI-powered automation connecting 6000+ apps.',pricing:'Free / $20/mo',url:'https://zapier.com'},
    {name:'Perplexity',cat:'Research',desc:'AI-powered search engine with source citations.',pricing:'Free / $20/mo',url:'https://www.perplexity.ai'},
    {name:'Consensus',cat:'Research',desc:'AI research engine for answers from scientific papers.',pricing:'Free / $10/mo',url:'https://consensus.app'},
    {name:'Elicit',cat:'Research',desc:'AI research assistant for literature review and analysis.',pricing:'Free / $10/mo',url:'https://elicit.com'},
    {name:'SurferSEO',cat:'Marketing',desc:'AI content optimization for better search rankings.',pricing:'From $89/mo',url:'https://surferseo.com'},
    {name:'Semrush AI',cat:'Marketing',desc:'AI-powered SEO toolkit for keyword research and audits.',pricing:'From $130/mo',url:'https://www.semrush.com'},
    {name:'AdCreative AI',cat:'Marketing',desc:'Generate high-converting ad creatives with AI.',pricing:'From $29/mo',url:'https://www.adcreative.ai'},
    {name:'Opus Clip',cat:'Marketing',desc:'AI tool that turns long videos into viral short clips.',pricing:'Free / $15/mo',url:'https://www.opus.pro'},
    {name:'Beautiful.ai',cat:'Design',desc:'AI-powered presentations that design themselves.',pricing:'From $12/mo',url:'https://www.beautiful.ai'},
    {name:'Looka',cat:'Design',desc:'AI logo maker and brand identity generator.',pricing:'From $20 one-time',url:'https://looka.com'},
    {name:'Uizard',cat:'Design',desc:'Turn sketches into editable UI designs with AI.',pricing:'Free / $12/mo',url:'https://uizard.io'},
    {name:'Tome',cat:'Design',desc:'AI-powered storytelling and presentation creator.',pricing:'Free / $10/mo',url:'https://tome.app'}
  ];
  var categories=['All']; aiTools.forEach(function(t){if(categories.indexOf(t.cat)===-1)categories.push(t.cat)});
  var activeFilter='All';

  function renderFilters(){
    var el=document.getElementById('filters'); el.innerHTML='';
    categories.forEach(function(c){
      var btn=document.createElement('button');
      btn.className='filter-btn'+(c===activeFilter?' active':'');
      btn.textContent=c;
      btn.addEventListener('click',function(){activeFilter=c;renderFilters();filterTools()});
      el.appendChild(btn);
    });
  }

  function filterTools(){
    var q=document.getElementById('searchInput').value.toLowerCase();
    var grid=document.getElementById('toolsGrid');
    var filtered=aiTools.filter(function(t){
      return (activeFilter==='All'||t.cat===activeFilter) && (!q||t.name.toLowerCase().indexOf(q)!==-1||t.desc.toLowerCase().indexOf(q)!==-1||t.cat.toLowerCase().indexOf(q)!==-1);
    });
    document.getElementById('toolCount').textContent='Showing '+filtered.length+' of '+aiTools.length+' tools';
    grid.innerHTML='';
    filtered.forEach(function(t){
      var card=document.createElement('div'); card.className='ai-card';
      card.innerHTML='<h3>'+t.name+' <span class="cat-tag">'+t.cat+'</span></h3><p>'+t.desc+'</p><div class="pricing">'+t.pricing+'</div><a href="'+t.url+'" target="_blank" rel="noopener" class="visit-btn">Visit '+t.name+' →</a>';
      grid.appendChild(card);
    });
  }
  renderFilters(); filterTools();
  </script>
</body>
</html>
""")


# ─── 5. BUDGET CALCULATOR (enhanced) ─────────────────────────────
def budget_calculator():
    return (_head("Budget Calculator — Smart Monthly Planner",
                  "Free budget calculator with 50/30/20 rule analysis, debt payoff estimates, savings projections, and emergency fund planning.")
    + _style("""
    --green-bg:#ecfdf5;--red-bg:#fef2f2;
    .page-hero{background:linear-gradient(135deg,#059669 0%,#10b981 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:520px;margin:0 auto}
    .calc-tabs{display:flex;justify-content:center;gap:8px;margin:24px 0;flex-wrap:wrap}
    .calc-tab{padding:10px 20px;border-radius:8px;border:2px solid var(--border);background:var(--bg);color:var(--text-secondary);cursor:pointer;font-size:14px;font-weight:600;font-family:inherit}
    .calc-tab:hover,.calc-tab.active{border-color:var(--green);color:var(--green);background:#ecfdf5}
    .calc-panel{display:none}.calc-panel.active{display:block}
    .calc-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:16px}
    .calc-card h2{font-size:17px;font-weight:800;margin-bottom:14px;display:flex;align-items:center;gap:8px}
    .form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:10px}
    .form-group{display:flex;flex-direction:column;gap:4px}
    .form-group label{font-size:12px;font-weight:600;color:var(--text-secondary)}
    .form-group input{padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:15px;font-family:inherit;outline:none}
    .form-group input:focus{border-color:var(--green)}
    .btn{background:#059669;color:#fff;border:none;padding:12px 24px;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;width:100%;transition:background .2s}
    .btn:hover{background:#047857}
    .results-panel{display:none;margin-top:20px}
    .result-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}
    .result-box{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px;text-align:center}
    .result-box.positive{background:#ecfdf5;border-color:#a7f3d0}.result-box.negative{background:#fef2f2;border-color:#fecaca}
    .result-box .rlabel{font-size:11px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
    .result-box .rvalue{font-size:26px;font-weight:800}.result-box.positive .rvalue{color:var(--green)}.result-box.negative .rvalue{color:var(--red)}
    .bar-chart{margin:16px 0}.bar-row{display:flex;align-items:center;gap:10px;margin-bottom:8px}.bar-label{width:90px;font-size:12px;font-weight:600;text-align:right;flex-shrink:0}.bar-track{flex:1;background:var(--surface);border-radius:4px;height:22px;overflow:hidden}.bar-fill{height:100%;border-radius:4px;transition:width .6s}.bar-value{width:80px;font-size:12px;font-weight:600;flex-shrink:0}
    .rule-section{margin-top:20px;padding:20px;background:var(--accent-light);border-radius:var(--radius)}
    .rule-section h3{font-size:15px;font-weight:700;color:var(--accent);margin-bottom:10px}
    .rule-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #bfdbfe;font-size:13px}.rule-row:last-child{border-bottom:none}.rule-row .ideal{color:var(--accent);font-weight:600}
    .insight-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px;margin-top:16px}
    .insight-card h3{font-size:15px;font-weight:700;margin-bottom:10px}.insight-card p,.insight-card li{font-size:13px;margin-bottom:6px}
    .print-btn{background:transparent;border:1px solid var(--border);color:var(--text);padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;margin-top:12px}
    .print-btn:hover{border-color:var(--accent);color:var(--accent)}
    @media(max-width:768px){.form-row,.result-summary{grid-template-columns:1fr}.calc-tabs{flex-direction:column;align-items:stretch}}
    @media print{.header,.page-hero,.calc-tabs,.subscribe-float,.footer,.print-btn,.disclaimer{display:none!important}.results-panel,.calc-panel{display:block!important}}
""")
    + NAV_HTML + """
  <div class="page-hero"><h1>💰 Smart Budget Calculator</h1><p>Plan your budget with the 50/30/20 rule, track debt payoff, and project your savings goals</p></div>

  <div class="container">
    <div class="calc-tabs">
      <button class="calc-tab active" onclick="switchCalc('budget',this)">📊 Monthly Budget</button>
      <button class="calc-tab" onclick="switchCalc('debt',this)">💳 Debt Payoff</button>
      <button class="calc-tab" onclick="switchCalc('savings',this)">🎯 Savings Goal</button>
      <button class="calc-tab" onclick="switchCalc('emergency',this)">🛡️ Emergency Fund</button>
    </div>

    <!-- MONTHLY BUDGET -->
    <div class="calc-panel active" id="panel-budget">
      <div class="calc-card"><h2>💵 Monthly Income</h2>
        <div class="form-row"><div class="form-group"><label>Take-Home Pay</label><input type="number" id="income" placeholder="e.g. 5000"></div><div class="form-group"><label>Other Income</label><input type="number" id="otherIncome" placeholder="0"></div></div></div>
      <div class="calc-card"><h2>🏠 Needs (Essential)</h2>
        <div class="form-row"><div class="form-group"><label>Rent / Mortgage</label><input type="number" class="expense needs" placeholder="0"></div><div class="form-group"><label>Utilities</label><input type="number" class="expense needs" placeholder="0"></div></div>
        <div class="form-row"><div class="form-group"><label>Groceries</label><input type="number" class="expense needs" placeholder="0"></div><div class="form-group"><label>Transportation</label><input type="number" class="expense needs" placeholder="0"></div></div>
        <div class="form-row"><div class="form-group"><label>Insurance</label><input type="number" class="expense needs" placeholder="0"></div><div class="form-group"><label>Min. Debt Payments</label><input type="number" class="expense needs" placeholder="0"></div></div></div>
      <div class="calc-card"><h2>🎉 Wants (Lifestyle)</h2>
        <div class="form-row"><div class="form-group"><label>Dining Out</label><input type="number" class="expense wants" placeholder="0"></div><div class="form-group"><label>Entertainment</label><input type="number" class="expense wants" placeholder="0"></div></div>
        <div class="form-row"><div class="form-group"><label>Shopping</label><input type="number" class="expense wants" placeholder="0"></div><div class="form-group"><label>Subscriptions</label><input type="number" class="expense wants" placeholder="0"></div></div>
        <div class="form-row"><div class="form-group"><label>Hobbies</label><input type="number" class="expense wants" placeholder="0"></div><div class="form-group"><label>Travel / Vacation</label><input type="number" class="expense wants" placeholder="0"></div></div></div>
      <button class="btn" onclick="calcBudget()">Calculate My Budget</button>
      <div class="results-panel" id="budgetResults">
        <div class="result-summary"><div class="result-box"><div class="rlabel">Total Income</div><div class="rvalue" id="rIncome">$0</div></div><div class="result-box"><div class="rlabel">Total Expenses</div><div class="rvalue" id="rExpenses">$0</div></div><div class="result-box" id="rSurplusBox"><div class="rlabel">Surplus / Deficit</div><div class="rvalue" id="rSurplus">$0</div></div></div>
        <div class="bar-chart" id="barChart"></div>
        <div class="rule-section"><h3>📏 50/30/20 Rule Analysis</h3><div id="ruleAnalysis"></div></div>
        <div class="insight-card" id="insightCard"></div>
        <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
      </div>
    </div>

    <!-- DEBT PAYOFF -->
    <div class="calc-panel" id="panel-debt">
      <div class="calc-card"><h2>💳 Debt Payoff Calculator</h2>
        <div class="form-row"><div class="form-group"><label>Total Debt Balance</label><input type="number" id="debtBalance" placeholder="e.g. 15000"></div><div class="form-group"><label>Interest Rate (APR %)</label><input type="number" id="debtRate" placeholder="e.g. 18" step="0.1"></div></div>
        <div class="form-row"><div class="form-group"><label>Monthly Payment</label><input type="number" id="debtPayment" placeholder="e.g. 500"></div><div class="form-group"><label>Extra Monthly Payment</label><input type="number" id="debtExtra" placeholder="0"></div></div>
        <button class="btn" onclick="calcDebt()">Calculate Payoff</button></div>
      <div class="results-panel" id="debtResults"></div>
    </div>

    <!-- SAVINGS GOAL -->
    <div class="calc-panel" id="panel-savings">
      <div class="calc-card"><h2>🎯 Savings Goal Projection</h2>
        <div class="form-row"><div class="form-group"><label>Savings Goal</label><input type="number" id="savGoal" placeholder="e.g. 50000"></div><div class="form-group"><label>Current Savings</label><input type="number" id="savCurrent" placeholder="e.g. 5000"></div></div>
        <div class="form-row"><div class="form-group"><label>Monthly Contribution</label><input type="number" id="savMonthly" placeholder="e.g. 1000"></div><div class="form-group"><label>Expected Annual Return (%)</label><input type="number" id="savReturn" placeholder="e.g. 7" step="0.1"></div></div>
        <button class="btn" onclick="calcSavings()">Calculate Timeline</button></div>
      <div class="results-panel" id="savResults"></div>
    </div>

    <!-- EMERGENCY FUND -->
    <div class="calc-panel" id="panel-emergency">
      <div class="calc-card"><h2>🛡️ Emergency Fund Calculator</h2><p style="font-size:13px;color:var(--text-secondary);margin-bottom:14px;">Financial experts recommend 3-6 months of essential expenses.</p>
        <div class="form-row"><div class="form-group"><label>Monthly Essential Expenses</label><input type="number" id="emExpenses" placeholder="e.g. 3000"></div><div class="form-group"><label>Current Emergency Savings</label><input type="number" id="emCurrent" placeholder="e.g. 2000"></div></div>
        <div class="form-row"><div class="form-group"><label>Monthly Contribution</label><input type="number" id="emMonthly" placeholder="e.g. 500"></div><div class="form-group"><label>Target Months (3-6 recommended)</label><input type="number" id="emMonths" placeholder="6" value="6"></div></div>
        <button class="btn" onclick="calcEmergency()">Calculate</button></div>
      <div class="results-panel" id="emResults"></div>
    </div>

    <div class="disclaimer"><strong>Disclaimer:</strong> This calculator is for educational purposes only and does not constitute financial advice. Consult a qualified financial advisor for personalized planning.</div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  function switchCalc(id,btn){
    document.querySelectorAll('.calc-tab').forEach(function(t){t.classList.remove('active')});
    document.querySelectorAll('.calc-panel').forEach(function(p){p.classList.remove('active')});
    btn.classList.add('active');
    document.getElementById('panel-'+id).classList.add('active');
  }
  function gv(id){return parseFloat(document.getElementById(id).value)||0}
  function sc(cls){var t=0;document.querySelectorAll('.expense.'+cls).forEach(function(e){t+=parseFloat(e.value)||0});return t}
  function fmt(n){return '$'+n.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:0})}

  function calcBudget(){
    var income=gv('income')+gv('otherIncome'), needs=sc('needs'), wants=sc('wants'), total=needs+wants, surplus=income-total;
    document.getElementById('rIncome').textContent=fmt(income);
    document.getElementById('rExpenses').textContent=fmt(total);
    document.getElementById('rSurplus').textContent=fmt(surplus);
    var box=document.getElementById('rSurplusBox');
    box.className='result-box '+(surplus>=0?'positive':'negative');
    var colors=['#3b82f6','#f59e0b','#10b981','#ef4444'];
    var items=[{l:'Needs',v:needs,c:colors[0]},{l:'Wants',v:wants,c:colors[1]},{l:'Savings',v:Math.max(surplus,0),c:colors[2]}];
    if(surplus<0)items.push({l:'Deficit',v:Math.abs(surplus),c:colors[3]});
    var mx=Math.max(income,total),html='';
    items.forEach(function(it){var pct=mx>0?(it.v/mx*100):0;html+='<div class="bar-row"><div class="bar-label">'+it.l+'</div><div class="bar-track"><div class="bar-fill" style="width:'+pct+'%;background:'+it.c+'"></div></div><div class="bar-value">'+fmt(it.v)+'</div></div>'});
    document.getElementById('barChart').innerHTML=html;
    var iN=income*.5,iW=income*.3,iS=income*.2;
    var ra='<div class="rule-row"><span>Needs (50%)</span><span>You: '+fmt(needs)+' / <span class="ideal">Ideal: '+fmt(iN)+'</span></span></div>';
    ra+='<div class="rule-row"><span>Wants (30%)</span><span>You: '+fmt(wants)+' / <span class="ideal">Ideal: '+fmt(iW)+'</span></span></div>';
    ra+='<div class="rule-row"><span>Savings (20%)</span><span>You: '+fmt(Math.max(surplus,0))+' / <span class="ideal">Ideal: '+fmt(iS)+'</span></span></div>';
    document.getElementById('ruleAnalysis').innerHTML=ra;
    var tips='<h3>💡 Smart Insights</h3><ul>';
    if(needs>iN)tips+='<li>⚠️ Your needs are '+fmt(needs-iN)+' over the ideal 50%. Look for ways to reduce fixed costs.</li>';
    if(wants>iW)tips+='<li>⚠️ Your wants exceed the ideal 30% by '+fmt(wants-iW)+'. Consider cutting subscriptions or dining out.</li>';
    if(surplus>=iS)tips+='<li>✅ Great job! You\'re saving at or above the recommended 20%.</li>';
    tips+='<li>📅 Annual income: '+fmt(income*12)+' · Annual expenses: '+fmt(total*12)+'</li>';
    if(surplus>0)tips+='<li>🎯 At '+fmt(surplus)+'/month, you\'ll save '+fmt(surplus*12)+' per year.</li>';
    tips+='</ul>';
    document.getElementById('insightCard').innerHTML=tips;
    document.getElementById('budgetResults').style.display='block';
    document.getElementById('budgetResults').scrollIntoView({behavior:'smooth'});
  }

  function calcDebt(){
    var bal=gv('debtBalance'),rate=gv('debtRate')/100/12,pay=gv('debtPayment'),extra=gv('debtExtra');
    if(!bal||!pay){alert('Please fill in debt balance and monthly payment');return;}
    var total=pay+extra,months=0,totalPaid=0,totalInterest=0,b=bal;
    while(b>0&&months<600){
      var interest=b*rate; b+=interest; var p=Math.min(total,b); b-=p;
      totalPaid+=p; totalInterest+=interest; months++;
    }
    var years=Math.floor(months/12),mo=months%12;
    var html='<div class="result-summary">';
    html+='<div class="result-box"><div class="rlabel">Payoff Time</div><div class="rvalue" style="color:var(--accent)">'+years+'y '+mo+'m</div></div>';
    html+='<div class="result-box"><div class="rlabel">Total Interest</div><div class="rvalue" style="color:var(--red)">'+fmt(totalInterest)+'</div></div>';
    html+='<div class="result-box"><div class="rlabel">Total Paid</div><div class="rvalue">'+fmt(totalPaid)+'</div></div>';
    html+='</div>';
    if(extra>0){
      var m2=0,b2=bal,ti2=0;
      while(b2>0&&m2<600){var i2=b2*rate;b2+=i2;var p2=Math.min(pay,b2);b2-=p2;ti2+=i2;m2++;}
      html+='<div class="insight-card"><h3>💡 Impact of Extra Payments</h3><ul>';
      html+='<li>Without extra: '+(Math.floor(m2/12))+'y '+(m2%12)+'m, '+fmt(ti2)+' interest</li>';
      html+='<li>With '+fmt(extra)+'/mo extra: '+years+'y '+mo+'m, '+fmt(totalInterest)+' interest</li>';
      html+='<li>You save <strong>'+fmt(ti2-totalInterest)+'</strong> in interest and <strong>'+(m2-months)+' months</strong>!</li></ul></div>';
    }
    document.getElementById('debtResults').innerHTML=html;
    document.getElementById('debtResults').style.display='block';
    document.getElementById('debtResults').scrollIntoView({behavior:'smooth'});
  }

  function calcSavings(){
    var goal=gv('savGoal'),current=gv('savCurrent'),monthly=gv('savMonthly'),ret=gv('savReturn')/100/12;
    if(!goal||!monthly){alert('Please fill in your savings goal and monthly contribution');return;}
    var b=current,months=0;
    while(b<goal&&months<600){b=b*(1+ret)+monthly;months++;}
    var years=Math.floor(months/12),mo=months%12;
    var totalContributed=current+monthly*months,growth=b-totalContributed;
    var html='<div class="result-summary">';
    html+='<div class="result-box"><div class="rlabel">Time to Goal</div><div class="rvalue" style="color:var(--green)">'+years+'y '+mo+'m</div></div>';
    html+='<div class="result-box"><div class="rlabel">Total Contributed</div><div class="rvalue">'+fmt(totalContributed)+'</div></div>';
    html+='<div class="result-box"><div class="rlabel">Investment Growth</div><div class="rvalue" style="color:var(--green)">'+fmt(growth)+'</div></div>';
    html+='</div>';
    html+='<div class="insight-card"><h3>📈 Savings Projection</h3><ul>';
    html+='<li>You\'ll reach '+fmt(goal)+' in <strong>'+years+' years and '+mo+' months</strong></li>';
    html+='<li>Final balance: '+fmt(b)+'</li>';
    html+='<li>Your money earned '+fmt(growth)+' in investment returns</li>';
    html+='<li>That\'s '+((growth/totalContributed)*100).toFixed(0)+'% growth on your contributions!</li>';
    html+='</ul></div>';
    document.getElementById('savResults').innerHTML=html;
    document.getElementById('savResults').style.display='block';
    document.getElementById('savResults').scrollIntoView({behavior:'smooth'});
  }

  function calcEmergency(){
    var expenses=gv('emExpenses'),current=gv('emCurrent'),monthly=gv('emMonthly'),target=gv('emMonths')||6;
    if(!expenses){alert('Please enter your monthly essential expenses');return;}
    var goal=expenses*target,remaining=Math.max(goal-current,0);
    var months=monthly>0?Math.ceil(remaining/monthly):0;
    var pct=goal>0?Math.min((current/goal)*100,100):0;
    var html='<div class="result-summary">';
    html+='<div class="result-box"><div class="rlabel">Target Fund</div><div class="rvalue" style="color:var(--accent)">'+fmt(goal)+'</div></div>';
    html+='<div class="result-box"><div class="rlabel">Current Progress</div><div class="rvalue" style="color:'+(pct>=100?'var(--green)':'var(--red)')+'">'+pct.toFixed(0)+'%</div></div>';
    html+='<div class="result-box"><div class="rlabel">Remaining</div><div class="rvalue">'+fmt(remaining)+'</div></div>';
    html+='</div>';
    html+='<div class="bar-row"><div class="bar-label">Progress</div><div class="bar-track"><div class="bar-fill" style="width:'+pct+'%;background:'+(pct>=100?'var(--green)':'var(--accent)')+'"></div></div><div class="bar-value">'+pct.toFixed(0)+'%</div></div>';
    if(monthly>0&&remaining>0)html+='<div class="insight-card"><h3>📅 Timeline</h3><p>At '+fmt(monthly)+'/month, you\'ll reach your '+target+'-month emergency fund ('+fmt(goal)+') in <strong>'+Math.floor(months/12)+'y '+months%12+'m</strong>.</p></div>';
    else if(remaining<=0)html+='<div class="insight-card"><h3>🎉 Congratulations!</h3><p>You\'ve fully funded your '+target+'-month emergency fund!</p></div>';
    document.getElementById('emResults').innerHTML=html;
    document.getElementById('emResults').style.display='block';
    document.getElementById('emResults').scrollIntoView({behavior:'smooth'});
  }
  </script>
</body>
</html>
""")


# ─── 6. WORKOUT GENERATOR (fixed validation) ─────────────────────
def workout_generator():
    return (_head("Workout Generator — Custom Exercise Plans",
                  "Generate a custom workout plan based on your fitness goals, equipment, and time. Free workout builder.")
    + _style("""
    .page-hero{background:linear-gradient(135deg,#5b21b6 0%,#7c3aed 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:520px;margin:0 auto}
    .config-section{padding:28px 0}
    .config-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:14px;transition:border-color .2s}
    .config-card.missing{border-color:var(--red);box-shadow:0 0 0 3px rgba(220,38,38,.1)}
    .config-card h2{font-size:16px;font-weight:700;margin-bottom:14px}
    .option-grid{display:flex;flex-wrap:wrap;gap:8px}
    .option-btn{padding:10px 18px;border:2px solid var(--border);border-radius:8px;background:transparent;color:var(--text);font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
    .option-btn:hover{border-color:#7c3aed;color:#7c3aed}
    .option-btn.selected{border-color:#7c3aed;background:#f5f3ff;color:#7c3aed}
    .btn{background:#7c3aed;color:#fff;border:none;padding:14px 28px;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;width:100%;margin-top:8px;transition:background .2s}
    .btn:hover{background:#5b21b6}
    .workout-result{display:none;margin-top:24px}
    .workout-header{background:#f5f3ff;border:1px solid #ddd6fe;border-radius:var(--radius);padding:20px 24px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
    .workout-header h2{font-size:18px;font-weight:800;color:#7c3aed}
    .exercise-card{border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin-bottom:8px;display:flex;align-items:center;gap:16px}
    .exercise-num{width:36px;height:36px;border-radius:50%;background:#7c3aed;color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0}
    .exercise-info h3{font-size:15px;font-weight:700;margin-bottom:2px}.exercise-info p{font-size:13px;color:var(--text-secondary)}
    .exercise-detail{display:flex;gap:10px;margin-top:4px}.exercise-detail span{font-size:12px;background:var(--surface);padding:2px 8px;border-radius:4px;font-weight:600}
    .section-label{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#7c3aed;margin:16px 0 8px;padding-left:52px}
    .print-btn{background:transparent;border:1px solid var(--border);color:var(--text);padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}
    .print-btn:hover{border-color:#7c3aed;color:#7c3aed}
    @media(max-width:768px){.workout-header{flex-direction:column}}
    @media print{.header,.page-hero,.config-section,.subscribe-float,.footer,.print-btn,.disclaimer{display:none!important}.workout-result{display:block!important}}
""")
    + NAV_HTML + """
  <div class="page-hero"><h1>💪 Workout Generator</h1><p>Get a custom workout plan based on your goals, equipment, and available time</p></div>
  <div class="container"><div class="config-section">
    <div class="config-card" id="cardGoal"><h2>🎯 Fitness Goal</h2><div class="option-grid">
      <button class="option-btn" onclick="sel(this,'goal','strength')">Build Strength</button>
      <button class="option-btn" onclick="sel(this,'goal','muscle')">Build Muscle</button>
      <button class="option-btn" onclick="sel(this,'goal','cardio')">Improve Cardio</button>
      <button class="option-btn" onclick="sel(this,'goal','weight_loss')">Lose Weight</button>
      <button class="option-btn" onclick="sel(this,'goal','flexibility')">Flexibility</button>
      <button class="option-btn" onclick="sel(this,'goal','general')">General Fitness</button>
    </div></div>
    <div class="config-card" id="cardEquip"><h2>🏋️ Equipment</h2><div class="option-grid">
      <button class="option-btn" onclick="sel(this,'equip','none')">No Equipment</button>
      <button class="option-btn" onclick="sel(this,'equip','dumbbells')">Dumbbells Only</button>
      <button class="option-btn" onclick="sel(this,'equip','home')">Home Gym</button>
      <button class="option-btn" onclick="sel(this,'equip','full')">Full Gym</button>
    </div></div>
    <div class="config-card" id="cardTime"><h2>⏱️ Time</h2><div class="option-grid">
      <button class="option-btn" onclick="sel(this,'time','15')">15 min</button>
      <button class="option-btn" onclick="sel(this,'time','30')">30 min</button>
      <button class="option-btn" onclick="sel(this,'time','45')">45 min</button>
      <button class="option-btn" onclick="sel(this,'time','60')">60 min</button>
    </div></div>
    <div class="config-card" id="cardLevel"><h2>📊 Level</h2><div class="option-grid">
      <button class="option-btn" onclick="sel(this,'level','beginner')">Beginner</button>
      <button class="option-btn" onclick="sel(this,'level','intermediate')">Intermediate</button>
      <button class="option-btn" onclick="sel(this,'level','advanced')">Advanced</button>
    </div></div>
    <button class="btn" onclick="generate()">Generate My Workout</button>
  </div>

  <div class="workout-result" id="workoutResult">
    <div class="workout-header"><h2 id="workoutTitle">Your Workout</h2><div><span id="workoutStats" style="font-size:13px;color:var(--text-secondary);margin-right:8px;"></span><button class="print-btn" onclick="window.print()">🖨️ Print</button></div></div>
    <div id="exerciseList"></div>
  </div>

  <div class="disclaimer"><strong>Disclaimer:</strong> This workout generator provides general exercise suggestions. Consult a doctor before starting any exercise program. Stop if you feel pain.</div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  var S={goal:'',equip:'',time:'',level:''};
  function sel(btn,key,val){
    S[key]=val;
    btn.parentElement.querySelectorAll('.option-btn').forEach(function(b){b.classList.remove('selected')});
    btn.classList.add('selected');
    var card=btn.closest('.config-card'); if(card)card.classList.remove('missing');
  }

  var EX={
    bodyweight:{warmup:['Jumping Jacks','High Knees','Arm Circles','Leg Swings','Bodyweight Squats','Butt Kicks'],
      strength:['Push-ups','Diamond Push-ups','Pike Push-ups','Bodyweight Squats','Lunges','Glute Bridges','Plank','Side Plank','Superman','Tricep Dips (chair)','Bulgarian Split Squats','Calf Raises','Wall Sit','Decline Push-ups'],
      cardio:['Burpees','Mountain Climbers','Jump Squats','High Knees','Skaters','Tuck Jumps','Bear Crawls','Star Jumps'],
      flexibility:['Cat-Cow Stretch','Pigeon Pose','Hamstring Stretch','Quad Stretch',"Child's Pose",'Seated Twist','Hip Flexor Stretch','Shoulder Stretch','Downward Dog','Cobra Stretch']},
    dumbbells:{strength:['Dumbbell Bench Press','Dumbbell Rows','Dumbbell Shoulder Press','Goblet Squats','Romanian Deadlifts','Bicep Curls','Tricep Extensions','Lateral Raises','Dumbbell Lunges','Hammer Curls'],
      cardio:['Dumbbell Thrusters','Renegade Rows','Dumbbell Swings','Man Makers']},
    home:{strength:['Band Pull-aparts','Incline DB Press','Dumbbell Flyes','Bent Over Rows','Step-ups','Band Squats','Floor Press','Band Tricep Pushdowns'],
      cardio:['Box Jumps','Band Sprints','Kettlebell Swings']},
    full:{strength:['Barbell Bench Press','Barbell Squats','Deadlifts','Overhead Press','Pull-ups','Barbell Rows','Lat Pulldown','Leg Press','Cable Flyes','Hack Squat','T-Bar Row','Face Pulls','Leg Curls','Calf Raises Machine'],
      cardio:['Rowing Machine','Assault Bike','Stairclimber','Sled Push','Battle Ropes']}
  };

  function pick(arr,n){var a=arr.slice(),r=[];for(var i=0;i<Math.min(n,a.length);i++){var idx=Math.floor(Math.random()*a.length);r.push(a.splice(idx,1)[0])}return r}

  function generate(){
    var missing=false;
    ['goal','equip','time','level'].forEach(function(k,i){
      var ids=['cardGoal','cardEquip','cardTime','cardLevel'];
      if(!S[k]){document.getElementById(ids[i]).classList.add('missing');missing=true;}
    });
    if(missing){alert('Please select all options (highlighted in red)');return;}

    var mins=parseInt(S.time),numEx=Math.max(4,Math.floor(mins/5));
    var pool=JSON.parse(JSON.stringify(EX.bodyweight));
    if(S.equip==='dumbbells'||S.equip==='home'||S.equip==='full'){
      pool.strength=pool.strength.concat(EX.dumbbells.strength);pool.cardio=pool.cardio.concat(EX.dumbbells.cardio);
    }
    if(S.equip==='home'){pool.strength=pool.strength.concat(EX.home.strength);pool.cardio=pool.cardio.concat(EX.home.cardio)}
    if(S.equip==='full'){pool.strength=pool.strength.concat(EX.full.strength);pool.cardio=pool.cardio.concat(EX.full.cardio)}

    var warmupN=Math.min(3,Math.ceil(numEx*.2)),coolN=2,mainN=numEx-warmupN-coolN;
    var warmups=pick(pool.warmup,warmupN);
    var mainPool=S.goal==='cardio'?pool.cardio:S.goal==='flexibility'?pool.flexibility:S.goal==='weight_loss'||S.goal==='general'?pool.strength.concat(pool.cardio):pool.strength;
    var main=pick(mainPool,Math.max(mainN,3));
    var cooldown=pick(pool.flexibility,coolN);

    var sets=S.level==='beginner'?2:S.level==='intermediate'?3:4;
    var reps=S.goal==='strength'?'6-8':S.goal==='muscle'?'8-12':S.goal==='cardio'?'30 sec':'15-20';

    var workout=[];
    warmups.forEach(function(e){workout.push({name:e,phase:'Warm-up',sets:1,reps:'30 sec',rest:'15 sec'})});
    main.forEach(function(e){workout.push({name:e,phase:'Main',sets:sets,reps:reps,rest:S.goal==='cardio'?'30 sec':'60 sec'})});
    cooldown.forEach(function(e){workout.push({name:e,phase:'Cool-down',sets:1,reps:'45 sec hold',rest:'15 sec'})});

    var goalNames={strength:'Strength Building',muscle:'Muscle Hypertrophy',cardio:'Cardio Conditioning',weight_loss:'Fat Burning',flexibility:'Flexibility & Mobility',general:'General Fitness'};
    document.getElementById('workoutTitle').textContent=goalNames[S.goal]+' Workout';
    document.getElementById('workoutStats').textContent=mins+' min · '+workout.length+' exercises · '+S.level;

    var html='',lastPhase='';
    workout.forEach(function(ex,i){
      if(ex.phase!==lastPhase){html+='<div class="section-label">'+ex.phase+'</div>';lastPhase=ex.phase}
      html+='<div class="exercise-card"><div class="exercise-num">'+(i+1)+'</div><div class="exercise-info"><h3>'+ex.name+'</h3><div class="exercise-detail"><span>'+ex.sets+' set'+(ex.sets>1?'s':'')+'</span><span>'+ex.reps+'</span><span>Rest: '+ex.rest+'</span></div></div></div>';
    });
    document.getElementById('exerciseList').innerHTML=html;
    document.getElementById('workoutResult').style.display='block';
    document.getElementById('workoutResult').scrollIntoView({behavior:'smooth'});
  }
  </script>
</body>
</html>
""")


# ─── 7. PET FOOD ANALYZER (fixed split regex) ────────────────────
def pet_food_checker():
    return (_head("Pet Food Analyzer — Check Ingredient Quality",
                  "Analyze your pet food ingredients for quality and safety. Get ratings and recommendations for healthier pet nutrition.")
    + _style("""
    --accent:#ea580c;--accent-light:#fff7ed;
    .page-hero{background:linear-gradient(135deg,#c2410c 0%,#ea580c 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:520px;margin:0 auto}
    .input-section{padding:28px 0}
    .input-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:14px}
    .input-card h2{font-size:16px;font-weight:700;margin-bottom:12px}
    .pet-type{display:flex;gap:8px;margin-bottom:14px}
    .pet-btn{flex:1;padding:12px;border:2px solid var(--border);border-radius:8px;background:transparent;color:var(--text);font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s;text-align:center}
    .pet-btn:hover{border-color:#ea580c}.pet-btn.selected{border-color:#ea580c;background:#fff7ed;color:#ea580c}
    .pet-btn span{display:block;font-size:28px;margin-bottom:4px}
    textarea{width:100%;padding:14px;border:1px solid var(--border);border-radius:8px;font-size:14px;font-family:inherit;resize:vertical;min-height:100px;outline:none}
    textarea:focus{border-color:#ea580c}
    .btn{background:#ea580c;color:#fff;border:none;padding:14px;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;width:100%;margin-top:12px}
    .btn:hover{background:#c2410c}
    .results{display:none;margin-top:24px}
    .score-card{text-align:center;padding:28px;border-radius:var(--radius);margin-bottom:20px}
    .score-card.good{background:#ecfdf5;border:2px solid #a7f3d0}.score-card.ok{background:#fffbeb;border:2px solid #fde68a}.score-card.bad{background:#fef2f2;border:2px solid #fecaca}
    .score-num{font-size:52px;font-weight:900}.score-card.good .score-num{color:var(--green)}.score-card.ok .score-num{color:#d97706}.score-card.bad .score-num{color:var(--red)}
    .score-label{font-size:18px;font-weight:700;margin-top:4px}
    .ing-list{margin-top:16px}
    .ing-item{display:flex;align-items:center;gap:12px;padding:10px 14px;border:1px solid var(--border);border-radius:8px;margin-bottom:6px}
    .ing-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}.ing-dot.good{background:var(--green)}.ing-dot.ok{background:#d97706}.ing-dot.bad{background:var(--red)}
    .ing-name{font-size:14px;font-weight:600;flex:1}.ing-note{font-size:12px;color:var(--text-secondary);max-width:300px}
    .tips-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-top:20px}
    .tips-card h3{font-size:15px;font-weight:700;margin-bottom:10px}.tips-card li{font-size:13px;margin-bottom:6px}
""")
    + NAV_HTML + """
  <div class="page-hero"><h1>🐾 Pet Food Analyzer</h1><p>Paste your pet food's ingredient list to get a quality analysis and health rating</p></div>
  <div class="container"><div class="input-section">
    <div class="input-card">
      <h2>Select Pet Type</h2>
      <div class="pet-type">
        <button class="pet-btn selected" onclick="selPet(this,'dog')"><span>🐕</span>Dog</button>
        <button class="pet-btn" onclick="selPet(this,'cat')"><span>🐱</span>Cat</button>
      </div>
      <h2>Paste Ingredient List</h2>
      <textarea id="ingredients" placeholder="Paste the ingredient list from your pet food packaging here...&#10;&#10;Example: Chicken, Brown Rice, Chicken Meal, Barley, Oatmeal, Chicken Fat, Dried Beet Pulp, Natural Flavor..."></textarea>
      <button class="btn" onclick="analyzeFood()">🔬 Analyze Ingredients</button>
    </div>
    <div class="results" id="results">
      <div class="score-card" id="scoreCard"><div class="score-num" id="scoreNum">0</div><div class="score-label" id="scoreLabel">Quality Score</div></div>
      <h3 style="margin-bottom:12px">Ingredient Breakdown</h3>
      <div class="ing-list" id="ingList"></div>
      <div class="tips-card" id="tipsCard"></div>
    </div>
    <div class="disclaimer"><strong>Disclaimer:</strong> This tool provides general assessments based on common pet nutrition guidelines. It is NOT a substitute for veterinary advice. Consult your veterinarian before changing your pet's diet.</div>
  </div></div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  var petType='dog';
  function selPet(btn,type){petType=type;document.querySelectorAll('.pet-btn').forEach(function(b){b.classList.remove('selected')});btn.classList.add('selected')}

  var goodIng={dog:['chicken','beef','salmon','turkey','lamb','duck','venison','bison','brown rice','sweet potato','peas','blueberries','cranberries','spinach','carrots','pumpkin','flaxseed','fish oil','coconut oil','turmeric','probiotics','glucosamine','chondroitin','egg','sardine','herring','oatmeal','barley','quinoa','kale','broccoli','apple','deboned'],cat:['chicken','tuna','salmon','turkey','duck','rabbit','sardine','herring','egg','liver','heart','fish oil','pumpkin','cranberries','blueberries','taurine','probiotics','flaxseed','deboned']};
  var okIng=['chicken meal','fish meal','brewers rice','rice','corn','wheat','soybean','beet pulp','chicken fat','natural flavor','cellulose','tomato pomace','potassium chloride','salt','calcium carbonate','yeast','dried egg','pork meal','corn gluten meal','dried plain beet pulp','pea protein','pea fiber'];
  var badIng=['by-product','by product','byproduct','artificial','bha','bht','ethoxyquin','propylene glycol','menadione','food coloring','red 40','blue 2','yellow 5','yellow 6','sodium nitrite','carrageenan','xylitol','propyl gallate','tbhq','rendered fat','animal digest','sugar','corn syrup','sorbitol','animal fat'];

  function analyzeFood(){
    var raw=document.getElementById('ingredients').value.trim();
    if(!raw){alert('Please paste an ingredient list first');return;}
    var ings=raw.split(/,|;|\\n/).map(function(s){return s.trim()}).filter(function(s){return s.length>1});
    if(!ings.length){alert('No ingredients found. Paste a comma-separated ingredient list.');return;}
    var results=[],totalScore=0;
    ings.forEach(function(ing){
      var lower=ing.toLowerCase(),rating='ok',note='Common ingredient';
      for(var i=0;i<goodIng[petType].length;i++){if(lower.indexOf(goodIng[petType][i])!==-1){rating='good';note='Quality protein/nutrient source';break}}
      if(rating==='ok'){for(var i=0;i<badIng.length;i++){if(lower.indexOf(badIng[i])!==-1){rating='bad';note='Potentially harmful or low-quality';break}}}
      if(rating==='ok'){for(var i=0;i<okIng.length;i++){if(lower.indexOf(okIng[i])!==-1){note='Acceptable filler or supplement';break}}}
      totalScore+=rating==='good'?10:rating==='ok'?5:0;
      results.push({name:ing,rating:rating,note:note});
    });
    var maxScore=ings.length*10,pct=maxScore>0?Math.round(totalScore/maxScore*100):0;
    var sc=document.getElementById('scoreCard');
    sc.className='score-card '+(pct>=70?'good':pct>=40?'ok':'bad');
    document.getElementById('scoreNum').textContent=pct+'/100';
    document.getElementById('scoreLabel').textContent=pct>=70?'Good Quality':pct>=40?'Average Quality':'Below Average';
    var html='';results.forEach(function(r){html+='<div class="ing-item"><div class="ing-dot '+r.rating+'"></div><div class="ing-name">'+r.name+'</div><div class="ing-note">'+r.note+'</div></div>'});
    document.getElementById('ingList').innerHTML=html;
    var gc=results.filter(function(r){return r.rating==='good'}).length;
    var bc=results.filter(function(r){return r.rating==='bad'}).length;
    var tips='<h3>💡 Analysis Tips</h3><ul>';
    if(gc)tips+='<li>✅ Found <strong>'+gc+'</strong> high-quality ingredients</li>';
    if(bc)tips+='<li>⚠️ Found <strong>'+bc+'</strong> potentially concerning ingredients</li>';
    tips+='<li>First ingredient should be a named protein (chicken, beef, salmon — not "meat")</li>';
    tips+='<li>Avoid foods with artificial colors/preservatives (BHA/BHT) or unnamed by-products</li>';
    tips+='<li>Whole foods in the first 5 ingredients indicates higher quality</li>';
    tips+='</ul>';
    document.getElementById('tipsCard').innerHTML=tips;
    document.getElementById('results').style.display='block';
    document.getElementById('results').scrollIntoView({behavior:'smooth'});
  }
  </script>
</body>
</html>
""")


# ─── 8. SMART HOME HUB (fixed JS + enhanced) ─────────────────────
def smart_home():
    return (_head("Smart Home Hub — Device Compatibility Checker",
                  "Check smart home device compatibility across Alexa, Google Home, Apple HomeKit, and Matter. Build your smart home setup.")
    + _style("""
    --accent:#0891b2;--accent-light:#ecfeff;
    .page-hero{background:linear-gradient(135deg,#0e7490 0%,#0891b2 100%);color:#fff;padding:48px 0;text-align:center}
    .page-hero h1{font-size:32px;font-weight:900;margin-bottom:8px}.page-hero p{font-size:16px;opacity:.85;max-width:560px;margin:0 auto}
    .section{padding:28px 0}
    .eco-selector{display:flex;gap:12px;margin-bottom:20px;justify-content:center;flex-wrap:wrap}
    .eco-btn{padding:14px 24px;border:2px solid var(--border);border-radius:var(--radius);background:transparent;color:var(--text);font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:all .15s;text-align:center;min-width:150px}
    .eco-btn:hover{border-color:#0891b2}.eco-btn.selected{border-color:#0891b2;background:#ecfeff;color:#0891b2}
    .eco-btn span{display:block;font-size:28px;margin-bottom:4px}
    .cat-filter{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;justify-content:center}
    .cat-btn{padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
    .cat-btn:hover,.cat-btn.active{border-color:#0891b2;color:#0891b2;background:#ecfeff}
    .search-wrap{max-width:400px;margin:0 auto 16px}.search-wrap input{width:100%;padding:10px 16px;border-radius:50px;border:1px solid var(--border);font-size:14px;font-family:inherit;outline:none}
    .search-wrap input:focus{border-color:#0891b2}
    .device-count{text-align:center;padding:8px 0;font-size:13px;color:var(--text-secondary)}
    .device-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .device-card{border:1px solid var(--border);border-radius:var(--radius);padding:16px;transition:all .15s}
    .device-card:hover{border-color:#0891b2;box-shadow:var(--shadow)}
    .device-card h3{font-size:14px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:6px}
    .device-card .cat-tag{font-size:10px;font-weight:600;color:#0891b2;background:#ecfeff;padding:2px 6px;border-radius:8px}
    .device-card p{font-size:12px;color:var(--text-secondary);margin-bottom:6px}
    .device-card .price{font-size:12px;font-weight:600;color:var(--text);margin-bottom:6px}
    .compat-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
    .compat-badge{font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600}
    .compat-badge.yes{background:#ecfdf5;color:var(--green)}.compat-badge.no{background:#fef2f2;color:var(--red)}
    .buy-link{display:inline-block;font-size:11px;font-weight:600;color:var(--accent);margin-top:4px}
    .buy-link:hover{text-decoration:underline}
    @media(max-width:768px){.device-grid{grid-template-columns:1fr}.eco-selector{flex-direction:column;align-items:center}}
""")
    + NAV_HTML + """
  <div class="page-hero"><h1>🏠 Smart Home Hub</h1><p>Check device compatibility across Alexa, Google Home, Apple HomeKit, and Matter</p></div>
  <div class="container"><div class="section">
    <div class="eco-selector">
      <button class="eco-btn selected" onclick="setEco(this,'all')"><span>🌐</span>All</button>
      <button class="eco-btn" onclick="setEco(this,'alexa')"><span>🔵</span>Alexa</button>
      <button class="eco-btn" onclick="setEco(this,'google')"><span>🔴</span>Google</button>
      <button class="eco-btn" onclick="setEco(this,'homekit')"><span>⚪</span>HomeKit</button>
      <button class="eco-btn" onclick="setEco(this,'matter')"><span>🟢</span>Matter</button>
    </div>
    <div class="search-wrap"><input type="text" id="searchInput" placeholder="Search devices..." oninput="renderDevices()"></div>
    <div class="cat-filter" id="catFilter"></div>
    <div class="device-count" id="deviceCount"></div>
    <div class="device-grid" id="deviceGrid"></div>
    <div class="disclaimer"><strong>Disclaimer:</strong> Compatibility info is based on publicly available data and may not reflect latest firmware. Verify on the manufacturer's website. Some links are affiliate links.</div>
  </div></div>
""" + FOOTER + '\n' + SUB_BTN + """
  <script>
  var devices=[
    {name:'Amazon Echo Dot (5th)',cat:'Speaker',alexa:1,google:0,homekit:0,matter:0,price:'$50',desc:'Compact smart speaker with improved sound'},
    {name:'Google Nest Mini',cat:'Speaker',alexa:0,google:1,homekit:0,matter:0,price:'$50',desc:'Compact Google Assistant speaker'},
    {name:'Apple HomePod Mini',cat:'Speaker',alexa:0,google:0,homekit:1,matter:1,price:'$99',desc:'Compact Siri speaker with Thread'},
    {name:'Sonos Era 100',cat:'Speaker',alexa:1,google:1,homekit:1,matter:0,price:'$249',desc:'Premium smart speaker with spatial audio'},
    {name:'Philips Hue Starter Kit',cat:'Lighting',alexa:1,google:1,homekit:1,matter:1,price:'$130',desc:'Smart LED bulbs with 16M colors + hub'},
    {name:'LIFX A19 Bulb',cat:'Lighting',alexa:1,google:1,homekit:1,matter:0,price:'$35',desc:'Wi-Fi smart bulb — no hub needed'},
    {name:'Nanoleaf Shapes',cat:'Lighting',alexa:1,google:1,homekit:1,matter:1,price:'$200',desc:'Modular RGB light panels'},
    {name:'Wyze Bulb Color',cat:'Lighting',alexa:1,google:1,homekit:0,matter:0,price:'$8',desc:'Budget smart bulb with colors'},
    {name:'Govee LED Strip',cat:'Lighting',alexa:1,google:1,homekit:0,matter:0,price:'$20',desc:'RGB LED strip with app control'},
    {name:'Ring Video Doorbell 4',cat:'Security',alexa:1,google:0,homekit:0,matter:0,price:'$200',desc:'1080p doorbell with pre-roll'},
    {name:'Google Nest Doorbell',cat:'Security',alexa:0,google:1,homekit:0,matter:0,price:'$180',desc:'24/7 recording doorbell'},
    {name:'Arlo Pro 5S',cat:'Security',alexa:1,google:1,homekit:1,matter:0,price:'$250',desc:'2K wireless security camera'},
    {name:'Eufy Security Cam 3',cat:'Security',alexa:1,google:1,homekit:1,matter:0,price:'$100',desc:'Local storage — no subscription'},
    {name:'Ring Alarm System',cat:'Security',alexa:1,google:0,homekit:0,matter:0,price:'$200',desc:'DIY home security system'},
    {name:'ecobee Smart Thermostat',cat:'Climate',alexa:1,google:1,homekit:1,matter:0,price:'$250',desc:'Smart thermostat with room sensors'},
    {name:'Google Nest Thermostat',cat:'Climate',alexa:0,google:1,homekit:0,matter:0,price:'$130',desc:'Learning thermostat with Sash display'},
    {name:'Honeywell T9',cat:'Climate',alexa:1,google:1,homekit:0,matter:0,price:'$200',desc:'Smart thermostat with room sensors'},
    {name:'August Smart Lock 4',cat:'Locks',alexa:1,google:1,homekit:1,matter:0,price:'$230',desc:'Retrofit smart lock — keeps key'},
    {name:'Yale Assure Lock 2',cat:'Locks',alexa:1,google:1,homekit:1,matter:1,price:'$250',desc:'Keyless smart lock with touchscreen'},
    {name:'Schlage Encode Plus',cat:'Locks',alexa:1,google:1,homekit:1,matter:0,price:'$300',desc:'Smart lock with Apple Home Key'},
    {name:'iRobot Roomba j9+',cat:'Cleaning',alexa:1,google:1,homekit:0,matter:0,price:'$800',desc:'Self-emptying robot vacuum'},
    {name:'Roborock S8 MaxV',cat:'Cleaning',alexa:1,google:1,homekit:0,matter:0,price:'$1,400',desc:'Robot vacuum + mop combo'},
    {name:'TP-Link Kasa Plug',cat:'Plugs',alexa:1,google:1,homekit:0,matter:0,price:'$15',desc:'Wi-Fi plug with energy monitoring'},
    {name:'Meross Smart Plug',cat:'Plugs',alexa:1,google:1,homekit:1,matter:1,price:'$12',desc:'Compact plug with HomeKit'},
    {name:'Eve Energy',cat:'Plugs',alexa:0,google:0,homekit:1,matter:1,price:'$40',desc:'Thread-enabled Apple plug'},
    {name:'Samsung SmartThings Hub',cat:'Hubs',alexa:1,google:1,homekit:0,matter:1,price:'$130',desc:'Universal hub: Zigbee, Z-Wave, Matter'},
    {name:'Apple TV 4K',cat:'Hubs',alexa:0,google:0,homekit:1,matter:1,price:'$130',desc:'HomeKit/Matter hub + streaming'},
    {name:'Echo Show 15',cat:'Display',alexa:1,google:0,homekit:0,matter:0,price:'$280',desc:'15" smart display + Fire TV'},
    {name:'Google Nest Hub Max',cat:'Display',alexa:0,google:1,homekit:0,matter:0,price:'$230',desc:'10" display with camera'},
    {name:'Lutron Caseta Dimmer',cat:'Switches',alexa:1,google:1,homekit:1,matter:0,price:'$60',desc:'Reliable in-wall smart dimmer'},
    {name:'Leviton Decora Smart',cat:'Switches',alexa:1,google:1,homekit:1,matter:1,price:'$45',desc:'In-wall switch with Matter'}
  ];

  var activeEco='all',activeCat='All';
  var categories=['All']; devices.forEach(function(d){if(categories.indexOf(d.cat)===-1)categories.push(d.cat)});

  function setEco(btn,eco){
    activeEco=eco;
    document.querySelectorAll('.eco-btn').forEach(function(b){b.classList.remove('selected')});
    btn.classList.add('selected');
    renderDevices();
  }

  function renderFilters(){
    var el=document.getElementById('catFilter'); el.innerHTML='';
    categories.forEach(function(c){
      var btn=document.createElement('button');
      btn.className='cat-btn'+(c===activeCat?' active':'');
      btn.textContent=c;
      btn.addEventListener('click',function(){activeCat=c;renderFilters();renderDevices()});
      el.appendChild(btn);
    });
  }

  function renderDevices(){
    var q=(document.getElementById('searchInput').value||'').toLowerCase();
    var filtered=devices.filter(function(d){
      var mc=activeCat==='All'||d.cat===activeCat;
      var mq=!q||d.name.toLowerCase().indexOf(q)!==-1||d.cat.toLowerCase().indexOf(q)!==-1||d.desc.toLowerCase().indexOf(q)!==-1;
      var me=activeEco==='all'||d[activeEco]===1;
      return mc&&mq&&me;
    });
    document.getElementById('deviceCount').textContent='Showing '+filtered.length+' of '+devices.length+' devices';
    var grid=document.getElementById('deviceGrid'); grid.innerHTML='';
    filtered.forEach(function(d){
      var card=document.createElement('div'); card.className='device-card';
      var compat='<div class="compat-row">';
      compat+='<span class="compat-badge '+(d.alexa?'yes':'no')+'">'+(d.alexa?'✓':'✗')+' Alexa</span>';
      compat+='<span class="compat-badge '+(d.google?'yes':'no')+'">'+(d.google?'✓':'✗')+' Google</span>';
      compat+='<span class="compat-badge '+(d.homekit?'yes':'no')+'">'+(d.homekit?'✓':'✗')+' HomeKit</span>';
      if(d.matter)compat+='<span class="compat-badge yes">✓ Matter</span>';
      compat+='</div>';
      var buyUrl='https://www.amazon.com/s?k='+encodeURIComponent(d.name)+'&tag=techlife0ac-20';
      card.innerHTML='<h3>'+d.name+' <span class="cat-tag">'+d.cat+'</span></h3><p>'+d.desc+'</p><div class="price">'+d.price+'</div>'+compat+'<a href="'+buyUrl+'" target="_blank" rel="noopener" class="buy-link">View on Amazon →</a>';
      grid.appendChild(card);
    });
  }

  renderFilters(); renderDevices();
  </script>
</body>
</html>
""")


# ─── 9. TOOLS INDEX ──────────────────────────────────────────────
def tools_index():
    return (_head("Free Tools & Resources",
                  "Free tools: deal finder, AI tool directory, budget calculator, workout generator, pet food analyzer, smart home hub, travel search, market data.")
    + _style("""
    .page-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#7c3aed 100%);color:#fff;padding:56px 0;text-align:center}
    .page-hero h1{font-size:36px;font-weight:900;margin-bottom:10px}.page-hero p{font-size:17px;opacity:.85;max-width:560px;margin:0 auto}
    .tools-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;padding:40px 0}
    .tool-card{border:1px solid var(--border);border-radius:var(--radius);padding:28px;transition:all .2s;text-decoration:none;color:var(--text);display:block}
    .tool-card:hover{border-color:var(--accent);box-shadow:var(--shadow);transform:translateY(-3px)}
    .tool-card .icon{font-size:36px;margin-bottom:12px}
    .tool-card h2{font-size:18px;font-weight:800;margin-bottom:6px}
    .tool-card p{font-size:14px;color:var(--text-secondary);line-height:1.6}
    .tool-card .tag{display:inline-block;margin-top:10px;font-size:12px;font-weight:600;color:var(--accent);background:var(--accent-light);padding:3px 10px;border-radius:12px}
    @media(max-width:768px){.tools-grid{grid-template-columns:1fr}}
""")
    + NAV_HTML + """
  <div class="page-hero"><h1>🛠️ Free Tools & Resources</h1><p>Smart tools to help you save money, stay healthy, and make better decisions</p></div>
  <div class="container">
    <div class="tools-grid">
      <a href="/tools/deal-finder.html" class="tool-card"><div class="icon">🔍</div><h2>Deal Finder</h2><p>Search any product across 9 top retailers — Amazon, Best Buy, Walmart, Target, and more. Compare deals with one click or open all at once.</p><span class="tag">Shopping</span></a>
      <a href="/personal_finance/markets.html" class="tool-card"><div class="icon">📊</div><h2>Market Data Center</h2><p>Real-time stock charts, crypto prices, forex rates, and commodities powered by TradingView. Search any symbol, auto-refreshing data.</p><span class="tag">Finance</span></a>
      <a href="/travel/search.html" class="tool-card"><div class="icon">✈️</div><h2>Travel Search</h2><p>Compare flights, hotels & car rentals across Skyscanner, Kayak, Booking.com, and more. Smart airport autocomplete, multi-provider results.</p><span class="tag">Travel</span></a>
      <a href="/tools/budget-calculator.html" class="tool-card"><div class="icon">💰</div><h2>Smart Budget Calculator</h2><p>Monthly budget planner with 50/30/20 analysis, debt payoff calculator, savings projections, and emergency fund planning.</p><span class="tag">Finance</span></a>
      <a href="/tools/ai-tool-finder.html" class="tool-card"><div class="icon">🤖</div><h2>AI Tool Directory</h2><p>Browse 60+ curated AI tools across 10 categories. Find tools for writing, images, video, code, voice, productivity, and more.</p><span class="tag">AI & Tech</span></a>
      <a href="/tools/workout-generator.html" class="tool-card"><div class="icon">💪</div><h2>Workout Generator</h2><p>Generate custom workout plans based on your goals, equipment, time, and fitness level. Printable plans with exercise details.</p><span class="tag">Fitness</span></a>
      <a href="/tools/pet-food-checker.html" class="tool-card"><div class="icon">🐾</div><h2>Pet Food Analyzer</h2><p>Paste any pet food ingredient list to get a quality score. Identifies good, acceptable, and concerning ingredients for dogs and cats.</p><span class="tag">Pet Care</span></a>
      <a href="/tools/smart-home.html" class="tool-card"><div class="icon">🏠</div><h2>Smart Home Hub</h2><p>Check compatibility of 30+ smart home devices across Alexa, Google, HomeKit, and Matter. Prices and Amazon buy links included.</p><span class="tag">Home Tech</span></a>
    </div>
  </div>
""" + FOOTER + '\n' + SUB_BTN + """
</body>
</html>
""")


# ─── Main ─────────────────────────────────────────────────────────
def write(name, content):
    path = TMPL / name
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ {name} ({len(content):,} chars)")


if __name__ == "__main__":
    print("🔧 Rebuilding tool templates...\n")
    write("market_data.html", market_data())
    write("travel_search.html", travel_search())
    write("deal_finder.html", deal_finder())
    write("ai_tool_finder.html", ai_tool_finder())
    write("budget_calculator.html", budget_calculator())
    write("workout_generator.html", workout_generator())
    write("pet_food_checker.html", pet_food_checker())
    write("smart_home.html", smart_home())
    write("tools_index.html", tools_index())
    print(f"\n✅ All 9 templates rebuilt successfully!")
