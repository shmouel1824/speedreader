from django.contrib import admin
from .models import (Subject, Text, Quiz, UserProfile, UserSession,
                     Badge, UserBadge, DailyChallenge, DailyChallengeEntry,
                     Lesson, LessonProgress, SpeedReadingQA, AssistantMessage)


# ─────────────────────────────────────────
# SUBJECT
# ─────────────────────────────────────────
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ("name", "description", "created_at")
    search_fields = ("name",)
    ordering      = ("name",)


# ─────────────────────────────────────────
# TEXT
# ─────────────────────────────────────────
@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display   = ("title", "subject", "difficulty", "word_count", "created_at")
    list_filter    = ("difficulty", "subject")
    search_fields  = ("title", "content")
    ordering       = ("difficulty", "subject")
    readonly_fields = ("word_count", "created_at")


# ─────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────
class QuizInline(admin.TabularInline):
    model  = Quiz
    extra  = 1
    fields = ("question", "choice_a", "choice_b", "choice_c", "choice_d", "correct_choice")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display  = ("question", "text", "correct_choice", "created_at")
    list_filter   = ("correct_choice", "text__subject")
    search_fields = ("question",)


# ─────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display   = ("user", "current_level", "average_wpm", "average_score", "total_sessions")
    list_filter    = ("current_level",)
    search_fields  = ("user__username",)
    readonly_fields = ("created_at",)


# ─────────────────────────────────────────
# USER SESSION
# ─────────────────────────────────────────
@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display   = ("user", "text", "wpm", "score", "time_spent", "completed", "created_at")
    list_filter    = ("completed", "text__subject")
    search_fields  = ("user__username", "text__title")
    readonly_fields = ("created_at",)
    ordering       = ("-created_at",)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display  = ("icon", "code", "name", "category", "description")
    list_filter   = ("category",)
    search_fields = ("name", "code")
    ordering      = ("category", "name")

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display  = ("user", "badge", "earned_at")
    list_filter   = ("badge__category",)
    search_fields = ("user__username", "badge__name")
    ordering      = ("-earned_at",)

@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display  = ("date", "text", "created_at")
    ordering      = ("-date",)

@admin.register(DailyChallengeEntry)
class DailyChallengeEntryAdmin(admin.ModelAdmin):
    list_display  = ("challenge", "user", "wpm", "score", "rank", "created_at")
    list_filter   = ("challenge",)
    ordering      = ("-created_at",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("number", "icon", "title", "subtitle")
    ordering     = ("number",)

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "score", "completed_at")
    list_filter  = ("completed",)

@admin.register(SpeedReadingQA)
class SpeedReadingQAAdmin(admin.ModelAdmin):
    list_display  = ("question", "times_used", "created_at")
    ordering      = ("-times_used",)
    search_fields = ("question",)

@admin.register(AssistantMessage)
class AssistantMessageAdmin(admin.ModelAdmin):
    list_display  = ("user", "role", "from_cache", "created_at")
    list_filter   = ("role", "from_cache")
    ordering      = ("-created_at",)