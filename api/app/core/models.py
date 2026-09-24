from django.db import models


class Speaker(models.Model):
    """A person whose speech or writing is recorded in the corpus.

    ``speaker_id`` is the slug that the annotation files use to refer to this
    person, for example "vasil_iljoski".  It is the key that links an
    annotation file to this table, so it must be written the same way in both.
    """

    speaker_id = models.SlugField(max_length=100, unique=True)
    # The name this person is known by, which for a writer may be a pen name.
    full_name = models.CharField(max_length=255)
    # The name on their papers, filled in only when it differs from full_name:
    # "Коле Чашуле" was born "Никола Кепев".
    birth_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    birthyear = models.PositiveIntegerField(blank=True, null=True)
    # Where the person was born, split so the data can be asked geographic
    # questions: "Brajchino", "village", "Resen".
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    place_type = models.CharField(max_length=20, blank=True, null=True)
    municipality = models.CharField(max_length=255, blank=True, null=True)
    # The dialect area the speaker comes from. Named apart from Text.variety,
    # which is a different thing: whether a text is standard or dialectal.
    dialect_region = models.CharField(max_length=100, blank=True, null=True)
    education_level = models.CharField(max_length=50, blank=True, null=True)
    education_note = models.CharField(max_length=255, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    # First, second and third language, as ISO 639-1 codes. A slot may hold
    # several codes separated by a semicolon.
    l1 = models.CharField(max_length=50, blank=True, null=True)
    l2 = models.CharField(max_length=50, blank=True, null=True)
    l3 = models.CharField(max_length=50, blank=True, null=True)
    # Remarks the source files kept inside cells meant to hold a value.
    notes = models.TextField(blank=True, null=True)
    # False keeps this person's details out of the public API: only the name,
    # gender and languages are shown. The details stay in the database.
    show_metadata = models.BooleanField(default=True)
    # Row number in the editors' spreadsheet, so a record can be checked
    # against their own copy.
    source_row = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.speaker_id})"

    class Meta:
        ordering = ['speaker_id']


class Text(models.Model):
    """One document of the corpus, together with its metadata.

    ``text_id`` is the slug shared by the metadata table and the annotation
    files, for example "vasil_iljoski_corbadji_1937".  Using it as the primary
    key means an annotation file can be attached to its text without guessing
    from the title.
    """

    text_id = models.SlugField(max_length=200, primary_key=True)
    # The running number from the editors' metadata spreadsheet ("Text_ID").
    # Kept so a row here can still be matched against their own tables.
    source_number = models.PositiveIntegerField(blank=True, null=True)
    text_name = models.CharField(max_length=255)
    data_genre = models.CharField(max_length=100, blank=True, null=True)
    text_genre = models.CharField(max_length=100, blank=True, null=True)
    # Whether the text is in the standard language or a dialect, and whatever
    # the editors wrote beside that.
    variety = models.CharField(max_length=255, blank=True, null=True)
    variety_note = models.TextField(blank=True, null=True)
    text_date = models.CharField(max_length=50, blank=True, null=True)
    # Further years, for a text published more than once.
    year_note = models.CharField(max_length=100, blank=True, null=True)
    source = models.URLField(blank=True, null=True)
    # Name of the file the editors delivered, kept as the record of where this
    # row came from.
    source_file = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Speaker, related_name='texts', blank=True)

    def __str__(self):
        return self.text_name

    class Meta:
        ordering = ['text_id']


class Sentence(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE, related_name='sentences')
    sentence_id = models.PositiveIntegerField()
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True, related_name='sentences')

    def __str__(self):
        return f"Sentence {self.sentence_id} in {self.text.text_name}"

    class Meta:
        unique_together = ('text', 'sentence_id')


class Token(models.Model):
    """One annotated word form.

    The annotation files carry two parallel tag sets: the Universal
    Dependencies one (``ud_pos``, ``pos_ext``, ``ud_type``, ``head_ud_id``) and
    the MULTEXT-East morphosyntactic description (``pos_tag``).
    """

    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='tokens')
    ud_id = models.PositiveIntegerField()
    source = models.CharField(max_length=255, blank=True, null=True)
    diplomatic = models.CharField(max_length=255, blank=True, null=True)
    lemma = models.CharField(max_length=255, blank=True, null=True)
    # Universal PoS tag, e.g. "NOUN".
    ud_pos = models.CharField(max_length=50, blank=True, null=True)
    # MULTEXT-East tag, e.g. "Ncmsnn".
    pos_tag = models.CharField(max_length=50, blank=True, null=True)
    # UD morphological features, e.g. "Case=Nom|Gender=Masc|Number=Sing".
    pos_ext = models.CharField(max_length=255, blank=True, null=True)
    # ``ud_id`` of this token's syntactic head inside the same sentence.
    # 0 means the token is the root, i.e. it has no head.
    head_ud_id = models.PositiveIntegerField(blank=True, null=True)
    # UD relation to the head, e.g. "nsubj" or the subtype "nsubj:pass".
    ud_type = models.CharField(max_length=50, blank=True, null=True)
    # Timecode in the recording; only spoken material has one.
    time = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Token {self.ud_id} in Sentence {self.sentence.sentence_id}"

    class Meta:
        unique_together = ('sentence', 'ud_id')
        ordering = ['sentence', 'ud_id']
        # The corpus is searched by these columns far more often than it is
        # written to, so each one gets its own index.
        indexes = [
            models.Index(fields=['lemma']),
            models.Index(fields=['pos_tag']),
            models.Index(fields=['ud_type']),
            models.Index(fields=['head_ud_id']),
        ]
