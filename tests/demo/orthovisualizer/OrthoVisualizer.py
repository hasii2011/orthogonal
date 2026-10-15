"""
Visual GUI demo application demonstrating Orthogonalization and FlowNet minimum-cost circulation.

Uses wxPython and wx.lib.ogl (Object Graphics Library) to interactively display
planar graphs, dual face nodes, vertex supply, face demands, directed angle flows,
and edge bend circulation arcs.
"""

from wx import App
from wx.lib.ogl import OGLInitialize

from tests.demo.orthovisualizer.OrthoVisualizerFrame import OrthoVisualizerFrame


def main():
    """
    Launch the Orthogonalization & FlowNet visualizer demo application.
    """
    app: App = App(False)
    OGLInitialize()
    frame: OrthoVisualizerFrame = OrthoVisualizerFrame()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()
