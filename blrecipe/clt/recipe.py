"""
Submodule to handle printing a recipe
"""
from sys import exit
from ..storage import Database, Translation, Item, i18n


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


def print_furnace_recipe_wiki(recipe):
    """
    Format the furnace recipe for WIKI
    """
    print('{{FurnaceRecipe')
    print('| name = {}'.format(recipe.item.display_name))
    icount = 1
    for ingredient in recipe.ingredients:
        if ingredient.quantity.quantity_id == 0:
            print("| ingredient{} = {}".format(icount, ingredient.display_name), end=' ')
            print("| ingredient{} required = {}".format(icount, ingredient.amount))
            icount += 1

    for quantity in recipe.quantities:
        if quantity.quantity.quantity_id == 0:
            if quantity.wear > 0:
                print('| wear = {} '.format(quantity.wear))
            if quantity.duration > 0:
                print('| time = {} '.format(_format_time(quantity.duration)))
            if quantity.produces:
                print('| produces = {} '.format(quantity.produces))
    if recipe.heat > 0:
        print('| heat = {}'.format(recipe.heat))
    if recipe.attribute:
        print('| skill = {}'.format(recipe.attribute), end='')
        if recipe.attribute_level:
            print(' | skill level = {}'.format(recipe.attribute_level), end='')
        print('')
    print('| machine = {}'.format(recipe.machine.display_name))
    print('}}')


def get_item_info(session, item):
    """
    Gets translated information related to the item.
    """
    item_info = {}

    item_info['name'] = item.display_name

    class_id = item.string_id + '_SUBTITLE'
    item_info['class'] = i18n(session, class_id)

    description_id = item.string_id + '_DESCRIPTION'
    item_info['description'] = i18n(session, description_id)
    item_info['prestige'] = item.prestige
    item_info['mine_xp'] = item.mine_xp
    item_info['build_xp'] = item.build_xp
    return item_info


def print_infobox_wiki(item_info):
    """
    Prints an infobox for the rexipe item.
    """
    infobox = '{{Infobox\n'
    infobox += '| name = {}\n'.format(item_info['name'])
    infobox += '| image = {}.png\n'.format(item_info['name'])
    if item_info['class']:
        infobox += '| class = {}\n'.format(item_info['class'])
    if item_info['description']:
        infobox += '| description = {}\n'.format(item_info['description'])
    if item_info['prestige'] > 0:
        infobox += '| prestige = {}\n'.format(item_info['prestige'])
    if item_info['mine_xp'] > 0:
        infobox += '| mineXP = {}\n'.format(item_info['mine_xp'])
    if item_info['build_xp'] > 0:
        infobox += '| buildXP = {}\n'.format(item_info['build_xp'])
    infobox += '}}'
    print('<noinclude>{{Version|224}}</noinclude>')
    print(infobox)


def print_categories_wiki(item_info, recipe):
    """
    Prints some categories at the end
    """
    print('<noinclude>')
    print('[[Category:Item]]')
    print('[[Category:{}]]'.format(item_info['class']))
    if recipe:
        print('[[Category:{} Crafted Item]]'.format(recipe.machine.display_name))
    print('</noinclude>')


def print_recipe(args):
    """
    Print the recipe
    """
    if args.verbose > 0:
        print('recipe for "{}"'.format(args.item_name))

    database = Database()
    session = database.session()

    item_trans = session.query(Translation).filter_by(value=args.item_name).all()
    if item_trans is None or len(item_trans) == 0:
        print('no item matches "{}"'.format(args.item_name))
        exit(1)
    for it in item_trans:
        if args.verbose > 0:
            print('item {} ({})'.format(it.id, it.string_id))
        if it.string_id.startswith('ITEM_TYPE_'):
            for item in session.query(Item).filter_by(string_id=it.string_id):
                item_info = get_item_info(session, item)
                if args.print_infobox:
                    print_infobox_wiki(item_info)
                final_recipe = None
                for recipe in item.recipes:
                    if recipe.machine.name == 'FURNACE':
                        print_furnace_recipe_wiki(recipe)
                    else:
                        print_recipe_wiki(recipe)
                    final_recipe = recipe
                print_categories_wiki(item_info, final_recipe)
