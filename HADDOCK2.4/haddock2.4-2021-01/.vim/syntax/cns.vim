
if exists("b:current_syntax")
    finish
endif

"keywords
syn keyword cnsGlobalStatement stop abort end if then while loop inline fix flag flags else for in
syn keyword cnsGlobalStatement elseif eval evaluate fileexist set close define igroup
syn keyword cnsGlobalStatement procedure endprocedure proc endp call module
syn keyword cnsStatement coor dani delete do duplicate dyna energy fix minimize ncs noe
syn keyword cnsStatement parameter patch sani segment show structure topology write xray
syn keyword cnsStatement print xrdc vean identity

"remarks statement
syn keyword cnsRemarkStatement remarks display nextgroup=cnsRemarkLine skipwhite
syn region cnsRemarkLine start=" " end="$" contained contains=cnsRemarkVariable
"syn match cnsRemarkVariable '[&|$][a-zA-Z][a-zA-Z0-9._]\+' contained
syn match cnsRemarkVariable '[&|$][a-zA-Z][a-zA-Z0-9_-]*' contained

"@-statement
syn match cnsFileStatement "@@\?\$\?[a-zA-Z][a-zA-Z]*:\?[a-zA-Z0-9/._-]\+"

"variables
syn match cnsVariable "[&|$][a-zA-Z][a-zA-Z0-9._]*"
syn region cnsString start='"' end='"'

"booleans
syn keyword cnsBoolean true false True False TRUE FALSE
"names
syn match cnsName '[a-zA-Z][a-zA-Z0-9_]*'
"numbers
syn match cnsNumber '-\?\d\+\.\?\d*'


"comments
syn match cnsComment "!.*$"
syn region cnsCommentBlock start="{" end="}" 

"run.cns
syn match cnsDefineArrow "{===>}"

let b:current_syntax = "cns"

hi def link cnsGlobalStatement Statement
hi def link cnsStatement Statement
hi def link cnsDispStatement Statement
hi def link cnsRemarkStatement Statement

hi def link cnsDefineArrow Include
hi def link cnsFileStatement Include

hi def link cnsVariable Type
hi def link cnsRemarkVariable Type

hi def link cnsDispString String
hi def link cnsRemarkLine String
hi def link cnsString String
hi def link cnsNumber String
hi def link cnsBoolean String

hi def link cnsComment Comment
hi def link cnsCommentBlock Comment
