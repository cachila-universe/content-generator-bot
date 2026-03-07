#!/usr/bin/env python3
"""Update niches.yaml with subtopics for all 8 niches."""
import yaml
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NICHES_PATH = os.path.join(ROOT, 'config', 'niches.yaml')

with open(NICHES_PATH) as f:
    data = yaml.safe_load(f)

niches = data['niches']

# ── Subtopics for each niche ──────────────────────────────────
subtopics = {
    'ai_tools': {
        'ai_apps': {'name': 'AI Apps & Software', 'keywords': ['AI app', 'AI software', 'AI platform', 'AI tool review']},
        'ai_news': {'name': 'AI News', 'keywords': ['AI news', 'AI update', 'OpenAI', 'Google AI', 'AI launch']},
        'ai_automation': {'name': 'AI Automation', 'keywords': ['AI automation', 'workflow', 'AI agent', 'no-code AI']},
        'ai_for_business': {'name': 'AI for Business', 'keywords': ['AI business', 'enterprise AI', 'AI startup', 'AI SaaS']},
        'ai_creative': {'name': 'AI Creative Tools', 'keywords': ['AI art', 'AI video', 'AI music', 'AI design', 'generative AI']},
        'ai_coding': {'name': 'AI for Developers', 'keywords': ['AI coding', 'Copilot', 'Cursor', 'AI IDE', 'code generation']},
    },
    'personal_finance': {
        'investing': {'name': 'Investing', 'keywords': ['investing', 'portfolio', 'ETF', 'index fund', 'dividend']},
        'stocks': {'name': 'Stocks', 'keywords': ['stock', 'shares', 'S&P 500', 'NASDAQ', 'stock pick', 'earnings']},
        'crypto': {'name': 'Crypto', 'keywords': ['crypto', 'Bitcoin', 'Ethereum', 'blockchain', 'DeFi', 'altcoin']},
        'budgeting': {'name': 'Budgeting & Saving', 'keywords': ['budget', 'saving', 'emergency fund', 'frugal', 'money saving']},
        'market_news': {'name': 'Market News', 'keywords': ['market news', 'economy', 'Fed', 'interest rate', 'inflation', 'GDP']},
        'retirement': {'name': 'Retirement', 'keywords': ['401k', 'IRA', 'retirement', 'pension', 'FIRE']},
        'credit': {'name': 'Credit & Loans', 'keywords': ['credit score', 'credit card', 'loan', 'mortgage', 'refinance']},
        'real_estate': {'name': 'Real Estate', 'keywords': ['real estate', 'property', 'housing market', 'rent', 'REIT']},
    },
    'health_biohacking': {
        'supplements': {'name': 'Supplements & Vitamins', 'keywords': ['supplement', 'vitamin', 'magnesium', 'protein', 'creatine', 'omega']},
        'biohacking': {'name': 'Biohacking', 'keywords': ['biohacking', 'nootropic', 'cold plunge', 'red light therapy', 'sauna']},
        'nutrition': {'name': 'Nutrition & Diet', 'keywords': ['nutrition', 'diet', 'fasting', 'keto', 'meal plan', 'macro']},
        'sleep': {'name': 'Sleep Optimization', 'keywords': ['sleep', 'insomnia', 'melatonin', 'circadian', 'sleep tracker']},
        'mental_health': {'name': 'Mental Health', 'keywords': ['mental health', 'stress', 'anxiety', 'meditation', 'mindfulness']},
        'longevity': {'name': 'Longevity & Anti-Aging', 'keywords': ['longevity', 'anti-aging', 'NAD', 'resveratrol', 'telomere']},
    },
    'home_tech': {
        'smart_home': {'name': 'Smart Home', 'keywords': ['smart home', 'home automation', 'Alexa', 'Google Home', 'HomeKit']},
        'security': {'name': 'Home Security', 'keywords': ['security camera', 'Ring', 'smart lock', 'doorbell', 'alarm']},
        'appliances': {'name': 'Smart Appliances', 'keywords': ['robot vacuum', 'Roomba', 'smart TV', 'air purifier', 'smart oven']},
        'entertainment': {'name': 'Home Entertainment', 'keywords': ['home theater', 'soundbar', 'projector', 'streaming device', 'speaker']},
        'networking': {'name': 'Wi-Fi & Networking', 'keywords': ['mesh wifi', 'router', 'Wi-Fi 7', 'range extender', 'smart switch']},
        'energy': {'name': 'Energy & Solar', 'keywords': ['solar panel', 'smart thermostat', 'energy monitor', 'EV charger', 'battery']},
        'product_reviews': {'name': 'Product Reviews', 'keywords': ['review', 'best', 'comparison', 'vs', 'unboxing', 'hands-on']},
    },
    'travel': {
        'tips': {'name': 'Travel Tips & Advice', 'keywords': ['travel tips', 'travel hacks', 'packing', 'airport', 'travel advice', 'budget travel']},
        'destinations': {'name': 'Destinations', 'keywords': ['destination', 'country', 'city guide', 'where to go', 'best places', 'island', 'beach']},
        'flights': {'name': 'Flights & Airports', 'keywords': ['flight', 'airline', 'cheap flights', 'airport', 'booking', 'first class', 'business class']},
        'hotels': {'name': 'Hotels & Accommodation', 'keywords': ['hotel', 'resort', 'Airbnb', 'hostel', 'accommodation', 'booking', 'stay']},
        'car_rental': {'name': 'Car Rental & Transport', 'keywords': ['car rental', 'rental car', 'road trip', 'transport', 'train', 'bus']},
        'travel_gear': {'name': 'Travel Gear & Products', 'keywords': ['luggage', 'backpack', 'travel gear', 'packing cubes', 'travel pillow', 'travel gadget']},
        'digital_nomad': {'name': 'Digital Nomad', 'keywords': ['digital nomad', 'remote work travel', 'coworking', 'visa', 'expat']},
        'travel_insurance': {'name': 'Travel Insurance', 'keywords': ['travel insurance', 'SafetyWing', 'World Nomads', 'coverage', 'medical']},
        'food_culture': {'name': 'Food & Culture', 'keywords': ['food', 'cuisine', 'culture', 'local', 'street food', 'restaurant']},
    },
    'pet_care': {
        'dogs': {'name': 'Dogs', 'keywords': ['dog', 'puppy', 'canine', 'dog breed', 'dog training']},
        'cats': {'name': 'Cats', 'keywords': ['cat', 'kitten', 'feline', 'cat breed', 'indoor cat']},
        'pet_food': {'name': 'Pet Food & Nutrition', 'keywords': ['pet food', 'dog food', 'cat food', 'raw diet', 'grain free']},
        'pet_products': {'name': 'Pet Products & Gear', 'keywords': ['pet product', 'dog toy', 'cat tree', 'pet bed', 'collar', 'leash', 'carrier']},
        'pet_health': {'name': 'Pet Health', 'keywords': ['pet health', 'vet', 'pet insurance', 'vaccination', 'flea', 'tick']},
        'fish_aquarium': {'name': 'Fish & Aquarium', 'keywords': ['fish', 'aquarium', 'fish tank', 'tropical fish', 'reef', 'filter']},
        'exotic_pets': {'name': 'Exotic & Small Pets', 'keywords': ['hamster', 'rabbit', 'bird', 'reptile', 'guinea pig', 'turtle']},
    },
    'fitness_wellness': {
        'workouts': {'name': 'Workouts & Training', 'keywords': ['workout', 'exercise', 'training', 'routine', 'HIIT', 'strength']},
        'equipment': {'name': 'Gym Equipment & Gear', 'keywords': ['equipment', 'dumbbells', 'treadmill', 'kettlebell', 'resistance band', 'home gym']},
        'nutrition': {'name': 'Sports Nutrition', 'keywords': ['protein powder', 'pre-workout', 'creatine', 'BCAA', 'mass gainer']},
        'running': {'name': 'Running & Cardio', 'keywords': ['running', 'running shoes', 'marathon', 'jogging', 'cardio', 'cycling']},
        'yoga_flexibility': {'name': 'Yoga & Flexibility', 'keywords': ['yoga', 'stretching', 'flexibility', 'Pilates', 'mobility']},
        'wearables': {'name': 'Fitness Wearables', 'keywords': ['fitness tracker', 'smartwatch', 'Apple Watch', 'Garmin', 'Fitbit', 'Whoop']},
        'product_reviews': {'name': 'Product Reviews', 'keywords': ['review', 'best', 'comparison', 'vs', 'tested', 'rating']},
    },
    'remote_work': {
        'office_setup': {'name': 'Office Setup', 'keywords': ['home office', 'desk setup', 'standing desk', 'monitor', 'ergonomic chair']},
        'productivity_apps': {'name': 'Productivity Apps', 'keywords': ['productivity app', 'Notion', 'Todoist', 'Trello', 'project management']},
        'remote_jobs': {'name': 'Remote Jobs', 'keywords': ['remote job', 'work from home', 'freelance', 'hiring', 'remote career']},
        'equipment': {'name': 'Equipment & Gear', 'keywords': ['webcam', 'microphone', 'headphones', 'keyboard', 'mouse', 'desk lamp']},
        'tips': {'name': 'Tips & Guides', 'keywords': ['productivity tips', 'time management', 'focus', 'work-life balance']},
        'coworking': {'name': 'Coworking & Spaces', 'keywords': ['coworking', 'shared office', 'workspace', 'coffee shop', 'remote workspace']},
    },
}

