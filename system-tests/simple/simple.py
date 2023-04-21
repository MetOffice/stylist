from stylist.rule import LimitLineLength, TrailingWhitespace
from stylist.source import FilePipe, PlainText
from stylist.style import Style

txt = FilePipe(PlainText)

line_length_default = Style(LimitLineLength())
line_length_default_indent \
    = Style(LimitLineLength(ignore_leading_whitespace=True))
line_length_forty = Style(LimitLineLength(length=40))
line_length_forty_indent \
    = Style(LimitLineLength(length=40, ignore_leading_whitespace=True))
line_length_120 = Style(LimitLineLength(length=120))
line_length_120_indent = Style(LimitLineLength(length=120,
                                               ignore_leading_whitespace=True))

whitespace = Style(TrailingWhitespace())
