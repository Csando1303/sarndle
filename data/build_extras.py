"""Build meal-deal sides (snacks) and drinks data for the future full Sarndle meal deal.

Sources (checked 18 Nov 2026, standard non-loyalty shelf prices):
  Tesco     https://www.tesco.com/shop/en-GB/buylists/lunch-meal-deals/meal-deal-snacks (+ /crisps, /sweet-treats)
            https://www.tesco.com/shop/en-GB/buylists/lunch-meal-deals/meal-deal-drinks (+ /water, /juice-and-smoothies, /fizzy-drinks)
  Morrisons https://groceries.morrisons.com/offers/food-to-go-meal-deal-for-3-75/BUL-cc5dd9850e98816cc521280
Online lists are a subset of what's in store (Tesco online shows ~70 of its sides/drinks; Morrisons ~295).
Sainsbury's, Asda, Co-op, Waitrose, Boots and M&S didn't give a readable list (bot-blocked or JS-only).

Outputs: sides.csv/json, drinks.csv/json (one row per shop listing) and
         sides_products.json / drinks_products.json (merged by product, with every shop + price).
"""
import csv, json, re
from pathlib import Path

HERE = Path(__file__).parent
CHECKED = "2026-11-18"
SRC = {
    "Tesco": "https://www.tesco.com/shop/en-GB/buylists/lunch-meal-deals",
    "Morrisons": "https://groceries.morrisons.com/offers/food-to-go-meal-deal-for-3-75/BUL-cc5dd9850e98816cc521280",
}
DEAL = {"Tesco": "£3.85 Clubcard / £4.25", "Morrisons": "£3.65 More Card / £3.75"}

