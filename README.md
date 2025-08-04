
# jump

`jump` is a templating language for Python.

###### example:
```python
import jump

template = '''

@for user, lang in greetings
    @if lang == 'en'
        Hello, {user}!
    @elif lang == 'tlh'
        Qapla, {user}!
    @end
@end

'''

args = {
    'greetings': {
        'Jadzia': 'en',
        'Quark': 'en', 
        'Worf': 'tlh',
    }
}

print(jump.render(template, args))
```
###### output:
```
        Hello, Jadzia!
        Hello, Quark!
        Qapla, Worf!
```

## table of contents
 * [language basics](#language-basics)
     * [commands](#commands)
     * [expressions](#expressions)
     * [echoes](#echoes)
     * [filters](#filters)
     * [built-in filters](#built-in-filters)
 * [control structures](#control-structures)
     * [if](#if)
     * [for](#for)
     * [with/without](#with/without)
 * [functions](#functions)
     * [def](#def)
     * [box](#box)
     * [mdef/mbox](#mdef/mbox)
     * [return](#return)
 * [variables and code](#variables-and-code)
     * [let](#let)
     * [code](#code)
     * [import](#import)
 * [other commands](#other-commands)
     * [do](#do)
     * [print](#print)
     * [include](#include)
     * [quote](#quote)
     * [skip](#skip)
     * [option](#option)
 * [python API](#python-api)
     * [rendering](#rendering)
     * [engine](#engine)
     * [compilation](#compilation)
     * [options](#options)
 * [info](#info)
## language basics

A `jump` template consists of plain text, expressions, or "echoes", enclosed in `{}` and "commands", or statements, which start with a `@`. Lines starting with `@#` are considered comments and ignored.

```
@# test                     -- this is a comment
@let foo = 0                -- this is a command
<h1>{@include header}</h1>  -- this is an inline command
Hello, {person.name}        -- this is an echo
```

A command always starts with a word, and there should be no whitespace after a `@`. If `@` occurs elsewhere, it's not special. `{` is only special if followed by a non-whitespace, other occurrences are not special.  In "parsed" positions, `@`, `{` and `}` can be escaped by doubling them:

###### example:
```
@@escaped command

no need to escape some@email

this is {{escaped}}

no need to escape { this }
```
###### output:
```
@escaped command

no need to escape some@email

this is {escaped}

no need to escape { this }
```

You can easily change the delimiters `@` and `{}` to something else (see "options" below).

### commands

Commands can start on a new line, like in Python, or inline, mixed with plain text:

###### example:
```
@# line command
@print 'Quark'

@# inline command
<h1>{@print 'Rom'}</h1>
```
###### output:
```
Quark

<h1>Rom</h1>
```


"Block" commands, like `if` or `for`, can span across multiple lines and are closed with `@end`, optionally followed by the command name:

```
@if enemy
    red alert
    lock phasers
@end if

all hands {@if enemy} to battlestations {@else} dismissed {@end}
```

### expressions

`jump` expressions are similar to Python expressions. This is what is supported:

- names like `foo` and attributes like `foo.bar`
- strings, numbers, list and dict literals
- subscripts and slices
- arithmetic, boolean and comparison operators
- conditional operator `...if...else...`
- function calls with keyword and star arguments
- the pipe or "filter" operator `expression | function`

Commas in list/dict literals and argument lists are optional.

`jump` is picky about whitespace in expressions. Binary operators must have equal amount of whitespace on both sides, there must be no whitespace after unary `+` and `-`, no whitespace in star and keyword arguments and no whitespace before a `(` or `[` in function calls and indexes.  To put it simply, just stick to PEP8 all the time.

```
a + b, a+b                 - ok
a+ b                       - not ok
-a + 1                     - ok
- a + 1                    - not ok
foo(*a, **kw, bar=1)       - ok
foo(* a, ** kw, bar = 1)   - not ok
fun(11),  lst[12]          - ok
fun (11), lst [12]         - not ok
```

Names (identifiers) in expressions can reference python builtins, arguments (passed to the template) or local variables (defined in the template). Dot syntax `object.property` picks an object attribute or a dict key:

###### example:
```
@# built-in
@print len('hi')

@# arguments
{alert} alert, all hands {personnel.status}

@# local variable
@let names = ['Jadzia' 'Julian' 'Kira']
@print names|spaces
```
###### arguments:
```
{
    'alert': 'yellow',
    'personnel': {
        'status': 'standby',
    }
}
```
###### output:
```
2

yellow alert, all hands standby

Jadzia Julian Kira
```


### echoes

Echoes are expressions enclosed in `{}`. When rendering a template, `jump` replaces an echo with its value.

###### example:
```
{person.name.first}'s debt = {person.income - sum(person.expenses)}
```
###### arguments:
```
{
    'person': {
        'name': {'first': 'Quark'},
        'income': 400,
        'expenses': [100, 200, 300],
    }
}
```
###### output:
```
Quark's debt = -200
```

An echo expression can be followed by a Python format specifier, starting with a `:` or a `!`:

###### example:
```
{amount:,} strips = {amount/20 :.5f} bars
```
###### arguments:
```
{'amount': 123456.7}
```
###### output:
```
123,456.7 strips = 6172.83500 bars
```


### filters

The pipe operator `|` runs an expression through a "filter". In the simplest case, a filter is just a function name (predefined or defined in the template).

###### example:
```
<h1> {title | html} </h1>
```
###### arguments:
```
{'title': 'Profit & Lace'}
```
###### output:
```
<h1> Profit &amp; Lace </h1>
```

A filter can be also a function call, in which case the expression is injected as its first argument.

###### example:
```
@print couple | str.replace('Jadzia', 'Ezri')
```
###### arguments:
```
{'couple': 'Jadzia & Worf'}
```
###### output:
```
Ezri & Worf
```

Filters can be chained:

###### example:
```
@print people | sort | commas | upper
```
###### arguments:
```
{'people': ['Quark', 'Miles', 'Julian', 'Kira']}
```
###### output:
```
JULIAN,KIRA,MILES,QUARK
```

Any built-in or locally defined function can act as a filter:

###### example:
```
@def mirror x = ''.join(reversed(x))

{'quark' | len}
{'quark' | mirror}
```
###### output:
```
5
krauq
```

With the option `filter` you can define the default filter, which is applied to all echoes, unless they are marked as `safe`:

###### example:
```
@option filter = 'html'

<h1>{title}</h1>

<h2>{sub}</h2>

{body | safe}
```
###### arguments:
```
{
    'title': 'Rocks & Shoals',
    'sub': 'Episode <2>',
    'body': '<b>Garak</b> and <b>Keevan</b>',
}
```
###### output:
```
<h1>Rocks &amp; Shoals</h1>

<h2>Episode &lt;2&gt;</h2>

<b>Garak</b> and <b>Keevan</b>
```


### built-in filters

`jump` comes with a set of built-in filters:

filter|input|output
---|---|---
`as_int` | `{40 + ("2" \| as_int)}` | `42`
`as_float` | `{40 + ("2e5" \| as_float)}` | `200040.0`
`as_str` | `{bytes.fromhex('66c3bcc39f6368656e') \| as_str}` | `füßchen`
`commas` | `{['no' 'funny' 'stuff'] \| commas}` | `no,funny,stuff`
`cut` | `{'yoknapatawpha' \| cut(3, ' etc.')}` | `yok etc.`
`h` | `{'<b>hi</b>' \| h}` | `&lt;b&gt;hi&lt;/b&gt;`
`html` | `{'<b>hi</b>' \| html}` | `&lt;b&gt;hi&lt;/b&gt;`
`join` | `{[11 22 33] \| join(':')}` | `11:22:33`
`json` | `{'füßchen' \| json}` | `"f\u00fc\u00dfchen"`
`lines` | `{'one \n two \n three' \| lines(strip=True) \| join('=')}` | `one=two=three`
`linkify` | `{'see http://google.com' \| linkify(target='_blank')}` | `see <a href="http://google.com" target="_blank">http://google.com</a>`
`lower` | `{'HELLO' \| lower}` | `hello`
`nl2br` | `{'one\ntwo\nthree' \| nl2br}` | `one<br/>two<br/>three`
`shorten` | `{'yoknapatawpha' \| shorten(6, '...')}` | `yok...pha`
`sort` | `{'QUARK' \| sort \| join}` | `AKQRU`
`spaces` | `{['no' 'funny' 'stuff'] \| spaces}` | `no funny stuff`
`split` | `{'1/2/3' \| split('/') \| join('.')}` | `1.2.3`
`strip` | `<{' xyz ' \| strip}>` | `<xyz>`
`titlecase` | `{'hi there' \| titlecase}` | `Hi There`
`unhtml` | `{'&lt;b&gt;' \| unhtml}` | `<b>`
`upper` | `{'hello' \| upper}` | `HELLO`




## control structures

### if

Conditional output. The syntax is

```
@if expression
    text
@elif expression
    text
@elif expression
    text
@else
    text
@end
```

`elif` and `else` are optional.

###### example:
```
@if race == 'human'
    Hello
@elif race == 'klingon'
    Qapla
@end
```
###### arguments:
```
{'race': 'klingon'}
```
###### output:
```
    Qapla
```

### for

Loop construct.

```
@for variables in expression
    text
@end
```

An extra clause `index someVariable` stores the loop index (1-based) in a variable. An extra clause `length someVariable` stores the overall length of the iterable. If two loop variables are given and the loop expression happens to be a dict, its `items` are iterated automatically. An optional `else` block is rendered when a loop expression is empty:

###### example:
```
@for name, friends in people index num length total

    Member {num} of {total}: {name}

    @for f in friends
        - friend {f}
    @else
        - no friends!
    @end
@end
```
###### arguments:
```
{
    'people': {
        'Kira': ['Odo'],
        'Jadzia': ['Julian', 'Worf'],
        'Quark': None,
    }
}
```
###### output:
```
    Member 1 of 3: Kira

        - friend Odo

    Member 2 of 3: Jadzia

        - friend Julian
        - friend Worf

    Member 3 of 3: Quark

        - no friends!
```

`break` and `continue` are also supported:

###### example:
```
@for number in '12345678'
    @if number == '3'
        @continue
    @elif number == '6'
        @break
    @else
        {number}
    @end
@end
```
###### output:
```
        1
        2
        4
        5
```

### with/without

Conditionally renders a block if the expression is not "empty" (undefined, whitespace-only string, an empty list or dict). A complex expression can be aliased with `as variable`. An optional `else` block is rendered for empty expressions. Undefined variables and properties in the `with` expression are considered "empty" and no error is raised:

###### example:
```
@for ship in ships
    {ship.name}
    @with ship.properties.physical.weight as w
        weight {w}
    @else
        weight unknown
    @end
@end
```
###### arguments:
```
{
    'ships': [
        {'name': 'Defiant', 'properties': {
            'physical': {'weight': 1234}
        }},
        {'name': 'Valiant'},
    ]
}
```
###### output:
```
    Defiant
        weight 1234
    Valiant
        weight unknown
```

`@without` is the same as `@with`, but the condition is inverted:

###### example:
```
@without messages
    No messages!
@end
```
###### arguments:
```
{'messages': []}
```
###### output:
```
    No messages!
```

## functions

### def

Defines a function. A function definition can be written in a block form:

```
@def name arguments
    content
@end
```

or as an expression:

```
@def name arguments = expression
```

Parentheses around arguments are optional. Arguments can be separated by whitespace or commas. The result of a block function is its content, unless there is an explicit `@return` command. The result of an expression function is the evaluated expression.

Once defined, a function can be called as an ordinary python function, or as a single-line `@` command, or used as a filter:

###### example:
```
@def square n = n * n

{42 + square(10)}

@def banner(text open close)
    {open * 3} {text} {close * 3}
@end

@banner 'red alert' open='!' close='*'

@def translate(text)
    @if text == 'Hello'
        @return 'Qapla'
    @end
@end

Worf says: {'Hello' | translate}
```
###### output:
```
142


    !!! red alert ***


Worf says: Qapla
```

### box

Defines a "box" function. Box functions are similar to `def` functions, but can be used as block commands. When such a command is used, the content until the respective `@end` is captured, evaluated and passed as a first argument to the function:

###### example:
```
@box header(text)
    <h1> !!! {text | strip} !!! </h1>
@end

@header
    Attention citizens
@end
```
###### output:
```
    <h1> !!! Attention citizens !!! </h1>
```

Box functions can accept other arguments as well:


###### example:
```
@box header2(text className symbol)
    <h2 class="{className}"> {symbol*3} {text|strip} {symbol*3} </h2>
@end

@header2 'red' symbol='*'
    Stand by for an update
@end
```
###### output:
```
    <h2 class="red"> *** Stand by for an update *** </h2>
```

### mdef/mbox

"Macro" commands `mdef` and `mbox` are similar to `def` and `box`, but their arguments are passed as is, without parsing. These commands can be used to implement custom mini-languages within `jump` templates.

###### example:
```
@# definitions

@import subprocess

@mdef bash(command)
    @print subprocess.check_output(command, shell=True) | as_str
@end

@mbox javascript(source)
    @do open('/tmp/js', 'wt').write(source)
    @print subprocess.check_output(['node', '/tmp/js']) | as_str
@end

@# usage

@bash cat /usr/share/dict/words | grep jump$ | tr -s '\n' ','

@javascript
    const lang = 'javascript'
    console.log(`hello from ${lang}`.toUpperCase())
@end javascript
```
###### output:
```
buckjump,gelandejump,jump,outjump,overjump,

HELLO FROM JAVASCRIPT
```

### return

`@return expression` returns an expression as a result of a `def` or `box` function. If you return `None`, nothing will be rendered:

###### example:
```
@def div a, b
    @if b == 0
        @return
    @end
    @return a / b
@end

@div 200 100

@div 200 0

@div 500 100
```
###### output:
```
2.0

5.0
```


When used at the top level, `@return` terminates the template, discards all evaluated content so far and returns its argument to the caller:

###### example:
```
some text...

@if error
    @return 'no way!'
@end

more text...
```
###### arguments:
```
{'error': True}
```
###### output:
```
no way!
```

## variables and code

### let

Adds a new local variable. Like `@def`, can have a block form:

```
@let variable
    text
@end
```

or an expression form:

```
@let variable = expression
@let list of variables = list of expressions
```

###### example:
```
@let number = 5
@let race = 'klingon'
@let c1 c2 = 100 200

@let message
    {number} {race} ships detected, heading {c1}-mark-{c2}
@end

The message was: {message | strip}
```
###### output:
```
The message was: 5 klingon ships detected, heading 100-mark-200
```

### code

Inserts raw python code. The indentation doesn't have to match the outer level, but has to be consistent within a block. `print` emits the content to the template output. Template arguments can be accessed via the `ARGS` object, using dict or object notation.

###### example:
```
<div>
    @code
        a = ARGS['first']
        b = ARGS.second
        if a > b:
            print(a, 'is smarter than', b)
        else:
            print(a, 'is no smarter than', b)
    @end
</div>
```
###### arguments:
```
{'first': 'Quark', 'second': 'Rom' }
```
###### output:
```
<div>
Quark is no smarter than Rom
</div>
```

### import

`@import module` imports a python module into the template

###### example:
```
@import sys

This is python {sys.version}
```
###### output:
```
This is python 3.10.13 (main, Jan 16 2024, 14:50:45) [Clang 15.0.0 (clang-1500.1.0.2.5)]
```

## other commands


### do

`@do expression` evaluates an expression and discards the result. Useful for side effects:

###### example:
```
@let lst = [1 2 3]

@do lst.append(9)

{lst | commas}
```
###### output:
```
1,2,3,9
```

### print

`@print expression, expression...` evaluates and prints expressions:

###### example:
```
@print 'test:', 2+2, 'should be', 10 // 2
```
###### output:
```
test: 4 should be 5
```


### include

`@include path` includes another template. The path argument, unless starts with a `/`, is relative to the current template path:

```
@include sub/directory/other-template
```

Template loading can be customized by passing the `loader` option. A `loader` is a function which accepts the current template path and the include path and is expected to return a tuple `(source_text, resolved_path)`:

```python
loader(template_path: str, include_path: str) -> Tuple(str, str)
```

### quote

`@quote name` returns the unparsed text until `@end name` is encountered. `name` can be omitted if there are no other `@end`s in the text.

###### example:
```
Try this:

@quote test
    @if expression
        {variable}
    @end
@end test

{@quote}{no}{escaping}{needed}{@end}
```
###### output:
```
Try this:

    @if expression
        {variable}
    @end

{no}{escaping}{needed}
```

### skip

`@skip name` ignores the text until `@end name` is encountered. `name` can be omitted if there are no commands in the text.

###### example:
```
Quark
Julian
@skip
    Jadzia
@end
Ezri
```
###### output:
```
Quark
Julian
Ezri
```

### option

`@option name = value` sets a compile-time option for this template (see "options" below):

###### example:
```
@option filter = 'html'
{text}

@option filter = None
{text}
```
###### arguments:
```
{'text': 'this & that' }
```
###### output:
```
this &amp; that

this & that
```

## python API

### rendering

```python
jump.render(text: str, args: dict = None, error: Callable = None, **options) -> Any

jump.render_path(path: PathLike, args: dict = None, error: Callable = None, **options) -> Any
```

`render/render_path` accept a template source or a path and return the template output. The output is normally a `str`, but can also be something else if the template has a `@return` at the top level.

An optional `error` callback is invoked when a runtime error occurs in the template. The signature of the callback is

```python
error(exc: Exception, source_path: str, source_lineno: int, env)
```

where `env` is the jump runtime environment object. You can use `env.print()` to emit error messages in the template output and `env.ARGS` to access the arguments. If the callback returns `True`, the template is evaluated further.

###### example:
```python
import jump

def log_error(exc, path, line, env):
    env.print('<ERROR', exc, ', count is', env.ARGS.count, end='>')
    return True

template = '''\
    first line
    undefined {foo} here
    next line
    runtime error {100 / count} here
    one more
'''

print(jump.render(template, {'count': 0}, error=log_error))
```
###### output:
```
    first line
    undefined <ERROR name 'foo' is not defined , count is 0> here
    next line
    runtime error <ERROR division by zero , count is 0> here
    one more
```


### engine

The core of `jump` is its `Engine`. It provides runtime support for templates and contains the built-in filters.

You can obtain the default `Engine` object by calling `jump.engine()`. All `jump` public functions are actually methods of the default `Engine`:

```python
jump.render(tpl, args)

# is the same as

jump.engine().render(tpl, args)
```

You can extend the default `Engine` to add new filters or commands. In this case, `render` and friends must be called as methods of your engine.

###### example:
```python
import jump

class MyEngine(jump.Engine):
    def box_my_custom_command(self, text):
        return '((( ' + text.strip() + ' )))'

template = '''
    @my_custom_command
        hey
    @end
'''

eng = MyEngine()
print(eng.render(template))
```
###### output:
```
((( hey )))
```

### compilation

Internally, `jump` templates are compiled to python functions. The following compiler API is available:

```python
jump.parse(text: str, **options) -> object

jump.parse_path(path: PathLike, **options) -> object

jump.translate(text: str, **options) -> str

jump.translate_path(path: PathLike, **options) -> str

jump.compile(text: str, **options) -> Callable

jump.compile_path(path: PathLike, **options) -> Callable
```

`parse`, `translate` and `compile` compile the template into an AST, python source code and a function object respectively.

The signature of the compiled function is

```python
template_fn(engine: jump.Engine, args: dict=None, error: Callable=None) -> Any
```

It can be invoked directly, or using the `call` shortcut:

```python
# compile once

cached_template_fn = jump.compile_path('some.template')

# invoke with the default Engine

output = cached_template_fn(jump.engine(), args, error_handler)
# or
output = jump.call(cached_template_fn, args, error_handler)

# invoke with the custom Engine

eng = MyEngine()

output = cached_template_fn(eng, args, error_handler)
# or
output = eng.call(my_template_fn, args, error_handler)
```


### options

The APIs accept a variety of options, which affect how templates are compiled:

option| | default value
---|---|---
`path` | override the default path for the template | `'<string>'`
`name` | name for the compiled function | `'_RENDER_'`
`filter` | default filter function | `None`
`loader` | template loader | `None`
`strip` | remove leading and trailing whitespace from each text line | `False`
`escapes` | a space-separated sting "escape replacement escape replacement..." | `'@@ @ {{ { }} }'`
`comment_symbol` | a string that starts a comment | `'@#'`
`command_symbol` | a string that starts a line command | `'@'`
`inline_open_symbol` | a string that starts an inline command | `'{@'`
`inline_close_symbol` | a string that ends an inline command | `'}'`
`inline_start_whitespace` | whether a space is allowed after the inline open symbol | `False`
`echo_open_symbol` | a string that starts an echo | `'{'`
`echo_close_symbol` | a string that ends an echo | `'}'`
`echo_start_whitespace` | whether a space is allowed after the echo open symbol | `False`

`...symbol` options can be used to change `jump` syntax:

###### example:
```python
alt_syntax = {
    'command_symbol': '# ',
    'echo_open_symbol': '<%=',
    'echo_close_symbol': '%>',
    'echo_start_whitespace': True,
}

template = '''
    # for name in ['Quark', 'Jadzia', 'Miles']
        Hello, <%= name %>
    # end
'''

print(jump.render(template, **alt_syntax))
```
###### output:
```
           Hello, Quark
           Hello, Jadzia
           Hello, Miles
```



## info

(c) 2022 Georg Barikin (https://github.com/gebrkn). MIT license.

