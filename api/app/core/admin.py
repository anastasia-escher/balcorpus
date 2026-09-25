
from django.contrib import admin
from .models import Text, Speaker, Sentence, Token

admin.site.site_header = "Balkan Corpus Admin Interface"
admin.site.site_title = "Balkan Corpus Admin Portal"
admin.site.index_title = "Welcome to Balkan Corpus Admin Panel"


# --------- Inlines ---------

class TokenInline(admin.TabularInline):
    model = Token
    extra = 0
    fields = [
        'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos', 'pos_tag',
        'pos_ext', 'head_ud_id', 'ud_type', 'time'
    ]
    ordering = ['ud_id']
    show_change_link = True

class SentenceInline(admin.TabularInline):
    model = Sentence
    extra = 0
    fields = ['sentence_id', 'speaker']
    # A text has over a thousand sentences; a dropdown of every speaker on
    # each of them would make the page unusably slow.
    raw_id_fields = ['speaker']
    ordering = ['sentence_id']
    show_change_link = True

# --------- Admins ---------

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('text_id', 'text_name', 'data_genre', 'text_genre', 'variety', 'text_date', 'source')
    search_fields = ('text_name', 'short_description', 'source')
    list_filter = ('data_genre', 'text_genre', 'variety', 'text_date')
    filter_horizontal = ('authors',)
    inlines = [SentenceInline]
    ordering = ['text_id']

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('speaker_id', 'full_name', 'gender', 'birthyear', 'place_of_birth',
                    'municipality', 'dialect_region', 'education_level', 'religion', 'l1', 'l2', 'l3',
                    'show_metadata')
    search_fields = ('speaker_id', 'full_name', 'birth_name', 'place_of_birth',
                     'municipality', 'notes')
    list_filter = ('gender', 'place_type', 'dialect_region', 'education_level', 'religion', 'l1',
                   'show_metadata')
    ordering = ['speaker_id']

@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'sentence_id', 'speaker')
    search_fields = ('text__text_name', 'speaker__full_name', 'sentence_id')
    list_filter = ('text', 'speaker')
    raw_id_fields = ('text', 'speaker')
    list_select_related = ('text', 'speaker')
    ordering = ['text', 'sentence_id']
    inlines = [TokenInline]

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sentence', 'ud_id', 'source', 'diplomatic', 'lemma', 'ud_pos',
        'pos_tag', 'pos_ext', 'head_ud_id', 'ud_type', 'time'
    )
    search_fields = (
        'sentence__text__text_name', 'sentence__sentence_id', 'source', 'diplomatic',
        'lemma', 'ud_pos', 'pos_tag', 'pos_ext', 'ud_type'
    )
    # pos_tag is left out of the filters: it has hundreds of values, and
    # listing them means reading every token on each page load.
    list_filter = (
        'ud_pos', 'ud_type',
        'sentence__text', 'sentence__speaker'
    )
    # Without these, each row's sentence would be fetched on its own, and
    # the edit form would list every sentence of the corpus in a dropdown.
    raw_id_fields = ('sentence',)
    list_select_related = ('sentence__text',)
    ordering = ['sentence', 'ud_id']