# ---------------- raw lists: name|price (blank price = out of stock online) ----------------
SIDES = {"Tesco": """The Gym Kitchen Chicken Tikka Bites 45g|1.30
Tesco Vegetable Samosa 110g|2.00
Tesco Mini Savoury Eggs 65g|
Tesco Egg Protein Pot 90g|1.40
Fridge Raiders Slow Roasted Chicken Bites 45g|1.35
Taste Original Chicken Satay Snack 40g|1.30
Tesco 2 Mini Melton Mowbray Pork Pies 100g|1.40
Wall's Large Pork Sausage Roll 100g|1.30
Tesco Egg & Salad Cream 130g|1.40
Fridge Raiders Southern Style Chicken Bites 45g|1.35
Higgidy Cheddar & Caramelised Onion Chutney Rolls x2 54g|1.50
Strings & Things Cheestrings Twin Pack 40g|1.30
Peperami Original Salami 22.5g|1.30
Tesco Green Olives With Herbs 60g|1.40
Tesco Cocktail Sausages & Ketchup Dip 98g|1.30
Higgidy Ham Hock & Cheddar Sausage Rolls x2 54g|1.50
Peperami Red Hot Stick 22.5g|1.30
Jacob's Mini Cheddars Original Grab Bag 45g|1.10
Discos Salt & Vinegar Grab Bag Crisps 50g|1.25
Pringles Original Snacking Crisps 40g|1.25
Pringles Sour Cream & Onion Snacking Crisps 40g|1.25
Hula Hoops Big Hoops Salt & Vinegar Grab Bag 45g|1.25
Walkers Baked Sea Salt Crisps 37.5g|1.35
McCoy's Cheddar & Onion Grab Bag Crisps 45g|1.25
Nik Naks Nice 'N' Spicy Grab Bag Crisps 45g|1.25
McCoy's Thai Sweet Chicken Grab Bag Crisps 45g|1.25
Walkers Baked Cheese & Onion Grab Bag Crisps 37.5g|1.35
Hula Hoops Big Hoops Salted Grab Bag 45g|1.25
McCoy's Salt & Vinegar Grab Bag Crisps 45g|1.25
McCoy's Flame Grilled Steak Grab Bag 45g|1.25
Hula Hoops Big Hoops Barbecue Beef 45g|1.25
McCoy's Sizzling King Prawn Grab Bag Crisps 45g|1.25
Propercorn Sweet & Salty 30g|1.15
Walkers Wotsits Cheese Grab Bag 36g|1.35
Walkers Ready Salted Grab Bag Crisps 45g|1.35
Walkers Squares Salt & Vinegar Grab Bag 40g|1.35
Walkers Quavers Cheese Grab Bag 34g|1.35
Walkers Cheese & Onion Grab Bag Crisps 45g|1.35
Kinder Bueno Bar 43g|1.00
Kinder Bueno White 39g|1.00
KitKat 4 Finger Milk Chocolate Bar 41.5g|1.00
Nutella & Go! Hazelnut Spread and Breadsticks 48g|
Ferrero Rocher 3 Pack 37.5g|1.65
Cadbury Wispa Gold Chocolate & Caramel Bar 48g|1.00""",
"Morrisons": """Morrisons Golden Syrup Porridge|0.55
Morrisons Original Porridge Pot|0.55
Morrisons 2 Hard Boiled Eggs Pot 90g|1.55
Nutella & Go! Hazelnut Spread and Breadsticks 48g|1.35
Hula Hoops Big Hoops Barbecue Beef 45g|1.25
Nomadic Oat Crunch Chocolate & Yogurt|1.85
Hula Hoops Big Hoops Salted Grab Bag 45g|1.25
Ginsters Original Cornish Pasty 130g|1.65
Morrisons Jumbo Vegetable Samosa|1.50
Taste Original Chicken Satay With Sweet Chilli Dip 55g|1.75
Morrisons Mini Pork Pies (2 per pack)|1.40
Morrisons Snack Seafood Sticks With Marie Rose Sauce|2.30
Morrisons Individual Sausage Roll|1.35
Del Monte Apple, Grape & Strawberry|1.50
Morrisons Carrot Sticks & Houmous|1.40
Del Monte Pineapple Chunks|1.50
Graze Oat Boosts Lemon Drizzle Flapjack 50g|1.00
Tyrrells Sea Salted Crisps|1.10
Maltesers Chocolate & Honeycomb Snack Bag 37g|1.20
Walkers Quavers Cheese Grab Bag 34g|1.25
Gu Zillionaire Cheesecake|2.00
Twix Xtra Chocolate Biscuit Twin Bars 75g|1.50
Maltesers Chocolate Reindeer 29g|0.70
Fridge Raiders Slow Roasted Chicken Bites 45g|1.40
Cadbury Twirl Xtra Duo Chocolate Bar|1.35
Cadbury Starbar Chocolate Bar|1.00
Morrisons King Prawns With A Sweet Chilli Dip|2.30
Lindt Lindor Milk Chocolate Treat Bar 38g|1.35
McCoy's Flame Grilled Steak Grab Bag 45g|1.25
Wall's Individual Scotch Egg 113g|1.50
Walkers Wotsits Really Cheesy Grab Bag|1.25
KitKat Chunky Milk Chocolate Duo 64g|1.30
Nomadic Power Pot Vanilla Yogurt & Granola Smooth Caramel|2.25
Walkers Monster Munch Sweet & Spicy|1.25
Walkers Monster Munch Pickled Onion 40g|1.25
Eatlean Protein Cheese Bar 60g|1.25
Soreen 2 Malt Loaf Slices 45g|1.30
Walkers Baked Prawn Cocktail Crisps|1.25
Nestle Milkybar Medium|1.00
Kinder Bueno Bar 43g|1.00
Cadbury Dairy Milk Chocolate Puds 35g|0.70
Walkers Ready Salted Grab Bag Crisps 45g|1.25
McCoy's Salt & Vinegar Grab Bag Crisps 45g|1.25
KitKat Santa Milk Chocolate Christmas Figure 29g|0.70
Skips Prawn Cocktail Crisps|1.25
Walkers Baked Cheese & Onion Grab Bag Crisps 37.5g|1.25
McCoy's Cheddar & Onion Grab Bag Crisps 45g|1.25
Walkers Baked Salt & Vinegar Crisps|1.20
Cadbury Crunchie Chocolate Bar|1.00
Morrisons Onion Bhaji & Mango Chutney Snack Pot|1.50
Morrisons Millionaire Bar|1.30
Nomadic Power Pot Vanilla Yogurt & Granola & Chocolate Brownie|2.25
Kinder Surprise Milk Chocolate Egg Natoons|1.25
Morrisons Brookie Bar|1.45
Jacob's Mini Cheddars Original Grab Bag 45g|1.10
Morrisons All Butter Flapjack Bar 50g|1.45
Walkers Squares Salt & Vinegar Grab Bag 40g|1.25
Muller MyProtein Vanilla Yogurt with Chocolate Balls 180g|2.00
McCoy's Hot 'N' Spicy Crisps 45g|1.25
Walkers Baked Sea Salt Crisps 37.5g|1.25
Cadbury Wispa Duo Chocolate Bar|1.35
Fridge Raiders Southern Style Chicken Bites 45g|1.40
Walkers French Fries Worcester Sauce|0.95
Morrisons Brownie Bar|1.25
Graze Oat Boosts Cherry Bakewell Flapjack 50g|1.00
McCoy's Thai Sweet Chicken Grab Bag Crisps 45g|1.25
Cadbury Twirl Orange|1.00
Cadbury Boost Duo Chocolate Bar|1.35
Walkers Sensations Thai Sweet Chilli Grab Bag Crisps|1.25
Dairylea Dunkers Jumbo 41g|1.30
KitKat 4 Finger Milk Chocolate Bar 41.5g|1.00
Maltesers Gingerbread Chocolate Reindeer 29g|0.70
Popchips Sea Salt|1.00
Walkers Prawn Cocktail Crisps 45g|1.25
Cadbury Starbar Duo|1.35
Yorkie Original Duo|1.30
Bounty Coconut & Chocolate Duo 57g|1.20
Activia Fibre Yogurt & Red Berries Granola 165g|1.70
Strings & Things Cheestrings Twin Pack 40g|1.40
M&M's Crispy Milk Chocolate Christmas Santa 29g|0.70
Cadbury Double Decker Duo Chocolate Bar|1.35
Fruitella Strawberry Stick 40g|0.75
Kinder Bueno White 39g|1.00
Galaxy Caramel Milk Chocolate Bar 48g|1.20
Popchips Barbecue|1.00
Nomadic Protein Pudding Chocolate 200g|2.00
Walkers Smoky Bacon Crisps 45g|1.25
Kinder Surprise Milk Chocolate Egg 20g|1.25
Walkers Lea & Perrins Worcester Sauce Crisps 45g|1.20
Morrisons Chocolate Caramel Tiffin Bar|1.45
Cuzena Chip & Dip Jalapeno Houmous With Toasted Pretzels|2.70
Cadbury Boost Chocolate Bar 48.5g|1.00
Walkers Heinz Tomato Ketchup Crisps 45g|1.25
Cadbury Wispa|1.00
Cadbury Double Decker Chocolate Bar|1.00
Yorkie Brownie Duo|1.30
Walkers Sensations Mature Cheddar & Chilli Crisps|1.10
Morrisons All Butter Flapjack Bar 45g|1.25
Graze Oat Boosts Cocoa & Vanilla Flapjack 50g|1.00
Cadbury Twirl Chocolate Bar|1.00
Nik Naks Nice 'N' Spicy Grab Bag Crisps 45g|1.25
Galaxy Milk Chocolate Bar 42g|1.20
Morrisons Rocky Road With Belgian Milk Chocolate Bar|1.45
Walkers BBQ Sauce Crisps 45g|1.20
Cadbury Wispa Gold Chocolate & Caramel Bar 48g|1.00
Morrisons Chocolate Brownie Bar 45g|1.25
Nomadic Yogurt And Oat Bar Chocolate|2.00
Yorkie Brownie|1.00
Cheez-It Snap'd Cheese & Chilli 40g|1.00
Walkers Salt & Vinegar Crisps 45g|1.25
Discos Salt & Vinegar Grab Bag Crisps 50g|1.25
Cadbury Dairy Milk Caramel|1.00
Kinder Milk Chocolate Medium Bars|0.90
Galaxy Ripple Chocolate Bar 30g|1.20
Twix Caramel Biscuit Chocolate Bars 50g|1.20
Lion Milk Duo|1.30
Walkers Roast Chicken Crisps 45g|1.25
Properchips Barbecue Lentil Chips|1.35
Popchips Sour Cream & Onion|1.10
Propercorn Sweet & Salty 30g|1.00
Mentos Fruit 38g|0.95
Cheez-It Snap'd Double Cheese 40g|1.00
Cadbury Fairtrade Dairy Milk|1.00
Morrisons Millionaire Shortbread Bar 45g|1.25
Popworks Sweet BBQ Popped Crisps|1.10
Doritos Tangy Cheese 48g|1.10
Popchips Sea Salt & Vinegar|1.00
Twix Crispy Wafer Roll|0.75
Aero Bubbly Peppermint Bar|1.00
Walkers Sticky Teriyaki Crisps|1.10
Walkers Masala Chicken Crisps|1.10
Walkers Max Pizza Hut Texan BBQ Grab Bag 50g|1.10
Walkers Quavers Prawn Cocktail|1.10
Taste Original Southern Fried Chicken Skewers With Chipotle BBQ Dip 55g|1.75
Walkers Less Salt Lightly Salted Crisps 45g|1.20
Nakd Cocoa Orange Bar|0.99
Walkers Max Paprika Crisps|1.20
KitKat Chunky Caramel Milk Chocolate Bar|0.75
Nakd Bakewell Tart Bar|1.00
Walkers Quavers BBQ Sauce 34g|1.10
Kettle Ridge Cut Asian Chilli Beef 40g|1.45
Morrisons 2 Pork & Cranberry Pies 100g|1.50
Walkers Sensations Thai Sweet Chilli Crisps|1.10
Proper Chips Sea Salt Lentil Chips 31g|1.10
Popworks Sweet & Salty Popped Crisps|1.20
Philadelphia Light Cream Cheese Snacks 42g|1.50"""}

