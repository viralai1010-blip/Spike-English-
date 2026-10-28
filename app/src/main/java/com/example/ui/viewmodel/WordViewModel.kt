package com.example.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.AppDatabase
import com.example.data.Word
import com.example.data.WordRepository
import com.example.util.TtsManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class LearningStats(
    val totalWords: Int = 5200,
    val learnedCount: Int = 0,
    val favoriteCount: Int = 0,
    val progressPercent: Float = 0f
)

enum class QuizPromptType {
    AR_TO_EN, // "What is تفاحة؟" -> Options in English
    EN_TO_AR  // "What is Apple in Arabic?" -> Options in Arabic
}

data class QuizQuestion(
    val word: Word,
    val promptType: QuizPromptType,
    val options: List<Word>,
    val correctIndex: Int
)

data class QuizState(
    val questions: List<QuizQuestion> = emptyList(),
    val currentIndex: Int = 0,
    val selectedOptionIndex: Int? = null,
    val isSubmitted: Boolean = false,
    val score: Int = 0,
    val isFinished: Boolean = false
) {
    val currentQuestion: QuizQuestion?
        get() = questions.getOrNull(currentIndex)
    val progressPercent: Float
        get() = if (questions.isNotEmpty()) ((currentIndex) / questions.size.toFloat()) * 100f else 0f
}

data class FlashcardState(
    val cards: List<Word> = emptyList(),
    val currentIndex: Int = 0,
    val isFlipped: Boolean = false
) {
    val currentCard: Word?
        get() = cards.getOrNull(currentIndex)
}

