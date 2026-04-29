from django.db import models
from django.contrib.auth.models import User


# ─────────────────────────────────────────
# 1. SUBJECT
# ─────────────────────────────────────────
class Subject(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────
# 2. DIFFICULTY
# ─────────────────────────────────────────
class DifficultyLevel(models.IntegerChoices):
    BEGINNER     = 1, "Beginner"
    ELEMENTARY   = 2, "Elementary"
    INTERMEDIATE = 3, "Intermediate"
    ADVANCED     = 4, "Advanced"
    EXPERT       = 5, "Expert"


# ─────────────────────────────────────────
# 3. TEXT
# ─────────────────────────────────────────
class Text(models.Model):
    subject    = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="texts")
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    difficulty = models.IntegerField(choices=DifficultyLevel.choices, default=DifficultyLevel.BEGINNER)
    word_count = models.PositiveIntegerField(default=0)
    language   = models.CharField(max_length=20, default='English')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[Level {self.difficulty}] [{self.language}] {self.title}"


# ─────────────────────────────────────────
# 4. QUIZ
# ─────────────────────────────────────────
class Quiz(models.Model):
    text           = models.ForeignKey(Text, on_delete=models.CASCADE, related_name="quizzes")
    question       = models.TextField()
    choice_a       = models.CharField(max_length=300)
    choice_b       = models.CharField(max_length=300)
    choice_c       = models.CharField(max_length=300)
    choice_d       = models.CharField(max_length=300)
    correct_choice = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    )
    created_at     = models.DateTimeField(auto_now_add=True)

    @property
    def choices(self):
        return [
            ('A', self.choice_a),
            ('B', self.choice_b),
            ('C', self.choice_c),
            ('D', self.choice_d),
        ]

    def __str__(self):
        return f"Q: {self.question[:60]}..."


# ─────────────────────────────────────────
# 5. USER PROFILE  ← only ONE definition
# ─────────────────────────────────────────
class UserProfile(models.Model):
    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    current_level     = models.IntegerField(choices=DifficultyLevel.choices, default=DifficultyLevel.BEGINNER)
    average_wpm       = models.FloatField(default=0.0)
    total_sessions    = models.PositiveIntegerField(default=0)
    average_score     = models.FloatField(default=0.0)
    current_streak    = models.PositiveIntegerField(default=0)
    longest_streak    = models.PositiveIntegerField(default=0)
    last_session_date = models.DateField(null=True, blank=True)
    font_size         = models.CharField(max_length=10, default='1.2rem')
    font_family       = models.CharField(max_length=50, default='Lora')
    line_spacing      = models.CharField(max_length=10, default='2.0')
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username} — Level {self.current_level}"


# ─────────────────────────────────────────
# 6. USER SESSION  ← only ONE definition
# ─────────────────────────────────────────
class UserSession(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    text         = models.ForeignKey(Text, on_delete=models.CASCADE, related_name="sessions")
    wpm          = models.FloatField(default=0.0)
    score        = models.FloatField(default=0.0)
    time_spent   = models.PositiveIntegerField(default=0)
    chunk_size   = models.PositiveIntegerField(default=1)
    reading_mode = models.CharField(max_length=20, default='highlight')
    completed    = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.text.title[:40]} | WPM: {self.wpm} | Score: {self.score}"


# ─────────────────────────────────────────
# 7. BADGE
# ─────────────────────────────────────────
class Badge(models.Model):
    code        = models.CharField(max_length=50, unique=True)
    name        = models.CharField(max_length=100)
    description = models.TextField()
    icon        = models.CharField(max_length=10)
    category    = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.icon} {self.name}"


# ─────────────────────────────────────────
# 8. USER BADGE
# ─────────────────────────────────────────
class UserBadge(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} — {self.badge.name}"


# ─────────────────────────────────────────
# 9. DAILY CHALLENGE
# ─────────────────────────────────────────
class DailyChallenge(models.Model):
    date       = models.DateField(unique=True)
    text       = models.ForeignKey(Text, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Challenge {self.date} — {self.text.title}"


# ─────────────────────────────────────────
# 10. DAILY CHALLENGE ENTRY
# ─────────────────────────────────────────
class DailyChallengeEntry(models.Model):
    challenge  = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name="entries")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenge_entries")
    session    = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    wpm        = models.FloatField(default=0.0)
    score      = models.FloatField(default=0.0)
    rank       = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('challenge', 'user')
        verbose_name_plural = "Daily Challenge Entries"

    def __str__(self):
        return f"{self.user.username} — {self.challenge.date} — Score:{self.score}"


# ─────────────────────────────────────────
# 11. LESSON
# ─────────────────────────────────────────
class Lesson(models.Model):
    number     = models.PositiveIntegerField(unique=True)
    title      = models.CharField(max_length=200)
    subtitle   = models.CharField(max_length=200, blank=True)
    icon       = models.CharField(max_length=10, default='📖')
    theory     = models.TextField()
    science    = models.TextField()
    how_to     = models.TextField()
    exercise   = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Lesson {self.number}: {self.title}"


# ─────────────────────────────────────────
# 12. LESSON PROGRESS
# ─────────────────────────────────────────
class LessonProgress(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed    = models.BooleanField(default=False)
    score        = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name_plural = "Lesson Progress"

    def __str__(self):
        return f"{self.user.username} — Lesson {self.lesson.number} — {'✓' if self.completed else '…'}"


# ─────────────────────────────────────────
# 13. SPEED READING Q&A
# ─────────────────────────────────────────
class SpeedReadingQA(models.Model):
    question   = models.TextField()
    answer     = models.TextField()
    times_used = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Q: {self.question[:80]}..."


# ─────────────────────────────────────────
# 14. ASSISTANT MESSAGE
# ─────────────────────────────────────────
class AssistantMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assistant_messages")
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content    = models.TextField()
    from_cache = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} [{self.role}]: {self.content[:60]}..."