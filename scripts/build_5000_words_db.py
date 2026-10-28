#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds an SQLite database containing over 5,000 English-Arabic words
from ArabEyes dictionary and frequency lists, categorized by CEFR level and topic,
with phonetic transcription, examples, and emoji.
"""

import sqlite3
import os
import re
import urllib.request

output_db = "app/src/main/assets/database/words.db"
os.makedirs(os.path.dirname(output_db), exist_ok=True)
if os.path.exists(output_db):
    os.remove(output_db)

print("1. Fetching Frequency List...")
freq_url = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt"
freq_data = urllib.request.urlopen(urllib.request.Request(freq_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8', errors='ignore')

freq_rank = {}
rank = 1
for line in freq_data.splitlines():
    parts = line.strip().split()
    if parts:
        w = parts[0].lower()
        if w.isalpha() and len(w) >= 2 and w not in freq_rank:
            freq_rank[w] = rank
            rank += 1

print(f"Loaded {len(freq_rank)} ranked words.")

print("2. Fetching ArabEyes Dictionary...")
dict_url = "https://raw.githubusercontent.com/usefksa/engAraDictionaryFrom_ArabEyes/master/engAraDictionary.sql"
dict_data = urllib.request.urlopen(urllib.request.Request(dict_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25).read().decode('utf-8', errors='ignore')

matches = re.findall(r"\((\d+),\s*'([^']*)',\s*'([^']*)'\)", dict_data)
print(f"Loaded {len(matches)} dictionary entries from ArabEyes.")

dict_map = {}
for _, eng, ara in matches:
    eng_clean = eng.strip()
    key = eng_clean.lower()
    if not key.isalpha() or len(key) < 2:
        continue
    # Clean arabic translation
    # If contains ::, take the first clean part
    parts = ara.split("::")
    primary_ar = parts[0].strip()
    # Remove unwanted punctuation
    primary_ar = re.sub(r'[\(\)\[\]\{\}\*]', '', primary_ar).strip()
    # If multiple alternatives separated by commas or slashes, keep first two
    alt_parts = [p.strip() for p in re.split(r'[,،؛/]', primary_ar) if p.strip()]
    if alt_parts:
        clean_ar = " / ".join(alt_parts[:2])
    else:
        clean_ar = primary_ar
    if clean_ar and key not in dict_map:
        dict_map[key] = (eng_clean, clean_ar)

print(f"Unique clean dictionary keys: {len(dict_map)}")

# Emoji and category mapping dictionaries
CATEGORY_RULES = [
    # Category, CategoryAr, Emoji, keywords
    ("Food & Dining", "الأطعمة والمشروبات", "🍎", {"apple", "banana", "orange", "lemon", "grape", "bread", "milk", "coffee", "tea", "water", "meat", "beef", "chicken", "fish", "rice", "soup", "salad", "sugar", "salt", "cheese", "egg", "butter", "honey", "juice", "pasta", "pizza", "cake", "cookie", "garlic", "onion", "potato", "tomato", "carrot", "cucumber", "fruit", "vegetable", "dessert", "snack", "breakfast", "lunch", "dinner", "restaurant", "recipe", "cook", "bake", "drink", "taste", "sweet", "sour", "bitter", "spicy", "fork", "spoon", "knife", "dish", "plate", "cup", "bowl", "steak", "pie", "beer", "wine", "sauce", "bean", "flour", "pepper", "olive", "oil"}),
    ("Home & Daily Life", "المنزل والحياة اليومية", "🏠", {"house", "home", "room", "door", "window", "bed", "chair", "table", "sofa", "kitchen", "bathroom", "bedroom", "garden", "floor", "roof", "wall", "key", "clock", "mirror", "lamp", "curtain", "carpet", "blanket", "pillow", "towel", "soap", "shampoo", "toothbrush", "fridge", "oven", "sink", "clean", "wash", "sleep", "wake", "morning", "night", "balcony", "furniture", "stairs", "gate", "garage", "cabinet", "shelf", "closet"}),
    ("Family & People", "العائلة والناس", "👨‍👩‍👧", {"father", "mother", "parent", "brother", "sister", "son", "daughter", "grandfather", "grandmother", "husband", "wife", "baby", "child", "children", "kid", "family", "friend", "neighbor", "uncle", "aunt", "cousin", "person", "people", "man", "woman", "boy", "girl", "youth", "adult", "teenager", "gentleman", "lady", "human", "crowd", "partner", "relative", "marriage", "bride", "groom"}),
    ("Animals & Nature", "الحيوانات والطبيعة", "🐾", {"dog", "cat", "bird", "lion", "tiger", "horse", "cow", "sheep", "goat", "elephant", "bear", "monkey", "rabbit", "wolf", "fox", "deer", "camel", "dolphin", "whale", "shark", "eagle", "falcon", "duck", "snake", "insect", "bee", "ant", "butterfly", "forest", "tree", "plant", "flower", "grass", "mountain", "river", "lake", "ocean", "sea", "beach", "sky", "sun", "moon", "star", "cloud", "rain", "snow", "wind", "storm", "desert", "island", "jungle"}),
    ("Travel & Transport", "السفر والمواصلات", "✈️", {"car", "bus", "train", "plane", "airplane", "ship", "boat", "bicycle", "bike", "taxi", "subway", "metro", "station", "airport", "ticket", "passport", "visa", "hotel", "luggage", "baggage", "tourist", "tourism", "trip", "travel", "journey", "flight", "road", "street", "highway", "bridge", "map", "guide", "destination", "vacation", "holiday", "cruise", "voyage"}),
    ("Work & Business", "العمل والتجارة", "💼", {"work", "job", "office", "company", "business", "boss", "manager", "employee", "worker", "career", "salary", "wage", "contract", "meeting", "interview", "hire", "resume", "project", "client", "customer", "market", "trade", "profit", "industry", "factory", "deal", "negotiate", "strategy", "leader", "profession", "colleague", "firm", "enterprise"}),
    ("Education & Science", "التعليم والعلوم", "📚", {"school", "university", "college", "student", "teacher", "professor", "class", "classroom", "lesson", "homework", "exam", "test", "grade", "degree", "book", "pen", "pencil", "notebook", "library", "study", "learn", "science", "physics", "chemistry", "biology", "math", "history", "geography", "laboratory", "research", "experiment", "theory", "knowledge"}),
    ("Technology & Devices", "التكنولوجيا والأجهزة", "💻", {"computer", "laptop", "phone", "mobile", "internet", "website", "software", "hardware", "screen", "keyboard", "mouse", "app", "application", "data", "file", "network", "digital", "online", "download", "upload", "password", "email", "server", "robot", "artificial", "camera", "battery", "code", "programming", "device", "smart", "electronic"}),
    ("Health & Medicine", "الصحة والطب", "🩺", {"doctor", "nurse", "hospital", "clinic", "patient", "medicine", "pill", "drug", "health", "healthy", "disease", "illness", "sick", "pain", "fever", "cough", "headache", "wound", "injury", "blood", "heart", "brain", "body", "muscle", "bone", "tooth", "teeth", "eye", "ear", "diet", "fitness", "exercise", "surgery", "therapy", "cure", "vitamin"}),
    ("Clothes & Fashion", "الملابس والموضة", "👗", {"shirt", "t-shirt", "pants", "trousers", "jeans", "dress", "skirt", "jacket", "coat", "sweater", "shoes", "boots", "sneakers", "socks", "hat", "cap", "gloves", "scarf", "belt", "tie", "suit", "watch", "ring", "glasses", "sunglasses", "bag", "wallet", "pocket", "zipper", "button", "fashion", "style", "wear", "cotton", "silk", "wool"}),
    ("Emotions & Feelings", "المشاعر والأحاسيس", "❤️", {"happy", "sad", "angry", "fear", "scared", "love", "hate", "joy", "smile", "cry", "laugh", "hope", "peace", "calm", "nervous", "anxious", "excited", "proud", "shy", "brave", "kind", "cruel", "jealous", "guilty", "lonely", "bored", "tired", "stressed", "confident", "surprise", "delight", "mood", "feeling", "emotion", "passion"}),
    ("City & Places", "المدينة والأماكن", "🏙️", {"city", "town", "village", "country", "capital", "center", "square", "park", "museum", "cinema", "theater", "mall", "shop", "store", "supermarket", "bank", "police", "post", "pharmacy", "bakery", "mosque", "church", "stadium", "zoo", "palace", "tower", "building", "neighborhood", "corner", "sidewalk", "traffic"}),
    ("Sports & Hobbies", "الرياضة والهوايات", "⚽", {"sport", "game", "play", "football", "soccer", "basketball", "tennis", "swimming", "running", "match", "team", "player", "coach", "ball", "goal", "win", "lose", "champion", "race", "music", "guitar", "piano", "song", "sing", "dance", "art", "paint", "draw", "photo", "reading", "gaming", "hobby", "fitness"}),
    ("Time & Numbers", "الوقت والأرقام", "⏰", {"time", "hour", "minute", "second", "day", "week", "month", "year", "decade", "century", "today", "yesterday", "tomorrow", "morning", "afternoon", "evening", "night", "early", "late", "now", "soon", "always", "never", "sometimes", "often", "first", "last", "one", "two", "three", "ten", "hundred", "thousand", "million"}),
]

def find_category(word):
    w = word.lower()
    for cat_en, cat_ar, emo, kws in CATEGORY_RULES:
        if w in kws or any(w.startswith(kw) for kw in kws if len(kw) > 4):
            return cat_en, cat_ar, emo
    # Default categorized by endings / POS
    if w.endswith("ly"):
        return "Adverbs & Modifiers", "الظروف والأحوال", "✨"
    if w.endswith("tion") or w.endswith("ment") or w.endswith("ness"):
        return "Abstract & Concepts", "مفاهيم ومصطلحات عامة", "💡"
    if w.endswith("able") or w.endswith("ful") or w.endswith("ive") or w.endswith("ous"):
        return "Descriptions & Qualities", "الصفات والأوصاف", "🌟"
    if w.endswith("ed") or w.endswith("ing"):
        return "Actions & Verbs", "أفعال وأنشطة", "⚡"
    return "General Vocabulary", "المفردات العامة الشائعة", "📖"

def estimate_pos(word):
    w = word.lower()
    if w.endswith("ly"):
        return "Adverb"
    if w.endswith("ful") or w.endswith("less") or w.endswith("ous") or w.endswith("ive") or w.endswith("able") or w.endswith("ish"):
        return "Adjective"
    if w.endswith("tion") or w.endswith("sion") or w.endswith("ment") or w.endswith("ness") or w.endswith("ity") or w.endswith("ship"):
        return "Noun"
    if w.endswith("ize") or w.endswith("ise") or w.endswith("ify") or w.endswith("ate"):
        return "Verb"
    return "Noun"

def generate_phonetic(word):
    # Generates a clean readable approximate phonetic transcription
    w = word.lower()
    vowels = {"a": "æ", "e": "e", "i": "ɪ", "o": "ɒ", "u": "ʌ"}
    res = []
    for ch in w:
        if ch in vowels:
            res.append(vowels[ch])
        elif ch == 'c':
            res.append('k')
        elif ch == 'x':
            res.append('ks')
        elif ch == 'q':
            res.append('kw')
        else:
            res.append(ch)
    return f"/{''.join(res)}/"

# Sort words by frequency rank
candidate_words = []
for w, r in freq_rank.items():
    if w in dict_map:
        orig_en, clean_ar = dict_map[w]
        candidate_words.append((r, orig_en, clean_ar))

candidate_words.sort(key=lambda x: x[0])
print(f"Total candidate intersected words: {len(candidate_words)}")

# Select top 5,200 words
TARGET_COUNT = 5200
selected = candidate_words[:TARGET_COUNT]

# If fewer than 5200, pad from dictionary
if len(selected) < TARGET_COUNT:
    for k, v in dict_map.items():
        if len(selected) >= TARGET_COUNT:
            break
        if k not in freq_rank:
            selected.append((99999, v[0], v[1]))

print(f"Final selected count: {len(selected)}")

# Assign CEFR level based on frequency rank
# Rank 1..800 -> A1 (Beginner)
# Rank 801..1800 -> A2 (Elementary)
# Rank 1801..3000 -> B1 (Intermediate)
# Rank 3001..4200 -> B2 (Upper Intermediate)
# Rank 4201+ -> C1 (Advanced)
def assign_level(idx):
    if idx < 800:
        return "A1"
    elif idx < 1800:
        return "A2"
    elif idx < 3000:
        return "B1"
    elif idx < 4200:
        return "B2"
    else:
        return "C1"

# Prepare inserts
insert_rows = []
for idx, (rank_val, eng_word, ara_word) in enumerate(selected):
    level = assign_level(idx)
    cat_en, cat_ar, emoji = find_category(eng_word)
    pos = estimate_pos(eng_word)
    phon = generate_phonetic(eng_word)
    
    # Natural bilingual example sentence
    if pos == "Verb":
        ex_en = f"You should {eng_word.lower()} regularly."
        ex_ar = f"عليك أن {ara_word} بانتظام."
    elif pos == "Adjective":
        ex_en = f"This result is very {eng_word.lower()}."
        ex_ar = f"هذه النتيجة {ara_word} للغاية."
    elif pos == "Adverb":
        ex_en = f"She spoke {eng_word.lower()} to everyone."
        ex_ar = f"تحدثت {ara_word} مع الجميع."
    else:
        ex_en = f"The {eng_word.lower()} is well known here."
        ex_ar = f"الـ {ara_word} معروف(ة) جداً هنا."

    insert_rows.append((
        eng_word.capitalize(),
        ara_word,
        phon,
        pos,
        ex_en,
        ex_ar,
        cat_en,
        cat_ar,
        level,
        emoji,
        0, # isFavorite
        0, # isLearned
        0  # masteryScore
    ))

conn = sqlite3.connect(output_db)
cur = conn.cursor()

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

cur.executemany("""
INSERT INTO words (
    english, arabic, phonetic, partOfSpeech, exampleEn, exampleAr,
    category, categoryAr, level, emoji, isFavorite, isLearned, masteryScore
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", insert_rows)

# Create helpful indexes
cur.execute("CREATE INDEX IF NOT EXISTS index_words_english ON words(english);")
cur.execute("CREATE INDEX IF NOT EXISTS index_words_arabic ON words(arabic);")
cur.execute("CREATE INDEX IF NOT EXISTS index_words_category ON words(category);")
cur.execute("CREATE INDEX IF NOT EXISTS index_words_level ON words(level);")
cur.execute("CREATE INDEX IF NOT EXISTS index_words_isFavorite ON words(isFavorite);")
cur.execute("CREATE INDEX IF NOT EXISTS index_words_isLearned ON words(isLearned);")

conn.commit()

# Verify count
cur.execute("SELECT COUNT(*) FROM words")
total_in_db = cur.fetchone()[0]
print(f"SUCCESS: Inserted {total_in_db} words into {output_db}!")

# Sample verification
cur.execute("SELECT id, english, arabic, category, level, emoji FROM words LIMIT 10")
for row in cur.fetchall():
    print(row)

conn.close()
