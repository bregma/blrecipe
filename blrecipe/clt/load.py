"""
Submodule to handle new file loads
"""
import json
import os
import msgpack
from ..storage import Database, Translation, Item

def add_parser(subparsers):
    """
    Add the CLI argument parser for this submodule
    """
    parser = subparsers.add_parser('load',
                                   help='load JSON files from a new release')
    parser.add_argument('-R', '--release',
                        help='game release number')
    parser.add_argument('assetdir',
                        help='root folder of the game assets')
    parser.set_defaults(func=load_file)


def msgpack_transform(keys, data):
    if isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, str):
        return str
    elif isinstance(data, list):
        return [msgpack_transform(keys, element) for element in data]
    elif isinstance(data, dict):
        return {keys[int(key)].decode('utf-8'): msgpack_transform(keys, value) for key, value in data.items()}
    return data


def unpack(filename):
    with open(filename, 'rb') as infile:
        unpacked = msgpack.unpack(infile)
        return msgpack_transform(unpacked[1], unpacked[0])


class Loader(object):

    def __init__(self, args):
        if args.verbose > 0:
            print('processing "{}"'.format(args.assetdir))
        self._db = Database()
        self._session = self._db.session()

    def load_translation(self, filename):
        """
        Load the translations file into the translations table
        """
        with open(filename) as tfile:
            translations = json.loads(tfile.read())
            for key, value in translations.items():
                if isinstance(value, str):
                    self._session.add(Translation(string_id=key, value=value, lang='en'))
        self._session.commit()

    def load_itemlist(self, filename):
        itemlist = unpack(filename)
        for key, item in itemlist.items():
            self._session.add(Item(name=item['name'], string_id=item['stringID']))
        self._session.commit()


def load_file(args):
    """
    Perform the file load
    """
    loader = Loader(args)
    for dirname, _, files in os.walk(args.assetdir):
        for filename in files:
            if filename == 'english.json':
                loader.load_translation(os.path.join(dirname, filename))
            elif filename == 'compileditems.msgpack':
                loader.load_itemlist(os.path.join(dirname, filename))
