
from django.contrib import admin
from .models import Text, Speaker, Sentence, Token

admin.site.site_header = "Balcan Corpus Admin Interface"
admin.site.site_title = "Balcan Corpus Admin Portal"
admin.site.index_title = "Welcome to Balcan Corpus Admin Panel"


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
    ordering = ['sentence_id']
    show_change_link = True

# --------- Admins ---------

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('text_id', 'source_number', 'text_name', 'data_genre', 'text_genre', 'variety', 'text_date', 'source')
    search_fields = ('text_name', 'short_description', 'source')
    list_filter = ('data_genre', 'text_genre', 'variety', 'text_date')
    filter_horizontal = ('authors',)
    inlines = [SentenceInline]
    ordering = ['text_id']

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('speaker_id', 'full_name', 'gender', 'place_of_birth', 'birthyear', 'variety', 'education', 'religion', 'l1', 'l2', 'l3')
    search_fields = ('speaker_id', 'full_name', 'place_of_birth', 'variety', 'education', 'religion', 'l1', 'l2', 'l3')
    list_filter = ('gender', 'variety', 'education', 'religion', 'l1', 'l2', 'l3')
    ordering = ['speaker_id']

@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'sentence_id', 'speaker')
    search_fields = ('text__text_name', 'speaker__full_name', 'sentence_id')
    list_filter = ('text', 'speaker')
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
    list_filter = (
        'ud_pos', 'pos_tag', 'ud_type',
        'sentence__text', 'sentence__speaker'
    )
    ordering = ['sentence', 'ud_id']

