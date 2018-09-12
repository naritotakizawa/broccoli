"""broccoliフレームワークで使う、カスタムコンテナ型を提供する。"""
from collections import UserDict


class IndexDict(UserDict):
    """[0]のようなインデックスでのアクセスに対応した辞書。

    ゲームキャンバスを格納する辞書に便利です(次マップへの移動や、マップ名での移動に使えるため)。
    重要な注意点として、キーを数値にはしないでください。

    辞書が順序を保持する、Python3.6から使えます。
    もしかしたらOrderedDictを基にした、下位互換性のあるものに変更するかも。

    # インデックスと、キーでのアクセステスト
    >>> index_dict = IndexDict({'first': 'ファースト', 'second': 'セカンド', 'third': 'サード'})
    >>> index_dict
    {'first': 'ファースト', 'second': 'セカンド', 'third': 'サード'}
    >>> index_dict[0]
    'ファースト'
    >>> index_dict[-1]
    'サード'
    >>> index_dict[100]
    Traceback (most recent call last):
    ...
    IndexError: list index out of range
    >>> index_dict['first']
    'ファースト'
    >>> index_dict['nothing_key']
    Traceback (most recent call last):
    ...
    KeyError: 'nothing_key'

    # あるキーの値を書き換えるテスト
    >>> index_dict['second'] = 'two'
    >>> index_dict['second']
    'two'
    >>> index_dict[1]
    'two'
    >>> index_dict
    {'first': 'ファースト', 'second': 'two', 'third': 'サード'}
    >>> index_dict.get_key_from_index(1)
    'second'
    >>> index_dict.get_index_from_key('third')
    2

    # インデックスとキーでの削除テスト
    >>> del index_dict[0]
    >>> index_dict
    {'second': 'two', 'third': 'サード'}
    >>> del index_dict['second']
    >>> index_dict
    {'third': 'サード'}

    # 新しいキーで値を追加した場合のテスト
    >>> index_dict['four'] = 'フォー'
    >>> index_dict
    {'third': 'サード', 'four': 'フォー'}
    >>> index_dict[1]
    'フォー'
    >>> index_dict.get_key_from_index(-1)
    'four'
    >>> index_dict.get_index_from_key('four')
    1

    # あるインデックスの値を書き換えるテスト
    >>> index_dict[0] = 'ファースト'
    >>> index_dict
    {'third': 'ファースト', 'four': 'フォー'}
    >>> index_dict[0]
    'ファースト'
    >>> index_dict.get_key_from_index(0)
    'third'
    >>> index_dict.get_index_from_key('third')
    0

    """

    def __getitem__(self, item):
        if isinstance(item, int):
            values = list(self.data.values())
            return values[item]
        else:
            return self.data[item]

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self.get_key_from_index(key)
        self.data[key] = value

    def __delitem__(self, key):
        if isinstance(key, int):
            key = self.get_key_from_index(key)
        del self.data[key]

    def get_key_from_index(self, index):
        """その位置にあるkeyを返す。"""
        dict_keys = list(self.data.keys())
        return dict_keys[index]

    def get_index_from_key(self, key):
        """そのキーのインデックスを返す。"""
        dict_keys = list(self.data.keys())
        return dict_keys.index(key)
