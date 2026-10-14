"""
Visual GUI demo application demonstrating Doubly-Connected Edge List (DCEL) operations.

Uses wxPython and wx.lib.ogl (Object Graphics Library) to interactively display
planar graphs, directed twin half-edges, and topological updates resulting from
stepping through addNodeBetween() operations.
"""

from wx import App
from wx.lib.ogl import OGLInitialize

from tests.demo.dcelvisualizer.VisualizerFrame import VisualizerFrame


def main():
    """
    Launch the DCEL visualizer demo application.
    """
    app: App = App(False)
    OGLInitialize()
    frame: VisualizerFrame = VisualizerFrame()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()