# Add new travel affiliate programs
if 'affiliate_programs' in niches['travel']:
    existing_names = [p['name'] for p in niches['travel']['affiliate_programs']]
    if 'Skyscanner' not in existing_names:
        niches['travel']['affiliate_programs'].append({
            'name': 'Skyscanner',
            'url': 'https://skyscanner.com?aff=YOUR_ID',
            'keywords': ['cheap flights', 'flight deals', 'airline tickets']
        })
    if 'RentalCars' not in existing_names:
        niches['travel']['affiliate_programs'].append({
            'name': 'RentalCars',
            'url': 'https://rentalcars.com?aff=YOUR_ID',
            'keywords': ['car rental', 'rental car', 'rent a car']
        })
    if 'Booking.com' not in existing_names:
        niches['travel']['affiliate_programs'].append({
            'name': 'Booking.com',
            'url': 'https://booking.com?aid=YOUR_ID',
            'keywords': ['hotel', 'accommodation', 'resort', 'hostel']
        })

# Inject subtopics
for niche_id, subs in subtopics.items():
    niches[niche_id]['subtopics'] = subs

with open(NICHES_PATH, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print("SUCCESS - subtopics added to all 8 niches")
for nid, n in niches.items():
    subs = n.get('subtopics', {})
    print(f"  {nid}: {len(subs)} subtopics - {list(subs.keys())}")
