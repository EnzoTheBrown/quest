import requests
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import json
from time import time
import jinja2


class QuestModel(BaseModel):
    id: str = Field(default_factory=lambda: str(time()))
    def __str__(self):
        return json.dumps(self.dict())


class Quest(QuestModel):
    name: str
    url: str
    data: Optional[Dict] = None
    headers: Optional[Dict] = None
    method: str
    spell: Optional[str] = None


class Bundle(QuestModel):
    version: str = '0.1'
    items: Dict = {}


class Adventure(QuestModel):
    name: str
    quests: List[Quest] = []
    bundle: Bundle = Bundle()

    def call(self, quest: Quest):
        result = requests.request(
            quest.method,
            url=jinja2.Template(quest.url).render(self.bundle.items),
            data=json.loads(jinja2.Template(json.dumps(quest.data)).render(self.bundle.items)),
            headers=json.loads(jinja2.Template(json.dumps(quest.headers)).render(self.bundle.items)),
        )
        if quest.spell is not None:
            local_vars = {}
            exec(quest.spell, {}, local_vars)
            spell_function = local_vars['spell']
            self.bundle.items = {**self.bundle.items, **spell_function(result)}
        return result.content
