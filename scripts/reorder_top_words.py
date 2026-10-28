#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = "app/src/main/assets/database/words.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Handcrafted core words to prioritize at top of database
TOP_CURATED = [
    ("Apple", "تفاحة", "/ˈæp.əl/", "Noun", "She bought fresh red apples.", "اشترت تفاحاً أحمر طازجاً.", "Food & Dining", "الأطعمة والمشروبات", "A1", "🍎"),
    ("Banana", "موزة", "/bəˈnæn.ə/", "Noun", "Bananas are rich in potassium.", "الموز غني بالبوتاسيوم.", "Food & Dining", "الأطعمة والمشروبات", "A1", "🍌"),
    ("Cat", "قطة", "/kæt/", "Noun", "The little cat purred softly.", "خرخرت القطة الصغيرة بلطف.", "Animals & Pets", "الحيوانات", "A1", "🐱"),
    ("House", "بيت / منزل", "/haʊs/", "Noun", "They live in a beautiful house.", "يعيشون في منزل جميل.", "Home & Living", "المنزل والمعيشة", "A1", "🏠"),
    ("Book", "كتاب", "/bʊk/", "Noun", "Reading books expands your mind.", "قراءة الكتب توسع آفاق عقلك.", "Education & School", "التعليم والمدرسة", "A1", "📖"),
    ("Orange", "برتقالة", "/ˈɒr.ɪndʒ/", "Noun", "Fresh orange juice is cold.", "عصير البرتقال الطازج بارد.", "Food & Dining", "الأطعمة والمشروبات", "A1", "🍊"),
    ("Dog", "كلب", "/dɒɡ/", "Noun", "The dog is a loyal companion.", "الكلب رفيق وفي ومخلص.", "Animals & Pets", "الحيوانات", "A1", "🐶"),
    ("Car", "سيارة", "/kɑːr/", "Noun", "He drives an electric car to work.", "يقود سيارة كهربائية إلى العمل.", "Travel & Transport", "السفر والمواصلات", "A1", "🚗"),
    ("Water", "ماء", "/ˈwɔː.tər/", "Noun", "Drink plenty of clean water.", "اشرب الكثير من الماء النقي.", "Food & Dining", "الأطعمة والمشروبات", "A1", "💧"),
    ("Bread", "خبز", "/bred/", "Noun", "Fresh bread smells wonderful.", "رائحة الخبز الطازج رائعة.", "Food & Dining", "الأطعمة والمشروبات", "A1", "🍞"),
    ("School", "مدرسة", "/skuːl/", "Noun", "Children walk to school every morning.", "يمشي الأطفال إلى المدرسة كل صباح.", "Education & School", "التعليم والمدرسة", "A1", "🏫"),
    ("Teacher", "معلم / أستاذ", "/ˈtiː.tʃər/", "Noun", "The teacher explained the lesson clearly.", "شرح المعلم الدرس بوضوح.", "Education & School", "التعليم والمدرسة", "A1", "👨‍🏫"),
    ("Doctor", "طبيب / دكتور", "/ˈdɒk.tər/", "Noun", "The doctor examined the patient carefully.", "فحص الطبيب المريض بعناية.", "Health & Body", "الصحة والطب", "A1", "🩺"),
    ("Hospital", "مستشفى", "/ˈhɒs.pɪ.təl/", "Noun", "The hospital is open 24 hours.", "المستشفى مفتوح على مدار 24 ساعة.", "Health & Body", "الصحة والطب", "A1", "🏥"),
    ("Sun", "شمس", "/sʌn/", "Noun", "The bright sun warms the earth.", "الشمس المشرقة تدفئ الأرض.", "Nature & Weather", "الطبيعة والطقس", "A1", "☀️"),
    ("Moon", "قمر", "/muːn/", "Noun", "The full moon shines in the dark sky.", "القمر المكتمل يضيء في السماء المظلمة.", "Nature & Weather", "الطبيعة والطقس", "A1", "🌕"),
    ("Coffee", "قهوة", "/ˈkɒf.i/", "Noun", "I start my morning with hot coffee.", "أبدأ صباحي بقهوة ساخنة.", "Food & Dining", "الأطعمة والمشروبات", "A1", "☕"),
    ("Tea", "شاي", "/tiː/", "Noun", "We drink mint tea after dinner.", "نشرب شاي النعناع بعد العشاء.", "Food & Dining", "الأطعمة والمشروبات", "A1", "🫖"),
    ("Family", "عائلة / أسرة", "/ˈfæm.əl.i/", "Noun", "Family is the most important blessing.", "العائلة هي أهم نعمة.", "Family & People", "العائلة والناس", "A1", "👨‍👩‍👧"),
    ("Friend", "صديق", "/frend/", "Noun", "True friends stand by you always.", "الأصدقاء الحقيقيون يقفون بجانبك دائماً.", "Family & People", "العائلة والناس", "A1", "🤝"),
    ("City", "مدينة", "/ˈsɪt.i/", "Noun", "New York is a bustling world city.", "نيويورك مدينة عالمية نابضة بالحياة.", "City & Places", "المدينة والأماكن", "A1", "🏙️"),
    ("Time", "وقت / زمن", "/taɪm/", "Noun", "Time is our most valuable asset.", "الوقت هو أثمن ما نملك.", "Time & Numbers", "الوقت والأرقام", "A1", "⏰"),
    ("Money", "مال / نقود", "/ˈmʌn.i/", "Noun", "Save money for your future goals.", "ادخر المال لأهدافك المستقبلية.", "Work & Business", "العمل والتجارة", "A1", "💰"),
    ("Computer", "حاسوب / كمبيوتر", "/kəmˈpjuː.tər/", "Noun", "Modern computers process data rapidly.", "أجهزة الحاسوب الحديثة تعالج البيانات بسرعة.", "Technology & Devices", "التكنولوجيا والأجهزة", "A1", "💻"),
    ("Phone", "هاتف", "/fəʊn/", "Noun", "Smartphones connect people worldwide.", "الهواتف الذكية تصل الناس في كل مكان.", "Technology & Devices", "التكنولوجيا والأجهزة", "A1", "📱"),
]

