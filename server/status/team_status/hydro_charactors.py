from typing import Any, Literal

from ...consts import DamageType, ObjectPositionType

from ...modifiable_values import DamageMultiplyValue
from .base import UsageTeamStatus


class IllusoryBubble(UsageTeamStatus):
    """
    Team status generated by Mona.
    """
    name: Literal['Illusory Bubble'] = 'Illusory Bubble'
    desc: str = (
        'When dealing Skill DMG: Remove this status and double the DMG dealt '
        'for this instance.'
    )
    version: Literal['3.3'] = '3.3'
    usage: int = 1
    max_usage: int = 1

    def value_modifier_DAMAGE_MULTIPLY(
        self, value: DamageMultiplyValue, match: Any,
        mode: Literal['TEST', 'REAL']
    ) -> DamageMultiplyValue:
        """
        Double damage when skill damage made.
        """
        if value.damage_type != DamageType.DAMAGE:
            # not damage, not modify
            return value
        if not self.position.check_position_valid(
            value.position, match,
            player_idx_same = True, target_area = ObjectPositionType.CHARACTOR,
        ):
            # not from self position or not charactor skill
            return value
        if value.target_position.player_idx == self.position.player_idx:
            # attack self, not activate
            return value
        if self.usage > 0:
            value.damage *= 2
            assert mode == 'REAL'
            self.usage -= 1
        return value


HydroCharactorTeamStatus = IllusoryBubble | IllusoryBubble
