"""
Submodule to handle new file loads
"""
import json
import os
import msgpack
from ..storage import Database, Translation, Item, Quantity
from ..storage import Recipe, RecipeQuantity, Machine, Ingredient


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
    """
    Transform the msgpack data into useful Python data.
    """
    if isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, list):
        return [msgpack_transform(keys, element) for element in data]
    elif isinstance(data, dict):
        return {keys[int(key)].decode('utf-8'): msgpack_transform(keys, value)
                for key, value in data.items()}
    return data


def unpack(filename):
    """
    Open and unpack a named msgpack file.
    """
    with open(filename, 'rb') as infile:
        unpacked = msgpack.unpack(infile)
        return msgpack_transform(unpacked[1], unpacked[0])


def _handcraft_from_recipe(recipe):
    return recipe['canHandCraft'] if 'canHandCraft' in recipe else None


class Loader(object):  # pylint: disable=too-few-public-methods
    """
    Wrap the stateful loading of game files into the database.
    """

    def __init__(self, args):
        if args.verbose > 0:
            print('processing "{}"'.format(args.assetdir))
        self._args = args
        self._db = Database()
        self._session = self._db.session()

        self.quantities = self._session.query(Quantity)[:]
        self.machines = {machine.name: machine for machine in self._session.query(Machine)}

    def load_files(self):
        """
        Performs the actual load of various game files to the database.
        """
        self._find_and_process_file('english.json', self._load_translation)
        self._find_and_process_file('compileditems.msgpack', self._load_itemlist)
        self._find_and_process_file('compiledblocks.msgpack', self._load_blocks)
        self._find_and_process_file('recipes.msgpack', self._load_recipes)

    def _find_and_process_file(self, target_filename, handler):
        """
        Find a named file and hand it off to a processor function
        """
        for dirname, _, files in os.walk(self._args.assetdir):
            for filename in files:
                if filename == target_filename:
                    handler(os.path.join(dirname, filename))
                    return
        print('{} not found'.format(target_filename))

    def _load_translation(self, filename):
        """
        Load the translations file into the translations table
        """
        with open(filename) as tfile:
            translations = json.loads(tfile.read())
            for key, value in translations.items():
                if isinstance(value, str):
                    self._session.add(Translation(string_id=key, value=value, lang='en'))
        self._session.commit()

    def _load_itemlist(self, filename):
        """
        Load the compiled items JSON
        """
        itemlist = unpack(filename)
        for key, item in itemlist.items():
            self._session.add(Item(id=key, name=item['name'], string_id=item['stringID']))
        self._session.commit()

    def _load_blocks(self, filename):
        """
        Load the blocks JSON
        """
        pass

    def _load_recipes(self, filename):
        """
        Load the recipes JSON
        """
        contents = unpack(filename)
        recipes = contents['recipes']
        for recipe in recipes:
            output_item = recipe['outputItem']
            item = self._session.query(Item).filter_by(id=output_item).first()
            if item is None:
                print('item "{}" not found'.format(output_item))
                continue

            new_recipe = Recipe(experience=recipe['craftXP'] if 'craftXP' in recipe else None,
                                heat=recipe['heat'] if 'heat' in recipe else None,
                                power=recipe['power'] if 'power' in recipe else None,
                                handcraftable=_handcraft_from_recipe(recipe))
            if 'machine' in recipe:
                new_recipe.machine = self.machines[recipe['machine']]
            item.recipes.append(new_recipe)

            for i, amount in enumerate(recipe['outputQuantity']):
                rquant = RecipeQuantity()
                rquant.recipe = new_recipe
                rquant.quantity = self.quantities[i]
                rquant.spark = recipe['spark'][i]
                rquant.wear = recipe['wear'][i]
                rquant.duration = recipe['duration'][i]
                rquant.produces = amount

            inputs = recipe['inputs']
            if inputs:
                for recipe_input in inputs:
                    item = self._session.query(Item)\
                            .filter_by(id=recipe_input['inputItems'][0])\
                            .first()
                    print('  "{}"'.format(item))
                    for i, amount in enumerate(recipe_input['inputQuantity']):
                        ringr = Ingredient()
                        ringr.recipe = new_recipe
                        ringr.item = item
                        ringr.quantity = self.quantities[i]
                        ringr.amount = amount

            try:
                new_recipe.power = recipe['powerRequired']
            except KeyError:
                if self._args.verbose:
                    print('  item {} missing power'.format(item.name))

            try:
                prereqs = recipe['prerequisites']
                if prereqs:
                    for req in prereqs:
                        skill = req['attribute'].rpartition(' Level')[0]
                        level = req['level']
                        new_recipe.attribute = skill
                        new_recipe.attribute_level = level
            except KeyError:
                if self._args.verbose:
                    print('  item {} missing prereqs'.format(item.name))

            self._session.commit()
            print('{}'.format(new_recipe))


def load_file(args):
    """
    Perform the file load
    """
    loader = Loader(args)
    loader.load_files()
