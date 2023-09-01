"""
Base class of charactors. Each charactor should have its own file, the file
contains the charactor class, talent class, talent card class, skill classes.
DO NOT implement status, summons, weapons, artifacts, etc. in this file, which
will break the import loop.
"""


from typing import List, Literal, Any
from ..consts import (
    ELEMENT_TO_DIE_COLOR, DamageElementalType, DamageType, ObjectType, 
    SkillType, WeaponType, ElementType, FactionType, 
    ObjectPositionType, CostLabels
)
from ..object_base import (
    ObjectBase, WeaponBase, CardBase
)
from ..struct import Cost, ObjectPosition
from ..modifiable_values import DamageValue
from ..status import CharactorStatus
from ..card.equipment.artifact import Artifacts
from ..action import (
    ChargeAction, CombatActionAction, MakeDamageAction, MoveObjectAction, 
    RemoveObjectAction, Actions
)


class SkillBase(ObjectBase):
    """
    Base class of skills.
    """
    name: str
    desc: str
    type: Literal[ObjectType.SKILL] = ObjectType.SKILL
    skill_type: SkillType
    damage_type: DamageElementalType
    damage: int
    cost: Cost
    cost_label: int
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        # set cost label into cost
        self.cost.label = self.cost_label
        # based on charactor id, calculate skill id.

    def is_valid(self, match: Any) -> bool:
        """
        Check if the skill can be used.
        """
        return True

    def get_actions(self, match: Any) -> List[Actions]:
        """
        The skill is triggered, and get actions of the skill.
        By default, it will generate three actions:
        1. MakeDamageAction to attack the enemy active charactor with damage
            `self.damage` and damage type `self.damage_type`.
        2. ChargeAction to charge the active charactor by 1.
        3. SkillEndAction to declare skill end, and trigger the event.
        """
        target_table = match.player_tables[1 - self.position.player_idx]
        target_charactor_idx = target_table.active_charactor_idx
        target_charactor = target_table.charactors[target_charactor_idx]
        return [
            ChargeAction(
                player_idx = self.position.player_idx,
                charactor_idx = self.position.charactor_idx,
                charge = 1,
            ),
            MakeDamageAction(
                source_player_idx = self.position.player_idx,
                target_player_idx = 1 - self.position.player_idx,
                damage_value_list = [
                    DamageValue(
                        position = self.position,
                        damage_type = DamageType.DAMAGE,
                        target_position = target_charactor.position,
                        damage = self.damage,
                        damage_elemental_type = self.damage_type,
                        charge_cost = 0,
                    )
                ],
                charactor_change_rule = 'NONE'
            ),
        ]


class PhysicalNormalAttackBase(SkillBase):
    """
    Base class of physical normal attacks.
    """
    desc: str = """Deals 2 Physical DMG."""
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    damage: int = 2
    cost_label: int = CostLabels.NORMAL_ATTACK.value

    @staticmethod
    def get_cost(element: ElementType) -> Cost:
        return Cost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 1,
            any_dice_number = 2,
        )


class ElementalNormalAttackBase(SkillBase):
    """
    Base class of elemental normal attacks.
    """
    desc: str = """Deals 1 _ELEMENT_ DMG."""
    skill_type: Literal[SkillType.NORMAL_ATTACK] = SkillType.NORMAL_ATTACK
    damage_type: DamageElementalType
    damage: int = 1
    cost_label: int = CostLabels.NORMAL_ATTACK.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())

    @staticmethod
    def get_cost(element: ElementType) -> Cost:
        return Cost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 1,
            any_dice_number = 2,
        )


class ElementalSkillBase(SkillBase):
    """
    Base class of elemental skills.
    """
    desc: str = """Deals 3 _ELEMENT_ DMG."""
    skill_type: Literal[SkillType.ELEMENTAL_SKILL] = SkillType.ELEMENTAL_SKILL
    damage_type: DamageElementalType
    damage: int = 3
    cost_label: int = CostLabels.ELEMENTAL_SKILL.value

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())

    @staticmethod
    def get_cost(element: ElementType) -> Cost:
        return Cost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = 3,
        )


