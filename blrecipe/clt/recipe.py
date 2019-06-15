"""
Submodule to handle printing a recipe
"""
from sys import exit
from ..storage import Database, Translation, Item, Ingredient, i18n


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


def format_recipe_wiki(recipe):
    """
    Format the recipe for WIKI
    """
    wiki_text = '{{RecipeBox\n'
    wiki_text += '| name = {}\n'.format(recipe.item.display_name)
    ingredients = {}
    for ingredient in recipe.ingredients:
        try:
            ingredients[ingredient.item][ingredient.quantity] = ingredient.amount
        except KeyError:
            ingredients[ingredient.item] = {ingredient.quantity: ingredient.amount}

    icount = 1
    for ingredient in ingredients:
        wiki_text += "| ingredient{} = {}".format(icount, ingredient.display_name)
        sorted_quant = sorted(ingredients[ingredient].items())
        for quantity in sorted_quant:
            wiki_text += "| ingredient{} {} = {}".format(icount,
                                                  quantity[0].name,
                                                  quantity[1])
        icount = icount + 1
        wiki_text += '\n'
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
        wiki_text += spark_row + '\n'
    if len(wear_row) > 0:
        wiki_text += wear_row + '\n'
    if len(time_row) > 0:
        wiki_text += time_row + '\n'
    if len(produces_row) > 0:
        wiki_text += produces_row + '\n'
    if recipe.power:
        wiki_text += '| power = {}\n'.format(recipe.power)
    if recipe.attribute:
        wiki_text += '| skill = {}'.format(recipe.attribute)
        if recipe.attribute_level:
            wiki_text += '| skill level = {}'.format(recipe.attribute_level)
        wiki_text += '\n'
    wiki_text += '| machine = {}\n'.format(recipe.machine.display_name)
    wiki_text += '}}'
    return wiki_text


def format_furnace_recipe_wiki(recipe):
    """
    Format the furnace recipe for WIKI
    """
    wiki_text = '{{FurnaceRecipe\n'
    wiki_text += '| name = {}\n'.format(recipe.item.display_name)
    icount = 1
    for ingredient in recipe.ingredients:
        if ingredient.quantity.quantity_id == 0:
            wiki_text += "| ingredient{} = {}".format(icount, ingredient.display_name)
            wiki_text += "| ingredient{} required = {}\n".format(icount, ingredient.amount)
            icount += 1

    for quantity in recipe.quantities:
        if quantity.quantity.quantity_id == 0:
            if quantity.wear > 0:
                wiki_text += '| wear = {}\n'.format(quantity.wear)
            if quantity.duration > 0:
                wiki_text += '| time = {}\n'.format(_format_time(quantity.duration))
            if quantity.produces:
                wiki_text += '| produces = {}\n'.format(quantity.produces)
    if recipe.heat > 0:
        wiki_text += '| heat = {}\n'.format(recipe.heat)
    if recipe.attribute:
        wiki_text += '| skill = {}'.format(recipe.attribute)
        if recipe.attribute_level:
            wiki_text += ' | skill level = {}'.format(recipe.attribute_level)
        wiki_text += '\n'
    wiki_text += '| machine = {}\n'.format(recipe.machine.display_name)
    wiki_text += '}}'
    return wiki_text


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


def _format_infobox_wiki(item_info):
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
    try:
        if item_info['craft_xp'] > 0:
            infobox += '| craftXP = {}\n'.format(item_info['craft_xp'])
    except KeyError:
        pass
    infobox += '}}\n'
    return infobox


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


def _get_uses(session, item):
    """
    Gets a list of items for which the key item is used as a recipe ingredient.
    """
    results = session.query(Ingredient).filter_by(item_id=item.id).all()
    return sorted({use.recipe.item.display_name for use in results})


def format_uses_wiki(uses):
    """
    Prints the Uses wiki text.
    """
    wiki_text = '{{UsedIn|\n'
    for use in uses:
        wiki_text += '* {{ItemLink|{}}}\n'.format(use)
    wiki_text += '}}\n'
    return wiki_text


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
            recipe_boxes = []
            for item in session.query(Item).filter_by(string_id=it.string_id):
                item_info = get_item_info(session, item)
                uses = _get_uses(session, item)
                final_recipe = None
                for recipe in item.recipes:
                    if recipe.machine.name == 'FURNACE':
                        recipe_boxes.append(format_furnace_recipe_wiki(recipe))
                    else:
                        recipe_boxes.append(format_recipe_wiki(recipe))
                    item_info['craft_xp'] = recipe.experience
                    final_recipe = recipe

                if args.print_infobox:
                    print('<noinclude>{{Version|224}}</noinclude>')
                    print(_format_infobox_wiki(item_info))
                for recipe in recipe_boxes:
                    print(recipe)
                if len(uses) > 0:
                    print(format_uses_wiki(uses))
                if args.print_infobox:
                    print_categories_wiki(item_info, final_recipe)