@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class WordViewModel(application: Application) : AndroidViewModel(application) {

    private val repository: WordRepository
    val ttsManager: TtsManager = TtsManager(application)

    init {
        val db = AppDatabase.getDatabase(application)
        repository = WordRepository(db.wordDao())
    }

    // Filter states
    val searchQuery = MutableStateFlow("")
    val selectedCategory = MutableStateFlow("All")
    val selectedLevel = MutableStateFlow("All")
    val filterFavoritesOnly = MutableStateFlow(false)
    val filterLearnedOnly = MutableStateFlow(false)

    // Reactive filtered words list
    val wordsList: StateFlow<List<Word>> = combine(
        searchQuery,
        selectedCategory,
        selectedLevel,
        filterFavoritesOnly,
        filterLearnedOnly
    ) { query, cat, lvl, favs, learned ->
        FilterParams(
            query = query,
            category = if (cat == "All") "" else cat,
            level = if (lvl == "All") "" else lvl,
            favorites = favs,
            learned = learned
        )
    }.flatMapLatest { params ->
        repository.filterWords(
            query = params.query,
            category = params.category,
            level = params.level,
            onlyFavorites = params.favorites,
            onlyLearned = params.learned,
            limit = 400
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    // Stats
    val totalCount: StateFlow<Int> = repository.totalCount
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 5200)

    val learnedCount: StateFlow<Int> = repository.learnedCount
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    val favoriteCount: StateFlow<Int> = repository.favoriteCount
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    val stats: StateFlow<LearningStats> = combine(
        totalCount,
        learnedCount,
        favoriteCount
    ) { total, learned, favs ->
        val safeTotal = if (total > 0) total else 5200
        val percent = (learned.toFloat() / safeTotal) * 100f
        LearningStats(
            totalWords = safeTotal,
            learnedCount = learned,
            favoriteCount = favs,
            progressPercent = percent
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), LearningStats())

    // All available categories
    val categories: StateFlow<List<String>> = repository.allCategories
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    // Daily Word
    private val _dailyWord = MutableStateFlow<Word?>(null)
    val dailyWord: StateFlow<Word?> = _dailyWord.asStateFlow()

    // Selected Word for detail bottom sheet
    private val _selectedWord = MutableStateFlow<Word?>(null)
    val selectedWord: StateFlow<Word?> = _selectedWord.asStateFlow()

    // Quiz State
    private val _quizState = MutableStateFlow(QuizState())
    val quizState: StateFlow<QuizState> = _quizState.asStateFlow()

    // Flashcard State
    private val _flashcardState = MutableStateFlow(FlashcardState())
    val flashcardState: StateFlow<FlashcardState> = _flashcardState.asStateFlow()

    // Speech speed: 1.0f (Normal), 0.75f (Slow)
    val speechSpeed = MutableStateFlow(1.0f)

    init {
        loadDailyWord()
        startNewQuiz(count = 5)
        initFlashcards()
    }

    private fun loadDailyWord() {
        viewModelScope.launch {
            val random = repository.getRandomWord()
            _dailyWord.value = random
        }
    }

    fun selectWord(word: Word?) {
        _selectedWord.value = word
    }

    fun toggleFavorite(word: Word) {
        viewModelScope.launch {
            val newFav = !word.isFavorite
            repository.setFavorite(word.id, newFav)
            if (_selectedWord.value?.id == word.id) {
                _selectedWord.value = _selectedWord.value?.copy(isFavorite = newFav)
            }
        }
    }

    fun toggleLearned(word: Word) {
        viewModelScope.launch {
            val newLearned = !word.isLearned
            repository.setLearned(word.id, newLearned)
            if (_selectedWord.value?.id == word.id) {
                _selectedWord.value = _selectedWord.value?.copy(isLearned = newLearned)
            }
        }
    }

    fun speak(text: String) {
        ttsManager.speak(text, speechSpeed.value)
    }

    // --- QUIZ LOGIC ---
    fun startNewQuiz(count: Int = 5, level: String? = null, category: String? = null) {
        viewModelScope.launch {
            val targetWords = when {
                !level.isNullOrBlank() && level != "All" -> repository.getRandomWordsForLevel(level, count * 4)
                !category.isNullOrBlank() && category != "All" -> repository.getRandomWordsForCategory(category, count * 4)
                else -> repository.getRandomWords(count * 4)
            }

            if (targetWords.size < count) {
                return@launch
            }

            val questionWords = targetWords.shuffled().take(count)
            val questionList = mutableListOf<QuizQuestion>()

            for (target in questionWords) {
                // Pick 3 distractors
                val distractors = targetWords.filter { it.id != target.id }.shuffled().take(3)
                if (distractors.size < 3) continue

                val allOptions = (distractors + target).shuffled()
                val correctIndex = allOptions.indexOf(target)
                val promptType = if (questionList.size % 2 == 0) QuizPromptType.AR_TO_EN else QuizPromptType.EN_TO_AR

                questionList.add(
                    QuizQuestion(
                        word = target,
                        promptType = promptType,
                        options = allOptions,
                        correctIndex = correctIndex
                    )
                )
            }

            _quizState.value = QuizState(
                questions = questionList,
                currentIndex = 0,
                selectedOptionIndex = null,
                isSubmitted = false,
                score = 0,
                isFinished = false
            )
        }
    }

    fun selectQuizOption(index: Int) {
        val current = _quizState.value
        if (current.isSubmitted || current.isFinished) return

        val q = current.currentQuestion ?: return
        val isCorrect = index == q.correctIndex
        val addedScore = if (isCorrect) 10 else 0

        _quizState.value = current.copy(
            selectedOptionIndex = index,
            isSubmitted = true,
            score = current.score + addedScore
        )

        // Pronounce the word automatically when answered!
        speak(q.word.english)

        if (isCorrect) {
            viewModelScope.launch {
                repository.setLearned(q.word.id, true)
            }
        }
    }

    fun nextQuizQuestion() {
        val current = _quizState.value
        if (current.currentIndex + 1 < current.questions.size) {
            _quizState.value = current.copy(
                currentIndex = current.currentIndex + 1,
                selectedOptionIndex = null,
                isSubmitted = false
            )
        } else {
            _quizState.value = current.copy(
                isFinished = true
            )
        }
    }

    // --- FLASHCARDS LOGIC ---
    fun initFlashcards() {
        viewModelScope.launch {
            val list = repository.getRandomWords(20)
            _flashcardState.value = FlashcardState(
                cards = list,
                currentIndex = 0,
                isFlipped = false
            )
        }
    }

    fun flipFlashcard() {
        _flashcardState.value = _flashcardState.value.copy(
            isFlipped = !_flashcardState.value.isFlipped
        )
    }

    fun nextFlashcard() {
        val cur = _flashcardState.value
        if (cur.currentIndex + 1 < cur.cards.size) {
            _flashcardState.value = cur.copy(
                currentIndex = cur.currentIndex + 1,
                isFlipped = false
            )
        }
    }

    fun prevFlashcard() {
        val cur = _flashcardState.value
        if (cur.currentIndex > 0) {
            _flashcardState.value = cur.copy(
                currentIndex = cur.currentIndex - 1,
                isFlipped = false
            )
        }
    }

    fun markCurrentFlashcardLearned() {
        val card = _flashcardState.value.currentCard ?: return
        toggleLearned(card)
        nextFlashcard()
    }

    override fun onCleared() {
        super.onCleared()
        ttsManager.shutdown()
    }
}

private data class FilterParams(
    val query: String,
    val category: String,
    val level: String,
    val favorites: Boolean,
    val learned: Boolean
)
