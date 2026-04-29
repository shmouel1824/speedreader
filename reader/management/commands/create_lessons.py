from django.core.management.base import BaseCommand
from reader.models import Lesson

LESSONS = [
    {
        "number":   1,
        "title":    "Eliminate Subvocalization",
        "subtitle": "Stop the inner voice that slows you down",
        "icon":     "🤫",
        "theory":   """Subvocalization is the habit of silently pronouncing each word in your head as you read. Most people learned to read by sounding out words aloud, and this inner voice never went away. The problem is that your inner voice is limited to speaking speed — around 150-200 words per minute — which acts as a hard ceiling on how fast you can read.

The good news is that subvocalization is a habit, not a requirement. Your brain is fully capable of extracting meaning from text without needing to "hear" every word. Visual processing is far faster than auditory processing — your eyes can take in information much faster than your voice can speak it.

Elite speed readers have largely eliminated subvocalization, allowing them to process text at 400-1000 WPM because their comprehension comes directly from visual recognition rather than internal narration.""",

        "science":  """Neuroscience research using brain imaging has shown that subvocalization activates Broca's area — the speech production region of the brain — even during silent reading. This creates an unnecessary bottleneck.

Studies by researchers at the University of California found that readers who suppressed subvocalization showed up to 25% faster reading speeds with no significant loss in comprehension. The key insight is that the brain has two parallel pathways for language processing: the phonological route (sound-based) and the direct visual route. Training yourself to use the direct visual route bypasses the speed limitation entirely.

Research also shows that subvocalization is more pronounced with difficult text, suggesting it is used as a comprehension aid — which is why eliminating it requires building strong visual recognition skills first.""",

        "how_to":   """Here are three proven techniques to reduce subvocalization:

1. Humming or counting: While reading, hum quietly or count "1-2-3" repeatedly in your head. This occupies the speech center of your brain, making subvocalization impossible.

2. Chewing gum: The physical act of chewing occupies the motor pathways used for speech production, naturally reducing the tendency to subvocalize.

3. Speed up deliberately: Read faster than your inner voice can keep up. When words flash faster than speaking speed, the brain is forced to switch to direct visual processing. This is exactly what RSVP mode in this app trains.

4. Focus on meaning, not sound: Actively redirect your attention to the meaning and images that words evoke, rather than their sounds. Ask yourself "what does this mean?" rather than "how does this sound?""",

        "exercise": """EXERCISE: Flash Reading
In this exercise, words will flash at 300 WPM — faster than most people can subvocalize. Your inner voice cannot keep up at this speed, forcing your brain to switch to direct visual comprehension.

Focus on absorbing meaning, not sound. Do not try to pronounce the words — just let the meaning wash over you like watching a film.

Start the RSVP exercise below and try to follow the meaning without any inner voice. After 30 seconds, you will answer one simple comprehension question to verify understanding.""",
    },
    {
        "number":   2,
        "title":    "Word Chunking",
        "subtitle": "Train your eyes to grab groups of words at once",
        "icon":     "👁️",
        "theory":   """Chunking is the practice of training your eyes to fixate on groups of 2, 3, or more words simultaneously rather than moving word by word. The average reader makes 4-5 eye fixations per line of text. An expert reader makes only 1-2 fixations on the same line.

Each time your eyes stop (called a fixation), you spend about 250 milliseconds reading. Reducing fixations from 5 to 2 per line can cut reading time by 60%. The secret is that your eyes have a natural span — with training, you can learn to take in 3-5 words in a single glance.

This app's chunk mode directly trains this skill by highlighting multiple words at once, forcing your visual system to process them as a single unit.""",

        "science":  """Eye-tracking research pioneered at MIT has shown that skilled readers have significantly wider perceptual spans — the area of text they can process in a single fixation. While beginners process 1-2 words per fixation, expert readers process 3-5 words.

The brain uses a process called parallel processing to handle multiple words simultaneously. When words appear together within the visual span, the brain groups them into semantic chunks — meaning units — rather than processing individual words. This is why "the big dog" is processed as a single concept rather than three separate words.

Studies show that training with expanded chunk sizes for just 20 minutes per day produces measurable improvements in fixation span within 2 weeks.""",

        "how_to":   """To develop chunking ability:

1. Start with 2-word chunks: Practice reading pairs of words as single units. "The dog", "runs fast", "over hills" — train your eye to land between two words and capture both.

2. Use a visual anchor: Fix your gaze at the center of a chunk. Your peripheral vision handles the surrounding words automatically.

3. Gradually expand: Move from 2 to 3 to 4 words per chunk over several weeks. Never jump too fast — comprehension must be maintained.

4. Practice with this app: Use chunk sizes 2-5 in your reading sessions. Start each session at your comfort level, then push one level higher for the last few paragraphs.""",

        "exercise": """EXERCISE: Chunk Trainer
You will see groups of words highlighted simultaneously. Start with 2-word chunks and try to absorb each group as a single meaning unit — not as individual words.

Resist the urge to read word by word. Let your eyes rest in the center of each highlighted group and trust your peripheral vision to capture the edges.

After the exercise, you will answer a comprehension question. This proves that meaning is preserved even when reading in chunks.""",
    },
    {
        "number":   3,
        "title":    "Expand Your Visual Span",
        "subtitle": "Use peripheral vision to read more with each glance",
        "icon":     "🌐",
        "theory":   """Your visual field is much wider than you think. While your sharp foveal vision (the center of your visual field) covers only about 2 degrees of arc, your parafoveal vision extends to about 5 degrees on each side and can still process word shapes and meaning. Expert readers exploit this peripheral zone to preview upcoming words while their eyes are still fixated on the current word.

The goal of visual span expansion is to train your brain to extract useful reading information from a wider area of text on each fixation. This is different from chunking — instead of moving your fixation point to different groups, you are expanding how much you can process from a single fixation point.""",

        "science":  """Research by Keith Rayner at the University of California showed that readers extract different types of information from different zones of their visual field. From the foveal zone (1-2 words), readers extract full meaning. From the parafoveal zone (next 3-4 words), readers extract word length and initial letters. From the peripheral zone (further words), readers extract general structure.

Importantly, this preview information is used to prepare the brain for upcoming words — reducing processing time when the eyes finally arrive at those words. Studies showed that blocking parafoveal preview increased reading time by 10-15% even for skilled readers.""",

        "how_to":   """To expand your visual span:

1. Soft focus practice: Instead of sharply focusing on each word, practice softening your gaze so that surrounding words appear in your awareness. This is similar to "magic eye" pictures.

2. Center fixation: When reading, try to fixate on the middle of each line rather than at the beginning. Let peripheral vision handle both sides.

3. Column reading: Practice reading narrow columns (like newspaper columns) where peripheral vision can capture the entire width in one fixation.

4. Daily span training: Hold a book at arm's length and practice reading without moving your eyes — just expanding your awareness to take in more text.""",

        "exercise": """EXERCISE: Peripheral Vision Training
A series of word groups will appear. Your task is to fixate on the CENTER word only — do not move your eyes — and try to identify the words on either side using only your peripheral vision.

This directly trains the parafoveal processing that expert readers rely on. It feels difficult at first — that is normal! Your visual span expands with consistent practice.""",
    },
    {
        "number":   4,
        "title":    "Eliminate Regression",
        "subtitle": "Break the re-reading habit that wastes your time",
        "icon":     "➡️",
        "theory":   """Regression is the habit of moving your eyes backward to re-read words or sentences you have already passed. Eye-tracking studies show that average readers regress 15-20% of the time — meaning one in every five to seven word fixations is a backward movement. For a 300-word text, this could mean 50-60 unnecessary backward eye movements.

The paradox is that most regressions are unnecessary. Research shows that in the majority of cases, the meaning would have become clear if the reader had simply continued forward. The habit of regression creates a cycle of dependency — the more you allow yourself to re-read, the less your brain tries to understand on the first pass.""",

        "science":  """Studies by Rayner and Pollatsek using eye-tracking technology found that skilled readers regress only 5-10% of the time, compared to 15-25% for average readers. More importantly, when skilled readers do regress, it is almost always to clarify a genuine structural ambiguity — not simply because they lost attention.

The key finding is that regression is largely a confidence issue rather than a comprehension issue. Readers who trust their first-pass comprehension regress less and actually understand more — because their brains work harder on the initial reading when they know there is no second chance.""",

        "how_to":   """To eliminate regression:

1. Use a physical pointer: Run your finger or a pen under the line at a steady pace. Your eyes instinctively follow the pointer — and a pointer only moves forward.

2. Cover what you have read: Use a card or your hand to cover each line after you read it. This makes regression physically impossible.

3. Accept imperfect comprehension: Train yourself to tolerate some uncertainty and keep moving. In most cases, later sentences clarify earlier confusion.

4. Use this app's modes: Both the Scroll mode and the Highlight mode are designed to make regression impossible — the text moves forward automatically.""",

        "exercise": """EXERCISE: Forward-Only Reading
The highlight will move through the text at a steady pace and cannot go backward. Your task is to keep up without trying to go back.

If you miss something — keep going. Trust that the meaning will become clear. After the exercise, note how much you understood despite not being able to re-read. Most readers are surprised by how well they comprehend without regression.""",
    },
    {
        "number":   5,
        "title":    "The Preview Strategy",
        "subtitle": "Prepare your brain before reading a single word",
        "icon":     "🔭",
        "theory":   """Previewing is the practice of spending 30-60 seconds scanning a text before reading it properly. You look at the title, headings, first and last sentences of paragraphs, bold words, and any structural markers. This gives your brain a mental map of the text before you begin.

The power of previewing comes from how human memory works. When you read new information, your brain searches for existing mental hooks to attach it to. If it finds none, comprehension and retention are slower. Previewing creates those hooks in advance — so when you read the full text, your brain already knows roughly where each piece of information fits.""",

        "science":  """This technique is supported by schema theory in cognitive psychology, developed by psychologist Frederic Bartlett. A schema is a mental framework that helps organize and interpret new information. Previewing activates relevant schemas before reading, dramatically improving both speed and retention.

Research by Francis Robinson, developer of the famous SQ3R reading method, showed that students who previewed a chapter before reading it retained 40% more information than those who read straight through. More recent studies using fMRI brain imaging show that previewing activates the prefrontal cortex in preparation for incoming information — essentially pre-loading the relevant neural networks.""",

        "how_to":   """The 60-second preview method:

1. Read the title (5 seconds): What is this about? What do you already know about this topic?

2. Scan headings and subheadings (10 seconds): What are the main sections? What is the logical structure?

3. Read first sentences of paragraphs (20 seconds): The first sentence usually contains the main idea of each paragraph.

4. Read the conclusion (10 seconds): What is the final message? What did the author want you to take away?

5. Note bold/italic words (5 seconds): These are the author's own emphasis markers.

6. Form a question (10 seconds): What do you expect to learn? What question will this text answer?""",

        "exercise": """EXERCISE: Predict and Read
You will be given 45 seconds to preview a text — title, first sentences, and structure only. Then you will answer a prediction question: what do you think the main argument is?

After your prediction, you will read the full text and discover how accurate your preview was. Experienced previewers can predict with 70-80% accuracy — which means their brain is already 70-80% prepared before reading a word.""",
    },
    {
        "number":   6,
        "title":    "Active Reading",
        "subtitle": "Engage your brain as a participant, not a passenger",
        "icon":     "🧠",
        "theory":   """Active reading means engaging consciously with text rather than passively letting words wash over you. It involves asking questions, making predictions, connecting ideas, and evaluating arguments as you read. The goal is to make reading a dialogue between you and the author rather than a one-way transmission.

Paradoxically, active reading makes you both faster and more comprehending. When your brain is engaged in questioning and connecting, it processes information more efficiently and retains it far longer. Passive readers finish a page and realize they absorbed nothing — active readers finish the same page and could write a summary.""",

        "science":  """The testing effect, also called retrieval practice, is one of the most robust findings in cognitive psychology. Studies by Roediger and Karpicke at Washington University showed that self-testing during reading produces 50% better long-term retention than re-reading the same material.

The generation effect is equally powerful: information that you actively generate or predict is retained significantly better than information you passively receive. This is why making predictions before reading a paragraph dramatically improves retention of that paragraph's content.

Working memory research also shows that active engagement keeps information in working memory longer and transfers it to long-term memory more reliably.""",

        "how_to":   """Five active reading techniques:

1. The question method: Before each paragraph, ask "what will this tell me?" After each paragraph, ask "what did this tell me?"

2. Keyword extraction: As you read, mentally flag the 3-5 most important words per paragraph. This forces selective attention.

3. Margin dialogue: If reading a physical text, write brief reactions in the margins. Even "?" or "!" counts — any mark shows engagement.

4. The journalist's test: After each section, ask: Who? What? When? Where? Why? How? Can you answer all six questions?

5. Connect and contrast: Actively look for connections to things you already know. "This reminds me of...", "This contradicts what I know about...".""",

        "exercise": """EXERCISE: Keyword Hunter
As the text scrolls through in Spotlight mode, your task is to mentally identify the single most important word in each highlighted line.

Do not try to remember every word — just find the one word that carries the most meaning. This exercise trains selective attention — the foundation of active reading.

After the exercise, you will be asked to recall 5 keywords from the text. Readers who practiced the keyword method typically recall 3-4, versus 1-2 for passive readers.""",
    },
    {
        "number":   7,
        "title":    "Meta-Cognition and Flow",
        "subtitle": "Read with awareness — monitor and adjust as you go",
        "icon":     "🌊",
        "theory":   """Meta-cognition means thinking about your own thinking — in reading, it means monitoring your own comprehension as you read and adjusting your strategy when needed. Elite readers constantly ask themselves "am I understanding this?" and change speed, re-engage attention, or adjust strategy based on the answer.

Flow state in reading — the experience of deep, effortless engagement with text — is the ultimate goal. In flow, reading feels natural and fast, comprehension is high, and time passes unnoticed. Flow is not mysterious — it is the result of the right balance between challenge and skill, combined with focused attention and clear goals.""",

        "science":  """Metacognitive monitoring in reading was studied extensively by Ann Brown at the University of Illinois. Her research showed that good readers constantly evaluate their own understanding, while poor readers often do not notice when they have stopped comprehending — they just keep moving their eyes without processing.

Mihaly Csikszentmihalyi's flow theory describes the optimal experience as occurring when challenge and skill are in balance. Applied to reading, this means choosing texts that are slightly beyond your comfort zone — enough to engage attention, not so hard as to cause frustration. This is exactly why this app's adaptive difficulty system matters: it keeps you in the flow zone.""",

        "how_to":   """To develop meta-cognitive reading and achieve flow:

1. Set a clear purpose before reading: "I am reading this to find out..." A clear goal focuses attention and activates monitoring.

2. Check comprehension every paragraph: Take one second to ask "did I understand that?" If no — stop, re-read that paragraph only. If yes — continue.

3. Notice attention drift early: The moment you realize your eyes are moving but your mind is elsewhere — stop. Take a breath. Re-read the last sentence. Then continue with renewed focus.

4. Match speed to difficulty: Hard passages deserve slower reading. Easy passages can be accelerated. Adjust constantly.

5. Create reading rituals: Same time, same place, same preparation. Rituals reduce the mental startup cost of entering focus mode.""",

        "exercise": """EXERCISE: Comprehension Monitor
You will read a text at a challenging speed. Every 30 seconds, the text will pause and ask you one comprehension question. If you answer correctly — the text continues at the same speed. If you miss — the text slows slightly.

This real-time feedback loop trains metacognitive monitoring: you learn to feel when your comprehension is slipping before it becomes a problem. After 5 minutes of this exercise, most readers report a significantly heightened sense of reading awareness.""",
    },
]


class Command(BaseCommand):
    help = "Create all 7 speed reading lessons"

    def handle(self, *args, **options):
        created = 0
        for data in LESSONS:
            lesson, was_created = Lesson.objects.get_or_create(
                number=data["number"],
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Created: {lesson.icon} Lesson {lesson.number}: {lesson.title}"
                    )
                )
            else:
                self.stdout.write(
                    f"  · Exists:  {lesson.icon} Lesson {lesson.number}: {lesson.title}"
                )

        self.stdout.write("─" * 50)
        self.stdout.write(self.style.SUCCESS(f"Done! {created} new lessons created."))