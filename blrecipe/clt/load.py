"""
Submodule to handle new file loads
"""
import json
import os
import msgpack
from ..storage import Database, Translation, Item, Quantity
from ..storage import AttrBundle, AttrBundleGroup, AttrConstant, AttrModifier, AttrArchetype
from ..storage import Recipe, RecipeQuantity, Machine, Ingredient
from ..storage import ResourceTag
from sqlalchemy.exc import IntegrityError


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
        if self._args.verbose > 0:
            print('-=*=- loading translations -=*=-')
        self._find_and_process_file('english.json', self._load_translation)
        self._find_and_process_file('english.msgpack', self._load_packed_translation)
        if self._args.verbose > 0:
            print('-=*=- loading attributes -=*=-')
        self._find_and_process_file('attributes.msgpack', self._load_attributes)
        if self._args.verbose > 0:
            print('-=*=- loading resource tags -=*=-')
        self._find_and_process_file('resourcetags.json', self._load_resourcetags)
        if self._args.verbose > 0:
            print('-=*=- loading items -=*=-')
        self._find_and_process_file('compileditems.msgpack', self._load_itemlist)
        if self._args.verbose > 0:
            print('-=*=- loading blocks -=*=-')
        self._find_and_process_file('compiledblocks.msgpack', self._load_blocks)
        if self._args.verbose > 0:
            print('-=*=- loading recipes -=*=-')
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

    def _load_packed_translation(self, filename):
        """
        Load the translations file into the translations table
        """
        translations = unpack(filename)
        for key, value in translations.items():
            if isinstance(value, str):
                self._session.add(Translation(string_id=key, value=value, lang='en'))
                try:
                    self._session.commit()
                except IntegrityError:
                    self._session.rollback()
                    if self._args.verbose > 0:
                        print('.. duplicate translation key: {}'.format(key))

    def _load_attributes(self, filename):
        """
        Translate and load the attributes msgpack
        """
        attributes = unpack(filename)
        self._load_attr_constant(attributes['constants'])
        self._load_attr_modifier(attributes['modifiers'])
        self._load_attr_bundle(attributes['bundles'])
        self._load_attr_archetype(attributes['archetypes'])

    def _load_attr_constant(self, constants):
        """
        Load the attribute msgpack constants section
        """
        for name, value in constants.items():
            if self._args.verbose:
                print('processing constant "{}"'.format(name))
            self._session.add(AttrConstant(name=name, value=value))
        self._session.commit()

    def _load_attr_modifier(self, modifiers):
        """
        Load the attribute msgpack modifiers section
        """
        for name, value in modifiers.items():
            if self._args.verbose:
                print('processing modifier "{}"'.format(name))
            self._session.add(AttrModifier(name=name, **value))
        self._session.commit()

    def _load_attr_bundle(self, bundles):
        """
        Load the attribute msgpack bundles section
        """
        for name, attrs in bundles.items():
            if self._args.verbose:
                print('processing bundle "{}"'.format(name))
            self._session.add(AttrBundle(name=name, **attrs))
        for name, attrs in bundles.items():
            bundle = self._session.query(AttrBundle).filter_by(name=name).first()
            if 'bundles' in attrs:
                for sub in attrs['bundles']:
                    if self._args.verbose:
                        print('processing bundle group "{}" for {}'.format(sub, bundle.name))
                    subbundle = self._session.query(AttrBundle).filter_by(name=sub).first()
                    bundle.bundleGroup.append(AttrBundleGroup(bundle_id=bundle.id,
                                                              subbundle_id=subbundle.id))
            if 'modifiers' in attrs:
                for mod in attrs['modifiers']:
                    if self._args.verbose:
                        print('processing modifier "{}" for {}'.format(mod, bundle.name))
                    modifier = self._session.query(AttrModifier).filter_by(name=mod).first()
                    bundle.modifier = modifier
        self._session.commit()

    def _load_attr_archetype(self, archetypes):
        """
        Load the attribute msgpack archetypes section
        """
        for target, arches in archetypes.items():
            if self._args.verbose:
                print('processing archetype "{}"'.format(target))
            for name, attrs in arches['attributes'].items():
                self._session.add(AttrArchetype(target=target, name=name, **attrs))
        self._session.commit()

    def _load_resourcetags(self, filename):
        """
        Load the resource tags file into the resourcetag table
        """
        with open(filename) as tfile:
            rtags = json.loads(tfile.read())
            for key, value in rtags.items():
                self._session.add(ResourceTag(string_id=key,
                                              found_altitude=value['foundAltitude'],
                                              found_depth=value['foundDepth'],
                                              found_material=value['foundMaterial'])
                                 )
        self._session.commit()

    def _load_itemlist(self, filename):
        """
        Load the compiled items JSON
        """
        itemlist = unpack(filename)
        for key, item in itemlist.items():
            if self._args.verbose:
                print('adding item"{}"'.format(item['name']))
            itemrec = Item(id=key,
                           name=item['name'],
                           string_id=item['stringID'],
                           coin_value=item['coinValue'],
                           list_type_id=item['listTypeName'])
            self._session.add(itemrec)
        self._session.commit()

    def _load_blocks(self, filename):
        """
        Load the blocks JSON
        """
        contents = unpack(filename)
        blocks = contents['BlockTypesData']
        for block in blocks:
            if block is None:
                continue
            block_id = block['id']
            items = self._session.query(Item).filter_by(id=block_id).all()
            if len(items) == 0:
                print('no item matches block id "{}"'.format(block_id))
            try:
                item = items[0]
                if self._args.verbose:
                    print('processing block "{}"'.format(item.display_name))
                item.prestige = block['prestige']
                item.build_xp = block['buildXP']
                item.mine_xp = block['mineXP']
            except IndexError:
                if self._args.verbose:
                    print('no item for block id={}'.format(block_id))

        self._session.commit()

    def _load_recipes(self, filename):
        """
        Load the recipes JSON
        """
        for recipe in unpack(filename)['recipes']:
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
                rquant = RecipeQuantity(new_recipe, self.quantities[i])
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
                for req in prereqs:
                    new_recipe.attribute = req['attribute'].rpartition(' Level')[0]
                    new_recipe.attribute_level = req['level']
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
