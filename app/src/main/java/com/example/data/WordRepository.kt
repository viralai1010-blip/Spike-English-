package com.example.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext

class WordRepository(private val wordDao: WordDao) {

    val allWords: Flow<List<Word>> = wordDao.getAllWords()
    val totalCount: Flow<Int> = wordDao.getTotalCount()
    val learnedCount: Flow<Int> = wordDao.getLearnedCount()
    val favoriteCount: Flow<Int> = wordDao.getFavoriteCount()
    val allCategories: Flow<List<String>> = wordDao.getAllCategories()
    val favoriteWords: Flow<List<Word>> = wordDao.getFavoriteWords()
    val learnedWords: Flow<List<Word>> = wordDao.getLearnedWords()

    fun filterWords(
        query: String,
        category: String,
        level: String,
        onlyFavorites: Boolean,
        onlyLearned: Boolean,
        limit: Int = 300
    ): Flow<List<Word>> {
        return wordDao.filterWords(
            query = query.trim(),
            category = category,
            level = level,
            onlyFavorites = if (onlyFavorites) 1 else 0,
            onlyLearned = if (onlyLearned) 1 else 0,
            limit = limit
        )
    }

    suspend fun getWordById(id: Int): Word? = withContext(Dispatchers.IO) {
        wordDao.getWordById(id)
    }

    suspend fun getRandomWord(): Word? = withContext(Dispatchers.IO) {
        wordDao.getRandomWord()
    }

    suspend fun getRandomWords(count: Int): List<Word> = withContext(Dispatchers.IO) {
        wordDao.getRandomWords(count)
    }

    suspend fun getRandomWordsForLevel(level: String, count: Int): List<Word> = withContext(Dispatchers.IO) {
        wordDao.getRandomWordsForLevel(level, count)
    }

    suspend fun getRandomWordsForCategory(category: String, count: Int): List<Word> = withContext(Dispatchers.IO) {
        wordDao.getRandomWordsForCategory(category, count)
    }

    suspend fun setFavorite(id: Int, isFavorite: Boolean) = withContext(Dispatchers.IO) {
        wordDao.setFavorite(id, isFavorite)
    }

    suspend fun setLearned(id: Int, isLearned: Boolean) = withContext(Dispatchers.IO) {
        wordDao.setLearned(id, isLearned)
    }

    suspend fun updateWord(word: Word) = withContext(Dispatchers.IO) {
        wordDao.updateWord(word)
    }
}
