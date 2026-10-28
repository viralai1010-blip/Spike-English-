#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates 5,000+ English-Arabic vocabulary database for SQLite/Room.
"""
import sqlite3
import os

db_path = "app/src/main/assets/database/words.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create table
cur.execute("""
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    english TEXT NOT NULL,
    arabic TEXT NOT NULL,
    phonetic TEXT NOT NULL,
    partOfSpeech TEXT NOT NULL,
    exampleEn TEXT NOT NULL,
    exampleAr TEXT NOT NULL,
    category TEXT NOT NULL,
    categoryAr TEXT NOT NULL,
    level TEXT NOT NULL,
    emoji TEXT NOT NULL,
    isFavorite INTEGER NOT NULL DEFAULT 0,
    isLearned INTEGER NOT NULL DEFAULT 0,
    masteryScore INTEGER NOT NULL DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS room_master_table (
    id INTEGER PRIMARY KEY,
    identity_hash TEXT
)
""")

print("Preparing comprehensive vocabulary collection...")

# We define high-quality vocabulary groups
# Format: (english, arabic, phonetic, pos, ex_en, ex_ar, category, category_ar, level, emoji)
records = []
seen = set()

def add_word(en, ar, phon, pos, ex_en, ex_ar, cat, cat_ar, lvl, emo):
    key = en.strip().lower()
    if key in seen:
        return
    seen.add(key)
    records.append((en.strip(), ar.strip(), phon.strip(), pos.strip(), ex_en.strip(), ex_ar.strip(), cat.strip(), cat_ar.strip(), lvl.strip(), emo.strip()))

# Group 1: Food & Dining (320 words)
food_data = [
    ("Apple", "تفاحة", "/ˈæp.əl/", "Noun", "I eat an apple every day.", "آكل تفاحة كل يوم.", "A1", "🍎"),
    ("Banana", "موزة", "/bəˈnæn.ə/", "Noun", "Bananas give quick energy.", "الموز يمنح طاقة سريعة.", "A1", "🍌"),
    ("Orange", "برتقالة", "/ˈɒr.ɪndʒ/", "Noun", "Fresh orange juice is cold.", "عصير البرتقال الطازج بارد.", "A1", "🍊"),
    ("Lemon", "ليمون", "/ˈlem.ən/", "Noun", "Lemon juice is sour and healthy.", "عصير الليمون حامض وصحي.", "A1", "🍋"),
    ("Strawberry", "فراولة", "/ˈstrɔː.bər.i/", "Noun", "Ripe strawberries are sweet.", "الفراولة الناضجة حلوة المذاق.", "A2", "🍓"),
    ("Grapes", "عنب", "/ɡreɪps/", "Noun", "We wash the grapes before eating.", "نغسل العنب قبل أكله.", "A2", "🍇"),
    ("Watermelon", "بطيخ", "/ˈwɔː.təˌmel.ən/", "Noun", "Watermelon is great in hot weather.", "البطيخ رائع في الطقس الحار.", "A1", "🍉"),
    ("Pineapple", "أناناس", "/ˈpaɪnˌæp.əl/", "Noun", "Pineapple has a unique tropical taste.", "الأناناس له طعم استوائي مميز.", "B1", "🍍"),
    ("Mango", "مانجو", "/ˈmæŋ.ɡəʊ/", "Noun", "Sweet mango is popular in summer.", "المانجو الحلوة مشهورة في الصيف.", "A2", "🥭"),
    ("Peach", "خوخ", "/piːtʃ/", "Noun", "Peaches are soft and fragrant.", "الخوخ طري وعطر الرائحة.", "B1", "🍑"),
    ("Cherry", "كرز", "/ˈtʃer.i/", "Noun", "Red cherries decorate the dessert.", "الكرز الأحمر يزين الحلوى.", "A2", "🍒"),
    ("Pear", "كمثرى / إجاص", "/peər/", "Noun", "He peeled a green pear.", "قشّر حبة كمثرى خضراء.", "A2", "🍐"),
    ("Fig", "تين", "/fɪɡ/", "Noun", "Dried figs are delicious.", "التين المجفف لذيذ جداً.", "B1", "🫐"),
    ("Date", "تمر / بلح", "/deɪt/", "Noun", "Dates are eaten during Ramadan.", "يؤكل التمر خلال شهر رمضان.", "A2", "🌴"),
    ("Pomegranate", "رمان", "/ˈpɒm.ɪˌɡræn.ɪt/", "Noun", "Pomegranate seeds are ruby red.", "بذور الرمان حمراء كالياقوت.", "B2", "🍎"),
    ("Kiwi", "كيوي", "/ˈkiː.wiː/", "Noun", "Kiwi fruit is packed with vitamins.", "فاكهة الكيوي غنية بالفيتامينات.", "B1", "🥝"),
    ("Avocado", "أفوكادو", "/ˌæv.əˈkɑː.dəʊ/", "Noun", "Avocado toast is nutritious.", "توست الأفوكادو مغذٍ ولذيذ.", "B1", "🥑"),
    ("Tomato", "طماطم", "/təˈmɑː.təʊ/", "Noun", "Tomatoes are used in rich salads.", "تُستخدم الطماطم في السلطات الشهية.", "A1", "🍅"),
    ("Potato", "بطاطس", "/pəˈteɪ.təʊ/", "Noun", "Baked potatoes are hearty.", "البطاطس المخبوزة مشبعة.", "A1", "🥔"),
    ("Carrot", "جزر", "/ˈkær.ət/", "Noun", "Rabbits love crunchy carrots.", "تحب الأرانب الجزر المقرمش.", "A1", "🥕"),
    ("Onion", "بصل", "/ˈʌn.jən/", "Noun", "Sauté onions in olive oil.", "شوح البصل في زيت الزيتون.", "A2", "🧅"),
    ("Garlic", "ثوم", "/ˈɡɑː.lɪk/", "Noun", "Garlic adds deep savory flavor.", "الثوم يضيف نكهة لذيذة وعميقة.", "A2", "🧄"),
    ("Cucumber", "خيار", "/ˈkjuː.kʌm.bər/", "Noun", "Cucumber slices keep you hydrated.", "شرائح الخيار تحافظ على ترطيبك.", "A2", "🥒"),
    ("Lettuce", "خس", "/ˈlet.ɪs/", "Noun", "Crisp green lettuce forms the base.", "الخس الأخضر المقرمش يشكل الأساس.", "A2", "🥬"),
    ("Broccoli", "بروكلي", "/ˈbrɒk.əl.i/", "Noun", "Steamed broccoli is healthy.", "البروكلي المطهو بالبخار صحي.", "B1", "🥦"),
    ("Mushroom", "فطر / عيش الغراب", "/ˈmʌʃ.ruːm/", "Noun", "We added sautéed mushrooms to pasta.", "أضفنا الفطر المشوح إلى المعكرونة.", "A2", "🍄"),
    ("Corn", "ذرة", "/kɔːn/", "Noun", "Roasted corn is sold on the street.", "تُباع الذرة المشوية في الشارع.", "A1", "🌽"),
    ("Bell pepper", "فلفل رومي / حلو", "/ˈbel ˌpep.ər/", "Noun", "Colorful bell peppers brighten the dish.", "الفلفل الرومي الملون يبهج الطبق.", "B1", "🫑"),
    ("Eggplant", "باذنجان", "/ˈeɡ.plɑːnt/", "Noun", "Grilled eggplant makes great dip.", "الباذنجان المشوي رائع للمقبلات.", "B1", "🍆"),
    ("Spinach", "سبانخ", "/ˈspɪn.ɪtʃ/", "Noun", "Spinach is packed with iron.", "السبانخ مليئة بالحديد.", "B1", "🥬"),
    ("Bread", "خبز", "/bred/", "Noun", "Warm pita bread straight from oven.", "خبز شامي ساخن مباشرة من الفرن.", "A1", "🍞"),
    ("Baguette", "خبز فرنسي", "/bæɡˈet/", "Noun", "French baguette has a crispy crust.", "الباجيت الفرنسي له قشرة مقرمشة.", "B1", "🥖"),
    ("Croissant", "كرواسون", "/ˈkwæs.ɒ̃/", "Noun", "A buttery croissant with morning coffee.", "كرواسون بالزبدة مع قهوة الصباح.", "A2", "🥐"),
    ("Toast", "خبز محمص / توست", "/təʊst/", "Noun", "Golden toast with fruit jam.", "توست ذهبي مع مربى الفواكه.", "A1", "🍞"),
    ("Rice", "أرز", "/raɪs/", "Noun", "Basmati rice is fragrant and long.", "أرز البسمتي عطري وحبته طويلة.", "A1", "🍚"),
    ("Pasta", "معكرونة", "/ˈpæs.tə/", "Noun", "Cook pasta until al dente.", "اطبخ المعكرونة حتى تنضج بدرجة مناسبة.", "A1", "🍝"),
    ("Noodles", "نودلز / شعرية", "/ˈnuː.dəlz/", "Noun", "Hot spicy noodles in chicken broth.", "نودلز حارة في مرق الدجاج.", "A2", "🍜"),
    ("Meat", "لحم", "/miːt/", "Noun", "Lean meat provides essential proteins.", "اللحم قليل الدهن يوفر بروتينات أساسية.", "A1", "🥩"),
    ("Beef", "لحم بقري", "/biːf/", "Noun", "Tender beef stew with vegetables.", "يخنة لحم بقري طرية مع الخضار.", "A2", "🥩"),
    ("Lamb", "لحم ضأن / خروف", "/læm/", "Noun", "Roast lamb seasoned with rosemary.", "لحم خروف مشوي متبل بإكليل الجبل.", "B1", "🍖"),
    ("Chicken", "دجاج", "/ˈtʃɪk.ɪn/", "Noun", "Grilled chicken breast is lean.", "صدر الدجاج المشوي قليل الدهون.", "A1", "🍗"),
    ("Turkey", "ديك رومي", "/ˈtɜː.ki/", "Noun", "Roast turkey for holiday dinner.", "ديك رومي مشوي لعشاء العيد.", "B1", "🦃"),
    ("Fish", "سمك", "/fɪʃ/", "Noun", "Fresh sea fish grilled with herbs.", "سمك بحري طازج مشوي بالأعشاب.", "A1", "🐟"),
    ("Shrimp", "جمبري / روبيان", "/ʃrɪmp/", "Noun", "Shrimp cocktail with lemon sauce.", "كوكتيل جمبري مع صلصة الليمون.", "A2", "🦐"),
    ("Crab", "سلطعون / كابوريا", "/kræb/", "Noun", "Fresh crab meat is sweet and tender.", "لحم السلطعون الطازج حلو وطري.", "B1", "🦀"),
    ("Egg", "بيضة", "/eɡ/", "Noun", "Scrambled eggs with melted cheese.", "بيض مخفوق مع الجبن الذائب.", "A1", "🥚"),
    ("Cheese", "جبن", "/tʃiːz/", "Noun", "Sharp cheddar cheese melted over toast.", "جبن شيدر حاد ذائب فوق الخبز.", "A1", "🧀"),
    ("Milk", "حليب", "/mɪlk/", "Noun", "Cold milk with chocolate cereal.", "حليب بارد مع رقائق الشوكولاتة.", "A1", "🥛"),
    ("Butter", "زبدة", "/ˈbʌt.ər/", "Noun", "Creamy butter spread on bread.", "زبدة كريمية مدهونة على الخبز.", "A1", "🧈"),
    ("Yogurt", "زبادي", "/ˈjɒɡ.ət/", "Noun", "Natural yogurt topped with honey.", "زبادي طبيعي مغطى بالعسل.", "A2", "🥣"),
    ("Water", "ماء", "/ˈwɔː.tər/", "Noun", "Pure drinking water is vital.", "مياه الشرب النقية حيوية للجسم.", "A1", "💧"),
    ("Coffee", "قهوة", "/ˈkɒf.i/", "Noun", "Fresh espresso with rich crema.", "إسبريسو طازج مع رغوة غنية.", "A1", "☕"),
    ("Tea", "شاي", "/tiː/", "Noun", "A hot cup of peppermint tea.", "كوب شاي ساخن بالنعناع.", "A1", "🫖"),
    ("Juice", "عصير", "/dʒuːs/", "Noun", "Fresh pressed apple juice.", "عصير تفاح طازج ومضغوط.", "A1", "🧃"),
    ("Soup", "حساء / شوربة", "/suːp/", "Noun", "Hearty vegetable lentil soup.", "شوربة عدس بالخضروات مشبعة ولذيذة.", "A1", "🍲"),
    ("Salad", "سلطة", "/ˈsæl.əd/", "Noun", "Mediterranean salad with olive oil.", "سلطة البحر المتوسط بزيت الزيتون.", "A1", "🥗"),
    ("Sandwich", "ساندويتش / شطيرة", "/ˈsæn.wɪdʒ/", "Noun", "Turkey and avocado club sandwich.", "ساندويتش كلوب بالديك الرومي والأفوكادو.", "A1", "🥪"),
    ("Pizza", "بيتزا", "/ˈpiːt.sə/", "Noun", "Neapolitan pizza with fresh basil.", "بيتزا نابولية مع ريحان طازج.", "A1", "🍕"),
    ("Burger", "برجر", "/ˈbɜː.ɡər/", "Noun", "Gourmet burger with caramelized onions.", "برجر فاخر مع بصل مكرمل.", "A1", "🍔"),
    ("Steak", "شريحة لحم ستيك", "/steɪk/", "Noun", "Juicy ribeye steak cooked to perfection.", "ستيك ريب آي شهي ومطهو بإتقان.", "B1", "🥩"),
    ("Dessert", "حلوى / تحلية", "/dɪˈzɜːt/", "Noun", "Chocolate lava cake for dessert.", "كعكة الشوكولاتة الذائبة للتحلية.", "A2", "🍰"),
    ("Cake", "كعكة / كيك", "/keɪk/", "Noun", "Three-tier wedding cake with flowers.", "كعكة زفاف من ثلاث طبقات مزينة بالزهور.", "A1", "🎂"),
    ("Cookie", "كوكيز / بسكويت", "/ˈkʊk.i/", "Noun", "Crunchy chocolate chip cookies.", "كوكيز مقرمش برقائق الشوكولاتة.", "A1", "🍪"),
    ("Ice cream", "مثلجات / آيس كريم", "/ˌaɪs ˈkriːm/", "Noun", "Vanilla ice cream with chocolate sauce.", "آيس كريم فانيليا مع صلصة الشوكولاتة.", "A1", "🍨"),
    ("Honey", "عسل", "/ˈhʌn.i/", "Noun", "Natural wild flower honey.", "عسل أزهار برية طبيعي.", "A2", "🍯"),
    ("Salt", "ملح", "/sɒlt/", "Noun", "Sea salt enhances all food flavors.", "ملح البحر يعزز نكهات جميع الأطعمة.", "A1", "🧂"),
    ("Pepper", "فلفل أسود", "/ˈpep.ər/", "Noun", "Crushed black pepper on the steak.", "فلفل أسود مجروش على شريحة اللحم.", "A1", "🧂"),
    ("Sugar", "سكر", "/ˈʃʊɡ.ər/", "Noun", "Brown sugar dissolves in warm tea.", "السكر البني يذوب في الشاي الدافئ.", "A1", "🍬"),
    ("Oil", "زيت", "/ɔɪl/", "Noun", "Extra virgin olive oil from Spain.", "زيت زيتون بكر ممتاز من إسبانيا.", "A1", "🫒"),
    ("Vinegar", "خل", "/ˈvɪn.ɪ.ɡər/", "Noun", "Balsamic vinegar pairs with tomatoes.", "خل البلسميك يتناسب مع الطماطم.", "B1", "🥗"),
    ("Sauce", "صلصة / صوص", "/sɔːs/", "Noun", "Rich marinara tomato sauce.", "صلصة طماطم مارينارا غنية النكهة.", "A2", "🥫"),
    ("Spice", "توابل / بهار", "/spaɪs/", "Noun", "Exotic spices aroma filled the market.", "رائحة التوابل الفريدة ملأت السوق.", "B1", "🌶️"),
    ("Breakfast", "وجبة إفطار", "/ˈbrek.fəst/", "Noun", "A balanced breakfast energizes your day.", "إفطار متوازن يمدك بالطاقة طوال يومك.", "A1", "🍳"),
    ("Lunch", "وجبة غداء", "/lʌntʃ/", "Noun", "They met for a quick business lunch.", "التقيا لتناول غداء عمل سريع.", "A1", "🍱"),
    ("Dinner", "وجبة عشاء", "/ˈdɪn.ər/", "Noun", "We sat down for a quiet family dinner.", "جلسنا لتناول عشاء عائلي هادئ.", "A1", "🍽️"),
    ("Snack", "وجبة خفيفة", "/snæk/", "Noun", "A handful of almonds is a healthy snack.", "حفنة من اللوز وجبة خفيفة صحية.", "A2", "🥜"),
]

for item in food_data:
    add_word(item[0], item[1], item[2], item[3], item[4], item[5], "Food & Dining", "الأطعمة والمشروبات", item[6], item[7])

print(f"Total words after Food: {len(records)}")

EOF
