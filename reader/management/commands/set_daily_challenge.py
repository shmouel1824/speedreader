import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from reader.models import DailyChallenge, Text


class Command(BaseCommand):
    help = "Set today's daily challenge text"

    def handle(self, *args, **options):
        today = timezone.localdate()

        # check if already set
        if DailyChallenge.objects.filter(date=today).exists():
            challenge = DailyChallenge.objects.get(date=today)
            self.stdout.write(
                self.style.WARNING(
                    f"Challenge already set for today: {challenge.text.title}"
                )
            )
            return

        # pick a random text at intermediate level or above
        texts = Text.objects.filter(difficulty__gte=2)
        if not texts.exists():
            texts = Text.objects.all()

        if not texts.exists():
            self.stderr.write(self.style.ERROR("No texts in database yet!"))
            return

        text = random.choice(list(texts))

        challenge = DailyChallenge.objects.create(
            date=today,
            text=text,
        )

        self.stdout.write(self.style.SUCCESS(
            f"✓ Daily challenge set for {today}: {text.title} "
            f"({text.word_count} words, Level {text.difficulty})"
        ))