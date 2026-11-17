import json,csv,re
SRC={"Tesco":"https://www.tesco.com/shop/en-GB/browse/fresh-food/chilled-soup-sandwiches-and-salad-pots/sandwiches-wraps-and-sushi/sandwiches",
"Sainsbury's":"https://www.sainsburys.co.uk (product pages)","Asda":"https://www.trolley.co.uk (Asda listings)",
"Morrisons":"https://groceries.morrisons.com/categories/fresh-foods/food-to-go/188187",
"Waitrose":"https://www.waitrose.com/ecom/shop/browse/groceries/fresh_and_chilled/food_to_go/sandwiches_and_wraps",
"M&S":"https://zoom.ocado.com/lunch/sandwiches-wraps/m-s-sandwiches-wraps","Co-op":"https://www.coop.co.uk/products/co-op-sandwiches",
"Aldi":"https://www.aldi.co.uk/products/chilled-food/food-to-go/k/1588161416978051013","Boots":"https://retailtimes.co.uk/boots-launches-new-christmas-and-premium-meal-deal-range/"}
# shop -> list of "name|price|range|bread(optional)"  range: V=Value S=Standard P=Premium F=Festive G=Plant-based X=Free From
D={"Tesco":"""Finest Honey Roasted Gammon & Barber's Cheddar Sandwich|4.50|P
Fully Loaded Chicken, Stuffing, Red Cabbage & Cranberry Sandwich|4.50|F
Prawn Mayonnaise Sandwich|3.00|S
Cheese Triple Sandwich|3.40|S
Smoked Ham & Cheddar Sandwich|2.75|S
Chicken Salad Sandwich|3.00|S
Chicken, Bacon & Stuffing Sandwich|3.25|S
Tuna & Cucumber Sandwich|2.25|S
Chicken, Bacon & Lettuce Sandwich|3.00|S
Brie & Cranberry Sandwich|3.25|F
Free Range Egg Mayonnaise Sandwich|2.25|S
Pigs in Blankets Sandwich|3.25|F
BBQ Chicken & Red Leicester Sandwich|3.25|S
The Christmas Triple Sandwich|3.50|F
Chicken Triple Sandwich|3.40|S
Cheese & Onion Sandwich|1.50|V
Sausage, Bacon & Egg Triple|3.40|S
Just Ham Sandwich|1.50|V
The Chicken Club Sandwich|3.40|S
Egg & Cress Sandwich|1.50|V
Turkey & Trimmings Sandwich|3.50|F
Free From Chicken & Trimmings Sandwich|3.50|X
Festive Pork Meatball Wrap|3.25|F
Chicken & Trimmings Sub Roll|3.25|F
Chicken, Bacon & Stuffing Wrap|3.25|S
Cracking Currywurst Sub Roll|3.25|S
Sausage, Bacon & Egg Sub|3.25|S
Southern Fried Chicken Sub with Chipotle Mayo|3.25|S
Ham & Cheddar Cheese Sub|3.25|S
Bacon, Lettuce & Tomato Sandwich|3.00|S
Tuna & Sweetcorn Sandwich|2.25|S
Cheese Sandwich No Mayonnaise|1.50|V
Tuna Crunch Sub|3.25|S
Finest Smoked Scottish Salmon & Cream Cheese Sandwich|4.50|P
Coronation Chicken Sandwich|3.00|S
Chicken & Sweetcorn Sandwich|2.25|S
Cheese & Pickle Sandwich|2.25|S
Chicken & Bacon Sandwich|2.25|S
Ham, Cheese & Chicken Triple Sandwich|3.40|S
Smoky Bacon Sarnie with Tangy Ketchup|3.00|S
Finest New York Deli Pastrami & Emmental Sandwich|4.50|P
Chicken Tikka & Mango Chutney Sandwich|3.00|S
Deli Style Cheese & Pickle Sandwich|3.00|S
Smoked Ham & Mustard Sandwich|2.25|S
Roast Chicken, Mozzarella & Pesto Sandwich|3.00|S
Free From BLT Sandwich|3.40|X
Finest Turkey Pastrami Panettone Style Roll|4.95|P|Roll
BBQ Chicken, Bacon & Cheese Sandwich|3.25|S
Chicken Salad Sub|3.00|S
Chicken & Stuffing Sandwich|3.00|S
Meatball Marinara Sub|3.00|S
Brie & Smoked Bacon with Chilli Jam Sandwich|2.85|S|Malted
Ploughman's Sandwich|2.75|S""",
"Sainsbury's":"""Cheese & Red Onion on Oatmeal Bread|1.80|V
Smoked Ham & Cheddar on Malted Bread|3.10|S
Tuna Mayo on Oatmeal Bread|1.80|V
Red Leicester Ploughman's Sandwich|3.10|S|Malted
BLT on Malted Bread|3.10|S
High Protein Chicken Salad Sandwich|3.15|S|Malted
Free Range Egg & Cress on Malted Bread|1.80|V
Bacon & Free Range Egg on Malted Bread|3.00|S
Brie, Bacon & Chilli Chutney on Malted Bread|3.25|S
Chicken & Sweetcorn with Black Pepper Mayo on Malted Bread|2.30|S
Falafel & Houmous Wrap|3.25|S
Tuna & Sweetcorn on Malted Bread|2.30|S
Chicken & Bacon with Black Pepper Mayo on Malted Bread|3.10|S
Chicken with Sage & Onion Stuffing on White Bread|3.10|S
No Mayo Ham on White Bread|1.70|V
Beef & Horseradish with Rocket on White Bread|3.50|S
Festive Chicken, Bacon & Stuffing Wrap|3.40|F
Turkey Feast Sandwich|3.40|F
Brie & Cranberry Sandwich|3.40|F
Plant Pioneers No Pigs Under Blankets|3.40|G
Pigs Under Blankets with Cranberry Chutney on Malted Bread|3.40|F
Christmas Cracker Club Sandwich|3.50|F
Southern Fried Chicken Wrap|3.40|S
Chicken & Bacon Caesar Wrap|3.40|S
High Protein Buffalo Chicken Wrap|3.40|S
Salt & Pepper Chicken Wrap|3.40|S
Taste the Difference Greek Style Chicken & Tzatziki Wrap|4.50|P
Free From Chicken Feast Sandwich|3.25|X|Seeded
High Protein Fajita Halloumi Wrap|3.40|S
No Mayo Hoisin Duck Wrap|3.40|S
Taste the Difference New Yorker Inspired Sandwich|4.50|P|Rye
Taste the Difference Burger Style Sandwich|4.50|P
Taste the Difference Steak & Caramelised Red Onion on Onion Bread|4.50|P|Onion bread
Taste the Difference Prawn Cocktail on Rye Bread|4.50|P
Taste the Difference Ham Hock & Mature Cheddar Sandwich|4.50|P
Taste the Difference Festive Ham Hock on Onion Bread|4.50|P|Onion bread
Taste the Difference Korean Chicken Sandwich|4.25|P|White
Cajun Chicken Wrap|3.40|S
Prawn Mayo on Malted Bread|3.00|S""",
"Asda":"""Egg & Cress Sandwich|1.50|V|Malted
BLT Sandwich|2.75|S|Malted
Cheddar Ploughman's Sandwich|2.75|S|Malted
Chicken & Sweetcorn Sandwich|2.20|S|Malted
Chicken Mayo Sandwich|2.20|S|Malted
Tuna & Sweetcorn Sandwich|2.20|S|Malted
Cheese & Onion Sandwich|1.50|V|Malted
Egg & Bacon Sandwich|2.75|S|Malted
Chicken Salad Sandwich|2.75|S|Malted
All-Day Breakfast Triple Sandwich|3.00|S
Tuna Mayo Sandwich|1.50|V|White
Cheese Sandwich|1.50|V
Cheese & Tomato Sandwich|2.20|S
Ham Sandwich|1.50|V
Chicken & Stuffing Sandwich|2.75|S
Chicken Triple Sandwich|3.00|S
Chicken & Bacon Sandwich|2.75|S|Malted
Brie, Bacon & Chilli Chutney Sandwich|2.75|S
Prawn Mayo Sandwich|2.75|S
Chicken & Bacon Club|3.00|S
Southern Fried Chicken Wrap|2.82|S
Chicken & Bacon Caesar Wrap|2.87|S
Sweet Chilli Chicken Wrap|2.82|S""",
"Morrisons":"""Chicken Caesar Wrap|3.40|S
Sweet Chilli Chicken Wrap|3.25|S
Christmas Lunch in a Tortilla Wrap|3.40|F
Cheese & Onion Sandwich|1.80|V|Oatmeal
Egg & Cress Sandwich|1.80|V
Prawn Mayo Sandwich|3.00|S
Roast Chicken & Bacon Sandwich|3.10|S
Turkey Lunch Sandwich|3.40|F
Mature Cheese & Pickle Sandwich|2.25|S
Ham & Cheese Sandwich|3.10|S|Malted
Chicken Salad Sandwich|3.15|S
Chicken & Stuffing Sandwich|3.25|S|White
BLT Sandwich|3.10|S
Pigs Under Blankets Christmas Sandwich|3.40|F
Tuna & Sweetcorn Sandwich|2.30|S
Salmon & Cream Cheese Sandwich|3.50|S""",
"Waitrose":"""Christmas Turkey, Stuffing & Bacon Sandwich|4.60|F
Christmas Pigs Under Blankets|4.00|F
Christmas Vegetable Festive Feast Sandwich|3.75|F
Christmas Merry Club'mas Sandwich|4.60|F
Prawn Mayo Sandwich|4.35|S|Malted
Egg Mayo & Cress Sandwich|2.75|S
Smoked Salmon & Cream Cheese Sandwich|4.60|S
Steak & Caramelised Onion Chutney Sandwich|4.60|S
Hoisin Duck Wrap|4.05|S
Chicken & Bacon Caesar Wrap|4.05|S
Essential Cheese & Onion Sandwich|1.95|V
Classic BLT Sandwich|4.15|S
Roast Chicken Salad Sandwich|4.05|S
Brie & Bacon Sandwich|4.00|S
Roast Chicken & Bacon Sandwich|4.05|S
Smoked Ham & Cheese Sandwich|3.30|S
All Day Breakfast Sandwich|4.15|S
Mature Cheddar Ploughman's Sandwich|3.30|S
Tuna Mayo & Sweetcorn Sandwich|3.30|S
Triple Sandwich Selection|4.55|S
Salt Beef & Mustard Mayo Sandwich|4.60|S
Cheddar & Celery Sandwich|3.35|S
Sweet Chilli Chicken Wrap|4.05|S
Southern Fried Chicken Wrap|4.05|S
Roast Chicken & Stuffing Sandwich|4.05|S
Piri Piri Chicken Wrap|4.05|S
Tuna & Cucumber Sub Roll|4.10|S
No.1 The Double Beef & Béarnaise Sandwich|4.95|P
Mozzarella & Roasted Tomato Wrap|3.90|S
Essential Tuna Mayo Sandwich|1.95|V
Seafood Cocktail Sandwich|4.15|S
PlantLiving Hoisin No Duck Wrap|4.05|G
Pastrami & Emmental Sandwich|4.55|S
No.1 The Perfect Ploughman's Cornish Cheddar Sandwich|4.95|P
Coronation Chicken Sandwich|4.15|S
Spicy Falafel Wrap|4.15|S
Brie & Cranberry Sandwich|3.75|F
Essential Egg Mayonnaise Sandwich|2.00|V
Korean Style Chicken Wrap|4.15|S
Freefrom Turkey Feast Sandwich|4.60|X
No.1 The King of Prawn Cocktails Sandwich|4.95|P
Chicken & Avocado Sandwich|4.15|S
High Protein Mexican Style Chicken Wrap|4.15|S
Ham Hock & Red Leicester Ploughman's Sandwich|4.60|S
Essential Smoked Ham Sandwich|2.20|V
Spiced Falafel & Feta Wrap|3.90|S
Chicken Katsu Curry Sando|4.05|S""",
"M&S":"""Prawn Mayo Sandwich|4.30|S|Malted
Tuna & Sweetcorn Sandwich|3.50|S|Malted
Smoked Salmon & Cream Cheese Sandwich|4.85|S|Wholemeal
Classic Selection|4.85|S
Cheese & Marmite Sandwich|3.25|S
Chicken Tikka Sandwich|4.30|S
Roast Chicken & Bacon Sandwich|4.20|S
Spinach & Falafel Wrap|4.45|S
Roast Chicken & Salad Sandwich|4.30|S
Honey Roast Ham & Cheddar Cheese Sandwich|3.50|S
Egg & Watercress Sandwich|2.85|S
Cheese & Onion Sandwich|2.45|S
New York Deli Pastrami Sandwich|4.85|S
All Day Breakfast Sandwich|4.30|S
Hoisin Duck Wrap|4.30|S
Ham & Farmhouse Cheese Toastie|4.60|S
Turkey Feast Christmas Sandwich|4.60|F
Pigs in Blankets Christmas Sandwich|4.60|F
Butter Chicken Pocket Naan|4.85|S
Bang Bang Chicken Wrap|4.20|S
Butter Chicken Wrap|4.20|S
Chocolate, Strawberry & Pistachio Sando|3.80|S|White
Green Goddess Sandwich|4.85|S
Red Diamond Strawberry & Cream Sando|3.05|S|White
Smoky Halloumi Burrito|5.40|S
Spicy Meatball Wrap|5.40|S
BLT Sandwich|4.00|S|Malted
Smoky Beef Burrito|6.00|S""",
"Co-op":"""Tuna Mayo Sandwich|1.40|V
Egg & Cress Sandwich|1.75|V|Malted
All Day Breakfast Sandwich|3.25|S|White
Chicken & Bacon Sandwich|3.25|S|Malted
Ham & Cheese Sandwich|3.00|S
Chicken & Stuffing Sandwich|3.25|S
Egg & Bacon Sandwich|3.25|S
Tuna & Sweetcorn Sandwich|2.65|S
Cheese Sandwich|1.40|V
Cheese & Red Onion Sandwich|1.55|V
Prawn Mayonnaise Sandwich|3.00|S
Bacon, Lettuce & Tomato Sandwich|3.25|S
Chicken Mayo Sandwich|2.00|S
Chicken & Sweetcorn Sandwich|2.65|S
Halloumi Wrap|3.75|S
Peking Duck Wrap|3.45|S
Turkey Feast Sandwich|3.25|F|Malted
Brie & Cranberry Sandwich|3.00|F|Malted
GRO Turk'y Feast Sandwich|3.25|G
Festive Onion Bhaji Sandwich|3.30|G
Festive Wrap|3.50|F""",
"Aldi":"""Oak Smoked Ham & Cheddar with Mayo Sandwich|1.99|S
Egg & Bacon with Mayo Sandwich|1.99|S|Malted
Specially Selected New York Deli Pastrami & Emmental Sandwich|2.99|P
Specially Selected Ayrshire Ham Hock & Farmhouse Cheddar Sandwich|2.99|P
Specially Selected King Prawn & Seafood Cocktail Sandwich|2.99|P
Tuna Sweetcorn Classic Sandwich|1.89|S
Prawn Mayonnaise on Malted Brown Bread|1.89|S|Malted
Cheese Ploughman's Classic Sandwich|1.89|S
Chicken Sweetcorn Classic Sandwich|1.89|S
All Day Breakfast Sandwich|2.59|S
Classic Selection Sandwich|2.59|S
Chicken & Bacon Club with Mayo Sandwich|2.59|S
Cheese & Onion Sandwich|1.29|V
Egg & Cress Sandwich|1.29|V
Smoked Ham Sandwich|1.29|V
BLT Deeper Fill Sandwich|2.09|S
Hunters Chicken Toastie|1.99|S
Ham & Cheese Toastie|1.99|S""",
"Boots":"""Steak & Balsamic Chutney|5.00|P
Mozzarella, Chargrilled Peppers & Pesto Mayo|5.00|P
New York Style Deli|5.00|P
Greek Style Chicken|5.00|P
Smoked Salmon & Soft Cheese|5.00|P"""}
RANGE={"V":"Value","S":"Standard","P":"Premium","F":"Festive","G":"Plant-based","X":"Free From"}
FILL=[("new york","Beef"),("red onion","Onion"),("chicken","Chicken"),("chick'n","Plant chicken"),("turkey|turk'y","Turkey"),("ham|gammon","Ham"),("bacon|blt|club","Bacon"),("sausage|pigs|currywurst","Sausage"),("pigs (in|under) blankets","Bacon"),
("beef|steak|(?<!turkey )pastrami|(?<!pork )meatball|burger","Beef"),("duck","Duck"),("pork","Pork"),("(?<!red )onion(?! bread| bhaji)","Onion"),("tuna","Tuna"),("prawn|seafood","Prawn"),("salmon","Salmon"),("egg","Egg"),
("cheese|cheddar|brie|mozzarella|halloumi|emmental|leicester|ploughman|feta","Cheese"),("falafel","Falafel"),("houmous","Houmous"),("onion bhaji","Onion bhaji"),
("stuffing|trimmings","Stuffing"),("cranberry","Cranberry"),("sweetcorn","Sweetcorn"),("cucumber","Cucumber"),("cress|watercress","Cress"),("lettuce|salad|blt","Salad"),
("tomato|blt","Tomato"),("pickle|ploughman","Pickle"),("avocado","Avocado"),("strawberr","Strawberry"),("chocolate","Chocolate"),("marmite","Marmite"),("pesto","Pesto"),("celery","Celery"),("vegetable|green goddess","Veg")]
def fills(n):
  l=n.lower();out=[]
  if "no duck" in l: l=l.replace("no duck","no-d")
  if "no pigs" in l: l=l.replace("no pigs","no-p");out.append("Plant sausage")
  if "all day breakfast" in l or "all-day breakfast" in l: out+=["Sausage","Bacon","Egg"]
  if "classic selection" in l or "triple sandwich selection" in l: out+=["Mixed"]
  if "no-d" in l: out.append("Plant duck")
  for k,v in FILL:
    if re.search(k,l) and v not in out: out.append(v)
  return out or ["Mixed"]
