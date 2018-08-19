from .tile import *


@register.function(name='generic.do_nothing', system='all', attr='all')
def do_nothing(self, *args, **kwargs):
    """何もしません。

    actionやon_selfなどで、何か関数を指定しなければいけないが
    特にさせたい処理がない場合は、この関数を指定してください。

    """
    pass


@register.function(name='generic.return_true', system='all', attr='all')
def return_true(self, *args, **kwargs):
    """Trueを返します。

    is_publicのように、TrueかFalseを返す関数が求められることがあります。
    この関数は必ずTrueを返します。is_publicに指定したならば、そのタイルは通行可能なタイルとなるでしょう。

    """
    return True


@register.function(name='generic.return_false', system='all', attr='all')
def return_false(self, *args, **kwargs):
    """Falseを返します。

    is_publicのように、TrueかFalseを返す関数が求められることがあります。
    この関数は必ずFalseを返します。is_publicに指定したならば、そのタイルは通行できなくなります。

    """
    return False
