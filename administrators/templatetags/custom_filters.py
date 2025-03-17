from django import template

register = template.Library()

@register.filter
def translate_question(question, lang):
    return question.safe_translation_getter('question', language_code=lang)
