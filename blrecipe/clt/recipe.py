"""
Submodule to handle printing a recipe
"""
from sys import exit
from ..storage import Database, Translation, Item


def add_parser(subparser):
    """
    Add the CLI argument parser for this submodule
    """
    parser = subparser.add_parser('recipe',
                                  help='print a recipe for a named Item')
    parser.add_argument('item_name',
                        help='name of the item')
    parser.set_defaults(func=print_recipe)


def print_recipe_wiki(recipe):
    """
    Format the recipe for WIKI
    """
    print('{{RecipeBox')
    print('| name = {}'.format(recipe.item.display_name))
    ingredients = {}
    for ingredient in recipe.ingredients:
        try:
            ingredients[ingredient.item][ingredient.quantity] = ingredient.amount
        except KeyError:
            ingredients[ingredient.item] = {ingredient.quantity: ingredient.amount}

    icount = 1
    for ingredient in ingredients:
        print("| ingredient{} = {}".format(icount, ingredient.display_name), end=' ')
        for quantity in ingredients[ingredient]:
            print("| ingredient{} {} = {}".format(icount,
                                                  quantity.name,
                                                  ingredients[ingredient][quantity]), end=' ')
        icount = icount + 1
        print('')
    for quantity in recipe.quantities:
        if quantity.spark:
            print("| spark {} = {}".format(quantity.display_name, quantity.spark), end=' ')
        if quantity.wear:
            print("| wear {} = {}".format(quantity.display_name, quantity.wear), end=' ')
        if quantity.duration:
            print("| time {} = {}".format(quantity.display_name, quantity.duration), end=' ')
        print('')
    if recipe.attribute:
        if recipe.attribute_level:
            print('| skill = {} ({})'.format(recipe.attribute, recipe.attribute_level))
        else:
            print('| skill = {}'.format(recipe.attribute))
    print('| machine = {}'.format(recipe.machine.display_name))
    print('}}')


def print_recipe(args):
    """
    Print the recipe
    """
    if args.verbose > 0:
        print('recipe for "{}"'.format(args.item_name))

    database = Database()
    session = database.session()

    item_trans = session.query(Translation).filter_by(value=args.item_name).first()
    if item_trans is None:
        print('no item matches "{}"'.format(args.item_name))
        exit(1)
    item = session.query(Item).filter_by(string_id=item_trans.string_id).first()
    for recipe in item.recipes:
        print_recipe_wiki(recipe)
