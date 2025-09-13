from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def extract_headings(stream_value):
    """
    Extract headings from StreamField content to generate table of contents
    """
    headings = []
    
    for block in stream_value:
        if block.block_type == 'heading':
            level = block.value['level']
            text = block.value['text']
            anchor = block.value.get('anchor') or text.lower().replace(' ', '-')
            
            # Clean anchor - remove special characters
            anchor = re.sub(r'[^\w\-]', '', anchor)
            
            headings.append({
                'level': level,
                'text': text,
                'anchor': anchor
            })
    
    return headings

@register.filter
def render_toc(headings):
    """
    Render table of contents HTML from extracted headings
    """
    if not headings:
        return mark_safe('')
    
    html = '<nav class="toc bg-gray-50 p-4 rounded-lg mb-8" aria-label="Table of contents">'
    html += '<h2 class="text-lg font-semibold text-gray-900 mb-3">Table of Contents</h2>'
    html += '<ul class="space-y-1">'
    
    for heading in headings:
        indent_class = 'ml-4' if heading['level'] == 'h3' else ''
        html += f'<li class="{indent_class}">'
        html += f'<a href="#{heading["anchor"]}" class="text-blue-600 hover:text-blue-800 hover:underline">'
        html += heading['text']
        html += '</a></li>'
    
    html += '</ul></nav>'
    
    return mark_safe(html)