DRINKS = {"Tesco": """Volvic Touch of Fruit Strawberry 750ml|1.95
Evian Still Mineral Water 750ml|1.85
Evian Still Mineral Water 500ml|1.50
Cano Still Spring Water 500ml|1.10
Innocent Super Smoothie Invigorate Kiwi & Cucumber 300ml|2.80
Innocent Super Smoothie Tropical Defence Mango & Coconut 300ml|2.80
Innocent Super Smoothie Energise 300ml|2.80
Naked Blue Machine Blueberry Smoothie 300ml|2.90
Copella Apple Juice 300ml|1.95
Vita Coco Original Coconut Water 500ml|2.50
Tropicana Orange Juice Original 300ml|2.25
Innocent Smoothie Strawberries & Bananas 250ml|2.00
Juice Burst Orange 500ml|2.00
Capri-Sun Orange 330ml|1.50
Diet Coke 500ml|1.85
Coca-Cola Original Taste 500ml|1.89
Coca-Cola Zero Sugar 330ml|1.45
Oasis Citrus Punch 500ml|2.15
Fanta Fruit Twist 500ml|2.10
Dr Pepper 500ml|2.10
Oasis Summer Fruits 500ml|2.15
Ribena Blackcurrant 500ml|1.85
Pepsi Max No Sugar 500ml|1.89
Pepsi Max Cherry No Sugar 500ml|1.89
Irn-Bru 500ml|1.29
Coca-Cola Zero Sugar Cherry 500ml|1.85
Diet Coke 330ml|1.45""",
"Morrisons": """Oasis Summer Fruits 500ml|2.15
Pepsi Max No Sugar 500ml|2.00
Diet Coke 500ml|2.00
Coca-Cola Original Taste 500ml|2.10
Oasis Citrus Punch 500ml|2.15
Red Bull Energy Drink 473ml|2.85
Ribena Blackcurrant No Added Sugar 500ml|1.70
Carabao Energy Drink Mixed Berry 330ml|0.85
Coca-Cola Zero Sugar 500ml|1.95
Highland Spring Still Water Sports Cap 750ml|1.15
Evian Still Mineral Water Sports Cap 750ml|1.85
Pepsi Max Cherry No Sugar 500ml|2.00
UFIT High Protein Shake White Chocolate 330ml|2.00
Fanta Orange Zero 500ml|1.95
Starbucks Caramel Macchiato Iced Coffee 330ml|2.80
Buxton Still Mineral Water Sports Cap 1L|1.75
Dr Pepper 500ml|2.05
Lucozade Energy Original 500ml|1.85
Starbucks Caffe Latte Iced Coffee 330ml|2.80
Ribena Blackcurrant 500ml|1.70
Rubicon Spring Orange Mango 500ml|1.60
Juice Burst Apple 500ml|1.95
Monster Energy Mango Loco 500ml|2.15
Carabao Energy Drink Original 330ml|0.85
Innocent Smoothie Strawberries, Bananas & Apples 250ml|2.00
Juice Burst Orange 500ml|1.95
Monster Energy Ultra Zero Sugar 500ml|2.10
Innocent Super Smoothie Energise 300ml|2.80
Relentless Origin Energy Drink 500ml|1.00
Starbucks Tripleshot Espresso Iced Coffee 300ml|2.50
Monster Energy Pacific Punch 500ml|2.10
Glaceau Smartwater Still 600ml|1.50
Vita Coco Original Coconut Water 500ml|2.50
Dr Pepper Zero 500ml|2.00
Sprite 500ml|1.95
Mountain Dew 500ml|1.95
Lucozade Energy Orange 500ml|1.85
Lipton Ice Tea Peach 500ml|2.10
Carabao Energy Drink Green Apple 330ml|0.85
Pepsi Max No Caffeine No Sugar 500ml|2.15
7UP Zero Sugar Lemon & Lime 500ml|2.10
Coca-Cola Cherry 500ml|2.10
Red Bull Energy Drink 250ml|1.85
Vimto 500ml|1.45
Monster Energy Ultra Fiesta Mango Zero Sugar 500ml|2.00
Monster Energy Ultra Strawberry Dreams Zero Sugar 500ml|2.10
San Pellegrino Sparkling Mineral Water 500ml|1.50
Coca-Cola Zero Sugar Cherry 500ml|2.00
Jimmy's Iced Coffee Original 380ml|2.75
Fanta Orange 500ml|2.05
7UP Zero Sugar Pink Lemonade 500ml|2.10
Irn-Bru Zero 500ml|1.60
Monster Energy Khaotic 500ml|2.10
Red Bull Sugar Free 473ml|2.75
Fanta Lemon 500ml|2.00
Powerade Berry & Tropical 500ml|2.20
Volvic Touch of Fruit Strawberry 750ml|1.95
Fanta Fruit Twist 500ml|2.05
Jimmy's Iced Coffee Caramel 380ml|2.75
Monster Energy 500ml|2.15
Dr Pepper Zero Cherry Crush 500ml|2.05
Diet Irn-Bru 500ml|1.60
Lucozade Sport Orange 500ml|1.85
Lipton Ice Tea Lemon 500ml|2.10
Red Bull Sugar Free 355ml|2.30
Evian Still Mineral Water 500ml|1.50
Red Bull Energy Drink 355ml|2.30
Irn-Bru 500ml|1.80
Monster Energy Monarch 500ml|2.10
Monster Energy Zero Sugar 500ml|2.10
Monster Energy Pipeline Punch 500ml|2.15
Lucozade Sport Raspberry 500ml|1.85
Lucozade Zero Sugar Pink Lemonade 500ml|1.85
Capri-Sun Orange 330ml|1.50
Pepsi Zero Sugar Cream Soda 500ml|2.00
Pepsi Zero Sugar Strawberries And Cream 500ml|2.00
Buxton Still Mineral Water 500ml|0.75
Monster Energy Aussie Style Lemonade 500ml|2.10
Vit Hit Lean & Green Apple & Elderflower 500ml|1.85
Pepsi Regular 500ml|2.15
Monster Energy Ultra Rosa Zero Sugar 500ml|2.10
Monster Energy Ultra Peachy Keen Zero Sugar 500ml|2.10
Plenish Ginger Immunity Shot 60ml|2.00
Red Bull Sugar Free Ice Edition Iced Vanilla Berry 355ml|2.20
Sprite Zero Sugar 500ml|2.00
Monster Energy Lando Norris Zero Sugar 500ml|2.10
Lipton Ice Tea Raspberry 500ml|2.15
Vit Hit Perform Orange Mango Passionfruit 500ml|1.80
Get More Vits Vitamin D Mango & Passionfruit 500ml|1.25
Monster Energy Ultra Fantasy Ruby Red Zero Sugar 500ml|2.10
Lucozade Sport Lemon & Lime 500ml|1.85
TRIP Wild Strawberry CBD Drink 330ml|2.20
Monster Energy Rio Punch 500ml|2.10
Red Bull Sugar Free Peach Edition White Peach 473ml|2.75
Vimto Original Energy 500ml|1.45
Monster Energy Full Throttle Zero Sugar 500ml|2.00
Coca-Cola Zero Sugar Lime 500ml|1.95
Deeside Still Mineral Water 500ml|0.55
Volvic Touch of Fruit Mango Passion Sugar Free 750ml|1.85
Red Bull Sugar Free Pink Edition Forest Fruits 355ml|2.20
Plenish Turmeric Defence Shot 60ml|2.00
Red Bull Sugar Free Blue Edition Juneberry 355ml|2.20
Red Bull Sugar Free 250ml|1.85
Rubicon Sparkling Mango 500ml|2.00
Red Bull Sugar Free Ice Edition Iced Vanilla Berry 473ml|2.75
Red Bull Zero 355ml|2.20
Tango Sugar Free Apple 500ml|2.00
Harry Brompton's Peach Iced Tea 500ml|1.80
Remedy Kombucha Wild Berry 250ml|1.85
Irn-Bru 1901 Can 330ml|0.72
Rubicon Sparkling Passion Fruit 500ml|1.95
Brecon Carreg Still Mineral Water 500ml|0.60
Starbucks Tripleshot Espresso No Added Sugar Iced Coffee 300ml|2.40
PWR-BRU Energy Drink Original 500ml|1.40
Vimto No Added Sugar Still 500ml|1.50
Vimto Still Fruity Spring Water 500ml|1.45
Tenzing Natural Energy Pineapple & Passion Fruit 330ml|1.95
PWR-BRU Energy Drink Diablo Cherry 500ml|1.40
Purdey's Natural Energy Apple & Grape 330ml|1.75
Tango Sugar Free Mango 500ml|1.60
Pepsi Cola 500ml|1.60
Prime Energy Blue Raspberry 330ml|1.49
Highland Spring Still Water 500ml|0.75
Overhang Orange, Ginger & Lime 250ml|1.50
Drip Sparkling Mineral Water 500ml|1.00
Pepsi Max Mango No Sugar 500ml|1.90
Diet Coke Sublime Lime 500ml|2.00
Drip Still Mineral Water 500ml|1.00
Rubicon Raw Energy Pineapple Passion Fruit 500ml|1.40
Fix8 Kombucha Sicilian Citrus 250ml|2.00
Prime Hydration Blue Raspberry 500ml|2.00
Highland Spring Sparkling Water 500ml|1.00
Buxton Still Mineral Water Sports Cap 750ml|1.00
Volvic Touch of Fruit Strawberry Sugar Free 750ml|1.45
Vimto Blackberry, Raspberry & Blueberry No Added Sugar 500ml|1.45
Prime Energy Ice Pop 330ml|1.49
Prime Energy Orange Mango 330ml|1.50
Juice Burst Summer Fruits 500ml|1.95
Prime Hydration Lemon Lime 500ml|2.00
Fix8 Kombucha Strawberry Basil 250ml|2.00
Prime Hydration Ice Pop 500ml|2.00
Prime Hydration Cherry Freeze 500ml|2.00
Prime Hydration Strawberry Watermelon 500ml|2.00
Prime Hydration Lemonade 500ml|2.00
Prime Hydration Meta Moon 500ml|2.00
UFIT Lite Smooth Chocolate Protein Shake 310ml|2.00
Starbucks Skinny Latte Iced Coffee 330ml|2.75
Red Bull Sugar Free Lilac Edition Grapefruit & Blossom 355ml|2.10"""}

