package com.example.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface WordDao {
    @Query("SELECT * FROM words ORDER BY id ASC")
    fun getAllWords(): Flow<List<Word>>

    @Query("SELECT * FROM words ORDER BY id ASC LIMIT :limit OFFSET :offset")
    suspend fun getWordsPaged(limit: Int, offset: Int): List<Word>

    @Query("""
        SELECT * FROM words 
        WHERE (:query = '' OR english LIKE '%' || :query || '%' OR arabic LIKE '%' || :query || '%')
          AND (:category = '' OR category = :category)
          AND (:level = '' OR level = :level)
          AND (:onlyFavorites = 0 OR isFavorite = 1)
          AND (:onlyLearned = 0 OR isLearned = 1)
        ORDER BY id ASC
        LIMIT :limit
    """)
    fun filterWords(
        query: String,
        category: String,
        level: String,
        onlyFavorites: Int,
        onlyLearned: Int,
        limit: Int = 300
    ): Flow<List<Word>>

    @Query("SELECT * FROM words WHERE id = :id LIMIT 1")
    suspend fun getWordById(id: Int): Word?

    @Query("SELECT * FROM words WHERE isFavorite = 1 ORDER BY id ASC")
    fun getFavoriteWords(): Flow<List<Word>>

    @Query("SELECT * FROM words WHERE isLearned = 1 ORDER BY id ASC")
    fun getLearnedWords(): Flow<List<Word>>

    @Query("SELECT COUNT(*) FROM words")
    fun getTotalCount(): Flow<Int>

    @Query("SELECT COUNT(*) FROM words WHERE isLearned = 1")
    fun getLearnedCount(): Flow<Int>

    @Query("SELECT COUNT(*) FROM words WHERE isFavorite = 1")
    fun getFavoriteCount(): Flow<Int>

    @Query("SELECT DISTINCT category FROM words ORDER BY category ASC")
    fun getAllCategories(): Flow<List<String>>

    @Query("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
    suspend fun getRandomWord(): Word?

    @Query("SELECT * FROM words ORDER BY RANDOM() LIMIT :count")
    suspend fun getRandomWords(count: Int): List<Word>

    @Query("SELECT * FROM words WHERE level = :level ORDER BY RANDOM() LIMIT :count")
    suspend fun getRandomWordsForLevel(level: String, count: Int): List<Word>

    @Query("SELECT * FROM words WHERE category = :category ORDER BY RANDOM() LIMIT :count")
    suspend fun getRandomWordsForCategory(category: String, count: Int): List<Word>

    @Update
    suspend fun updateWord(word: Word)

    @Query("UPDATE words SET isFavorite = :isFavorite WHERE id = :id")
    suspend fun setFavorite(id: Int, isFavorite: Boolean)

    @Query("UPDATE words SET isLearned = :isLearned WHERE id = :id")
    suspend fun setLearned(id: Int, isLearned: Boolean)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertWords(words: List<Word>)
}
