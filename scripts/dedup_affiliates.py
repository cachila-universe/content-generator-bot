#!/usr/bin/env python3
"""Remove duplicate affiliate blocks caused by double-matching during apply."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, 'site', 'templates')


def dedup_workout():
    path = os.path.join(TEMPLATES, 'workout_generator.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    n = c.count('var WAFF_TAG')
    if n <= 1:
        print(f"  workout: OK (WAFF_TAG count = {n})")
        return

    # Remove everything from second "/* ── Affiliate config" to the "var sel=" that follows it
    marker = '/* \u2500\u2500 Affiliate config'
    first = c.index(marker)
    second = c.index(marker, first + 1)
    sel_marker = "var sel={goal:'',equip:'',time:'',level:''};"
    # find the sel_marker that comes AFTER the second block
    sel_pos = c.index(sel_marker, second)
    c = c[:second] + c[sel_pos:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"  workout: fixed (removed {n-1} duplicate block(s))")


def dedup_workout_showgear():
    """Also check for duplicate showGear calls at end of generateWorkout"""
    path = os.path.join(TEMPLATES, 'workout_generator.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    n = c.count('showGear(sel.equip)')
    if n > 1:
        # Keep only first occurrence - remove trailing duplicates
        # Replace second occurrence with empty
        first = c.index('showGear(sel.equip)')
        second = c.index('showGear(sel.equip)', first + 1)
        c = c[:second] + c[second + len('showGear(sel.equip);\n'):]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  workout showGear call: deduped ({n} -> 1)")
    else:
        print(f"  workout showGear call: OK ({n})")


def dedup_pet_food():
    path = os.path.join(TEMPLATES, 'pet_food_checker.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Check for duplicate brandRecs div
    n = c.count('id="brandRecs"')
    if n > 1:
        marker = '    <!-- Pet food brand recommendations'
        first = c.index(marker)
        second = c.index(marker, first + 1)
        # Find the end of the second block (the closing </div> before disclaimer)
        disc = '    <div class="disclaimer">'
        disc_pos = c.index(disc, second)
        c = c[:second] + c[disc_pos:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  pet food brandRecs div: deduped ({n} -> 1)")
    else:
        print(f"  pet food brandRecs div: OK ({n})")

    # Check for duplicate PAFF block
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    n = c.count('var PAFF')
    if n > 1:
        marker = '  /* \u2500\u2500 Affiliate config'
        first = c.index(marker)
        second = c.index(marker, first + 1)
        pet_marker = "  var petType='dog';"
        pet_pos = c.index(pet_marker, second)
        c = c[:second] + c[pet_pos:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  pet food PAFF block: deduped ({n} -> 1)")
    else:
        print(f"  pet food PAFF block: OK ({n})")

    # Check for duplicate showBrandRecs calls
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    n = c.count('showBrandRecs(petType)')
    if n > 1:
        first = c.index('showBrandRecs(petType)')
        second = c.index('showBrandRecs(petType)', first + 1)
        c = c[:second] + c[second + len('showBrandRecs(petType);\n'):]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  pet food showBrandRecs: deduped ({n} -> 1)")
    else:
        print(f"  pet food showBrandRecs: OK ({n})")


def dedup_budget():
    path = os.path.join(TEMPLATES, 'budget_calculator.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Check for duplicate BAFF block
    n = c.count('var BAFF')
    if n > 1:
        marker = '  /* \u2500\u2500 Affiliate IDs'
        first = c.index(marker)
        second = c.index(marker, first + 1)
        tab_marker = '  // \u2500\u2500 Tab switching'
        tab_pos = c.index(tab_marker, second)
        c = c[:second] + c[tab_pos:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  budget BAFF block: deduped ({n} -> 1)")
    else:
        print(f"  budget BAFF block: OK ({n})")

    # Check for duplicate showRecs calls
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    for tab in ['budget', 'debt', 'savings', 'emergency']:
        call = f"showRecs('{tab}')"
        n = c.count(call)
        if n > 1:
            print(f"  budget showRecs({tab}): WARNING has {n} calls (leaving as-is, JS will just run twice)")


def dedup_ai_tool():
    path = os.path.join(TEMPLATES, 'ai_tool_finder.html')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    n = c.count('var AITAFF')
    if n > 1:
        marker = '  /* \u2500\u2500 Affiliate tracking'
        first = c.index(marker)
        second = c.index(marker, first + 1)
        tools_marker = '  var aiTools = ['
        tools_pos = c.index(tools_marker, second)
        c = c[:second] + c[tools_pos:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  ai tool AITAFF block: deduped ({n} -> 1)")
    else:
        print(f"  ai tool AITAFF block: OK ({n})")


if __name__ == '__main__':
    print("Deduplicating affiliate blocks...")
    dedup_ai_tool()
    dedup_budget()
    dedup_workout()
    dedup_workout_showgear()
    dedup_pet_food()
    print("\nDone!")