# ---------------- brands -> maker (yellow = same maker) ----------------
BRANDS = [  # (match text, brand, maker). Longest/most specific first.
 ("monster munch","Monster Munch","PepsiCo"),("wotsits","Wotsits","PepsiCo"),("quavers","Quavers","PepsiCo"),
 ("squares","Walkers","PepsiCo"),("sensations","Walkers","PepsiCo"),("french fries","Walkers","PepsiCo"),("walkers","Walkers","PepsiCo"),
 ("doritos","Doritos","PepsiCo"),("popworks","Popworks","PepsiCo"),("pepsi","Pepsi","PepsiCo"),("7up","7UP","PepsiCo"),
 ("mountain dew","Mountain Dew","PepsiCo"),("naked","Naked","PepsiCo"),("lipton","Lipton","PepsiCo"),
 ("mccoy","McCoy's","KP Snacks"),("hula hoops","Hula Hoops","KP Snacks"),("discos","Discos","KP Snacks"),("nik naks","Nik Naks","KP Snacks"),
 ("skips","Skips","KP Snacks"),("tyrrells","Tyrrells","KP Snacks"),("popchips","Popchips","KP Snacks"),
 ("pringles","Pringles","Kellanova"),("cheez-it","Cheez-It","Kellanova"),("jacob","Jacob's","Pladis"),
 ("propercorn","Propercorn","Propercorn"),("properchips","Proper","Propercorn"),("proper chips","Proper","Propercorn"),
 ("cadbury","Cadbury","Mondelez"),("philadelphia","Philadelphia","Mondelez"),("dairylea","Dairylea","Mondelez"),
 ("maltesers","Maltesers","Mars"),("galaxy","Galaxy","Mars"),("twix","Twix","Mars"),("bounty","Bounty","Mars"),("m&m","M&M's","Mars"),
 ("kitkat","KitKat","Nestlé"),("milkybar","Milkybar","Nestlé"),("aero","Aero","Nestlé"),("yorkie","Yorkie","Nestlé"),("lion","Lion","Nestlé"),
 ("kinder","Kinder","Ferrero"),("nutella","Nutella","Ferrero"),("ferrero","Ferrero Rocher","Ferrero"),
 ("lindt","Lindt","Lindt"),("mentos","Mentos","Perfetti"),("fruitella","Fruitella","Perfetti"),
 ("fridge raiders","Fridge Raiders","Pilgrim's"),("peperami","Peperami","Jack Link's"),("wall's","Wall's","Pork Farms"),
 ("ginsters","Ginsters","Samworth Brothers"),("higgidy","Higgidy","Samworth Brothers"),("strings & things","Cheestrings","Kerry"),
 ("taste original","Taste Original","Taste Original"),("gym kitchen","The Gym Kitchen","The Gym Kitchen"),
 ("nomadic","Nomadic","Nomadic"),("graze","Graze","Unilever"),("nakd","Nakd","Lotus Bakeries"),("soreen","Soreen","Soreen"),
 ("muller","Müller","Müller"),("activia","Activia","Danone"),("eatlean","Eatlean","Eatlean"),("gu","Gü","Gü"),
 ("del monte","Del Monte","Del Monte"),("cuzena","Cuzena","Cuzena"),("kettle","Kettle","Campbell's"),
 ("diet coke","Coca-Cola","Coca-Cola"),("coca-cola","Coca-Cola","Coca-Cola"),("fanta","Fanta","Coca-Cola"),("sprite","Sprite","Coca-Cola"),
 ("dr pepper","Dr Pepper","Coca-Cola"),("oasis","Oasis","Coca-Cola"),("innocent","Innocent","Coca-Cola"),("smartwater","Smartwater","Coca-Cola"),
 ("powerade","Powerade","Coca-Cola"),("monster","Monster","Coca-Cola"),("relentless","Relentless","Coca-Cola"),("capri-sun","Capri-Sun","Capri Sun"),
 ("ribena","Ribena","Suntory"),("lucozade","Lucozade","Suntory"),("evian","Evian","Danone"),("volvic","Volvic","Danone"),
 ("irn-bru","Irn-Bru","AG Barr"),("rubicon","Rubicon","AG Barr"),("pwr-bru","PWR-BRU","AG Barr"),("tango","Tango","Britvic"),
 ("red bull","Red Bull","Red Bull"),("carabao","Carabao","Carabao"),("prime","Prime","Prime"),("vimto","Vimto","Nichols"),
 ("starbucks","Starbucks","Arla"),("jimmy","Jimmy's","Jimmy's"),("ufit","UFIT","UFIT"),("vita coco","Vita Coco","Vita Coco"),
 ("tropicana","Tropicana","Tropicana"),("copella","Copella","Tropicana"),("juice burst","Juice Burst","Purity Soft Drinks"),
 ("highland spring","Highland Spring","Highland Spring"),("buxton","Buxton","Nestlé"),("san pellegrino","San Pellegrino","Nestlé"),
 ("deeside","Deeside","Deeside"),("brecon","Brecon Carreg","Brecon Carreg"),("drip","Drip","Drip"),("cano","Cano","Cano"),
 ("vit hit","Vit Hit","Vit Hit"),("get more vits","Get More Vits","Get More"),("plenish","Plenish","Plenish"),("trip","TRIP","TRIP"),
 ("tenzing","Tenzing","Tenzing"),("purdey","Purdey's","Britvic"),("overhang","Overhang","Overhang"),("harry brompton","Harry Brompton's","Harry Brompton's"),
 ("remedy","Remedy","Remedy"),("fix8","Fix8","Fix8"),
 ("tesco","Tesco","Tesco"),("morrisons","Morrisons","Morrisons"),
]
def brand(n):
    l=n.lower()
    for k,b,m in BRANDS:
        if re.search(r"(?<![a-z])"+re.escape(k.strip())+r"(?![a-z])",l): return b,m
    return n.split()[0],n.split()[0]

