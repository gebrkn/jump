from . import yy


def test_ext_commands():
    class MyEng(yy.jump.Engine):
        def def_fn(self, *args):
            return f'F={"-".join(args)}'

        def box_blk(self, *args):
            return f'B={"-".join(args)}'

    t = '''
        |
        @fn 'X'  'Y'
        |
        {'aaa' | fn}
        |
        {'bbb' | fn('ccc')}
        |
        @blk
            aa
        @end
        |
        @blk 'xx' 'yy'
            bb
        @end
        |
        
    '''
    s = MyEng().render(t)
    assert yy.nows(s) == "|F=X-Y|F=aaa|F=bbb-ccc|B=aa|B=bb-xx-yy|"


def test_ext_commands_precedence():
    class MyEng(yy.jump.Engine):
        def def_fn(self, *args):
            return f'ENG_FN={"-".join(args)}'

        def box_blk(self, *args):
            return f'ENG_BLK={"-".join(args)}'

    t = '''
        |
        @fn 'X'  'Y'
        |
        @def fn *args
            USER_FN={"-".join(args)}
        @end
        |
        @fn 'X'  'Y'
        |
        @blk
            abc
        @end
        |
        @def blk *args
            USER_BLK={"-".join(args)}
        @end
        |
        @blk 'X' 'Y'
        |
    '''

    s = MyEng().render(t)
    assert yy.nows(s) == "|ENG_FN=X-Y||USER_FN=X-Y|ENG_BLK=abc||USER_BLK=X-Y|"
