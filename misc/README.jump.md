@document

# jump

`jump` is a templating language for Python.

@eval
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
@end eval

@toc

## language basics

A `jump` template consists of plain text, expressions, or "echoes", enclosed in `{}` and "commands", or statements, which start with a `@`. Lines starting with `@#` are considered comments and ignored.

@xmp
    @# test                     -- this is a comment
    @let foo = 0                -- this is a command
    <h1>{@include header}</h1>  -- this is an inline command
    Hello, {person.name}        -- this is an echo
@end xmp

A command always starts with a word, and there should be no whitespace after a `@`. If `@` occurs elsewhere, it's not special. `{{` is only special if followed by a non-whitespace, other occurrences are not special.  In "parsed" positions, `@`, `{{` and `}}` can be escaped by doubling them:

@example
    @@escaped command

    no need to escape some@email

    this is {{escaped}}

    no need to escape { this }
@end example

You can easily change the delimiters `@` and `{{}}` to something else (see "options" below).

### commands

Commands can start on a new line, like in Python, or inline, mixed with plain text:

@example
    @# line command
    @print 'Quark'

    @# inline command
    <h1>{@print 'Rom'}</h1>
@end example


"Block" commands, like `if` or `for`, can span across multiple lines and are closed with `@end`, optionally followed by the command name:

@xmp
    @if enemy
        red alert
        lock phasers
    @end if

    all hands {@if enemy} to battlestations {@else} dismissed {@end}
@end xmp

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

@xmp
    a + b, a+b                 - ok
    a+ b                       - not ok
    -a + 1                     - ok
    - a + 1                    - not ok
    foo(*a, **kw, bar=1)       - ok
    foo(* a, ** kw, bar = 1)   - not ok
    fun(11),  lst[12]          - ok
    fun (11), lst [12]         - not ok
@end xmp

Names (identifiers) in expressions can reference python builtins, arguments (passed to the template) or local variables (defined in the template). Dot syntax `object.property` picks an object attribute or a dict key:

@example
    @# built-in
    @print len('hi')

    @# arguments
    {alert} alert, all hands {personnel.status}

    @# local variable
    @let names = ['Jadzia' 'Julian' 'Kira']
    @print names|spaces

    ARGS = {
        'alert': 'yellow',
        'personnel': {
            'status': 'standby',
        }
    }
@end example


### echoes

Echoes are expressions enclosed in `{}`. When rendering a template, `jump` replaces an echo with its value.

@example
    {person.name.first}'s debt = {person.income - sum(person.expenses)}

    ARGS = {
        'person': {
            'name': {'first': 'Quark'},
            'income': 400,
            'expenses': [100, 200, 300],
        }
    }
@end example

An echo expression can be followed by a Python format specifier, starting with a `:` or a `!`:

@example
    {amount:,} strips = {amount/20 :.5f} bars

    ARGS = {'amount': 123456.7}
@end example


### filters

The pipe operator `|` runs an expression through a "filter". In the simplest case, a filter is just a function name (predefined or defined in the template).

@example
    <h1> {title | html} </h1>

    ARGS = {'title': 'Profit & Lace'}
@end example

A filter can be also a function call, in which case the expression is injected as its first argument.

@example
    @print couple | str.replace('Jadzia', 'Ezri')

    ARGS = {'couple': 'Jadzia & Worf'}
@end example

Filters can be chained:

@example
    @print people | sort | commas | upper

    ARGS = {'people': ['Quark', 'Miles', 'Julian', 'Kira']}
@end example

Any built-in or locally defined function can act as a filter:

@example
    @def mirror x = ''.join(reversed(x))

    {'quark' | len}
    {'quark' | mirror}
@end example

With the option `filter` you can define the default filter, which is applied to all echoes, unless they are marked as `safe`:

@example
    @option filter = 'html'

    <h1>{title}</h1>

    <h2>{sub}</h2>

    {body | safe}

    ARGS = {
        'title': 'Rocks & Shoals',
        'sub': 'Episode <2>',
        'body': '<b>Garak</b> and <b>Keevan</b>',
    }
@end example


### built-in filters

`jump` comes with a set of built-in filters:

filter|input|output
---|---|---
{@filter} as_int     == {40 + ("2" | as_int)}  {@end filter}
{@filter} as_float   == {40 + ("2e5" | as_float)}  {@end filter}
{@filter} as_str     == {bytes.fromhex('66c3bcc39f6368656e') | as_str}  {@end filter}
{@filter} commas     == {['no' 'funny' 'stuff'] | commas}  {@end filter}
{@filter} cut        == {'yoknapatawpha' | cut(3, ' etc.')}  {@end filter}
{@filter} h          == {'<b>hi</b>' | h}  {@end filter}
{@filter} html       == {'<b>hi</b>' | html}  {@end filter}
{@filter} join       == {[11 22 33] | join(':')}  {@end filter}
{@filter} json       == {'füßchen' | json}  {@end filter}
{@filter} lines      == {'one \n two \n three' | lines(strip=True) | join('=')}  {@end filter}
{@filter} linkify    == {'see http://google.com' | linkify(target='_blank')}  {@end filter}
{@filter} lower      == {'HELLO' | lower}  {@end filter}
{@filter} nl2br      == {'one\ntwo\nthree' | nl2br}  {@end filter}
{@filter} shorten    == {'yoknapatawpha' | shorten(6, '...')}  {@end filter}
{@filter} sort       == {'QUARK' | sort | join}  {@end filter}
{@filter} spaces     == {['no' 'funny' 'stuff'] | spaces}  {@end filter}
{@filter} split      == {'1/2/3' | split('/') | join('.')}  {@end filter}
{@filter} strip      == <{' xyz ' | strip}>  {@end filter}
{@filter} titlecase  == {'hi there' | titlecase}  {@end filter}
{@filter} unhtml     == {'&lt;b&gt;' | unhtml}  {@end filter}
{@filter} upper      == {'hello' | upper}  {@end filter}




