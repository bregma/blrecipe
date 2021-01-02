"""
Submodule to handle printing a recipe
"""
import re
import string
from sys import exit
from ..storage import Database, Item, ItemName, ResourceTag


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


def _spark_column_wikitext(quantity):
    """
    Return a spark column in wikitext format
    """
    if quantity.spark:
        return "| spark {} = {} ".format(quantity.display_name,
                                         quantity.spark)
    return ''


def _wear_column_wikitext(quantity):
    """
    Return a wear column in wikitext format
    """
    if quantity.wear:
        return "| wear {} = {} ".format(quantity.display_name,
                                        quantity.wear)
    return ''


def _time_column_wikitext(quantity):
    """
    Return a time column in wikitext format
    """
    if quantity.duration:
        return "| time {} = {} ".format(quantity.display_name,
                                        _format_time(quantity.duration))
    return ''


def format_recipe_wiki(recipe):
    """
    Format the recipe for WIKI
    """
    wiki_text = '{{RecipeBox\n'
    wiki_text += '| name = {}\n'.format(recipe.item.name())
    ingredients = {}
    for ingredient in recipe.ingredients:
        try:
            ingredients[ingredient.item][ingredient.quantity] = ingredient.amount
        except KeyError:
            ingredients[ingredient.item] = {ingredient.quantity: ingredient.amount}

    icount = 1
    for ingredient in ingredients:
        wiki_text += "| ingredient{} = {}".format(icount, ingredient.name())
        sorted_quant = sorted(ingredients[ingredient].items())
        for quantity in sorted_quant:
            wiki_text += " | ingredient{} {} = {}".format(icount,
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
            spark_row += _spark_column_wikitext(quantity)
        if quantity.wear:
            wear_row += _wear_column_wikitext(quantity)
        if quantity.duration:
            time_row += _time_column_wikitext(quantity)
        produces_row += "| produces {} = {} ".format(quantity.display_name, quantity.produces)
    wiki_text += '{}\n'.format(spark_row) if len(spark_row) > 0 else ''
    wiki_text += '{}\n'.format(wear_row) if len(wear_row) > 0 else ''
    wiki_text += '{}\n'.format(time_row) if len(time_row) > 0 else ''
    wiki_text += '{}\n'.format(produces_row) if len(produces_row) > 0 else ''
    wiki_text += '| power = {}\n'.format(recipe.power) if recipe.power else ''
    if recipe.attribute:
        wiki_text += '| skill = {}'.format(recipe.attribute)
        if recipe.attribute_level:
            wiki_text += ' | skill level = {}'.format(recipe.attribute_level)
        wiki_text += '\n'
    if recipe.machine:
        wiki_text += '| machine = {}\n'.format(recipe.machine.display_name)
    wiki_text += '}}'
    return wiki_text


def format_furnace_recipe_wiki(recipe):
    """
    Format the furnace recipe for WIKI
    """
    wiki_text = '{{FurnaceRecipe\n'
    wiki_text += '| name = {}\n'.format(recipe.item.name())
    icount = 1
    for ingredient in recipe.ingredients:
        if ingredient.quantity.quantity_id == 0:
            wiki_text += "| ingredient{} = {}".format(icount, ingredient.name())
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

def make_cap(string):
    """Splits an underscore-separated string into a capitalized string"""
    return string.capwords(string.lower().replace('_', ' '))


def _repl_style(matches):
    if matches.group(2) == '1':
        return '{{{{Highlight|{}}}}}'.format(matches.group(1))
    else:
        return matches.group(0)

STYLE_REGEX = re.compile(r'\$\[STYLE\((?P<target>[^,]*),(?P<style>[^)])\)\]')

def _do_styling(text):
    return re.sub(STYLE_REGEX, _repl_style, text)


def get_item_info(item, tags):
    """
    Gets translated information related to the item.
    """
    item_info = {}

    item_info['name'] = item.name()
    item_info['class'] = item.subtitle()
    item_info['description'] = _do_styling(item.description)
    item_info['prestige'] = item.prestige
    item_info['mine_xp'] = item.mine_xp
    item_info['build_xp'] = item.build_xp
    item_info['coin_value'] = item.coin_value
    item_info['list_type'] = item.list_type
    item_info['uses'] = item.uses
    if tags is not None:
        item_info['found_altitude'] = make_cap(tags.found_altitude)
        item_info['found_depth'] = make_cap(tags.found_depth)
        item_info['found_material'] = make_cap(tags.found_material)
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
    try:
        if item_info['craft_xp'] > 0:
            infobox += '| craftXP = {}\n'.format(item_info['craft_xp'])
    except KeyError:
        pass
    if item_info['build_xp'] > 0:
        infobox += '| buildXP = {}\n'.format(item_info['build_xp'])
    if item_info['coin_value'] > 0:
        infobox += '| coin_value = {}\n'.format(item_info['coin_value'])
    try:
        if item_info['found_altitude']:
            infobox += '| found_altitude = {}\n'.format(item_info['found_altitude'])
        if item_info['found_depth']:
            infobox += '| found_depth = {}\n'.format(item_info['found_depth'])
        if item_info['found_material']:
            infobox += '| found_material = {}\n'.format(item_info['found_material'])
    except KeyError:
        pass
    if item_info['list_type']:
        infobox += '| list_type = {}\n'.format(item_info['list_type'])
    infobox += '}}\n'
    return infobox


def print_categories_wiki(item_info, recipe):
    """
    Prints some categories at the end
    """
    print('<noinclude>')
    if item_info['list_type']:
        print('[[Category:{}]]'.format(item_info['list_type']))
    if item_info['class']:
        print('[[Category:{}]]'.format(item_info['class']))
    if recipe and recipe.machine:
        print('[[Category:{} Crafted Items]]'.format(recipe.machine.display_name))
    print('</noinclude>')


def _format_uses_wiki(item_info):
    """
    Print the Used In wiki text.
    """
    wikitext = ''
    uses = item_info['uses']
    if len(uses) > 0:
        wikitext = '{{Used In|\n'
        for use in uses:
            wikitext += '* {{{{ItemLink|{}}}}}\n'.format(use)
        wikitext += '}}\n'
    return wikitext


def print_recipe(args):
    """
    Print the recipe
    """
    if args.verbose > 0:
        print('recipe for "{}"'.format(args.item_name))

    database = Database()
    session = database.session()

    target_item = session.query(ItemName).filter_by(lang="english", name=args.item_name).first()
    if target_item is None:
        print('no item matches "{}"'.format(args.item_name))
        exit(1)

    if args.verbose > 0:
        print('==> item {} ({})'.format(target_item.item_id, target_item.name))

    recipe_boxes = []
    items = session.query(Item).filter_by(id=target_item.item_id)
    if items.count() > 0:
        item = min(items, key=lambda i: len(i.name()))
        tags = session.query(ResourceTag).filter_by(string_id=item.string_id).first()
        item_info = get_item_info(item, tags)
        final_recipe = None
        for recipe in item.recipes:
            if recipe.machine and recipe.machine.name == 'FURNACE':
                recipe_boxes.append(format_furnace_recipe_wiki(recipe))
            else:
                recipe_boxes.append(format_recipe_wiki(recipe))
            item_info['craft_xp'] = recipe.experience
            final_recipe = recipe

        if args.print_infobox:
            print('<noinclude>{{Version|249}}</noinclude>')
            print(_format_infobox_wiki(item_info), end='')
        for recipe in recipe_boxes:
            print(recipe)
        if args.print_infobox:
            print(_format_uses_wiki(item_info), end='')
            print_categories_wiki(item_info, final_recipe)