class ElementalBurstBase(SkillBase):
    """
    Base class of elemental bursts.
    """
    desc: str = """Deals _DAMAGE_ _ELEMENT_ DMG."""
    skill_type: Literal[SkillType.ELEMENTAL_BURST] = SkillType.ELEMENTAL_BURST
    damage_type: DamageElementalType
    cost_label: int = CostLabels.ELEMENTAL_BURST.value

    @staticmethod
    def get_cost(element: ElementType, number: int, charge: int) -> Cost:
        return Cost(
            elemental_dice_color = ELEMENT_TO_DIE_COLOR[element],
            elemental_dice_number = number,
            charge = charge
        )

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.desc = self.desc.replace(
            '_ELEMENT_', self.damage_type.value.lower().capitalize())
        self.desc = self.desc.replace('_DAMAGE_', str(self.damage))

    def get_actions(self, match: Any) -> List[Actions]:
        """
        When using elemental burst, the charge of the active charactor will be
        reduced by `self.charge`.
        """
        actions = super().get_actions(match)
        for action in actions:
            if isinstance(action, ChargeAction):
                action.charge = -self.cost.charge
        return actions


class PassiveSkillBase(SkillBase):
    """
    Base class of passive skills.
    It has no cost and is always invalid (cannot be used).
    It has triggers to make effects.
    """
    skill_type: Literal[SkillType.PASSIVE] = SkillType.PASSIVE
    damage_type: DamageElementalType = DamageElementalType.PHYSICAL
    damage: int = 0
    cost: Cost = Cost()
    cost_label: int = 0

    def is_valid(self, match: Any) -> bool:
        """
        Passive skills are always invalid.
        """
        return False

    def get_actions(self, match: Any) -> List[Actions]:
        """
        Passive skills are always invalid, so it will return an empty list.
        """
        raise AssertionError('Try to get actions of a passive skill')
        return []


class TalentBase(CardBase):
    """
    Base class of talents. Note almost all talents are skills, and will receive
    cost decrease from other objects.
    """
    name: str
    charactor_name: str
    type: Literal[ObjectType.TALENT] = ObjectType.TALENT
    cost_label: int = CostLabels.CARD.value | CostLabels.TALENT.value

    def is_valid(self, match: Any) -> bool:
        """
        Only corresponding charactor is active charactor can equip this card.
        """
        if self.position.area != ObjectPositionType.HAND:
            # not in hand, cannot equip
            raise AssertionError('Talent is not in hand')
        table = match.player_tables[self.position.player_idx]
        return (table.charactors[table.active_charactor_idx].name
                == self.charactor_name)

    def get_targets(self, match: Any) -> List[ObjectPosition]:
        """
        For most talent cards, can quip only on active charactor, so no need
        to specify targets.
        """
        return []

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[Actions]:
        """
        Act the talent. will place it into talent area.
        When other talent is equipped, remove the old one.
        For subclasses, inherit this and add other actions (e.g. trigger
        correcponding skills)
        """
        assert target is None
        ret: List[Actions] = []
        table = match.player_tables[self.position.player_idx]
        charactor = table.charactors[table.active_charactor_idx]
        # check if need to remove current talent
        if charactor.talent is not None:
            ret.append(RemoveObjectAction(
                object_position = charactor.talent.position,
            ))
        new_position = charactor.position.set_id(self.position.id)
        ret.append(MoveObjectAction(
            object_position = self.position,
            target_position = new_position
        ))
        return ret


class SkillTalent(TalentBase):
    """
    Talents that trigger skills. They will get skill as input, which is
    saved as a private variable.
    """

    skill: SkillBase

    def is_valid(self, match: Any) -> bool:
        """
        Both TalentBase and SkillBase should be valid.
        """
        return super().is_valid(match) and self.skill.is_valid(match)

    def get_actions(
        self, target: ObjectPosition | None, match: Any
    ) -> List[Actions]:
        ret = super().get_actions(target, match)
        assert len(ret) > 0
        assert ret[-1].type == 'MOVE_OBJECT'
        self.skill.position = ret[-1].target_position
        ret += self.skill.get_actions(match)
        # use cards are quick actions, but equip talent card will use skills,
        # so should add CombatActionAction.
        ret.append(CombatActionAction(
            action_type = 'SKILL',
            position = self.skill.position
        ))
        return ret


