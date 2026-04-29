from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .badges import check_and_award_badges
import random
import json

from .forms import RegisterForm
from .models import (Subject, Text, Quiz, UserSession, UserProfile,
                     Badge, UserBadge, DailyChallenge, DailyChallengeEntry,
                     Lesson, LessonProgress, SpeedReadingQA, AssistantMessage)
from django.utils import timezone
from collections import defaultdict
from .models import Badge, UserBadge

from .services import generate_text_and_quiz
from .services import LANGUAGE_CONFIG
from .streak import update_streak

from .assistant import ask_assistant
from django.http import JsonResponse

from django.http import JsonResponse
import json as json_module

from django.db.models import Sum, Count
from django.http import HttpResponse


def get_lang_cfg(language):
    return LANGUAGE_CONFIG.get(language, {'rtl': False, 'font': None})

# ─────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # automatically create UserProfile
            UserProfile.objects.create(user=user)

            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'reader/register.html', {'form': form})


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'reader/login.html', {'form': form})


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ─────────────────────────────────────────
# DASHBOARD (protected)
# ─────────────────────────────────────────
import json

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # last 20 completed sessions for the chart
    sessions = UserSession.objects.filter(
        user=request.user,
        completed=True
    ).order_by('created_at')[:20]

    # build chart data
    chart_labels = [s.created_at.strftime("%d %b") for s in sessions]
    chart_wpm    = [s.wpm   for s in sessions]
    chart_scores = [s.score for s in sessions]
    earned_badges = UserBadge.objects.filter(user=request.user).count()
    total_badges  = Badge.objects.count()

    return render(request, 'reader/dashboard.html', {
        'profile':      profile,
        'chart_labels': json.dumps(chart_labels),
        'chart_wpm':    json.dumps(chart_wpm),
        'chart_scores': json.dumps(chart_scores),
        'session_count': sessions.count(),
        'earned_badges': earned_badges,
        'total_badges':  total_badges,
    })


# ─────────────────────────────────────────
# SPEED READING TIPS (shown before reading)
# ─────────────────────────────────────────
READING_TIPS = [
    {
        "title": "Chunking",
        "icon": "👁️",
        "tip": "Instead of reading word by word, train your eyes to grab 2-3 words at a time. Let your gaze flow in smooth groups across each line.",
    },
    {
        "title": "Avoid Subvocalization",
        "icon": "🤫",
        "tip": "Do not pronounce words in your head as you read. Try to absorb meaning visually, not through inner speech. This alone can double your speed.",
    },
    {
        "title": "Use a Pointer",
        "icon": "☝️",
        "tip": "Guide your eyes with your finger or a pen moving steadily under each line. Your eyes naturally follow movement — use this to your advantage.",
    },
    {
        "title": "Preview First",
        "icon": "🔭",
        "tip": "Before reading, quickly scan the title and first sentence of each paragraph. This primes your brain and makes full reading much faster.",
    },
    {
        "title": "Focus on Keywords",
        "icon": "🎯",
        "tip": "Not every word carries equal weight. Train yourself to land on nouns and verbs — the skeleton of meaning — and skip filler words.",
    },
    {
        "title": "Expand Your Visual Span",
        "icon": "🌐",
        "tip": "Fix your gaze in the center of each line and let your peripheral vision absorb the words on either side. Fewer fixations = faster reading.",
    },
    {
        "title": "Keep a Steady Pace",
        "icon": "⏱️",
        "tip": "Resist the urge to slow down or re-read. Trust your first pass. Comprehension improves naturally as your brain adapts to the pace.",
    },
]


# ─────────────────────────────────────────
# 1. SUBJECT SELECTION
# ─────────────────────────────────────────

