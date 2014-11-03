"
" Strings
"

" miter 2 strings
syn region miterId   start=+'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=miterBytesEscape,miterBytesEscapeError,miterUniEscape,miterUniEscapeError,miterIdQuote,@Spell
syn region miterString   start=+"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=miterBytesEscape,miterBytesEscapeError,miterUniEscape,miterUniEscapeError,@Spell

syn match miterBytesEscape       +\\[abfnrtv'"\\]+ display contained
syn match miterBytesEscape       "\\\o\o\=\o\=" display contained
syn match miterBytesEscapeError  "\\\o\{,2}[89]" display contained
syn match miterBytesEscape       "\\x\x\{2}" display contained
syn match miterBytesEscapeError  "\\x\x\=\X" display contained
syn match miterBytesEscape       "\\$"

syn match miterUniEscape         "\\u\x\{4}" display contained
syn match miterUniEscapeError    "\\u\x\{,3}\X" display contained
syn match miterUniEscape         "\\U\x\{8}" display contained
syn match miterUniEscapeError    "\\U\x\{,7}\X" display contained
syn match miterUniEscape         "\\N{[A-Z ]\+}" display contained
syn match miterUniEscapeError    "\\N{[^A-Z ]\+}" display contained

syn match miterIdQuote +'+ display contained

syn keyword miterConditional   if elif else
syn keyword miterDef define return

"
" Comments
"

syn match   miterComment	"#.*$" display contains=@Spell

command -nargs=+ HiLink hi link <args>


HiLink miterComment          Comment
HiLink miterId           Identifier
HiLink miterString       String
HiLink miterIdQuote   Comment
HiLink miterConditional      Conditional
HiLink miterDef Statement