class CharactorBase(ObjectBase):
    """
    Base class of charactors.
    """
    name: str
    desc: str
    version: str
    type: Literal[ObjectType.CHARACTOR] = ObjectType.CHARACTOR
    position: ObjectPosition = ObjectPosition(
        player_idx = -1,
        area = ObjectPositionType.INVALID,
        id = -1,
    )

    element: ElementType
    max_hp: int
    max_charge: int
    skills: List[SkillBase]

    # labels
    faction: List[FactionType]
    weapon_type: WeaponType

    # charactor status
    hp: int = 0
    charge: int = 0
    weapon: WeaponBase | None = None
    artifact: Artifacts | None = None
    talent: TalentBase | None = None
    status: List[CharactorStatus] = []
    element_application: List[ElementType] = []
    is_alive: bool = True

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.hp = self.max_hp
        old_skill_ids = [x.id for x in self.skills]
        self._init_skills()
        if len(old_skill_ids):
            new_skill_ids = [x.id for x in self.skills]
            if len(new_skill_ids) != len(old_skill_ids):
                raise AssertionError('Skill number changed after init')
            for id, skill in zip(old_skill_ids, self.skills):
                skill.id = id
                skill.position = skill.position.set_id(id)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        When position is edited, update skill positions.
        """
        super().__setattr__(name, value)
        if name == 'position':
            for skill in self.skills:
                skill.position = ObjectPosition(
                    player_idx = self.position.player_idx,
                    charactor_idx = self.position.charactor_idx,
                    area = ObjectPositionType.SKILL,
                    id = skill.id,
                )

    def _init_skills(self) -> None:
        """
        Initialize skills. It will be called in __init__.
        """
        raise NotImplementedError

    @property
    def is_defeated(self) -> bool:
        return not self.is_alive

    @property
    def is_stunned(self) -> bool:
        """
        Check if the charactor is stunned.
        """
        stun_status_names = [
            'Frozen',
            'Petrification',
            'Mist Bubble',
            'Stun',
        ]
        for status in self.status:
            if status.name in stun_status_names:
                return True
        return False

    @property
    def damage_taken(self) -> int:
        """
        Get damage taken by the charactor.
        """
        return self.max_hp - self.hp

    def get_object_lists(self) -> List[ObjectBase]:
        """
        Get all objects of the charactor, order is passive skill, weapon, 
        artifact, talent, status. For status, order is their index in status 
        list, i.e. generated time.
        """
        result: List[ObjectBase] = [self]
        for skill in self.skills:
            if skill.skill_type == SkillType.PASSIVE:
                result.append(skill)
        if self.weapon is not None:
            result.append(self.weapon)
        if self.artifact is not None:
            result.append(self.artifact)
        if self.talent is not None:
            result.append(self.talent)
        result += self.status
        return result

    def get_object(self, position: ObjectPosition) -> ObjectBase | None:
        """
        Get object by its position. If obect not exist, return None.
        """
        if position.area == ObjectPositionType.CHARACTOR_STATUS:
            for status in self.status:
                if status.id == position.id:
                    return status
            return None
        elif position.area == ObjectPositionType.SKILL:
            for skill in self.skills:
                if skill.id == position.id:
                    return skill
            raise AssertionError('Skill not found')
        else:
            assert position.area == ObjectPositionType.CHARACTOR
            if self.id == position.id:
                return self
            elif self.talent is not None and self.talent.id == position.id:
                return self.talent
            elif self.weapon is not None and self.weapon.id == position.id:
                return self.weapon
            elif self.artifact is not None and self.artifact.id == position.id:
                return self.artifact
            raise NotImplementedError('Not tested part')
            return None