LANGUAGE_CHOICES = [
    ('English', '🇬🇧 English'),
    ('French',  '🇫🇷 French'),
    ('Hebrew',  '🇮🇱 Hebrew'),
    ('Arabic',  '🇸🇦 Arabic'),
    ('Spanish', '🇪🇸 Spanish'),
    ('German',  '🇩🇪 German'),

]
@login_required
def subject_select_view(request):
    subjects = Subject.objects.all().order_by('name')
    difficulty_choices = [
        (1, 'Beginner'),
        (2, 'Elementary'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    return render(request, 'reader/subject_select.html', {
        'subjects':           subjects,
        'difficulty_choices': difficulty_choices,
        'language_choices':   LANGUAGE_CHOICES,
    })


# ─────────────────────────────────────────
# 2. READING SESSION
# ─────────────────────────────────────────
@login_required
def reading_session_view(request, subject_id):
    subject  = Subject.objects.get(id=subject_id)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    level    = profile.current_level
    language = request.GET.get('language', 'English')

    from .services import LANGUAGE_CONFIG
    lang_cfg = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG['English'])

    read_text_ids = UserSession.objects.filter(
        user=request.user,
        completed=True
    ).values_list('text_id', flat=True)

    text = Text.objects.filter(
        subject=subject,
        difficulty=level,
        language=language,
    ).exclude(id__in=read_text_ids).first()

    if not text:
        text = Text.objects.filter(
            subject=subject,
            difficulty=level,
            language=language,
        ).first()

    if not text:
        # generate on the fly for this language
        try:
            from .services import generate_text_and_quiz
            data = generate_text_and_quiz(subject.name, level, language)

            text = Text.objects.create(
                subject    = subject,
                title      = data["title"],
                content    = data["content"],
                difficulty = level,
                language   = language,
            )
            for q in data["quiz"]:
                Quiz.objects.create(
                    text           = text,
                    question       = q["question"],
                    choice_a       = q["choice_a"],
                    choice_b       = q["choice_b"],
                    choice_c       = q["choice_c"],
                    choice_d       = q["choice_d"],
                    correct_choice = q["correct_choice"].upper(),
                )
        except Exception as e:
            messages.error(request, f"Could not generate text: {e}")
            return redirect('subject_select')

    session = UserSession.objects.create(
        user=request.user,
        text=text,
        completed=False,
    )

    tip = random.choice(READING_TIPS)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    prefs = {
        'font_size':    profile.font_size,
        'font_family':  profile.font_family,
        'line_spacing': profile.line_spacing,
    }

    return render(request, 'reader/reading_session.html', {
        'text':     text,
        'session':  session,
        'tip':      tip,
        'subject':  subject,
        'lang_cfg': lang_cfg,
         'prefs': prefs,
    })
# ─────────────────────────────────────────
# 3. FINISH READING → save WPM, go to quiz
# ─────────────────────────────────────────
@login_required
def finish_reading_view(request, session_id):
    if request.method != 'POST':
        return redirect('subject_select')

    session      = UserSession.objects.get(id=session_id, user=request.user)
    time_spent   = int(request.POST.get('time_spent', 1))
    time_spent   = max(time_spent, 1)
    chunk_size   = int(request.POST.get('chunk_size', 1))
    reading_mode = request.POST.get('reading_mode', 'highlight')

    wpm = round((session.text.word_count / time_spent) * 60, 1)

    session.time_spent   = time_spent
    session.wpm          = wpm
    session.chunk_size   = chunk_size
    session.reading_mode = reading_mode
    session.save()

    return redirect('quiz_session', session_id=session.id)


# ─────────────────────────────────────────
# 4. QUIZ
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# QUIZ SESSION VIEW
# ─────────────────────────────────────────
@login_required
def quiz_session_view(request, session_id):
    session  = UserSession.objects.get(id=session_id, user=request.user)
    quizzes  = Quiz.objects.filter(text=session.text)
    lang_cfg = get_lang_cfg(session.text.language)

    if request.method == 'POST':
        correct = 0
        total   = quizzes.count()
        results = []

        for quiz in quizzes:
            user_answer = request.POST.get(f'quiz_{quiz.id}', '').upper()
            is_correct  = user_answer == quiz.correct_choice
            if is_correct:
                correct += 1
            results.append({
                'quiz':        quiz,
                'user_answer': user_answer,
                'is_correct':  is_correct,
            })

        # ── raw scores ────────────────────────────────
        comprehension = round((correct / total) * 100, 1) if total > 0 else 0
        quiz_seconds  = int(request.POST.get('quiz_time_seconds', 1))
        time_limit    = int(request.POST.get('time_limit_per_question', 20))

        # ── time multiplier ───────────────────────────
        ratio      = (time_limit - 5) / (60 - 5)
        time_multi = round(2.0 - ratio * (2.0 - 0.5), 2)

        # ── chunk bonus ───────────────────────────────
        CHUNK_BONUS = {1: 1.0, 2: 1.2, 3: 1.5, 4: 1.8, 5: 2.2}
        chunk_size  = session.chunk_size
        chunk_bonus = CHUNK_BONUS.get(chunk_size, 1.0)

        # ── mode bonus ────────────────────────────────
        MODE_BONUS = {
            'highlight': 1.0,
            'scroll':    1.3,
            'spotlight': 1.5,
            'rsvp':      2.0,
        }
        mode_bonus = MODE_BONUS.get(session.reading_mode, 1.0)

        # ── final score ───────────────────────────────
        score = round(min(comprehension * time_multi * chunk_bonus * mode_bonus, 100), 1)

        # ── save session ──────────────────────────────
        session.score     = score
        session.completed = True
        session.save()

        # ── update profile ────────────────────────────
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        all_sessions = UserSession.objects.filter(user=request.user, completed=True)
        profile.total_sessions = all_sessions.count()
        profile.average_wpm    = round(
            sum(s.wpm for s in all_sessions) / all_sessions.count(), 1
        )
        profile.average_score  = round(
            sum(s.score for s in all_sessions) / all_sessions.count(), 1
        )

        # ── level up ──────────────────────────────────
        if score >= 80 and profile.current_level < 5:
            profile.current_level += 1
            messages.success(
                request,
                f"🎉 Congratulations! You leveled up to Level {profile.current_level}!"
            )

        profile.save()

        # ── update streak ─────────────────────────────
        current_streak, is_new_record = update_streak(profile)

        # ── check badges ──────────────────────────────
        newly_awarded = check_and_award_badges(request.user, session)

        # ── handle daily challenge ────────────────────
        challenge_entry  = None
        challenge_badges = []
        if request.session.get('active_challenge_id'):
            result = handle_daily_challenge_completion(request, session)
            if result:
                challenge_entry, challenge_badges = result
                newly_awarded.extend(challenge_badges)
        # ── personal best on this text ────────────────────────
        previous_best = UserSession.objects.filter(
            user=request.user,
            text=session.text,
            completed=True,
        ).exclude(id=session.id).order_by('-score').first()

        beat_record = previous_best and score > previous_best.score
        return render(request, 'reader/quiz_results.html', {
            'session':         session,
            'results':         results,
            'correct':         correct,
            'total':           total,
            'score':           score,
            'comprehension':   comprehension,
            'multiplier':      time_multi,
            'chunk_bonus':     chunk_bonus,
            'chunk_size':      chunk_size,
            'mode_bonus':      mode_bonus,
            'reading_mode':    session.reading_mode,
            'profile':         profile,
            'lang_cfg':        lang_cfg,
            'newly_awarded':   newly_awarded,
            'current_streak':  current_streak,
            'is_new_record':   is_new_record,
            'longest_streak':  profile.longest_streak,
            'challenge_entry': challenge_entry,
            'previous_best': previous_best,
            'beat_record':   beat_record,
        })

    # ── GET request → show quiz ───────────────────────
    return render(request, 'reader/quiz_session.html', {
        'session':  session,
        'quizzes':  quizzes,
        'lang_cfg': lang_cfg,
    })

@login_required
def history_view(request):
    sessions = UserSession.objects.filter(
        user=request.user,
        completed=True
    ).order_by('-created_at')

    return render(request, 'reader/history.html', {'sessions': sessions})

@login_required
def custom_text_view(request):
    if request.method == 'POST':
        topic      = request.POST.get('topic', '').strip()
        word_count = int(request.POST.get('word_count', 300))
        level      = int(request.POST.get('level', 2))
        language   = request.POST.get('language', 'English')

        if not topic:
            messages.error(request, "Please enter a topic.")
            return redirect('subject_select')

        from .services import LANGUAGE_CONFIG
        lang_cfg = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG['English'])

        # check DB first
        existing = Text.objects.filter(
            title__icontains=topic,
            difficulty=level,
            language=language,
        ).first()

        if existing:
            messages.info(
                request,
                f"We found an existing text on this topic: \"{existing.title}\". Enjoy!"
            )
            session = UserSession.objects.create(
                user=request.user,
                text=existing,
                completed=False,
            )
            tip = random.choice(READING_TIPS)
            return render(request, 'reader/reading_session.html', {
                'text':     existing,
                'session':  session,
                'tip':      tip,
                'subject':  existing.subject,
                'lang_cfg': lang_cfg,
            })

        subject, _ = Subject.objects.get_or_create(name=topic.title())

        try:
            data = generate_text_and_quiz(topic, level, language, word_count)

            text = Text.objects.create(
                subject    = subject,
                title      = data["title"],
                content    = data["content"],
                difficulty = level,
                language   = language,
            )
            for q in data["quiz"]:
                Quiz.objects.create(
                    text           = text,
                    question       = q["question"],
                    choice_a       = q["choice_a"],
                    choice_b       = q["choice_b"],
                    choice_c       = q["choice_c"],
                    choice_d       = q["choice_d"],
                    correct_choice = q["correct_choice"].upper(),
                )

            session = UserSession.objects.create(
                user=request.user,
                text=text,
                completed=False,
            )
            tip = random.choice(READING_TIPS)
            return render(request, 'reader/reading_session.html', {
                'text':     text,
                'session':  session,
                'tip':      tip,
                'subject':  subject,
                'lang_cfg': lang_cfg,
            })

        except Exception as e:
            messages.error(request, f"Generation failed: {e}. Please try again.")
            return redirect('subject_select')

    return redirect('subject_select')

