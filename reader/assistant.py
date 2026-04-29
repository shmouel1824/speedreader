import json
import anthropic
from difflib import SequenceMatcher
from django.conf import settings
from .models import SpeedReadingQA

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert Speed Reading Coach and cognitive scientist 
with deep knowledge of:
- Speed reading techniques (RSVP, chunking, subvocalization, regression, previewing)
- Cognitive psychology of reading (eye movements, working memory, schemas)
- Neuroscience of visual processing and language comprehension
- Evidence-based learning and memory research
- Practical exercises and training methods for reading improvement

You ONLY answer questions related to:
- Speed reading techniques and methods
- The science and psychology of reading
- Learning, memory, and comprehension strategies
- Eye movement and visual processing
- Practical advice for improving reading speed and comprehension

If a question is not related to reading, speed reading, or learning science, 
politely redirect the user back to these topics.

Format your answers with clear sections using these markers:
[THEORY] for theoretical explanation
[SCIENCE] for research and evidence  
[PRACTICE] for practical application tips
[TIP] for a quick actionable tip

Keep answers informative but concise — aim for 200-300 words per response.
Use a warm, encouraging, teacher-like tone."""


def find_similar_question(question, threshold=0.80):
    """
    Search the DB for a similar previously answered question.
    Returns (qa_object, similarity_score) or (None, 0)
    """
    all_qa = SpeedReadingQA.objects.all()
    best_match = None
    best_score = 0

    for qa in all_qa:
        score = SequenceMatcher(
            None,
            question.lower().strip(),
            qa.question.lower().strip()
        ).ratio()

        if score > best_score:
            best_score = score
            best_match = qa

    if best_score >= threshold:
        return best_match, best_score
    return None, 0


def ask_assistant(question, conversation_history=None):
    """
    Ask the speed reading assistant a question.
    First checks DB for similar questions.
    Returns dict: {
        'answer': str,
        'from_cache': bool,
        'similarity': float,
        'cached_question': str or None
    }
    """
    # ── check cache first ─────────────────────────────
    cached, similarity = find_similar_question(question)

    if cached:
        # update usage counter
        cached.times_used += 1
        cached.save()
        return {
            'answer':          cached.answer,
            'from_cache':      True,
            'similarity':      round(similarity * 100, 1),
            'cached_question': cached.question,
        }

    # ── build conversation for Claude ─────────────────
    messages = []

    if conversation_history:
        for msg in conversation_history[-6:]:  # last 6 messages for context
            messages.append({
                'role':    msg['role'],
                'content': msg['content'],
            })

    messages.append({'role': 'user', 'content': question})

    # ── call Claude API ───────────────────────────────
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    answer = response.content[0].text

    # ── save to DB ────────────────────────────────────
    SpeedReadingQA.objects.create(
        question=question,
        answer=answer,
    )

    return {
        'answer':          answer,
        'from_cache':      False,
        'similarity':      0,
        'cached_question': None,
    }