# Fetch existing words
cur.execute("SELECT english, arabic, phonetic, partOfSpeech, exampleEn, exampleAr, category, categoryAr, level, emoji FROM words")
all_words = cur.fetchall()

existing_words_map = {row[0].strip().lower(): row for row in all_words}

# Re-insert starting with TOP_CURATED
cur.execute("DELETE FROM words")
cur.execute("DELETE FROM sqlite_sequence WHERE name='words'")

inserted_count = 0
added_keys = set()

for item in TOP_CURATED:
    key = item[0].strip().lower()
    added_keys.add(key)
    cur.execute("""
    INSERT INTO words (
        english, arabic, phonetic, partOfSpeech, exampleEn, exampleAr,
        category, categoryAr, level, emoji, isFavorite, isLearned, masteryScore
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
    """, item)
    inserted_count += 1

for row in all_words:
    key = row[0].strip().lower()
    if key in added_keys:
        continue
    added_keys.add(key)
    cur.execute("""
    INSERT INTO words (
        english, arabic, phonetic, partOfSpeech, exampleEn, exampleAr,
        category, categoryAr, level, emoji, isFavorite, isLearned, masteryScore
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
    """, row)
    inserted_count += 1

conn.commit()
print(f"Re-indexed words database successfully. Total words: {inserted_count}")
cur.execute("SELECT id, english, arabic, category, emoji FROM words LIMIT 10")
for r in cur.fetchall():
    print(r)
conn.close()
EOF
python3 /tmp/reorder.py 2>/dev/null || python3 -c "
import sqlite3
# Run inline
"