@login_required
def text_list_view(request, subject_id):
    subject  = Subject.objects.get(id=subject_id)
    language = request.GET.get('language', 'English')
    lang_cfg = get_lang_cfg(language)

    texts = Text.objects.filter(
        subject=subject,
        language=language,
    ).order_by('difficulty')

    # get user's best session per text
    user_bests = {}
    for text in texts:
        best = UserSession.objects.filter(
            user=request.user,
            text=text,
            completed=True
        ).order_by('-score').first()
        if best:
            user_bests[text.id] = best

    return render(request, 'reader/text_list.html', {
        'subject':    subject,
        'texts':      texts,
        'language':   language,
        'lang_cfg':   lang_cfg,
        'user_bests': user_bests,
    })

@login_required
def start_reading_text_view(request, text_id):
    text     = Text.objects.get(id=text_id)
    language = request.GET.get('language', text.language)
    lang_cfg = get_lang_cfg(language)

    session = UserSession.objects.create(
        user=request.user,
        text=text,
        completed=False,
    )

    tip = random.choice(READING_TIPS)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    prefs = {
        'font_size':    profile.font_size,
        'font_family':  profile.font_family,
        'line_spacing': profile.line_spacing,
    }

    return render(request, 'reader/reading_session.html', {
        'text':     text,
        'session':  session,
        'tip':      tip,
        'subject':  text.subject,
        'lang_cfg': lang_cfg,
        'prefs': prefs,
    })

