from django.core.management.base import BaseCommand
from reader.models import Badge

BADGES = [
    # ── Milestones ──────────────────────────────────
    {
        "code": "first_steps",
        "name": "First Steps",
        "description": "Complete your very first reading session.",
        "icon": "👣",
        "category": "Milestones",
    },
    {
        "code": "bookworm",
        "name": "Bookworm",
        "description": "Complete 10 reading sessions.",
        "icon": "📚",
        "category": "Milestones",
    },
    {
        "code": "scholar",
        "name": "Scholar",
        "description": "Complete 25 reading sessions.",
        "icon": "🎓",
        "category": "Milestones",
    },
    {
        "code": "librarian",
        "name": "Librarian",
        "description": "Complete 50 reading sessions.",
        "icon": "🏛️",
        "category": "Milestones",
    },
    # ── Speed ───────────────────────────────────────
    {
        "code": "speed_reader",
        "name": "Speed Reader",
        "description": "Reach 200 words per minute.",
        "icon": "💨",
        "category": "Speed",
    },
    {
        "code": "speed_demon",
        "name": "Speed Demon",
        "description": "Reach 300 words per minute.",
        "icon": "🚀",
        "category": "Speed",
    },
    {
        "code": "lightning",
        "name": "Lightning",
        "description": "Reach 500 words per minute.",
        "icon": "⚡",
        "category": "Speed",
    },
    # ── Comprehension ────────────────────────────────
    {
        "code": "sharp_mind",
        "name": "Sharp Mind",
        "description": "Score 80% or above on a quiz.",
        "icon": "🧠",
        "category": "Comprehension",
    },
    {
        "code": "perfectionist",
        "name": "Perfectionist",
        "description": "Score 100% on a quiz.",
        "icon": "💎",
        "category": "Comprehension",
    },
    {
        "code": "consistent",
        "name": "Consistent",
        "description": "Score 80% or above 5 sessions in a row.",
        "icon": "🎯",
        "category": "Comprehension",
    },
    # ── Modes ───────────────────────────────────────
    {
        "code": "challenger",
        "name": "Challenger",
        "description": "Complete a session using RSVP mode.",
        "icon": "⚡",
        "category": "Modes",
    },
    {
        "code": "spotlight_star",
        "name": "Spotlight Star",
        "description": "Complete a session using Spotlight mode.",
        "icon": "🔦",
        "category": "Modes",
    },
    {
        "code": "all_rounder",
        "name": "All Rounder",
        "description": "Use all 4 reading modes at least once.",
        "icon": "🌟",
        "category": "Modes",
    },
    # ── Chunks ──────────────────────────────────────
    {
        "code": "big_picture",
        "name": "Big Picture",
        "description": "Complete a session with chunk size 5.",
        "icon": "👁️",
        "category": "Chunks",
    },
    # ── Languages ───────────────────────────────────
    {
        "code": "polyglot",
        "name": "Polyglot",
        "description": "Read texts in 3 different languages.",
        "icon": "🌐",
        "category": "Languages",
    },
    {
        "code": "babel",
        "name": "Tower of Babel",
        "description": "Read texts in all 6 available languages.",
        "icon": "🗼",
        "category": "Languages",
    },
    # ── Levels ──────────────────────────────────────
    {
        "code": "rising_star",
        "name": "Rising Star",
        "description": "Reach Level 3.",
        "icon": "⭐",
        "category": "Levels",
    },
    {
        "code": "master_reader",
        "name": "Master Reader",
        "description": "Reach the maximum Level 5.",
        "icon": "🏆",
        "category": "Levels",
    },
    {
    "code": "streak_3",
    "name": "3 Day Streak",
    "description": "Read for 3 consecutive days.",
    "icon": "🔥",
    "category": "Streaks",
    },
    {
        "code": "streak_7",
        "name": "Week Warrior",
        "description": "Read for 7 consecutive days.",
        "icon": "🗓️",
        "category": "Streaks",
    },
    {
        "code": "streak_30",
        "name": "Unstoppable",
        "description": "Read for 30 consecutive days.",
        "icon": "💪",
        "category": "Streaks",
    },
    {
    "code": "daily_champion",
    "name": "Daily Champion",
    "description": "Finish first on a daily challenge leaderboard.",
    "icon": "👑",
    "category": "Daily Challenge",
},
{
    "code": "daily_first",
    "name": "First Blood",
    "description": "Complete your first daily challenge.",
    "icon": "📅",
    "category": "Daily Challenge",
},
{
    "code": "daily_10",
    "name": "Daily Devotee",
    "description": "Complete 10 daily challenges.",
    "icon": "🗓️",
    "category": "Daily Challenge",
},
{
    "code": "speed_scholar",
    "name": "Speed Scholar",
    "description": "Complete all 7 speed reading lessons.",
    "icon": "🎓",
    "category": "Learning",
},
{
    "code": "curious_mind",
    "name": "Curious Mind",
    "description": "Ask 10 questions to the Speed Reading Assistant.",
    "icon": "🔍",
    "category": "Learning",
},
{
    "code": "theorist",
    "name": "Theorist",
    "description": "Ask 25 questions to the Speed Reading Assistant.",
    "icon": "📜",
    "category": "Learning",
},
{
    "code": "lesson_1",
    "name": "First Lesson",
    "description": "Complete Lesson 1: Eliminate Subvocalization.",
    "icon": "🤫",
    "category": "Learning",
},
]


class Command(BaseCommand):
    help = "Create all badges in the database"

    def handle(self, *args, **options):
        created = 0
        for data in BADGES:
            badge, was_created = Badge.objects.get_or_create(
                code=data["code"],
                defaults=data
            )
            if was_created:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created: {badge.icon} {badge.name}")
                )
            else:
                self.stdout.write(f"  · Exists:  {badge.icon} {badge.name}")

        self.stdout.write("─" * 40)
        self.stdout.write(
            self.style.SUCCESS(f"Done! {created} new badges created.")
        )