def has(n,*ws): l=n.lower(); return any(w in l for w in ws)

# ---------------- sides ----------------
SIDE_FAMILY={"Crisps":"Salty","Popcorn":"Salty","Crackers":"Salty",
 "Chocolate":"Sweet","Sweets":"Sweet","Bakes":"Sweet","Snack bar":"Sweet",
 "Yogurt & pots":"Fresh","Fruit & veg":"Fresh",
 "Meat bites":"Chilled savoury","Pastry":"Chilled savoury","Egg":"Chilled savoury","Seafood":"Chilled savoury","Cheese":"Chilled savoury","Dips & olives":"Chilled savoury"}
def side_type(n):
    if has(n,"porridge","yogurt","pudding","power pot","nutella"): return "Yogurt & pots"
    if has(n,"del monte","carrot"): return "Fruit & veg"
    if has(n,"egg") and not has(n,"kinder","scotch"): return "Egg"
    if has(n,"prawns with","seafood"): return "Seafood"
    if has(n,"sausage roll","pork pie","pies","pasty","samosa","bhaji","higgidy","scotch egg"): return "Pastry"
    if has(n,"chicken bites","chicken satay","skewers","tikka bites","peperami","cocktail sausages"): return "Meat bites"
    if has(n,"cheestrings","dunkers","cheese bar","philadelphia"): return "Cheese"
    if has(n,"olives","houmous"): return "Dips & olives"
    if has(n,"propercorn","popcorn"): return "Popcorn"
    if has(n,"mini cheddars","cheez-it"): return "Crackers"
    if has(n,"mentos","fruitella"): return "Sweets"
    if has(n,"flapjack","brownie","brookie","millionaire","tiffin","rocky road","malt loaf","cheesecake","puds"): return "Bakes"
    if has(n,"nakd","oat crunch","oat bar"): return "Snack bar"
    if has(n,"chocolate","kinder","kitkat","wispa","twirl","boost","starbar","crunchie","milkybar","aero","yorkie","lion","dairy milk","ferrero","galaxy","bounty","twix","maltesers","lindt"): return "Chocolate"
    return "Crisps"
FLAV=[("cheese & onion","Cheese & onion"),("cheddar & onion","Cheese & onion"),("sour cream & onion","Sour cream & onion"),
 ("salt & vinegar","Salt & vinegar"),("sea salt & vinegar","Salt & vinegar"),("prawn cocktail","Prawn cocktail"),
 ("sweet chilli","Sweet chilli"),("thai sweet chicken","Sweet chilli"),("bbq","BBQ"),("barbecue","BBQ"),("steak","Beef"),("beef","Beef"),
 ("smoky bacon","Bacon"),("worcester","Worcester sauce"),("ketchup","Tomato"),("pickled onion","Pickled onion"),("teriyaki","Teriyaki"),
 ("masala","Spicy"),("paprika","Spicy"),("chilli","Spicy"),("spicy","Spicy"),("hot","Spicy"),("jalapeno","Spicy"),("red hot","Spicy"),
 ("roast chicken","Chicken"),("chicken","Chicken"),("king prawn","Prawn"),("prawn","Prawn"),("seafood","Fish"),
 ("ham","Pork"),("pork","Pork"),("sausage","Pork"),("salami","Pork"),("peperami","Pork"),
 ("cheese","Cheese"),("cheesy","Cheese"),("cheddar","Cheese"),("cheestrings","Cheese"),("dunkers","Cheese"),
 ("egg","Egg"),("vegetable","Vegetable"),("samosa","Vegetable"),("bhaji","Onion"),("houmous","Houmous"),("olives","Olive"),
 ("sweet & salty","Sweet & salty"),("ready salted","Salted"),("sea salt","Salted"),("salted","Salted"),("lightly salted","Salted"),("original","Original"),
 ("caramel","Caramel"),("millionaire","Caramel"),("toffee","Caramel"),("hazelnut","Hazelnut"),("bueno","Hazelnut"),("ferrero","Hazelnut"),("nutella","Hazelnut"),
 ("honeycomb","Honeycomb"),("crunchie","Honeycomb"),("coconut","Coconut"),("orange","Orange"),("peppermint","Mint"),("vanilla","Vanilla"),
 ("strawberry","Strawberry"),("red berries","Berry"),("cherry","Cherry"),("bakewell","Cherry"),("lemon","Lemon"),("pineapple","Pineapple"),("apple","Apple"),("grape","Grape"),
 ("gingerbread","Ginger"),("mentos fruit","Mixed fruit"),("cranberry","Cranberry"),("oat","Oat"),("granola","Oat"),("flapjack","Oat"),("porridge","Oat"),("golden syrup","Syrup"),
 ("biscuit","Biscuit"),("wafer","Biscuit"),("kitkat","Biscuit"),("twix","Biscuit"),("shortbread","Biscuit"),("chutney","Chutney"),("carrot","Vegetable"),("malt","Malt")]