@login_required
def badges_view(request):
    all_badges    = Badge.objects.all().order_by('category', 'name')
    user_badges   = UserBadge.objects.filter(user=request.user).select_related('badge')
    earned_codes  = {ub.badge.code: ub.earned_at for ub in user_badges}

    # group by category
    badges_by_category = defaultdict(list)
    for badge in all_badges:
        badges_by_category[badge.category].append({
            'badge':     badge,
            'earned':    badge.code in earned_codes,
            'earned_at': earned_codes.get(badge.code),
        })

    earned_count  = len(earned_codes)
    total_count   = all_badges.count()
    progress_pct  = round((earned_count / total_count * 100), 1) if total_count > 0 else 0

    return render(request, 'reader/badges.html', {
        'badges_by_category': dict(badges_by_category),
        'earned_count':       earned_count,
        'total_count':        total_count,
        'progress_pct':       progress_pct,
    })

# ─────────────────────────────────────────
# DAILY CHALLENGE PAGE
# ─────────────────────────────────────────
@login_required
def daily_challenge_view(request):
    today     = timezone.localdate()
    lang_cfg  = get_lang_cfg('English')

    # get or create today's challenge
    try:
        challenge = DailyChallenge.objects.get(date=today)
    except DailyChallenge.DoesNotExist:
        # auto-create if admin forgot to run command
        texts = Text.objects.filter(difficulty__gte=2)
        if not texts.exists():
            texts = Text.objects.all()
        if not texts.exists():
            messages.error(request, "No texts available for today's challenge yet!")
            return redirect('dashboard')
        import random
        text      = random.choice(list(texts))
        challenge = DailyChallenge.objects.create(date=today, text=text)

    # check if user already completed today
    already_done = DailyChallengeEntry.objects.filter(
        challenge=challenge,
        user=request.user
    ).first()

    # leaderboard — top 10 entries
    leaderboard = DailyChallengeEntry.objects.filter(
        challenge=challenge
    ).select_related('user').order_by('-score', '-wpm')[:10]

    # update ranks
    for i, entry in enumerate(leaderboard, 1):
        if entry.rank != i:
            entry.rank = i
            entry.save()

    return render(request, 'reader/daily_challenge.html', {
        'challenge':    challenge,
        'already_done': already_done,
        'leaderboard':  leaderboard,
        'today':        today,
        'lang_cfg':     lang_cfg,
    })


