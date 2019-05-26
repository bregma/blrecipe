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
    parser.add_argument('-i', '--print-infobox',
                        action='store_true',
                        help='print an infobox for the item')
    parser.add_argument('item_name',
                        help='name of the item')
    parser.set_defaults(func=print_recipe)


def _format_time(time):
    minutes = int(time / 60)
    seconds = int(time - (minutes * 60))
    return '{:d}m {:d}s'.format(minutes, seconds)


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
        sorted_quant = sorted(ingredients[ingredient].items())
        for quantity in sorted_quant:
            print("| ingredient{} {} = {}".format(icount,
                                                  quantity[0].name,
                                                  quantity[1]), end=' ')
        icount = icount + 1
        print('')
    spark_row = ''
    wear_row = ''
    time_row = ''
    produces_row = ''
    for quantity in recipe.quantities:
        if quantity.spark:
            spark_row += "| spark {} = {} ".format(quantity.display_name, quantity.spark)
        if quantity.wear:
            wear_row += "| wear {} = {} ".format(quantity.display_name, quantity.wear)
        if quantity.duration:
            time_row += "| time {} = {} ".format(quantity.display_name,
                                                 _format_time(quantity.duration))
        produces_row += "| produces {} = {} ".format(quantity.display_name, quantity.produces)
    if len(spark_row) > 0:
        print(spark_row)
    if len(wear_row) > 0:
        print(wear_row)
    if len(time_row) > 0:
        print(time_row)
    if len(produces_row) > 0:
        print(produces_row)
    if recipe.power:
        print('| power = {}'.format(recipe.power))
    if recipe.attribute:
        print('| skill = {}'.format(recipe.attribute), end='')
        if recipe.attribute_level:
            print('| skill level = {}'.format(recipe.attribute_level), end='')
        print('')
    print('| machine = {}'.format(recipe.machine.display_name))
    print('}}')


def print_infobox_wiki(session, item):
    """
    Prints an infobox for the rexipe item.
    """
    class_id = item.string_id + '_SUBTITLE'
    description_id = item.string_id + '_DESCRIPTION'

    class_string = session.query(Translation).filter_by(string_id=class_id).first()
    descr_string = session.query(Translation).filter_by(string_id=description_id).first()

    infobox = '{{Infobox\n'
    infobox += '| name = {}\n'.format(item.display_name)
    infobox += '| image = {}.png\n'.format(item.display_name)
    if class_string:
        infobox += '| class = {}\n'.format(class_string.value)
    if descr_string:
        infobox += '| description = {}\n'.format(descr_string.value)
    infobox += '}}'
    print(infobox)


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
    for item in session.query(Item).filter_by(string_id=item_trans.string_id):
        if args.print_infobox:
            print_infobox_wiki(session, item)
        for recipe in item.recipes:
            print_recipe_wiki(recipe)