def flavours(n,t):
    l=n.lower().replace("pineapple","pineapple_").replace("cheesecake","cheezcake")
    l2=l.replace("sweet chilli",""); out=[]
    for k,f in FLAV:
        if k in l and f not in out:
            if f=="Cheese" and ("Cheese & onion" in out): continue
            if f=="Salted" and ("Salt & vinegar" in out or "Sweet & salty" in out): continue
            if f=="Prawn" and "Prawn cocktail" in out: continue
            if f=="Chicken" and "thai sweet" in l: continue
            if f=="Spicy" and not any(w in l2 for w in("masala","paprika","chilli","spicy","hot","jalapeno")): continue
            if f=="Egg" and "kinder" in l: continue
            if f=="Apple" and "pineapple_" in l and "apple," not in l: continue
            out.append(f)
    if "scotch egg" in l: out.append("Pork")
    if t=="Chocolate" or any(w in l for w in("choc","cocoa","brownie","brookie","rocky road","tiffin","millionaire","puds","zillionaire")):
        if "Chocolate" not in out: out.insert(0,"White chocolate" if "white" in l or "milkybar" in l else "Chocolate")
    if len(out)>1 and "Original" in out: out.remove("Original")
    if not out: out=["Original"]
    return out
def festive(n): return has(n,"christmas","santa","reindeer","gingerbread","cranberry")

def weight(n):
    m=re.search(r"(\d+(?:\.\d+)?)\s?g\b",n,re.I); return float(m.group(1)) if m else None

CHILLED={"Yogurt & pots","Fruit & veg","Meat bites","Pastry","Egg","Seafood","Cheese","Dips & olives"}

def rows(raw,kind):
    out=[]
    for shop,txt in raw.items():
        for line in txt.strip().splitlines():
            n,p=line.rsplit("|",1); b,m=brand(n)
            r={"name":n,"shop":shop,"price_gbp":float(p) if p else None,"brand":b,"maker":m}
            if kind=="side":
                t=side_type(n)
                if "porridge" in n.lower(): r_ch=False
                else: r_ch=t in CHILLED
                r.update(type=t,family=SIDE_FAMILY[t],flavours=flavours(n,t),weight_g=weight(n),chilled=r_ch,
                         range="Festive" if festive(n) else ("Protein" if has(n,"protein","gym kitchen","eatlean","myprotein") else "Standard"))
            else:
                t=drink_type(n)
                r.update(type=t,family=DRINK_FAMILY[t],flavours=dflavours(n,t),size_ml=size(n),sugar=sugar(n,t),
                         caffeine=caffeine(n,t),fizzy=fizzy(n,t))
            r.update(source=SRC[shop],checked=CHECKED); out.append(r)
    return out

# ---------------- drinks ----------------
DRINK_FAMILY={"Cola":"Fizzy","Fizzy":"Fizzy","Energy":"Energy & sport","Sports":"Energy & sport",
 "Water":"Water","Flavoured water":"Water","Coconut water":"Water",
 "Juice":"Juice & smoothie","Smoothie":"Juice & smoothie","Shot":"Juice & smoothie",
 "Iced coffee":"Milky","Protein shake":"Milky","Iced tea":"Tea & kombucha","Kombucha":"Tea & kombucha"}
def drink_type(n):
    if has(n,"coconut water"): return "Coconut water"
    if has(n,"touch of fruit","fruity spring water","vit hit","get more vits"): return "Flavoured water"
    if re.search(r"\bwater\b",n.lower()): return "Water"
    if has(n,"smoothie"): return "Smoothie"
    if has(n,"iced coffee","latte","macchiato"): return "Iced coffee"
    if has(n,"immunity shot","defence shot"): return "Shot"
    if has(n,"juice","capri-sun","juice burst") or (has(n,"ribena") ): return "Juice"
    if has(n,"iced coffee","latte","macchiato"): return "Iced coffee"
    if has(n,"protein shake","ufit"): return "Protein shake"
    if has(n,"kombucha"): return "Kombucha"
    if has(n,"ice tea","iced tea"): return "Iced tea"
    if has(n,"lucozade sport","powerade","prime hydration","lucozade zero"): return "Sports"
    if has(n,"energy","red bull","monster","relentless","carabao","pwr-bru","tenzing","purdey","lucozade"): return "Energy"
    if has(n,"coke","coca-cola","pepsi"): return "Cola"
    return "Fizzy"
def dflavours(n,t):
    l=n.lower(); out=[]
    pairs=[("cola","Cola"),("coke","Cola"),("coca-cola","Cola"),("pepsi","Cola"),("dr pepper","Cherry"),("cherry","Cherry"),("lime","Lime"),("lemon","Lemon"),
     ("orange","Orange"),("tropical","Tropical"),("mango","Mango"),("passion","Passion fruit"),("pineapple","Pineapple"),("peach","Peach"),("apple","Apple"),
     ("grape","Grape"),("blackcurrant","Blackcurrant"),("ribena","Blackcurrant"),("vimto","Mixed berry"),("raspberry","Raspberry"),("strawberr","Strawberry"),
     ("berry","Mixed berry"),("forest fruits","Mixed berry"),("juneberry","Mixed berry"),("ice pop","Mixed fruit"),("summer fruits","Mixed berry"),("citrus","Citrus"),("fruit twist","Mixed fruit"),("punch","Mixed fruit"),("banana","Banana"),
     ("kiwi","Kiwi"),("cucumber","Cucumber"),("coconut","Coconut"),("ginger","Ginger"),("turmeric","Turmeric"),("elderflower","Elderflower"),
     ("watermelon","Watermelon"),("grapefruit","Grapefruit"),("blueberry","Blueberry"),("vanilla","Vanilla"),("caramel","Caramel"),("chocolate","Chocolate"),
     ("cream soda","Cream soda"),("basil","Herb"),("lemonade","Lemon"),("irn-bru","Irn-Bru"),("mountain dew","Citrus"),("sprite","Lemon"),("7up","Lemon")]
    for k,f in pairs:
        if re.search(r"(?<![a-z])"+re.escape(k),l) and f not in out:
            if f=="Mixed berry" and any(x in out for x in("Strawberry","Raspberry","Blueberry")) and "summer fruits" not in l: continue
            if f=="Grape" and "grapefruit" in l and "grape &" not in l: continue
            if f=="Apple" and "pineapple" in l and "apple &" not in l and "green apple" not in l: continue
            out.append(f)
    if "coconut water" in l: out=["Coconut"]
    if t=="Iced coffee" and "Coffee" not in out: out.insert(0,"Coffee")
    if t in("Water",) and not out: out=["Plain"]
    if len(out)>1 and "Original" in out: out.remove("Original")
    if not out: out=["Original"]
    return out