# ─────────────────────────────────────────
# START DAILY CHALLENGE SESSION
# ─────────────────────────────────────────
@login_required
def start_daily_challenge_view(request, challenge_id):
    challenge = DailyChallenge.objects.get(id=challenge_id)
    today     = timezone.localdate()

    # prevent double attempt
    if DailyChallengeEntry.objects.filter(
        challenge=challenge,
        user=request.user
    ).exists():
        messages.warning(request, "You already completed today's challenge!")
        return redirect('daily_challenge')

    lang_cfg = get_lang_cfg(challenge.text.language)

    session = UserSession.objects.create(
        user=request.user,
        text=challenge.text,
        completed=False,
    )

    # store challenge_id in session for later
    request.session['active_challenge_id'] = challenge.id

    tip = random.choice(READING_TIPS)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    prefs = {
        'font_size':    profile.font_size,
        'font_family':  profile.font_family,
        'line_spacing': profile.line_spacing,
    }

    return render(request, 'reader/reading_session.html', {
        'text':          challenge.text,
        'session':       session,
        'tip':           tip,
        'subject':       challenge.text.subject,
        'lang_cfg':      lang_cfg,
        'is_challenge':  True,
        'prefs': prefs,
    })


# ─────────────────────────────────────────
# FINISH DAILY CHALLENGE
# ─────────────────────────────────────────
def handle_daily_challenge_completion(request, session):
    """
    Called from quiz_session_view when a challenge session completes.
    Creates a DailyChallengeEntry and awards badges.
    """
    challenge_id = request.session.pop('active_challenge_id', None)
    if not challenge_id:
        return None

    try:
        challenge = DailyChallenge.objects.get(id=challenge_id)
    except DailyChallenge.DoesNotExist:
        return None

    # create entry
    entry = DailyChallengeEntry.objects.create(
        challenge = challenge,
        user      = request.user,
        session   = session,
        wpm       = session.wpm,
        score     = session.score,
    )

    # recalculate ranks
    entries = DailyChallengeEntry.objects.filter(
        challenge=challenge
    ).order_by('-score', '-wpm')

    for i, e in enumerate(entries, 1):
        e.rank = i
        e.save()

    # award daily badges
    from .badges import award_badge
    total_challenges = DailyChallengeEntry.objects.filter(
        user=request.user
    ).count()

    new_badges = []
    b = award_badge(request.user, 'daily_first')
    if b: new_badges.append(b)

    if total_challenges >= 10:
        b = award_badge(request.user, 'daily_10')
        if b: new_badges.append(b)

    # champion badge if ranked first
    entry.refresh_from_db()
    if entry.rank == 1:
        b = award_badge(request.user, 'daily_champion')
        if b: new_badges.append(b)

    return entry, new_badges

