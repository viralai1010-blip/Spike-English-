package com.example.data

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "words",
    indices = [
        Index("english"),
        Index("arabic"),
        Index("category"),
        Index("level"),
        Index("isFavorite"),
        Index("isLearned")
    ]
)
data class Word(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val english: String,
    val arabic: String,
    val phonetic: String = "",
    val partOfSpeech: String = "Noun",
    val exampleEn: String = "",
    val exampleAr: String = "",
    val category: String = "General Vocabulary",
    val categoryAr: String = "المفردات العامة",
    val level: String = "A1",
    val emoji: String = "📖",
    val isFavorite: Boolean = false,
    val isLearned: Boolean = false,
    val masteryScore: Int = 0
)