def size(n):
    m=re.search(r"(\d+(?:\.\d+)?)\s?(ml|l)\b",n,re.I)
    if not m: return None
    v=float(m.group(1)); return int(v*1000) if m.group(2).lower()=="l" else int(v)
def sugar(n,t):
    if has(n,"zero","sugar free","diet","max","no sugar","ultra","skinny","lite","prime"): return "Zero sugar"
    if has(n,"no added sugar") or t in("Water","Coconut water","Smoothie","Juice","Shot") and not has(n,"capri-sun","juice burst","ribena blackcurrant 500"):
        return "Zero sugar" if t=="Water" else "No added sugar"
    if t=="Flavoured water": return "Zero sugar" if has(n,"sugar free","vit") else "Low sugar"
    return "Regular"
def caffeine(n,t):
    if has(n,"no caffeine"): return False
    return t in("Cola","Energy","Iced coffee","Iced tea") or has(n,"dr pepper","irn-bru","mountain dew","lipton","pepsi")
def fizzy(n,t):
    if t in("Cola","Fizzy","Kombucha"): return not has(n,"still")
    if t=="Energy": return True
    if t=="Water": return has(n,"sparkling","pellegrino")
    return False

# ---------------- hand fixes ----------------
# Same product listed under a different name at another shop -> canonical name.
ALIAS = {
 "Innocent Smoothie Strawberries, Bananas & Apples 250ml": "Innocent Smoothie Strawberries & Bananas 250ml",
 "Walkers Wotsits Really Cheesy Grab Bag": "Walkers Wotsits Cheese Grab Bag 36g",
}
# Field fixes where the keyword rules get it wrong (keyed by listing name, size included).
FIX = {
 # sides
 "Gu Zillionaire Cheesecake": {"flavours":["Chocolate","Caramel","Biscuit"]},
 "Nomadic Yogurt And Oat Bar Chocolate": {"type":"Snack bar","flavours":["Chocolate","Yogurt","Oat"]},
 "Nomadic Oat Crunch Chocolate & Yogurt": {"flavours":["Chocolate","Yogurt","Oat"]},
 "Nutella & Go! Hazelnut Spread and Breadsticks 48g": {"type":"Chocolate","flavours":["Chocolate","Hazelnut"],"chilled":False},
 "Morrisons Golden Syrup Porridge": {"type":"Porridge"}, "Morrisons Original Porridge Pot": {"type":"Porridge"},
 "Higgidy Cheddar & Caramelised Onion Chutney Rolls x2 54g": {"flavours":["Cheese","Onion"]},
 "Taste Original Chicken Satay Snack 40g": {"flavours":["Chicken","Satay"]},
 "Taste Original Chicken Satay With Sweet Chilli Dip 55g": {"flavours":["Chicken","Satay","Sweet chilli"]},
 "Pringles Original Snacking Crisps 40g": {"flavours":["Salted"]},
 "Wall's Individual Scotch Egg 113g": {"type":"Egg","flavours":["Egg","Pork"]},
 "Tesco Mini Savoury Eggs 65g": {"type":"Egg","flavours":["Egg","Pork"]},
 "Fridge Raiders Southern Style Chicken Bites 45g": {"flavours":["Chicken","Spicy"]},
 "Kinder Surprise Milk Chocolate Egg 20g": {"flavours":["Chocolate"]},
 # drinks
 "Dr Pepper 500ml": {"flavours":["Dr Pepper"]}, "Dr Pepper Zero 500ml": {"flavours":["Dr Pepper"]},
 "Dr Pepper Zero Cherry Crush 500ml": {"flavours":["Dr Pepper","Cherry"]},
 "Monster Energy Ultra Zero Sugar 500ml": {"flavours":["Citrus"]},
 "Monster Energy Khaotic 500ml": {"flavours":["Orange","Tropical"]},
 "Monster Energy Monarch 500ml": {"flavours":["Peach"]},
 "Monster Energy Ultra Rosa Zero Sugar 500ml": {"flavours":["Rose"]},
 "Monster Energy Pacific Punch 500ml": {"flavours":["Mixed fruit"]},
 "Monster Energy Pipeline Punch 500ml": {"flavours":["Passion fruit","Orange","Guava"]},
 "Red Bull Sugar Free Lilac Edition Grapefruit & Blossom 355ml": {"flavours":["Grapefruit","Floral"]},
 "Prime Hydration Ice Pop 500ml": {"flavours":["Cherry","Lime","Raspberry"]},
 "Prime Energy Ice Pop 330ml": {"flavours":["Cherry","Lime","Raspberry"]},
 "Prime Hydration Meta Moon 500ml": {"flavours":["Grape"]},
 "Starbucks Tripleshot Espresso Iced Coffee 300ml": {"flavours":["Coffee"]},
}
# Flavour not in the product name: looked up on the brand / retailer page (18 Nov 2026).
FIX.update({
 "Monster Energy Ultra Fantasy Ruby Red Zero Sugar 500ml": {"flavours":["Grapefruit","Citrus"]},   # monsterenergy.com: citrus, pink grapefruit
 "Monster Energy Lando Norris Zero Sugar 500ml": {"flavours":["Melon","Yuzu"]},                     # monsterenergy.com: melon with yuzu
 "Monster Energy Full Throttle Zero Sugar 500ml": {"flavours":["Peach","Nectarine"]},               # monsterenergy.com: peach and nectarine
 "Monster Energy Rio Punch 500ml": {"flavours":["Papaya","Vanilla","Blackcurrant"]},                # monsterenergy.com
 "Monster Energy Ultra Rosa Zero Sugar 500ml": {"flavours":["Mixed berry"]},                        # The Grocer: red berry blend
 "Innocent Super Smoothie Energise 300ml": {"flavours":["Strawberry","Cherry","Apple"]},            # "Berry Energise"
})
CHECK_FLAVOUR=set()
# ---------------- what goes in the game ----------------
# Energy drinks: lots of near-identical variants, so at most CAP per brand, best-known first (KEEP order), then sold at most shops.
CAP = {"Energy": 3}
KEEP = ["Monster Energy 500ml","Monster Energy Ultra Zero Sugar 500ml","Monster Energy Mango Loco 500ml",
        "Red Bull Energy Drink 473ml","Red Bull Sugar Free 473ml","Red Bull Sugar Free Peach Edition White Peach 473ml"]