@login_required
def retry_text_view(request, text_id):
    text     = Text.objects.get(id=text_id)
    lang_cfg = get_lang_cfg(text.language)

    # get user's previous best on this text
    previous_sessions = UserSession.objects.filter(
        user=request.user,
        text=text,
        completed=True,
    ).order_by('-score')

    best_score = previous_sessions.first().score if previous_sessions.exists() else 0
    best_wpm   = previous_sessions.order_by('-wpm').first().wpm if previous_sessions.exists() else 0
    attempts   = previous_sessions.count()

    # create new session
    session = UserSession.objects.create(
        user=request.user,
        text=text,
        completed=False,
    )

    tip = random.choice(READING_TIPS)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    prefs = {
        'font_size':    profile.font_size,
        'font_family':  profile.font_family,
        'line_spacing': profile.line_spacing,
    }

    return render(request, 'reader/reading_session.html', {
        'text':             text,
        'session':          session,
        'tip':              tip,
        'subject':          text.subject,
        'lang_cfg':         lang_cfg,
        'is_retry':         True,
        'best_score':       best_score,
        'best_wpm':         best_wpm,
        'attempts':         attempts,
        'prefs': prefs,
    })

# ─────────────────────────────────────────
# LEARN HUB
# ─────────────────────────────────────────
@login_required
def learn_hub_view(request):
    lessons  = Lesson.objects.all()
    progress = {
        lp.lesson_id: lp
        for lp in LessonProgress.objects.filter(user=request.user)
    }

    lessons_data = []
    completed_count = 0
    for lesson in lessons:
        lp = progress.get(lesson.id)
        is_completed = lp.completed if lp else False
        if is_completed:
            completed_count += 1
        lessons_data.append({
            'lesson':       lesson,
            'completed':    is_completed,
            'score':        lp.score if lp else 0,
        })

    total_qa = SpeedReadingQA.objects.count()

    return render(request, 'reader/learn/hub.html', {
        'lessons_data':    lessons_data,
        'completed_count': completed_count,
        'total_lessons':   lessons.count(),
        'total_qa':        total_qa,
    })


# ─────────────────────────────────────────
# LESSON DETAIL
# ─────────────────────────────────────────
@login_required
def lesson_view(request, number):
    lesson   = Lesson.objects.get(number=number)
    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
    )

    if request.method == 'POST':
        # quiz submission
        q1 = request.POST.get('q1', '').strip().lower()
        q2 = request.POST.get('q2', '').strip().lower()
        q3 = request.POST.get('q3', '').strip().lower()

        score = 0
        answers = LESSON_QUIZ_ANSWERS.get(lesson.number, {})

        if q1 and any(k in q1 for k in answers.get('q1', [])):
            score += 33
        if q2 and any(k in q2 for k in answers.get('q2', [])):
            score += 33
        if q3 and any(k in q3 for k in answers.get('q3', [])):
            score += 34

        progress.score     = max(progress.score, score)
        progress.completed = score >= 60
        if progress.completed and not progress.completed_at:
            progress.completed_at = timezone.now()
        progress.save()

        # check if all lessons completed
        total    = Lesson.objects.count()
        done     = LessonProgress.objects.filter(
            user=request.user, completed=True
        ).count()
        if done >= total:
            from .badges import award_badge
            award_badge(request.user, 'speed_scholar')

        # award individual lesson badge
        from .badges import award_badge
        award_badge(request.user, f'lesson_{lesson.number}')

        return render(request, 'reader/learn/lesson.html', {
            'lesson':   lesson,
            'progress': progress,
            'score':    score,
            'submitted': True,
        })

    return render(request, 'reader/learn/lesson.html', {
        'lesson':   lesson,
        'progress': progress,
        'submitted': False,
    })


