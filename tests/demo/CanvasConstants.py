"""
Common visual layout, color, and font constants shared across demo canvas panels.
"""

from wx import Colour

# Canvas & General Layout
CANVAS_BACKGROUND_COLOUR: Colour = Colour(255, 255, 255)

# Node / Vertex Styling
DEFAULT_NODE_COLOUR:  Colour = Colour(96, 165, 250)
PRIMAL_VERTEX_COLOUR: Colour = Colour(96, 165, 250)
INSERTED_NODE_COLOUR: Colour = Colour(244, 63, 94)

# Borders & Neutral Tones
BORDER_LIGHT_GREY: Colour = Colour(203, 213, 225)

# Typography
VERTEX_FONT_SIZE: int = 12