# Same thing as another listing (bigger "Duo" bar, grab-bag copy, alternate pack): kept in the data, left out of the game.
DUPLICATE = {"Cadbury Wispa Duo Chocolate Bar":"Cadbury Wispa","Cadbury Boost Duo Chocolate Bar":"Cadbury Boost Chocolate Bar 48.5g",
 "Cadbury Double Decker Duo Chocolate Bar":"Cadbury Double Decker Chocolate Bar","Cadbury Starbar Duo":"Cadbury Starbar Chocolate Bar",
 "Cadbury Twirl Xtra Duo Chocolate Bar":"Cadbury Twirl Chocolate Bar","Yorkie Brownie Duo":"Yorkie Brownie",
 "Walkers Sensations Thai Sweet Chilli Grab Bag Crisps":"Walkers Sensations Thai Sweet Chilli Crisps",
 "Kinder Surprise Milk Chocolate Egg Natoons":"Kinder Surprise Milk Chocolate Egg 20g",
 "Red Bull Zero 355ml":"Red Bull Sugar Free 473ml"}

def choose(ps):
    names={p["name"] for p in ps}
    for d,keep in DUPLICATE.items():
        if d in names: assert keep in names, f"DUPLICATE target not found: {keep}"
    groups={}
    for p in ps:
        p["in_game"]=True; p["left_out"]=None
        if p["name"] in DUPLICATE: p["in_game"]=False; p["left_out"]=f"same as {DUPLICATE[p['name']]}"; continue
        if p["type"] in CAP: groups.setdefault((p["type"],p["brand"]),[]).append(p)
    rank=lambda p:(KEEP.index(p["name"]) if p["name"] in KEEP else len(KEEP),-len(p["shops"]),p["name"])
    for (t,b),g in groups.items():
        for p in sorted(g,key=rank)[CAP[t]:]:
            p["in_game"]=False; p["left_out"]=f"cap of {CAP[t]} {t.lower()} drinks per brand"

SIDE_FAMILY["Porridge"]="Fresh"

def fix(rs,fam):
    for r in rs:
        r["name"]=ALIAS.get(r["name"],r["name"])
        f=FIX.get(r["name"])
        if f:
            r.update(f)
            if "type" in f: r["family"]=fam[r["type"]]
        if r["name"] in CHECK_FLAVOUR: r["flavours"]=["Unknown"]

SIZE=re.compile(r"\s*\b\d+(?:\.\d+)?\s?(?:ml|l|g)\b",re.I)
def base(name):
    """Product name without pack size / sports cap, so sizes of the same drink merge."""
    n=SIZE.sub("",name); n=re.sub(r"\s+sports cap\b","",n,flags=re.I); return re.sub(r"\s+"," ",n).strip()
def key(name): return re.sub(r"[^a-z0-9]","",base(name).lower())

def merge(rs,keys,unit):
    """One product per drink/side across shops and sizes.
    main size = 500ml if sold (drinks), else the largest; price = average across shops at the main size."""
    by={}
    for r in rs: by.setdefault(key(r["name"]),[]).append(r)
    out=[]
    for k,g in by.items():
        sizes=sorted({r[unit] for r in g if r[unit]})
        main=500 if 500 in sizes and unit=="size_ml" else (sizes[-1] if sizes else None)
        at=[r for r in g if r[unit]==main] or g
        first=at[0]
        shops={}
        for r in sorted(g,key=lambda r:(r[unit]!=main,)):
            shops.setdefault(r["shop"],{"price":r["price_gbp"],unit.split("_")[0]:r[unit]})
        prices=[r["price_gbp"] for r in at if r["price_gbp"] is not None]
        nm=base(first["name"])+(f" {main:g}{'ml' if unit=='size_ml' else 'g'}" if main else "")
        p={"name":nm,**{x:first[x] for x in keys if x not in("name",unit)},unit:main,
           "price_gbp":round(sum(prices)/len(prices),2) if prices else None,
           "shops":sorted({r["shop"] for r in g}),"shop_prices":shops,
           "sizes":sizes if len(sizes)>1 else None,"listings":sorted({r["name"] for r in g})}
        chk=[]
        if p["price_gbp"] is None: chk.append("no price (out of stock online)")
        if "Unknown" in p["flavours"]: chk.append("flavour not in name")
        p["needs_check"]=chk
        out.append(p)
    return sorted(out,key=lambda p:(p["type"],p["name"]))

def validate(ps,fam,unit):
    errs=[]
    names=[p["name"] for p in ps]
    for p in ps:
        if p["type"] not in fam: errs.append(f"{p['name']}: unknown type {p['type']}")
        if p["family"]!=fam.get(p["type"]): errs.append(f"{p['name']}: family mismatch")
        if not p["flavours"]: errs.append(f"{p['name']}: no flavours")
        if unit=="size_ml" and not p[unit]: errs.append(f"{p['name']}: no size")
        if p["price_gbp"] is None and not p["needs_check"]: errs.append(f"{p['name']}: no price")
        if names.count(p["name"])>1: errs.append(f"{p['name']}: duplicate name")
    if errs: raise SystemExit("Data problems:\n  "+"\n  ".join(sorted(set(errs))))

def write(name,rs,cols):
    with open(HERE/f"{name}.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(cols)
        for r in rs: w.writerow(["; ".join(r[c]) if isinstance(r[c],list) else ("" if r[c] is None else r[c]) for c in cols])
    (HERE/f"{name}.json").write_text(json.dumps(rs,ensure_ascii=False,indent=1),encoding="utf-8")

if __name__=="__main__":
    s=rows(SIDES,"side"); d=rows(DRINKS,"drink"); fix(s,SIDE_FAMILY); fix(d,DRINK_FAMILY)
    write("sides",s,["name","shop","price_gbp","type","family","flavours","brand","maker","weight_g","chilled","range","source","checked"])
    write("drinks",d,["name","shop","price_gbp","type","family","flavours","brand","maker","size_ml","sugar","caffeine","fizzy","source","checked"])
    sp=merge(s,["type","family","flavours","brand","maker","chilled","range"],"weight_g")
    dp=merge(d,["type","family","flavours","brand","maker","sugar","caffeine","fizzy"],"size_ml")
    validate(sp,SIDE_FAMILY,"weight_g"); validate(dp,DRINK_FAMILY,"size_ml")
    choose(sp); choose(dp)
    missing=set(DUPLICATE)-{p["name"] for p in sp+dp}
    if missing: raise SystemExit(f"DUPLICATE names not found: {sorted(missing)}")
    for nm,ps in (("sides_products",sp),("drinks_products",dp)):
        (HERE/f"{nm}.json").write_text(json.dumps(ps,ensure_ascii=False,indent=1),encoding="utf-8")
    for lbl,rs,ps in (("sides",s,sp),("drinks",d,dp)):
        print(f"{lbl}: {len(rs)} listings -> {len(ps)} products; {sum(len(p['shops'])>1 for p in ps)} at both shops; "
              f"{sum(bool(p['sizes']) for p in ps)} with several sizes; {sum(bool(p['needs_check']) for p in ps)} need checking; "
              f"{sum(p['in_game'] for p in ps)} in the game")
