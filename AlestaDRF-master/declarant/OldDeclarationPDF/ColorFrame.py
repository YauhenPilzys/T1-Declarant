# If you use this class instead of SimpleDocTemplate you can add ColorFrame objects along
# with regular Frame objects and the ColorFrame objects will have their background colour
# rendered at the appropriate time during the document build process.
from reportlab.lib.colors import toColor
from reportlab.platypus import SimpleDocTemplate, Frame


class ColorFrameDocTemplate(SimpleDocTemplate):
    def handle_frameBegin(self, *args):
        SimpleDocTemplate.handle_frameBegin(self, *args)

        if hasattr(self.frame, 'background'):
            self.frame.drawBackground(self.canv)


# From http://blog.stacktrace.ch/post/27830893647
class ColorFrame(Frame):
    """ Extends the reportlab Frame with the ability to draw a background color. """

    def __init__(self, x1, y1, width, height, leftPadding=6, bottomPadding=6,
                 rightPadding=6, topPadding=6, id=None, showBoundary=0,
                 overlapAttachedSpace=None, _debug=None, background=None):
        Frame.__init__(self, x1, y1, width, height, leftPadding,
                       bottomPadding, rightPadding, topPadding, id, showBoundary,
                       overlapAttachedSpace, _debug)

        self.background = background

    def drawBackground(self, canv):
        color = toColor(self.background)

        canv.saveState()
        canv.setFillColor(color)
        canv.rect(
            self._x1, self._y1, self._x2 - self._x1, self._y2 - self._y1,
            stroke=0, fill=1
        )
        canv.restoreState()

    def addFromList(self, drawlist, canv):
        if self.background:
            self.drawBackground(canv)
        Frame.addFromList(self, drawlist, canv)