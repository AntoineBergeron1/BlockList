"""
Custom template filters for reputation score display.
Centralizes color logic to avoid duplication across templates.
"""

from django import template

register = template.Library()


@register.filter
def score_text_class(score):
    """
    Returns CSS class for reputation score text color.
    Uses custom color for medium scores to meet WCAG AA contrast requirements.
    - Green (text-success): score >= 70 (good reputation)
    - Custom gold: score >= 40 (medium reputation) - via score-warning class
    - Red (text-danger): score < 40 (bad reputation)
    """
    try:
        score = int(score)
    except (ValueError, TypeError):
        return "text-secondary"

    if score >= 70:
        return "text-success"
    elif score >= 40:
        return "score-warning"
    return "text-danger"


@register.filter
def score_bg_class(score):
    """
    Returns Bootstrap background color class based on reputation score.
    Used for progress bars and badges.
    Includes text-dark for bg-warning to ensure readability.
    - Green (bg-success): score >= 70 (good reputation)
    - Yellow (bg-warning text-dark): score >= 40 (medium reputation)
    - Red (bg-danger): score < 40 (bad reputation)
    """
    try:
        score = int(score)
    except (ValueError, TypeError):
        return "bg-secondary"

    if score >= 70:
        return "bg-success"
    elif score >= 40:
        return "bg-warning text-dark"
    return "bg-danger"
