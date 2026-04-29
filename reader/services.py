import json
import anthropic
from django.conf import settings


# ─────────────────────────────────────────
# CLIENT
# ─────────────────────────────────────────
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


# ─────────────────────────────────────────
# DIFFICULTY SETTINGS
# ─────────────────────────────────────────
DIFFICULTY_CONFIG = {
    1: {"label": "Beginner",     "words": 150,  "complexity": "very simple words, short sentences, everyday topics"},
    2: {"label": "Elementary",   "words": 250,  "complexity": "simple vocabulary, clear structure, common topics"},
    3: {"label": "Intermediate", "words": 400,  "complexity": "varied vocabulary, medium sentences, informative topics"},
    4: {"label": "Advanced",     "words": 600,  "complexity": "rich vocabulary, complex sentences, academic topics"},
    5: {"label": "Expert",       "words": 900,  "complexity": "sophisticated vocabulary, dense argumentation, specialized topics"},
}

# ─────────────────────────────────────────
# LANGUAGE SETTINGS
# ─────────────────────────────────────────
LANGUAGE_CONFIG = {
    'English': {'name': 'English',  'rtl': False, 'font': None},
    'French':  {'name': 'French',   'rtl': False, 'font': None},
    'Hebrew':  {'name': 'Hebrew',   'rtl': True,  'font': 'Frank Ruhl Libre'},
    'Arabic':  {'name': 'Arabic',   'rtl': True,  'font': 'Noto Sans Arabic'},
    'Spanish': {'name': 'Spanish',  'rtl': False, 'font': None},
    'German':  {'name': 'German',   'rtl': False, 'font': None},
}
# ─────────────────────────────────────────
# 1. GENERATE TEXT
# ─────────────────────────────────────────
def generate_text(subject_name, difficulty_level, language='English', word_count=None):
    config   = DIFFICULTY_CONFIG.get(difficulty_level, DIFFICULTY_CONFIG[1])
    words    = word_count if word_count else config['words']
    lang_cfg = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG['English'])

    prompt = f"""
    You are an expert educational content writer.
    Write a reading text for a speed reading training app.

    Subject: {subject_name}
    Difficulty level: {config['label']}
    Target word count: approximately {words} words
    Language complexity: {config['complexity']}
    Language: Write ENTIRELY in {lang_cfg['name']}. Every single word must be in {lang_cfg['name']}.

    Rules:
    - The text must be informative, engaging, and factually correct.
    - It must have a clear title.
    - It must be written in clear paragraphs.
    - Do NOT use bullet points or numbered lists.
    - Do NOT include any introduction like "Here is a text about...".
    - Write ONLY the title and the text itself, entirely in {lang_cfg['name']}.

    Respond in this exact JSON format:
    {{
        "title": "the title in {lang_cfg['name']}",
        "content": "the full text content in {lang_cfg['name']}"
    }}
    """

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)



# ─────────────────────────────────────────
# 2. GENERATE QUIZ
# ─────────────────────────────────────────
def generate_quiz(text_title, text_content, difficulty_level, language='English'):
    config    = DIFFICULTY_CONFIG.get(difficulty_level, DIFFICULTY_CONFIG[1])
    lang_cfg  = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG['English'])
    num_questions = min(3 + difficulty_level, 7)

    prompt = f"""
    You are an expert educator creating comprehension questions.
    Based on the following text, create {num_questions} multiple choice questions
    to test the reader's understanding.

    Text title: {text_title}
    Difficulty level: {config['label']}
    Language: Write ALL questions and answers ENTIRELY in {lang_cfg['name']}.

    Text:
    {text_content}

    Rules:
    - Questions must test UNDERSTANDING, not just memory.
    - Each question must have exactly 4 choices (A, B, C, D).
    - Only ONE choice must be correct.
    - Wrong choices must be plausible but clearly incorrect.
    - Questions and all answers must be written entirely in {lang_cfg['name']}.

    Respond ONLY in this exact JSON format, no extra text:
    [
        {{
            "question": "the question in {lang_cfg['name']}",
            "choice_a": "first option in {lang_cfg['name']}",
            "choice_b": "second option in {lang_cfg['name']}",
            "choice_c": "third option in {lang_cfg['name']}",
            "choice_d": "fourth option in {lang_cfg['name']}",
            "correct_choice": "A"
        }}
    ]
    """

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ─────────────────────────────────────────
# 3. GENERATE TEXT + QUIZ TOGETHER
# ─────────────────────────────────────────
def generate_text_and_quiz(subject_name, difficulty_level, language='English', word_count=None):
    text_data = generate_text(subject_name, difficulty_level, language, word_count)
    quiz_data = generate_quiz(
        text_data["title"],
        text_data["content"],
        difficulty_level,
        language
    )
    return {
        "title":   text_data["title"],
        "content": text_data["content"],
        "quiz":    quiz_data,
    }