# ─────────────────────────────────────────
# LESSON QUIZ ANSWERS (keyword matching)
# ─────────────────────────────────────────
LESSON_QUIZ_ANSWERS = {
    1: {
        'q1': ['inner voice', 'subvocal', 'pronounc', 'sound', 'speech'],
        'q2': ['150', '200', 'speaking speed', 'voice speed'],
        'q3': ['hum', 'count', 'speed up', 'faster', 'visual'],
    },
    2: {
        'q1': ['fixation', 'group', 'chunk', 'multiple words', 'eyes stop'],
        'q2': ['2', 'two', 'peripheral', 'span'],
        'q3': ['center', 'middle', 'fixate', 'peripheral vision'],
    },
    3: {
        'q1': ['peripheral', 'parafoveal', 'visual span', 'wider'],
        'q2': ['5', 'five', 'preview', 'upcoming'],
        'q3': ['soft focus', 'center', 'column', 'arm'],
    },
    4: {
        'q1': ['backward', 're-read', 'regression', 'go back'],
        'q2': ['15', '20', 'one in five', 'unnecessary'],
        'q3': ['pointer', 'cover', 'forward', 'keep moving'],
    },
    5: {
        'q1': ['scan', 'preview', 'before reading', 'mental map'],
        'q2': ['schema', 'hook', 'framework', 'prepare'],
        'q3': ['title', 'heading', 'first sentence', 'conclusion'],
    },
    6: {
        'q1': ['question', 'predict', 'engage', 'active', 'participate'],
        'q2': ['testing', 'retrieval', 'self-test', '50'],
        'q3': ['keyword', 'journalist', 'margin', 'connect'],
    },
    7: {
        'q1': ['meta', 'monitor', 'awareness', 'thinking about'],
        'q2': ['flow', 'challenge', 'skill', 'balance'],
        'q3': ['purpose', 'check', 'drift', 'adjust', 'ritual'],
    },
}


# ─────────────────────────────────────────
# ASSISTANT PAGE
# ─────────────────────────────────────────
@login_required
def assistant_view(request):
    history = AssistantMessage.objects.filter(
        user=request.user
    ).order_by('created_at')

    total_questions = AssistantMessage.objects.filter(
        user=request.user, role='user'
    ).count()

    quick_questions = [
        "What is RSVP?",
        "How to stop subvocalization?",
        "What is chunking?",
        "How to improve WPM?",
    ]

    suggested_topics = [
        "What does science say about speed reading?",
        "How does peripheral vision help reading?",
        "What is the preview strategy?",
        "How to eliminate regression?",
        "What is active reading?",
        "How does chunking work neurologically?",
        "What is the optimal reading speed?",
        "How to enter flow state while reading?",
    ]

    return render(request, 'reader/learn/assistant.html', {
        'history':          history,
        'total_questions':  total_questions,
        'quick_questions':  quick_questions,
        'suggested_topics': suggested_topics,
    })

# ─────────────────────────────────────────
# ASSISTANT AJAX ENDPOINT
# ─────────────────────────────────────────
@login_required
def assistant_ask_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    import json as json_module
    body     = json_module.loads(request.body)
    question = body.get('question', '').strip()

    if not question:
        return JsonResponse({'error': 'Empty question'}, status=400)

    # get conversation history for context
    history = list(AssistantMessage.objects.filter(
        user=request.user
    ).order_by('created_at').values('role', 'content'))

    # ask assistant
    result = ask_assistant(question, conversation_history=history)

    # save to DB
    AssistantMessage.objects.create(
        user=request.user, role='user',
        content=question, from_cache=False,
    )
    AssistantMessage.objects.create(
        user=request.user, role='assistant',
        content=result['answer'],
        from_cache=result['from_cache'],
    )

    # check badges
    total_q = AssistantMessage.objects.filter(
        user=request.user, role='user'
    ).count()

    from .badges import award_badge
    new_badges = []
    if total_q >= 10:
        b = award_badge(request.user, 'curious_mind')
        if b: new_badges.append({'name': b.name, 'icon': b.icon})
    if total_q >= 25:
        b = award_badge(request.user, 'theorist')
        if b: new_badges.append({'name': b.name, 'icon': b.icon})

    return JsonResponse({
        'answer':          result['answer'],
        'from_cache':      result['from_cache'],
        'similarity':      result['similarity'],
        'cached_question': result['cached_question'],
        'new_badges':      new_badges,
    })

