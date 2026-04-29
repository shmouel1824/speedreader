import time
from django.core.management.base import BaseCommand
from reader.models import Subject, Text, Quiz
from reader.services import generate_text_and_quiz


class Command(BaseCommand):
    help = "Populate the database with AI-generated texts and quizzes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--subject",
            type=str,
            help="Subject name (e.g. 'Science')",
        )
        parser.add_argument(
            "--level",
            type=int,
            default=1,
            help="Difficulty level 1-5 (default: 1)",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=1,
            help="How many texts to generate (default: 1)",
        )

    def handle(self, *args, **options):
        subject_name = options["subject"]
        level        = options["level"]
        count        = options["count"]

        # ── validate inputs ──────────────────────────
        if not subject_name:
            self.stderr.write(self.style.ERROR("Please provide a subject with --subject"))
            return

        if level < 1 or level > 5:
            self.stderr.write(self.style.ERROR("Level must be between 1 and 5"))
            return

        # ── get or create subject ────────────────────
        subject, created = Subject.objects.get_or_create(name=subject_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new subject: {subject_name}"))
        else:
            self.stdout.write(f"Using existing subject: {subject_name}")

        # ── generate texts ───────────────────────────
        self.stdout.write(f"\nGenerating {count} text(s) at level {level}...\n")

        success_count = 0

        for i in range(count):
            self.stdout.write(f"  [{i+1}/{count}] Calling Claude API...")

            try:
                data = generate_text_and_quiz(subject_name, level)

                # ── save Text ────────────────────────
                text = Text.objects.create(
                    subject    = subject,
                    title      = data["title"],
                    content    = data["content"],
                    difficulty = level,
                )

                self.stdout.write(f"         Title   : {text.title}")
                self.stdout.write(f"         Words   : {text.word_count}")
                self.stdout.write(f"         Quiz Qs : {len(data['quiz'])}")

                # ── save Quiz questions ──────────────
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

                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"         ✓ Saved successfully!\n"))

                # ── small pause between API calls ────
                if i < count - 1:
                    time.sleep(2)

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"         ✗ Error: {e}\n"))

        # ── summary ──────────────────────────────────
        self.stdout.write("─" * 50)
        self.stdout.write(self.style.SUCCESS(
            f"Done! {success_count}/{count} texts generated and saved."
        ))