"
" Strings
"

" bart 2 strings
syn region bartId   start=+'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=bartBytesEscape,bartBytesEscapeError,bartUniEscape,bartUniEscapeError,bartIdQuote,@Spell
syn region bartString   start=+"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=bartBytesEscape,bartBytesEscapeError,bartUniEscape,bartUniEscapeError,@Spell

syn match bartBytesEscape       +\\[abfnrtv'"\\]+ display contained
syn match bartBytesEscape       "\\\o\o\=\o\=" display contained
syn match bartBytesEscapeError  "\\\o\{,2}[89]" display contained
syn match bartBytesEscape       "\\x\x\{2}" display contained
syn match bartBytesEscapeError  "\\x\x\=\X" display contained
syn match bartBytesEscape       "\\$"

syn match bartUniEscape         "\\u\x\{4}" display contained
syn match bartUniEscapeError    "\\u\x\{,3}\X" display contained
syn match bartUniEscape         "\\U\x\{8}" display contained
syn match bartUniEscapeError    "\\U\x\{,7}\X" display contained
syn match bartUniEscape         "\\N{[A-Z ]\+}" display contained
syn match bartUniEscapeError    "\\N{[^A-Z ]\+}" display contained

syn match bartIdQuote +'+ display contained

syn keyword bartConditional   if elif else
syn keyword bartDef define return

"
" Comments
"

syn match   bartComment	"#.*$" display contains=@Spell

command -nargs=+ HiLink hi link <args>


HiLink bartComment          Comment
HiLink bartId           Identifier
HiLink bartString       String
HiLink bartIdQuote   Comment
HiLink bartConditional      Conditional
HiLink bartDef Statement
