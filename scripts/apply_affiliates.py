#!/usr/bin/env python3
"""Apply affiliate placeholder changes to all remaining tool templates."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, 'site', 'templates')


def patch_ai_tool_finder():
    path = os.path.join(TEMPLATES, 'ai_tool_finder.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1) Insert AITAFF config block after <script>
    old = '  <script>\n  var aiTools = ['
    new = """  <script>
  /* ── Affiliate tracking IDs (injected from settings.yaml at build time) ── */
  var AITAFF = {
    jasper:     '{{ affiliates.jasper_fpr     | default("") }}',
    grammarly:  '{{ affiliates.grammarly_affiliate_id | default("") }}',
    semrush:    '{{ affiliates.semrush_ref     | default("") }}',
    surferseo:  '{{ affiliates.surferseo_ref   | default("") }}',
    canva:      '{{ affiliates.canva_affiliate_id | default("") }}',
    writesonic: '{{ affiliates.writesonic_ref  | default("") }}',
    descript:   '{{ affiliates.descript_ref    | default("") }}'
  };
  /* Helper: append affiliate param to a URL if the ID is set */
  function aitAff(base, key, param) {
    var id = AITAFF[key];
    if (!id) return base;
    return base + (base.indexOf('?') === -1 ? '?' : '&') + param + '=' + encodeURIComponent(id);
  }

  var aiTools = ["""
    c = c.replace(old, new, 1)

    # 2) Update URLs for tools with affiliate programs
    swaps = {
        "url:'https://www.jasper.ai'}":     "url:aitAff('https://www.jasper.ai','jasper','fpr')}",
        "url:'https://writesonic.com'}":    "url:aitAff('https://writesonic.com','writesonic','ref')}",
        "url:'https://www.grammarly.com'}": "url:aitAff('https://www.grammarly.com','grammarly','affiliateId')}",
        "url:'https://www.canva.com'}":     "url:aitAff('https://www.canva.com','canva','affiliateRef')}",
        "url:'https://www.descript.com'}":  "url:aitAff('https://www.descript.com','descript','ref')}",
        "url:'https://surferseo.com'}":     "url:aitAff('https://surferseo.com','surferseo','ref')}",
        "url:'https://www.semrush.com'}":   "url:aitAff('https://www.semrush.com','semrush','ref')}",
    }
    for old_url, new_url in swaps.items():
        c = c.replace(old_url, new_url, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✓ AI Tool Directory – affiliate placeholders added for 7 tools")


def patch_budget_calculator():
    path = os.path.join(TEMPLATES, 'budget_calculator.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1) Add recommendations section before disclaimer
    old_disc = '    <div class="disclaimer"><strong>Disclaimer:</strong> This calculator is for informational and educational purposes only'
    new_disc = """    <!-- Contextual product recommendations (affiliate-ready) -->
    <div class="calc-card" id="financeRecs" style="display:none;margin-top:24px;border:1px solid #bfdbfe;background:#eff6ff">
      <h2 style="color:#2563eb">\U0001f4a1 Recommended Financial Tools</h2>
      <p style="font-size:13px;color:var(--text-secondary);margin-bottom:16px">Based on your results, these tools could help you reach your goals faster:</p>
      <div id="recsContent"></div>
    </div>

    <div class="disclaimer"><strong>Disclaimer:</strong> This calculator is for informational and educational purposes only"""
    c = c.replace(old_disc, new_disc, 1)

    # 2) Add affiliate config + showRecs function after opening <script>
    old_script = '  <script>\n  // \u2500\u2500 Tab switching'
    new_script = """  <script>
  /* ── Affiliate IDs (injected from settings.yaml at build time) ── */
  var BAFF = {
    sofi:        '{{ affiliates.sofi_ref        | default("") }}',
    wealthfront: '{{ affiliates.wealthfront_ref  | default("") }}',
    betterment:  '{{ affiliates.betterment_ref   | default("") }}'
  };
  function baffUrl(base, key, param) {
    var id = BAFF[key]; if (!id) return base;
    return base + (base.indexOf('?') === -1 ? '?' : '&') + param + '=' + encodeURIComponent(id);
  }
  /* Product recommendations shown after calculations */
  var finProducts = [
    {id:'sofi',       name:'SoFi Checking & Savings',   desc:'4.00% APY, no fees, FDIC insured.',          url:baffUrl('https://www.sofi.com/banking','sofi','ref'),          icon:'\U0001f3e6', for:['savings','emergency','budget']},
    {id:'wealthfront',name:'Wealthfront',                desc:'Automated investing & 5.00% APY cash account.', url:baffUrl('https://www.wealthfront.com','wealthfront','inv'),   icon:'\U0001f4c8', for:['savings','budget']},
    {id:'betterment', name:'Betterment',                  desc:'Robo-advisor for hands-off investing.',       url:baffUrl('https://www.betterment.com','betterment','ref'),      icon:'\U0001f916', for:['savings','budget']}
  ];
  function showRecs(tab) {
    var recs = finProducts.filter(function(p){return p.for.indexOf(tab) !== -1;});
    if (!recs.length) { document.getElementById('financeRecs').style.display='none'; return; }
    var html = '';
    recs.forEach(function(p){
      html += '<div style="display:flex;align-items:center;gap:14px;padding:12px 0;border-bottom:1px solid #bfdbfe">';
      html += '<span style="font-size:28px">'+p.icon+'</span>';
      html += '<div style="flex:1"><strong style="font-size:14px">'+p.name+'</strong><br><span style="font-size:13px;color:var(--text-secondary)">'+p.desc+'</span></div>';
      html += '<a href="'+p.url+'" target="_blank" rel="noopener" style="background:#2563eb;color:#fff;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:700;text-decoration:none;white-space:nowrap">Learn More \\u2192</a>';
      html += '</div>';
    });
    document.getElementById('recsContent').innerHTML = html;
    document.getElementById('financeRecs').style.display = 'block';
  }

  // ── Tab switching"""
    c = c.replace(old_script, new_script, 1)

    # 3) Add showRecs() calls at end of each calculator function
    c = c.replace(
        "showPanel('results-budget');\n  }",
        "showPanel('results-budget');\n    showRecs('budget');\n  }",
        1
    )
    c = c.replace(
        "showPanel('results-debt');\n  }",
        "showPanel('results-debt');\n    showRecs('debt');\n  }",
        1
    )
    c = c.replace(
        "showPanel('results-savings');\n  }",
        "showPanel('results-savings');\n    showRecs('savings');\n  }",
        1
    )
    c = c.replace(
        "showPanel('results-emergency');\n  }",
        "showPanel('results-emergency');\n    showRecs('emergency');\n  }",
        1
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✓ Budget Calculator – financial product recommendations added")


def patch_workout_generator():
    path = os.path.join(TEMPLATES, 'workout_generator.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1) Add gear recommendations section before disclaimer
    old_disc = '  <div class="disclaimer"><strong>Disclaimer:</strong> This workout generator'
    new_disc = """  <!-- Equipment & Gear Recommendations (affiliate-ready) -->
  <div class="workout-result" id="gearRecs" style="display:none">
    <div style="background:#fff;border:1px solid #ddd6fe;border-radius:10px;padding:24px;margin-top:20px">
      <h3 style="font-size:16px;font-weight:800;color:#5b21b6;margin-bottom:14px">\U0001f6d2 Gear Up for Your Workout</h3>
      <div id="gearContent"></div>
      <p style="font-size:11px;color:var(--text-secondary);margin-top:12px">Prices & availability may vary. Some links may be affiliate links.</p>
    </div>
  </div>

  <div class="disclaimer"><strong>Disclaimer:</strong> This workout generator"""
    c = c.replace(old_disc, new_disc, 1)

    # 2) Add gear config and function before sel variable
    old_sel = "  var sel={goal:'',equip:'',time:'',level:''};"
    new_sel = """  /* ── Affiliate config (injected from settings.yaml) ── */
  var WAFF_TAG = '{{ affiliates.amazon_tag | default("techlife0ac-20") }}';
  function amzSearch(q){ return 'https://www.amazon.com/s?k='+encodeURIComponent(q)+'&tag='+WAFF_TAG; }
  var gearMap = {
    dumbbells: [
      {name:'Adjustable Dumbbells', icon:'\U0001f3cb\ufe0f', q:'adjustable dumbbells set'},
      {name:'Exercise Mat', icon:'\U0001f9d8', q:'thick exercise mat'},
      {name:'Workout Gloves', icon:'\U0001f9e4', q:'workout gloves weight lifting'}
    ],
    home: [
      {name:'Resistance Bands Set', icon:'\U0001f4aa', q:'resistance bands set workout'},
      {name:'Adjustable Weight Bench', icon:'\U0001fa91', q:'adjustable weight bench'},
      {name:'Pull-Up Bar', icon:'\U0001f529', q:'doorway pull up bar'},
      {name:'Foam Roller', icon:'\U0001f9ca', q:'foam roller muscle recovery'}
    ],
    full: [
      {name:'Lifting Belt', icon:'\U0001f512', q:'weightlifting belt leather'},
      {name:'Wrist Wraps', icon:'\u270b', q:'wrist wraps weightlifting'},
      {name:'Gym Bag', icon:'\U0001f45c', q:'gym bag with shoe compartment'}
    ],
    none: [
      {name:'Exercise Mat', icon:'\U0001f9d8', q:'thick exercise mat home workout'},
      {name:'Jump Rope', icon:'\u26a1', q:'speed jump rope fitness'},
      {name:'Resistance Bands', icon:'\U0001f4aa', q:'resistance bands set'}
    ]
  };
  function showGear(equip) {
    var items = gearMap[equip] || gearMap.none;
    var html = '';
    items.forEach(function(g){
      html += '<div style="display:flex;align-items:center;gap:14px;padding:10px 0;border-bottom:1px solid #e5e7eb">';
      html += '<span style="font-size:24px">'+g.icon+'</span>';
      html += '<span style="flex:1;font-size:14px;font-weight:600">'+g.name+'</span>';
      html += '<a href="'+amzSearch(g.q)+'" target="_blank" rel="noopener" style="background:#f59e0b;color:#111;padding:7px 14px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none">Shop on Amazon \\u2192</a>';
      html += '</div>';
    });
    document.getElementById('gearContent').innerHTML = html;
    document.getElementById('gearRecs').style.display = 'block';
  }

  var sel={goal:'',equip:'',time:'',level:''};"""
    c = c.replace(old_sel, new_sel, 1)

    # 3) Call showGear at end of generateWorkout
    c = c.replace(
        "document.getElementById('workoutResult').scrollIntoView({behavior:'smooth'});\n  }\n  </script>",
        "document.getElementById('workoutResult').scrollIntoView({behavior:'smooth'});\n    showGear(sel.equip);\n  }\n  </script>",
        1
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✓ Workout Generator – equipment recommendations added")


def patch_pet_food_checker():
    path = os.path.join(TEMPLATES, 'pet_food_checker.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1) Add brand recommendation section before disclaimer
    old_disc = '    <div class="disclaimer"><strong>Disclaimer:</strong> This tool provides general informational'
    new_disc = """    <!-- Pet food brand recommendations (affiliate-ready) -->
    <div class="results" id="brandRecs" style="display:none;margin-top:0">
      <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:24px">
        <h3 style="font-size:16px;font-weight:800;color:#c2410c;margin-bottom:14px">\U0001f6d2 Top-Rated Pet Food Brands</h3>
        <div id="brandContent"></div>
        <p style="font-size:11px;color:var(--text-secondary);margin-top:12px">Some links may be affiliate links \u2014 we may earn a commission at no extra cost to you.</p>
      </div>
    </div>

    <div class="disclaimer"><strong>Disclaimer:</strong> This tool provides general informational"""
    c = c.replace(old_disc, new_disc, 1)

    # 2) Add affiliate config before petType variable
    old_pet = "  var petType='dog';"
    new_pet = """  /* ── Affiliate config (injected from settings.yaml) ── */
  var PAFF = {
    amazon_tag: '{{ affiliates.amazon_tag        | default("techlife0ac-20") }}',
    chewy:      '{{ affiliates.chewy_affiliate_id | default("") }}'
  };
  function chewyUrl(q) {
    var base = 'https://www.chewy.com/s?query=' + encodeURIComponent(q);
    return PAFF.chewy ? base + '&ref=' + PAFF.chewy : base;
  }
  function amzPetUrl(q) {
    return 'https://www.amazon.com/s?k=' + encodeURIComponent(q) + '&tag=' + PAFF.amazon_tag;
  }
  var petBrands = {
    dog: [
      {name:'Blue Buffalo Life Protection', q:'Blue Buffalo Life Protection dog food', icon:'\U0001f415'},
      {name:'Taste of the Wild', q:'Taste of the Wild dog food grain free', icon:'\U0001f43a'},
      {name:'Orijen Original', q:'Orijen original dog food', icon:'\U0001f969'},
      {name:'Wellness CORE', q:'Wellness CORE grain free dog food', icon:'\U0001f49a'}
    ],
    cat: [
      {name:'Blue Buffalo Wilderness', q:'Blue Buffalo Wilderness cat food', icon:'\U0001f431'},
      {name:'Taste of the Wild Canyon River', q:'Taste of the Wild Canyon River cat food', icon:'\U0001f41f'},
      {name:'Orijen Cat & Kitten', q:'Orijen cat and kitten food', icon:'\U0001f969'},
      {name:'Wellness CORE Indoor', q:'Wellness CORE indoor cat food', icon:'\U0001f49a'}
    ]
  };
  function showBrandRecs(pet) {
    var brands = petBrands[pet] || petBrands.dog;
    var html = '';
    brands.forEach(function(b){
      html += '<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #fed7aa;flex-wrap:wrap">';
      html += '<span style="font-size:24px">'+b.icon+'</span>';
      html += '<span style="flex:1;font-size:14px;font-weight:600;min-width:160px">'+b.name+'</span>';
      html += '<a href="'+chewyUrl(b.q)+'" target="_blank" rel="noopener" style="background:#ea580c;color:#fff;padding:7px 12px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none">Chewy \\u2192</a> ';
      html += '<a href="'+amzPetUrl(b.q)+'" target="_blank" rel="noopener" style="background:#f59e0b;color:#111;padding:7px 12px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none">Amazon \\u2192</a>';
      html += '</div>';
    });
    document.getElementById('brandContent').innerHTML = html;
    document.getElementById('brandRecs').style.display = 'block';
  }

  var petType='dog';"""
    c = c.replace(old_pet, new_pet, 1)

    # 3) Call showBrandRecs at end of analyzeFood
    c = c.replace(
        "document.getElementById('results').scrollIntoView({behavior:'smooth'});\n  }\n  </script>",
        "document.getElementById('results').scrollIntoView({behavior:'smooth'});\n    showBrandRecs(petType);\n  }\n  </script>",
        1
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✓ Pet Food Analyzer – brand recommendations added")


if __name__ == '__main__':
    patch_ai_tool_finder()
    patch_budget_calculator()
    patch_workout_generator()
    patch_pet_food_checker()
    print("\n✅ All 4 templates patched with affiliate placeholders!")
