
from wx.lib.ogl import RectangleShape


class DcelRectangleShape(RectangleShape):
    """
    OGL rectangle shape with an explicit typed public tooltipText property for visualizer tooltips.
    """

    def __init__(self, width: float, height: float):
        """
        Construct a DcelRectangleShape.

        Args:
            width: Width of the rectangle in pixels.
            height: Height of the rectangle in pixels.
        """
        super().__init__(width, height)
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