@login_required
def save_preferences_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    body        = json_module.loads(request.body)
    font_size   = body.get('font_size',    '1.2rem')
    font_family = body.get('font_family',  'Lora')
    line_spacing= body.get('line_spacing', '2.0')

    # validate
    valid_sizes = ['0.9rem','1.05rem','1.2rem','1.45rem','1.75rem']
    valid_fonts = ['Lora','Georgia','Merriweather','Open Sans',
                   'Lexie Readable','Courier Prime']
    valid_spacing = ['1.6','2.0','2.6']

    if font_size    not in valid_sizes:    font_size    = '1.2rem'
    if font_family  not in valid_fonts:    font_family  = 'Lora'
    if line_spacing not in valid_spacing:  line_spacing = '2.0'

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.font_size    = font_size
    profile.font_family  = font_family
    profile.line_spacing = line_spacing
    profile.save()

    return JsonResponse({'status': 'saved'})

def landing_view(request):
    # redirect logged-in users directly to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # ── live stats from DB ────────────────────────────
    from django.contrib.auth.models import User
    total_users    = User.objects.count()
    total_sessions = UserSession.objects.filter(completed=True).count()
    total_texts    = Text.objects.count()
    total_languages= Text.objects.values('language').distinct().count()

     # pick 6 interesting badges for preview
    badges_preview = Badge.objects.filter(code__in=[
        'first_steps', 'speed_demon', 'perfectionist',
        'challenger', 'polyglot', 'speed_scholar',
    ])

    return render(request, 'reader/landing.html', {
        'total_users':     total_users,
        'total_sessions':  total_sessions,
        'total_texts':     total_texts,
        'total_languages': total_languages,
        'badges_preview':  badges_preview,
    })

def offline_view(request):
    return render(request, 'reader/offline.html')

def manifest_view(request):
    manifest = {
        "name": "SpeedReader",
        "short_name": "SpeedReader",
        "description": "Read faster. Understand deeper. Powered by AI.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#2c2416",
        "theme_color": "#2c2416",
        "orientation": "portrait-primary",
        "scope": "/",
        "icons": [
            {
                "src": request.build_absolute_uri('/static/icons/icon-192.png'),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": request.build_absolute_uri('/static/icons/icon-512.png'),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return JsonResponse(manifest)


def service_worker_view(request):
    sw_content = """
    const CACHE_NAME = 'speedreader-v1';

    self.addEventListener('install', function(e) {
        self.skipWaiting();
    });

    self.addEventListener('activate', function(e) {
        e.waitUntil(self.clients.claim());
    });

    self.addEventListener('fetch', function(e) {
        if (e.request.method !== 'GET') return;
        e.respondWith(
            fetch(e.request).catch(function() {
                return caches.match(e.request);
            })
        );
    });
    """
    return HttpResponse(sw_content,
                       content_type='application/javascript')

from django.http import HttpResponse, JsonResponse

def manifest_view(request):
    manifest = {
        "name": "SpeedReader",
        "short_name": "SpeedReader",
        "description": "Read faster. Understand deeper.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#2c2416",
        "theme_color": "#2c2416",
        "orientation": "portrait-primary",
        "scope": "/",
        "icons": [
            {
                "src": request.build_absolute_uri(
                    '/static/icons/icon-192.png'),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": request.build_absolute_uri(
                    '/static/icons/icon-512.png'),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return JsonResponse(manifest)


def service_worker_view(request):
    sw = """
const CACHE = 'speedreader-v2';

self.addEventListener('install', e => {
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', e => {
    if (e.request.method !== 'GET') return;
    e.respondWith(
        fetch(e.request)
            .then(response => {
                const clone = response.clone();
                caches.open(CACHE).then(c => c.put(e.request, clone));
                return response;
            })
            .catch(() => caches.match(e.request))
    );
});
"""
    return HttpResponse(sw, content_type='application/javascript')