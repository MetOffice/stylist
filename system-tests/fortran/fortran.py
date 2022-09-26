from re import compile as re_compile
from stylist.fortran import (AutoCharArrayIntent,
                             FortranCharacterset,
                             IntrinsicModule,
                             KindPattern,
                             LabelledDoExit,
                             MissingImplicit,
                             MissingIntent,
                             MissingOnly,
                             MissingPointerInit,
                             NakedImmediate)
from stylist.style import Style

bad_character = Style(FortranCharacterset())
missing_implicit = Style(MissingImplicit())
missing_implicit__everywhere = Style(MissingImplicit(require_everywhere=True))
missing_only = Style(MissingOnly())
missing_pointer_init = Style(MissingPointerInit())
wrong_kind = Style(KindPattern(integer=re_compile(r'.*_jazz'),
                               real=re_compile(r'.*_metal')))
labelled_do_exit = Style(LabelledDoExit())
missing_intent = Style(MissingIntent())
intrinsic_module = Style(IntrinsicModule())
auto_char_array_intent = Style(AutoCharArrayIntent())
naked_immediate = Style(NakedImmediate())
naked_immediate__integers = Style(NakedImmediate(reals=False))
naked_immediate__reals = Style(NakedImmediate(integers=False))
multiple = Style(FortranCharacterset(),
                 MissingImplicit(require_everywhere=True),
                 MissingPointerInit())
