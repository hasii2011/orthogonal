
from wx.lib.ogl import CircleShape


class VertexShape(CircleShape):
    """
    OGL circle shape representing a DCEL graph vertex, with an explicit typed tooltipText property.
    """

    def __init__(self, diameter: float):
        """
        Construct a VertexShape.

        Args:
            diameter: Diameter of the circle in pixels.
        """
        super().__init__(diameter)
        self._tooltipText: str = ''

    @property
    def tooltipText(self) -> str:
        """
        Get the tooltip text for this shape.

        Returns:
            The tooltip text string.
        """
        return self._tooltipText

    @tooltipText.setter
    def tooltipText(self, tooltipText: str):
        """
        Set the tooltip text for this shape.

        Args:
            tooltipText: The tooltip text string.
        """
        self._tooltipText = tooltipText