## control structures

### if

Conditional output. The syntax is

@xmp
    @if expression
        text
    @elif expression
        text
    @elif expression
        text
    @else
        text
    @end
@end xmp

`elif` and `else` are optional.

@example
    @if race == 'human'
        Hello
    @elif race == 'klingon'
        Qapla
    @end

    ARGS = {'race': 'klingon'}
@end example

### for

Loop construct.

@xmp
    @for variables in expression
        text
    @end
@end xmp

An extra clause `index someVariable` stores the loop index (1-based) in a variable. An extra clause `length someVariable` stores the overall length of the iterable. If two loop variables are given and the loop expression happens to be a dict, its `items` are iterated automatically. An optional `else` block is rendered when a loop expression is empty:

@example
    @for name, friends in people index num length total

        Member {num} of {total}: {name}

        @for f in friends
            - friend {f}
        @else
            - no friends!
        @end
    @end

    ARGS = {
        'people': {
            'Kira': ['Odo'],
            'Jadzia': ['Julian', 'Worf'],
            'Quark': None,
        }
    }
@end example

`break` and `continue` are also supported:

@example
    @for number in '12345678'
        @if number == '3'
            @continue
        @elif number == '6'
            @break
        @else
            {number}
        @end
    @end
@end example

### with/without

Conditionally renders a block if the expression is not "empty" (undefined, whitespace-only string, an empty list or dict). A complex expression can be aliased with `as variable`. An optional `else` block is rendered for empty expressions. Undefined variables and properties in the `with` expression are considered "empty" and no error is raised:

@example
    @for ship in ships
        {ship.name}
        @with ship.properties.physical.weight as w
            weight {w}
        @else
            weight unknown
        @end
    @end

    ARGS = {
        'ships': [
            {'name': 'Defiant', 'properties': {
                'physical': {'weight': 1234}
            }},
            {'name': 'Valiant'},
        ]
    }
@end example

`@without` is the same as `@with`, but the condition is inverted:

@example
    @without messages
        No messages!
    @end

    ARGS = {'messages': []}
@end example

## functions

### def

Defines a function. A function definition can be written in a block form:

@xmp
    @def name arguments
        content
    @end
@end xmp

or as an expression:

@xmp
    @def name arguments = expression
@end xmp

Parentheses around arguments are optional. Arguments can be separated by whitespace or commas. The result of a block function is its content, unless there is an explicit `@return` command. The result of an expression function is the evaluated expression.

Once defined, a function can be called as an ordinary python function, or as a single-line `@` command, or used as a filter:

@example
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
@end example

### box

Defines a "box" function. Box functions are similar to `def` functions, but can be used as block commands. When such a command is used, the content until the respective `@end` is captured, evaluated and passed as a first argument to the function:

@example
    @box header(text)
        <h1> !!! {text | strip} !!! </h1>
    @end

    @header
        Attention citizens
    @end
@end example

Box functions can accept other arguments as well:


@example
    @box header2(text className symbol)
        <h2 class="{className}"> {symbol*3} {text|strip} {symbol*3} </h2>
    @end

    @header2 'red' symbol='*'
        Stand by for an update
    @end
@end example

### mdef/mbox

"Macro" commands `mdef` and `mbox` are similar to `def` and `box`, but their arguments are passed as is, without parsing. These commands can be used to implement custom mini-languages within `jump` templates.

@example

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

@end example

### return

`@return expression` returns an expression as a result of a `def` or `box` function. If you return `None`, nothing will be rendered:

@example
    @def div a, b
        @if b == 0
            @return
        @end
        @return a / b
    @end

    @div 200 100

    @div 200 0

    @div 500 100
@end example


When used at the top level, `@return` terminates the template, discards all evaluated content so far and returns its argument to the caller:

@example
    some text...

    @if error
        @return 'no way!'
    @end

    more text...

    ARGS = {'error': True}
@end example

## variables and code

### let

Adds a new local variable. Like `@def`, can have a block form:

@xmp
    @let variable
        text
    @end
@end xmp

or an expression form:

@xmp
    @let variable = expression
    @let list of variables = list of expressions
@end xmp

@example
    @let number = 5
    @let race = 'klingon'
    @let c1 c2 = 100 200

    @let message
        {number} {race} ships detected, heading {c1}-mark-{c2}
    @end

    The message was: {message | strip}
