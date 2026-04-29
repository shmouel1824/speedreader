from .models import Badge, UserBadge, UserSession


def award_badge(user, code):
    """
    Award a badge to a user if they don't already have it.
    Returns the badge if newly awarded, None if already owned.
    """
    try:
        badge = Badge.objects.get(code=code)
    except Badge.DoesNotExist:
        return None

    _, created = UserBadge.objects.get_or_create(user=user, badge=badge)
    return badge if created else None


def check_and_award_badges(user, session):
    """
    Check all badge conditions after a completed session.
    Returns a list of newly awarded badges.
    """
    newly_awarded = []
    all_sessions  = UserSession.objects.filter(user=user, completed=True)
    total         = all_sessions.count()
    profile       = user.profile

    # ── helper ───────────────────────────────────────
    def award(code):
        badge = award_badge(user, code)
        if badge:
            newly_awarded.append(badge)

    # ── MILESTONES ───────────────────────────────────
    if total >= 1:  award("first_steps")
    if total >= 10: award("bookworm")
    if total >= 25: award("scholar")
    if total >= 50: award("librarian")

    # ── SPEED ────────────────────────────────────────
    if session.wpm >= 200: award("speed_reader")
    if session.wpm >= 300: award("speed_demon")
    if session.wpm >= 500: award("lightning")

    # ── COMPREHENSION ────────────────────────────────
    if session.score >= 80:  award("sharp_mind")
    if session.score >= 100: award("perfectionist")

    # consistency: last 5 sessions all >= 80
    last_5 = all_sessions.order_by('-created_at')[:5]
    if last_5.count() == 5 and all(s.score >= 80 for s in last_5):
        award("consistent")

    # ── MODES ────────────────────────────────────────
    if session.reading_mode == 'rsvp':      award("challenger")
    if session.reading_mode == 'spotlight': award("spotlight_star")

    modes_used = set(
        all_sessions.values_list('reading_mode', flat=True)
    )
    if {'highlight', 'scroll', 'spotlight', 'rsvp'}.issubset(modes_used):
        award("all_rounder")

    # ── CHUNKS ───────────────────────────────────────
    if session.chunk_size == 5: award("big_picture")

    # ── LANGUAGES ────────────────────────────────────
    langs_used = set(
        all_sessions.values_list('text__language', flat=True)
    )
    if len(langs_used) >= 3: award("polyglot")
    if len(langs_used) >= 6: award("babel")

    # ── LEVELS ───────────────────────────────────────
    if profile.current_level >= 3: award("rising_star")
    if profile.current_level >= 5: award("master_reader")

    # ── STREAKS ──────────────────────────────────────────
    if profile.current_streak >= 3:  award("streak_3")
    if profile.current_streak >= 7:  award("streak_7")
    if profile.current_streak >= 30: award("streak_30")

    return newly_awarded