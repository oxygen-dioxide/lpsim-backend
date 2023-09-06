from typing import Any, List, Literal

from ...action import Actions, CreateObjectAction
from ...struct import Cost, ObjectPosition

from ...consts import (
    DamageElementalType, DieColor, ElementType, FactionType, 
    ObjectPositionType, WeaponType
)
from ..charactor_base import (
    ElementalBurstBase, ElementalSkillBase, 
    PhysicalNormalAttackBase, CharactorBase, SkillTalent
)


# Skills


class FantasticVoyage(ElementalBurstBase):
    name: Literal['Fantastic Voyage'] = 'Fantastic Voyage'
    desc: str = '''Deals 2 Pyro DMG, creates 1 Inspiration Field.'''
    damage: int = 2
    damage_type: DamageElementalType = DamageElementalType.PYRO
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Attack and create object
        """
        charactor = match.player_tables[self.position.player_idx].charactors[
            self.position.charactor_idx]
        position = ObjectPosition(
            player_idx = self.position.player_idx,
            area = ObjectPositionType.TEAM_STATUS,
            id = -1
        )
        return super().get_actions(match) + [
            CreateObjectAction(
                object_name = 'Inspiration Field',
                object_position = position,
                object_arguments = {
                    'talent_activated': charactor.talent is not None
                }
            )
        ]


# Talents


class GrandExpectation(SkillTalent):
    name: Literal['Grand Expectation']
    desc: str = (
        'Combat Action: When your active character is Bennett, equip this '
        'card. After Bennett equips this card, immediately use Fantastic '
        'Voyage once. When your Bennett, who has this card equipped, creates '
        'an Inspiration Field, its DMG Bonus is now always active and will no '
        'longer have an HP restriction.'
    )
    version: Literal['3.3'] = '3.3'
    charactor_name: Literal['Bennett'] = 'Bennett'
    cost: Cost = Cost(
        elemental_dice_color = DieColor.PYRO,
        elemental_dice_number = 4,
        charge = 2
    )
    skill: FantasticVoyage = FantasticVoyage()


# charactor base


class Bennett(CharactorBase):
    name: Literal['Bennett']
    version: Literal['3.3'] = '3.3'
    desc: str = '''"Trial by Fire" Bennett'''
    element: ElementType = ElementType.PYRO
    max_hp: int = 10
    max_charge: int = 2
    skills: List[
        PhysicalNormalAttackBase | ElementalSkillBase | FantasticVoyage
    ] = []
    faction: List[FactionType] = [
        FactionType.MONDSTADT
    ]
    weapon_type: WeaponType = WeaponType.SWORD
    talent: GrandExpectation | None = None

    def _init_skills(self) -> None:
        self.skills = [
            PhysicalNormalAttackBase(
                name = 'Strike of Fortune',
                cost = PhysicalNormalAttackBase.get_cost(self.element),
            ),
            ElementalSkillBase(
                name = 'Passion Overload',
                damage_type = DamageElementalType.PYRO,
                cost = ElementalSkillBase.get_cost(self.element),
            ),
            FantasticVoyage(),
        ]
