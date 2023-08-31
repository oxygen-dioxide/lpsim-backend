"""
Charactor status generated by system.
"""

from typing import Any, List, Literal
from .base import RoundCharactorStatus
from ...modifiable_values import DamageIncreaseValue
from ...consts import DamageElementalType, DamageType
from ...event import MakeDamageEventArguments
from ...action import Actions


class Frozen(RoundCharactorStatus):
    """
    Frozen.
    """
    name: Literal['Frozen'] = 'Frozen'
    desc: str = (
        'Charactor cannot use skills. (Lasts until the end of this Round) '
        'When this charactor receives Pyro DMG or Physical DMG, '
        'removes this effect and increases DMG taken by 2.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_DAMAGE_INCREASE(
            self, value: DamageIncreaseValue, match: Any,
            mode: Literal['TEST', 'REAL']) -> DamageIncreaseValue:
        """
        Increase damage for pyro and physical damages to self by 2, and 
        decrease usage.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.target_position, match,
            player_idx_same = True, charactor_idx_same = True,
        ):
            # not attack self, not activate
            return value
        if value.damage_elemental_type in [
            DamageElementalType.PYRO,
            DamageElementalType.PHYSICAL,
        ] and self.usage > 0:
            value.damage += 2
            assert mode == 'REAL'
            self.usage -= 1
        return value

    def event_handler_MAKE_DAMAGE(
        self, event: MakeDamageEventArguments, match: Any
    ) -> List[Actions]:
        """
        When damage made, check whether the status should be removed.
        Not trigger on AFTER_MAKE_DAMAGE because when damage made, run out
        of usage, but new one is generated, should remove first then generate
        new one, otherwise newly updated status will be removed.
        """
        return list(self.check_should_remove())


SystemCharactorStatus = Frozen | Frozen
