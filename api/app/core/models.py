from django.db import models

class Text(models.Model):
    text_id = models.AutoField(primary_key=True)
    text_name = models.CharField(max_length=255)
    data_genre = models.CharField(max_length=100, blank=True, null=True)
    text_genre = models.CharField(max_length=100, blank=True, null=True)
    text_date = models.CharField(max_length=50, blank=True, null=True)
    source = models.URLField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text_name

class Speaker(models.Model):
    speaker_id = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    birthyear = models.PositiveIntegerField(blank=True, null=True)
    variety = models.CharField(max_length=50, blank=True, null=True)
    education = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    l1 = models.CharField(max_length=50, blank=True, null=True)
    l2 = models.CharField(max_length=50, blank=True, null=True)
    l3 = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.speaker_id} ({self.full_name})"

class Sentence(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE, related_name='sentences')
    sentence_id = models.PositiveIntegerField()
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True, related_name='sentences')

    def _build_text(self, attr):
        tokens = list(self.tokens.all())
        if not tokens:
            return ""

        words = []
        for token in tokens:
            word = getattr(token, attr, '') or ''
            if word in {'.', ',', '!', '?', ';', ':'} and words:
                words[-1] += word
            else:
                words.append(word)

        return ' '.join(words).strip()

    def source_full_text(self):
        return self._build_text('source')

    def diplomatic_full_text(self):
        return self._build_text('diplomatic')

    def __str__(self):
        return f"Sentence {self.sentence_id} in {self.text.text_name}"


    class Meta:
        unique_together = ('text', 'sentence_id')

class Token(models.Model):
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='tokens')
    ud_id = models.PositiveIntegerField()
    source = models.CharField(max_length=255, blank=True, null=True)
    diplomatic = models.CharField(max_length=255, blank=True, null=True)
    lemma = models.CharField(max_length=255, blank=True, null=True)
    ud_type_pos = models.CharField(max_length=50, blank=True, null=True)
    pos_tag = models.CharField(max_length=50, blank=True, null=True)
    ud_valency = models.CharField(max_length=255, blank=True, null=True)
    pos_tag2 = models.CharField(max_length=50, blank=True, null=True)
    ud_type = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Token {self.ud_id} in Sentence {self.sentence.sentence_id}"

    class Meta:
        unique_together = ('sentence', 'ud_id')
        ordering = ['sentence', 'ud_id']