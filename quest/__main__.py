import uuid
from .model import Quest, Adventure, Bundle
from .db import (
    con, create_quest, list_quests, update_quest, create_adventure, add_quest_to_adventure,
    get_adventures, get_adventure_quests, get_adventure_by_name, get_quest_by_name,
    create_bundle, delete_quest, update_bundle
)
import time
import click


@click.group()
def quest():
    pass


@quest.group()
def adventure():
    pass


@quest.group()
def bundle():
    pass


@adventure.command('create')
@click.argument('name')
def create_adventure_(name):
    adventure = Adventure(name=name)
    create_adventure(con, adventure)


@adventure.command('get')
@click.argument('name', default='')
def get_adventure(name):
    adventure = get_adventure_by_name(con, name)
    click.echo(adventure)


@adventure.command('list')
def list_adventures():
    import json
    adventures = get_adventures(con)
    print(json.dumps([adventure.dict() for adventure in adventures]))


def option_to_dict(option: list):
    payload = {}
    for item in option:
        key, value = tuple(item.split(': '))
        payload[key] = value
    return payload


@quest.command('create')
@click.argument('method')
@click.argument('name')
@click.argument('url')
@click.argument('adventure')
@click.option('--data', '-d', multiple=True)
@click.option('--headers', '-h', multiple=True)
def quest_create(method, name, url, data, headers, adventure):
    headers = option_to_dict(headers)
    data = option_to_dict(data)
    adventure = get_adventure_by_name(con, adventure)
    quest = Quest(name=name, url=url, method=method, data=data, headers=headers)
    create_quest(con, quest)
    add_quest_to_adventure(con, adventure, quest)


@quest.command('update')
@click.argument('method')
@click.argument('name')
@click.argument('url')
@click.argument('adventure')
@click.option('--data', '-d', multiple=True)
@click.option('--headers', '-h', multiple=True)
def quest_update(method, name, url, data, headers, adventure):
    headers = option_to_dict(headers)
    data = option_to_dict(data)
    adventure = get_adventure_by_name(con, adventure)
    quest = [q for q in adventure.quests if q.name == name][0]
    quest.method = method
    quest.name = name
    quest.url = url
    quest.data = data
    quest.headers = headers
    update_quest(con, quest)


@quest.command('spell')
@click.argument('name')
@click.argument('adventure')
def create_spell(name, adventure):
    adventure = get_adventure_by_name(con, adventure)
    quest = [q for q in adventure.quests if q.name == name][0]
    spell_content = quest.spell or 'def spell(response):\n\treturn {}'
    message = click.edit(spell_content)
    quest.spell = message
    update_quest(con, quest)


@quest.command('list')
@click.argument('adventure')
def quest_list(adventure):
    adventure = get_adventure_by_name(con, adventure)
    click.echo(str(adventure))


@quest.command('delete')
@click.argument('name')
@click.argument('adventure')
def quest_delete(name, adventure):
    adventure = get_adventure_by_name(con, adventure)
    quest = [quest for quest in adventure.quests if quest.name == name][0]
    delete_quest(con, quest)


@quest.command('call')
@click.argument('name')
@click.argument('adventure')
def quest_call(name, adventure):
    adventure = get_adventure_by_name(con, adventure)
    quest = [quest for quest in adventure.quests if quest.name == name][0]
    bundle = adventure.bundle
    print(adventure.call(quest))
    update_bundle(con, bundle)


@bundle.command('create')
@click.argument('adventure')
@click.option('--items', '-i', multiple=True)
def create_bundle_(adventure, items):
    items = option_to_dict(items)
    adventure = get_adventure_by_name(con, adventure)
    bundle = Bundle(items=items)
    create_bundle(con, bundle, adventure)


@bundle.command('update')
@click.argument('adventure')
@click.option('--items', '-i', multiple=True)
def update_bundle_(adventure, items):
    items = option_to_dict(items)
    adventure = get_adventure_by_name(con, adventure)
    bundle = adventure.bundle
    bundle.items = {**bundle.items, **items}
    update_bundle(con, bundle)


if __name__ == '__main__':
    quest()
