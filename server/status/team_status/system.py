"""
Team status generated by system.
"""

from typing import Any, Literal
from .base import UsageTeamStatus
from ...modifiable_values import DamageIncreaseValue, DamageDecreaseValue
from ...consts import DamageElementalType, DamageType


class CatalyzingField(UsageTeamStatus):
    """
    Catalyzing field.
    """
    name: Literal['Catalyzing Field'] = 'Catalyzing Field'
    desc: str = (
        'When you deal Electro DMG or Pyro DMG to an opposing active '
        'charactor, DMG dealt +1.'
    )
    version: Literal['3.4'] = '3.4'
    usage: int = 2
    max_usage: int = 2

    def value_modifier_DAMAGE_INCREASE(
            self, value: DamageIncreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        Increase damage for dendro or electro damages, and decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # source not self, not activate
            return value
        if not self.position.check_position_valid(
            value.target_position, match, 
            player_idx_same = False, target_is_active_charactor = True,
        ):
            # target not enemy, or target not active charactor, not activate
            return value
        if value.damage_elemental_type in [
            DamageElementalType.DENDRO,
            DamageElementalType.ELECTRO,
        ] and self.usage > 0:
            value.damage += 1
            assert mode == 'REAL'
            self.usage -= 1
        return value


class DendroCore(UsageTeamStatus):
    """
    Dendro core.
    """
    name: Literal['Dendro Core'] = 'Dendro Core'
    desc: str = (
        'When you deal Pyro DMG or Electro DMG to an opposing active '
        'charactor, DMG dealt +2.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_DAMAGE_INCREASE(
            self, value: DamageIncreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        Increase damage for electro or pyro damages by 2, and decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match, player_idx_same = True,
        ):
            # source not self, not activate
            return value
        if not self.position.check_position_valid(
            value.target_position, match, 
            player_idx_same = False, target_is_active_charactor = True,
        ):
            # target not enemy, or target not active charactor, not activate
            return value
        if value.damage_elemental_type in [
            DamageElementalType.ELECTRO,
            DamageElementalType.PYRO,
        ] and self.usage > 0:
            value.damage += 2
            assert mode == 'REAL'
            self.usage -= 1
        return value


class Crystallize(UsageTeamStatus):
    """
    Crystallize.
    """
    name: Literal['Crystallize'] = 'Crystallize'
    desc: str = (
        'Grants 1 Shield point to your active charactor. '
        '(Can stack. Max 2 Points.)'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 2

    def value_modifier_DAMAGE_DECREASE(
            self, value: DamageDecreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageDecreaseValue:
        """
        Decrease damage by its usage, and decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if value.target_position.player_idx != self.position.player_idx:
            # attack enemy, not activate
            return value
        if value.damage_elemental_type == DamageElementalType.PIERCING:
            # piercing damage, not activate
            return value
        assert self.usage > 0
        decrease = min(self.usage, value.damage)
        value.damage -= decrease
        assert mode == 'REAL'
        self.usage -= decrease
        return value


SystemTeamStatus = CatalyzingField | DendroCore | Crystallize
