from django.utils import timezone


def update_streak(profile):
    """
    Call this after every completed session.
    Updates current_streak and longest_streak on the profile.
    Returns (current_streak, is_new_record) tuple.
    """
    today = timezone.localdate()
    last  = profile.last_session_date

    if last is None:
        # very first session ever
        profile.current_streak = 1

    elif last == today:
        # already played today — no change to streak
        pass

    elif (today - last).days == 1:
        # played yesterday → extend streak
        profile.current_streak += 1

    else:
        # missed one or more days → reset streak
        profile.current_streak = 1

    # update longest streak record
    if profile.current_streak > profile.longest_streak:
        profile.longest_streak = profile.current_streak

    profile.last_session_date = today
    profile.save()

    is_new_record = profile.current_streak == profile.longest_streak and profile.current_streak > 1
    return profile.current_streak, is_new_record