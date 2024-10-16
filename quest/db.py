import json
import os
from .model import Quest, Adventure, Bundle
from typing import List
import sqlite3
db_path = os.path.expanduser("~/.config/quest/quest.db")
con = sqlite3.connect(db_path)


def init_quest(con):
    cur = con.cursor()
    cur.execute("CREATE TABLE quest(id, name, url, data, headers, method)")
    cur.execute("CREATE TABLE adventure(id, name)")
    cur.execute("CREATE TABLE adventure_quest(adventure_id, quest_id)")
    cur.execute("CREATE TABLE bundle(id, version, items)")
    cur.execute("CREATE TABLE adventure_bundle(adventure_id, bundle_id)")

def is_quest_initiated(con):
    cur = con.cursor()
    try:
        cur.execute('select * from quest')
        return True
    except sqlite3.OperationalError:
        return False


if not is_quest_initiated(con):
    print('init db')
    init_quest(con)


def create_adventure(con, adventure: Adventure):
    cur = con.cursor()
    sql = '''
    INSERT INTO adventure VALUES (?, ?)
    '''
    con.execute(sql, (adventure.id, adventure.name))
    con.commit()


def add_quest_to_adventure(con, adventure: Adventure, quest: Quest):
    cur = con.cursor()
    sql = '''
    INSERT INTO adventure_quest VALUES (?, ?)
    '''
    con.execute(sql, (adventure.id, quest.id))
    con.commit()


def get_quest_from_row(row) -> Quest:
    return Quest(
        id=row[0],
        name=row[1],
        url=row[2],
        data=json.loads(row[3]),
        headers=json.loads(row[4]),
        method=row[5]
    )


def get_quest_by_id(con, id: str) -> Quest:
    cur = con.cursor()
    res = cur.execute(
        '''
        SELECT id, name, url, data, headers, method
        FROM quest
        WHERE id = ?
        ''',
        (id,)
    )
    row = res.fetchone()
    return get_quest_from_row(row)


def get_adventure_quests(con, adventure: Adventure):
    cur = con.cursor()
    sql = '''
    SELECT adventure_id, quest_id
    FROM adventure_quest
    WHERE adventure_id = ?
    '''

    rows = cur.execute(sql, (adventure.id,))
    return [get_quest_by_id(con, row[1]) for row in rows]


def get_adventures(con) -> List[Adventure]:
    cur = con.cursor()
    sql = '''
    SELECT id, name
    FROM adventure
    '''
    res = con.execute(sql)
    rows = res.fetchall()
    adventures = [Adventure(id=row[0], name=row[1]) for row in rows]
    for adventure in adventures:
        adventure.quests = get_adventure_quests(con, adventure)
        adventure.bundle = get_bundle(con, adventure)
    return adventures


def get_adventure_by_name(con, name) -> Adventure:
    for adventure in get_adventures(con):
        if adventure.name == name:
            return adventure


def create_quest(con, quest: Quest):
    cur = con.cursor()
    sql = '''
    INSERT INTO quest (id, name, url, data, headers, method)
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    cur.execute(sql, (quest.id, quest.name, quest.url, json.dumps(quest.data), json.dumps(quest.headers), quest.method))
    con.commit()


def delete_quest(con, quest: Quest):
    cur = con.cursor()
    sql = '''
    DELETE FROM quest WHERE id = ?
    '''
    cur.execute(sql, (quest.id,))
    con.commit()


def update_quest(con, quest: Quest):
    cur = con.cursor()
    sql = '''
    UPDATE quest
    SET name = ?, url = ?, data = ?, headers = ?, method = ? 
    WHERE id = ?
    '''
    cur.execute(sql, (quest.name, quest.url, json.dumps(quest.data), json.dumps(quest.headers), quest.method, quest.id))
    con.commit()


def list_quests(con) -> List[Quest]:
    cur = con.cursor()
    res = cur.execute(
        '''
        SELECT id, name, url, data, headers, method
        FROM quest
        '''
    )
    rows = res.fetchall()
    return [
        Quest(
            id=row[0],
            name=row[1],
            url=row[2],
            data=json.loads(row[3]),
            headers=json.loads(row[4]),
            method=row[5]
        ) for row in rows
    ]


def get_quest_by_name(con, adventure, name) -> Quest:
    cur = con.cursor()
    res = cur.execute(
        '''
        SELECT q.id, q.name, q.url, q.data, q.headers, q.method
        FROM quest q INNER JOIN adventure_quest aq on q.id = aq.quest_id
        WHERE (q.name = ?) AND (aq.adventure_id = ?) 
        ''',
        (name, adventure.id,)
    )
    row = res.fetchone()
    return get_quest_from_row(row)


def create_bundle(con, bundle: Bundle, adventure: Adventure):
    cur = con.cursor()
    cur.execute('''
            INSERT INTO BUNDLE VALUES (?, ?, ?)
        ''',
        (bundle.id, bundle.version, json.dumps(bundle.items))
    )
    cur.execute(
        'INSERT INTO ADVENTURE_BUNDLE VALUES (?, ?)',
        (adventure.id, bundle.id,)
    )
    con.commit()


def get_bundle(con, adventure: Adventure) -> Bundle:
    try:
        cur = con.cursor()
        res = cur.execute('SELECT BUNDLE_ID FROM ADVENTURE_BUNDLE WHERE ADVENTURE_Id = ?', (adventure.id,))
        bundle_id = res.fetchone()[0]
        res = cur.execute('SELECT ID, VERSION, ITEMS FROM BUNDLE WHERE ID = ?', (bundle_id,))
        bundle = cur.fetchone()
        bundle = Bundle(
            id=bundle[0],
            version=bundle[1],
            items=json.loads(bundle[2])
        )
        return bundle
    except Exception as e:
        print(e)
        return Bundle()


def update_bundle(con, bundle: Bundle):
    cur = con.cursor()
    cur.execute(
        'UPDATE BUNDLE SET id = ?, version = ?, items = ? WHERE ID = ?',
        (bundle.id, bundle.version, json.dumps(bundle.items), bundle.id,)
    )
    con.commit()