def bread(n,b):
  if b: return b
  l=n.lower()
  for k,v in [("wrap|tortilla","Wrap"),("burrito","Wrap"),("naan","Naan"),("sub","Sub roll"),("baguette","Baguette"),("bagel","Bagel"),("brioche","Brioche"),("toastie","Toastie"),("panettone|roll","Roll"),("rye","Rye"),("onion bread","Onion bread"),("oatmeal","Oatmeal"),("malted","Malted"),("white","White"),("sando|sarnie|sandwich|selection|triple|club|blt|feast|ploughman","Sliced")]:
    if re.search(k,l): return v
  return "Sliced"
rows=[]
for shop,txt in D.items():
  for line in txt.strip().splitlines():
    p=line.split("|");n,pr,r=p[0],float(p[1]),RANGE[p[2]];b=p[3] if len(p)>3 else ""
    rows.append({"name":n,"shop":shop,"price":pr,"fillings":fills(n),"bread":bread(n,b),"range":r,"source":SRC[shop],"checked":"2026-11-17"})
keys=set()
for r in rows:
  k=(r["name"],r["shop"]);assert k not in keys,k;keys.add(k)
json.dump(rows,open("sandwiches.json","w"),indent=1,ensure_ascii=False)
with open("sandwiches.csv","w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(["name","shop","price_gbp","fillings","bread","range","source","checked"])
  for r in rows:w.writerow([r["name"],r["shop"],f'{r["price"]:.2f}',"; ".join(r["fillings"]),r["bread"],r["range"],r["source"],r["checked"]])
from collections import Counter
print(len(rows),Counter(r["shop"] for r in rows),Counter(r["bread"] for r in rows),Counter(r["range"] for r in rows),sep="\n")
print([ (r["name"],r["fillings"]) for r in rows if r["fillings"]==["Mixed"]])
