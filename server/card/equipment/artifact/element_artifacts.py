from typing import Any, Literal

from .base import RoundEffectArtifactBase
from ....struct import Cost
from ....modifiable_values import CostValue
from ....consts import (
    ELEMENT_TO_DIE_COLOR, ElementType, ObjectPositionType, CostLabels
)


class SmallElementalArtifact(RoundEffectArtifactBase):
    """
    Seven artifacts that decrease elemental cost.
    """

    name: Literal[
        "Broken Rime's Echo",  # cryo
        "Laurel Coronet",  # dendro
        "Mask of Solitude Basalt",  # geo
        "Thunder Summoner's Crown",  # electro
        "Viridescent Venerer's Diadem",  # anemo
        "Wine-Stained Tricorne",  # hydro
        "Witch's Scorching Hat",  # pyro
    ]

    desc: str = (
        'When the character uses a Skill or equips a Talent: Spend 1 less'
        'XXX Die. (Once per Round)'
    )
    version: Literal["4.0"] = "4.0"
    usage: int = 1
    cost: Cost = Cost(any_dice_number = 2)
    element: ElementType = ElementType.NONE
    max_usage_per_round: int = 1

    def __init__(self, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        if self.name == "Broken Rime's Echo":
            self.element = ElementType.CRYO
        elif self.name == "Laurel Coronet":
            self.element = ElementType.DENDRO
        elif self.name == "Mask of Solitude Basalt":
            self.element = ElementType.GEO
        elif self.name == "Thunder Summoner's Crown":
            self.element = ElementType.ELECTRO
        elif self.name == "Viridescent Venerer's Diadem":
            self.element = ElementType.ANEMO
        elif self.name == "Wine-Stained Tricorne":
            self.element = ElementType.HYDRO
        else:
            assert self.name == "Witch's Scorching Hat"
            self.element = ElementType.PYRO
        self.desc = self.desc.replace(
            "XXX", self.element.value.capitalize()
        )

    def value_modifier_COST(
        self, 
        value: CostValue, 
        match: Any,
        mode: Literal['TEST', 'REAL'],
    ) -> CostValue:
        """
        When charactor equipped with this artifact and used skill, decrease
        the elemental cost by 1. If element not match, decrease any dice cost
        by 1.
        """
        if self.usage > 0:  
            # has usage
            if not self.position.check_position_valid(
                value.position, match,
                player_idx_same = True, 
                source_area = ObjectPositionType.CHARACTOR,
            ):
                # not from self position or not equipped
                return value
            label = value.cost.label
            if label & (
                CostLabels.NORMAL_ATTACK.value
                | CostLabels.ELEMENTAL_SKILL.value
                | CostLabels.ELEMENTAL_BURST.value
                | CostLabels.TALENT.value
            ) == 0:  # no label match
                return value
            position = value.position
            assert self.position.charactor_idx != -1
            if position.area == ObjectPositionType.SKILL:
                # cost from charactor
                if position.charactor_idx != self.position.charactor_idx:
                    # not same charactor
                    return value
            else:
                assert position.area == ObjectPositionType.HAND
                # cost from hand card, is a talent card
                equipped_charactor = match.player_tables[
                    self.position.player_idx
                ].charactors[self.position.charactor_idx]
                for card in match.player_tables[
                        self.position.player_idx].hands:
                    if card.id == value.position.id:
                        if card.charactor_name != equipped_charactor.name:
                            # talent card not for this charactor
                            return value
            # can decrease cost
            if value.cost.decrease_cost(ELEMENT_TO_DIE_COLOR[self.element]):
                # decrease cost success
                if mode == 'REAL':
                    self.usage -= 1
        return value


ElementArtifacts = SmallElementalArtifact | SmallElementalArtifact