@end example

### code

Inserts raw python code. The indentation doesn't have to match the outer level, but has to be consistent within a block. `print` emits the content to the template output. Template arguments can be accessed via the `ARGS` object, using dict or object notation.

@example
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

    ARGS = {'first': 'Quark', 'second': 'Rom' }
@end example

### import

`@import module` imports a python module into the template

@example
    @import sys

    This is python {sys.version}
@end example

## other commands


### do

`@do expression` evaluates an expression and discards the result. Useful for side effects:

@example
    @let lst = [1 2 3]

    @do lst.append(9)

    {lst | commas}
@end example

### print

`@print expression, expression...` evaluates and prints expressions:

@example
    @print 'test:', 2+2, 'should be', 10 // 2
@end example


### include

`@include path` includes another template. The path argument, unless starts with a `/`, is relative to the current template path:

@xmp
    @include sub/directory/other-template
@end xmp

Template loading can be customized by passing the `loader` option. A `loader` is a function which accepts the current template path and the include path and is expected to return a tuple `(source_text, resolved_path)`:

@xmp 'python'
    loader(template_path: str, include_path: str) -> Tuple(str, str)
@end xmp

### quote

`@quote name` returns the unparsed text until `@end name` is encountered. `name` can be omitted if there are no other `@end`s in the text.

@example
    Try this:

    @quote test
        @if expression
            {variable}
        @end
    @end test

    {@quote}{no}{escaping}{needed}{@end}
@end example

### skip

`@skip name` ignores the text until `@end name` is encountered. `name` can be omitted if there are no commands in the text.

@example
    Quark
    Julian
    @skip
        Jadzia
    @end
    Ezri
@end example

### option

`@option name = value` sets a compile-time option for this template (see "options" below):

@example
    @option filter = 'html'
    {text}

    @option filter = None
    {text}

    ARGS = {'text': 'this & that' }
@end example

## python API

### rendering

@xmp 'python'
    jump.render(text: str, args: dict = None, error: Callable = None, **options) -> Any

    jump.render_path(path: PathLike, args: dict = None, error: Callable = None, **options) -> Any
@end xmp

`render/render_path` accept a template source or a path and return the template output. The output is normally a `str`, but can also be something else if the template has a `@return` at the top level.

An optional `error` callback is invoked when a runtime error occurs in the template. The signature of the callback is

@xmp 'python'
    error(exc: Exception, source_path: str, source_lineno: int, env)
@end xmp

where `env` is the jump runtime environment object. You can use `env.print()` to emit error messages in the template output and `env.ARGS` to access the arguments. If the callback returns `True`, the template is evaluated further.

@eval
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
@end eval


### engine

The core of `jump` is its `Engine`. It provides runtime support for templates and contains the built-in filters.

You can obtain the default `Engine` object by calling `jump.engine()`. All `jump` public functions are actually methods of the default `Engine`:

@xmp 'python'
    jump.render(tpl, args)

    # is the same as

    jump.engine().render(tpl, args)
@end xmp

You can extend the default `Engine` to add new filters or commands. In this case, `render` and friends must be called as methods of your engine.

@eval
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
@end eval

### compilation

Internally, `jump` templates are compiled to python functions. The following compiler API is available:

@xmp 'python'
    jump.parse(text: str, **options) -> object

    jump.parse_path(path: PathLike, **options) -> object

    jump.translate(text: str, **options) -> str

    jump.translate_path(path: PathLike, **options) -> str

    jump.compile(text: str, **options) -> Callable

    jump.compile_path(path: PathLike, **options) -> Callable
@end xmp

`parse`, `translate` and `compile` compile the template into an AST, python source code and a function object respectively.

The signature of the compiled function is

@xmp 'python'
    template_fn(engine: jump.Engine, args: dict=None, error: Callable=None) -> Any
@end xmp

It can be invoked directly, or using the `call` shortcut:

@xmp 'python'
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

@end xmp


### options

The APIs accept a variety of options, which affect how templates are compiled:

option| | default value
---|---|---
`path` | override the default path for the template | `'<string>'`
`name` | name for the compiled function | `'_RENDER_'`
`filter` | default filter function | `None`
`loader` | template loader | `None`
`strip` | remove leading and trailing whitespace from each text line | `False`
`escapes` | a space-separated sting "escape replacement escape replacement..." | {@quote}`'@@ @ {{ { }} }'`{@end}
`comment_symbol` | a string that starts a comment | `'@#'`
`command_symbol` | a string that starts a line command | `'@'`
`inline_open_symbol` | a string that starts an inline command | `'{{@'`
`inline_close_symbol` | a string that ends an inline command | `'}'`
`inline_start_whitespace` | whether a space is allowed after the inline open symbol | `False`
`echo_open_symbol` | a string that starts an echo | `'{{'`
`echo_close_symbol` | a string that ends an echo | `'}'`
`echo_start_whitespace` | whether a space is allowed after the echo open symbol | `False`

`...symbol` options can be used to change `jump` syntax:

@eval
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
@end eval



## info

(c) 2022 Georg Barikin (https://github.com/gebrkn). MIT license.

@end