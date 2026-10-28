package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.animation.Crossfade
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ListAlt
import androidx.compose.material.icons.automirrored.outlined.ListAlt
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Quiz
import androidx.compose.material.icons.filled.Style
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Quiz
import androidx.compose.material.icons.outlined.Style
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.ui.screens.FlashcardScreen
import com.example.ui.screens.HomeScreen
import com.example.ui.screens.ProfileScreen
import com.example.ui.screens.QuizScreen
import com.example.ui.screens.WordDetailSheet
import com.example.ui.screens.WordListScreen
import com.example.ui.theme.MyApplicationTheme
import com.example.ui.theme.PurpleContainer
import com.example.ui.theme.PurpleDark
import com.example.ui.theme.PurplePrimary
import com.example.ui.viewmodel.WordViewModel

enum class MainTab(val title: String, val titleAr: String, val activeIcon: ImageVector, val inactiveIcon: ImageVector) {
    HOME("Learn", "الرئيسية", Icons.Filled.AutoAwesome, Icons.Outlined.AutoAwesome),
    VOCABULARY("Vocabulary", "الكلمات", Icons.AutoMirrored.Filled.ListAlt, Icons.AutoMirrored.Outlined.ListAlt),
    QUIZ("Quiz", "الاختبار", Icons.Filled.Quiz, Icons.Outlined.Quiz),
    FLASHCARDS("Flashcards", "البطاقات", Icons.Filled.Style, Icons.Outlined.Style),
    PROFILE("Profile", "حسابي", Icons.Filled.Person, Icons.Outlined.Person)
}

class MainActivity : ComponentActivity() {

    private val viewModel: WordViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                MainAppContent(viewModel = viewModel)
            }
        }
    }
}

@Composable
fun MainAppContent(viewModel: WordViewModel) {
    var currentTab by rememberSaveable { mutableStateOf(MainTab.HOME) }
    val selectedWord by viewModel.selectedWord.collectAsState()

    // Handle back button
    BackHandler(enabled = selectedWord != null || currentTab != MainTab.HOME) {
        if (selectedWord != null) {
            viewModel.selectWord(null)
        } else if (currentTab != MainTab.HOME) {
            currentTab = MainTab.HOME
        }
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        contentWindowInsets = WindowInsets.safeDrawing,
        bottomBar = {
            NavigationBar(
                modifier = Modifier
                    .windowInsetsPadding(WindowInsets.navigationBars)
                    .testTag("main_bottom_nav"),
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 6.dp
            ) {
                MainTab.entries.forEach { tab ->
                    val isSelected = currentTab == tab
                    NavigationBarItem(
                        selected = isSelected,
                        onClick = { currentTab = tab },
                        icon = {
                            Icon(
                                imageVector = if (isSelected) tab.activeIcon else tab.inactiveIcon,
                                contentDescription = tab.title
                            )
                        },
                        label = {
                            Text(
                                text = tab.title,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                            )
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = PurpleDark,
                            selectedTextColor = PurplePrimary,
                            indicatorColor = PurpleContainer,
                            unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
                            unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant
                        ),
                        modifier = Modifier.testTag("nav_item_${tab.name.lowercase()}")
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            Crossfade(
                targetState = currentTab,
                label = "screenTransition"
            ) { tab ->
                when (tab) {
                    MainTab.HOME -> {
                        HomeScreen(
                            viewModel = viewModel,
                            onNavigateToWords = { category ->
                                if (category != null) {
                                    viewModel.selectedCategory.value = category
                                }
                                currentTab = MainTab.VOCABULARY
                            },
                            onNavigateToQuiz = {
                                viewModel.startNewQuiz(count = 5)
                                currentTab = MainTab.QUIZ
                            },
                            onNavigateToFlashcards = {
                                currentTab = MainTab.FLASHCARDS
                            }
                        )
                    }

                    MainTab.VOCABULARY -> {
                        WordListScreen(
                            viewModel = viewModel
                        )
                    }

                    MainTab.QUIZ -> {
                        QuizScreen(
                            viewModel = viewModel,
                            onBack = { currentTab = MainTab.HOME }
                        )
                    }

                    MainTab.FLASHCARDS -> {
                        FlashcardScreen(
                            viewModel = viewModel
                        )
                    }

                    MainTab.PROFILE -> {
                        ProfileScreen(
                            viewModel = viewModel
                        )
                    }
                }
            }

            // Word Detail Bottom Sheet
            WordDetailSheet(
                word = selectedWord,
                onDismiss = { viewModel.selectWord(null) },
                onSpeak = { text -> viewModel.speak(text) },
                onToggleFavorite = { word -> viewModel.toggleFavorite(word) },
                onToggleLearned = { word -> viewModel.toggleLearned(word) }
            )
        }
    }
}
