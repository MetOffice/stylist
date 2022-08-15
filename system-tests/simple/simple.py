from stylist.rule import TrailingWhitespace
from stylist.source import FilePipe, PlainText
from stylist.style import Style

txt = FilePipe(PlainText)

simple = Style(TrailingWhitespace())
