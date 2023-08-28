from agents.interaction_agent import InteractionAgent
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from server.consts import DamageElementalType
from tests.utils_for_test import (
    get_test_id_from_command, set_16_omni, check_hp, check_name, make_respond
)


def test_crystallize():
    """
    agent 0: 1 elec to p1c2, then nothing until r3, and c2 will be defeated,
        choose c0. in r3, 3 geo to p1c2
    agent 1: in r1, 1 elec to p1c2, 1 geo to p1c2, 1 elec to p1c2, 1 geo to 
        p1c2, in r2, 1 geo to p1c2, 1 elec to p1c2, 1 geo to p1c2, p0c2 
        defeated, switch to p1c2, end.
    result: agent 1 get two crystallize, and agent 0 attack 3 + 1 - 2 = 2hp.
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            # 'reroll',
            'skill 0 omni omni omni',
            'end',
            'end',
            'choose 0',
            'skill 1 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            # 'reroll',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'end',
            'end',
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'GeoMobMage',
                'element': 'GEO',
            },
            {
                'name': 'GeoMobMage',
                'element': 'GEO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0
    assert len(agent_1.commands) == 0
    assert match.round_number == 4
    check_hp(match, [[10, 10, 0], [10, 10, 7]])

    assert match.match_state != MatchState.ERROR


def test_frozen():
    """
    agent 0 goes first, sw 2, 1 cryo to p1c2, sw 0, 1 hydro to p1c2, sw 1,
        2 physical to p1c2, sw2, end, sw0, sw2, (cannot skill), end, 
        (can skill) 1 cryo to p0c2.
    agent 1 sw0, sw2, (cannot skill), end, (can skill) 3 cryo to p0c2, sw 0,
        1 hydro to p0c2, end.
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'sw_char 1 omni',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'end',
            'sw_char 0 omni',
            'sw_char 2 omni',
            'end',
            'skill 0 omni omni omni',
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'sw_char 0 omni',
            'sw_char 2 omni',
            'end',
            'skill 1 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'HydroMobMage',
                'element': 'HYDRO',
            },
            {
                'name': 'HydroMob',
                'element': 'HYDRO',
            },
            {
                'name': 'CryoMobMage',
                'element': 'CRYO',
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            if len(agent_0.commands) == 2:
                # p0c2 should be frozen, and cannot use skill
                check_name('Frozen', 
                           match.player_tables[0].charactors[2].status)
                check_name('UseSkillRequest', match.requests, exist = False)
            elif len(agent_0.commands) == 1:
                # now not frozen and can use skill
                check_name('Frozen', 
                           match.player_tables[0].charactors[2].status,
                           exist = False)
                check_name('UseSkillRequest', match.requests, exist = True)
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 5:
                # p1c2 should be frozen, and cannot use skill
                check_name('Frozen', 
                           match.player_tables[1].charactors[2].status)
                check_name('UseSkillRequest', match.requests, exist = False)
            elif len(agent_1.commands) == 4:
                # now not frozen and can use skill
                check_name('Frozen', 
                           match.player_tables[1].charactors[2].status,
                           exist = False)
                check_name('UseSkillRequest', match.requests, exist = True)
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0
    assert len(agent_1.commands) == 0
    assert match.round_number == 3
    check_hp(match, [[10, 10, 5], [9, 10, 3]])

    assert match.match_state != MatchState.ERROR


def test_frozen_and_pyro():
    """
    agent 0 goes first, sw 2, 1 cryo to p1c2, sw 0, 1 hydro to p1c2, 
        1 hydro to p1c2, sw 1, 1 pyro to p1c2, end, 1 pyro to p1c2, sw 2, 
        1 cryo to p1c2, 1 cryo to p1c2, sw 0, 1 hydro to p1c2, sw 1, end, 
        1 pyro to p1c2, end.
    agent 1 end, end, end.
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'sw_char 1 omni',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'sw_char 1 omni',
            'end',
            'skill 0 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'end',
            'end',
            'end',
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'HydroMobMage',
                'element': 'HYDRO',
            },
            {
                'name': 'PyroMobMage',
                'element': 'PYRO',
            },
            {
                'name': 'CryoMobMage',
                'element': 'CRYO',
                'hp': 99,
                'max_hp': 99,
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0
    assert len(agent_1.commands) == 0
    assert match.round_number == 4
    check_hp(match, [[10, 10, 99], [10, 10, 82]])
    assert match.player_tables[1].charactors[2].element_application == ['PYRO']

    assert match.match_state != MatchState.ERROR


def test_burning_flame():
    """
    agent 0 goes first, sw 2, 1 pyro to p1c2, sw 0, 1 dendro to p1c2, end,
        1 dendro to p1c2, end, 1 dendro to p1c2, 1 dendro to p1c2, sw 2, 
        1 pyro to p1c2, sw 0, 1 dendro to p1c2, end, 1 dendro to p1c2, 
        sw 2, 1 pyro to p1c2, end.
    agent 1 sw2, end, end, end, end.
    result: 18 damage and 2 burning flame.
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'end',
            'end',
            'end',
            'end',
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'PyroMobMage',
                'element': 'PYRO',
                'hp': 99,
                'max_hp': 99,
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0
    assert len(agent_1.commands) == 0
    assert match.round_number == 5
    assert len(match.player_tables[0].summons) == 1
    assert match.player_tables[0].summons[0].name == 'Burning Flame'
    assert match.player_tables[0].summons[0].usage == 1
    check_hp(match, [[10, 10, 99], [10, 10, 80]])

    assert match.match_state != MatchState.ERROR


def test_dendro_core_catalyzing_field():
    """
    agent 0 goes first, sw 2, 1 electro to p1c2, sw 0, 1 dendro to p1c2,
        1 dendro to p1c2, sw 1, 1 hydro to p1c2, sw 2, end, 1 electro to p1c2,
        sw 1, 1 hydro to p1c2, 1 hydro to p1c2, sw 0, 1 dendro to p1c2, end,
        1 dendro to p1c2, sw 1, 1 hydro to p1c2, sw 2, 1 electro to p1c2, 
        1 electro to p1c2, end.
    agent 1 sw2, end, end, end.
    tested catalyzing field and dendro core will not disappear at round end,
    can trigger simultaneously, and max dendro core number is 1.
    result: 22 damage and no status.
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'sw_char 1 omni',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'end',
            'skill 0 omni omni omni',
            'sw_char 1 omni',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'sw_char 0 omni',
            'skill 0 omni omni omni',
            'end',
            'skill 0 omni omni omni',
            'sw_char 1 omni',
            'skill 0 omni omni omni',
            'sw_char 2 omni',
            'skill 0 omni omni omni',
            'skill 0 omni omni omni',
            'end',
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            'sw_card',
            'choose 2',
            'end',
            'end',
            'end',
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'HydroMobMage',
                'element': 'HYDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
                'hp': 99,
                'max_hp': 99,
            },
        ],
        'cards': [
            {
                'name': 'Strategize',
            }
        ] * 30,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_0.commands) == 0
    assert len(agent_1.commands) == 0
    assert match.round_number == 4
    assert len(match.player_tables[0].team_status) == 0
    check_hp(match, [[10, 10, 99], [9, 9, 76]])

    assert match.match_state != MatchState.ERROR


def test_swirl():
    """
    first: swirl pyro and hydro
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 1 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2"
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = Deck.from_str(
        '''
        charactor:PyroMobMage
        charactor:HydroMobMage
        charactor:AnemoMobMage
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
        '''
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 1
    assert len(match.player_tables[0].team_status) == 0
    check_hp(match, [[6, 6, 6], [10, 10, 10]])

    assert match.match_state != MatchState.ERROR


def test_swirl_2():
    """
    second: swirl electro and hydro
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 1 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2"
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = Deck.from_str(
        '''
        charactor:ElectroMobMage
        charactor:HydroMobMage
        charactor:AnemoMobMage
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
        '''
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 1
    assert len(match.player_tables[0].team_status) == 0
    check_hp(match, [[4, 6, 6], [10, 10, 10]])

    assert match.match_state != MatchState.ERROR


def test_swirl_3():
    """
    third: swirl cryo and hydro, and swirl pyro. To apply four elements, 
    after match start, modify p1c0 skill 1 element to pyro.
    """
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            "sw_char 1 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "end",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "skill 1 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2"
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = Deck.from_str(
        '''
        charactor:CryoMobMage
        charactor:HydroMobMage
        charactor:AnemoMobMage
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
        '''
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.player_tables[1].charactors[0].skills[1].damage_type = \
        DamageElementalType.PYRO
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            if len(agent_1.commands) == 1:
                table = match.player_tables[0]
                charactors = table.charactors
                assert charactors[0].element_application == ['PYRO']
                assert charactors[1].element_application == []
                assert charactors[2].element_application == []
                assert len(charactors[0].status) == 0
                assert len(charactors[1].status) == 1
                assert len(charactors[2].status) == 1
                assert charactors[1].status[0].name == 'Frozen'
                assert charactors[2].status[0].name == 'Frozen'
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 2
    assert len(match.player_tables[0].team_status) == 0
    check_hp(match, [[2, 4, 4], [10, 10, 10]])
    assert match.player_tables[0].charactors[0].element_application == []
    assert match.player_tables[0].charactors[1].element_application == ['PYRO']
    assert match.player_tables[0].charactors[2].element_application == ['PYRO']
    assert len(match.player_tables[0].charactors[1].status) == 0
    assert len(match.player_tables[0].charactors[2].status) == 0

    assert match.match_state != MatchState.ERROR


def test_swirl_with_catalyzing_field():
    """
    four: electro and dendro to generate catalyzing field, and swirl electro
        will not trigger catalyzing field.
    """
    agent_0 = InteractionAgent(
        player_id = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "sw_char 0 0",
            "sw_char 1 0",
            "sw_char 0 0",
            "sw_char 2 0",
            "sw_char 1 0",
            "sw_char 2 0",
            "sw_char 1 0",
            "end",
            "end",
        ],
        random_after_no_command = True
    )
    agent_1 = InteractionAgent(
        player_id = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 1",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            # cannot swirl dendro
            "TEST 1 enemy dendro none none",
            "sw_char 1 1",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "sw_char 0 0",
            "end",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "sw_char 2 0",
            "skill 0 0 1 2",
            # no elemental application, 2 catalyzing field, field not increase
            # back electro damage.
        ],
        random_after_no_command = True
    )
    match = Match()
    deck = Deck.from_str(
        '''
        charactor:ElectroMobMage
        charactor:DendroMobMage
        charactor:AnemoMobMage
        Prophecy of Submersion*10
        Stellar Predator*10
        Wine-Stained Tricorne*10
        '''
    )
    match.set_deck([deck, deck])
    match.match_config.max_same_card_number = 30
    match.match_config.random_first_player = False
    set_16_omni(match)
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    for charactor, app in zip(
                        match.player_tables[0].charactors,
                        [['DENDRO'], [], []]
                    ):
                        assert charactor.element_application == app
                else:
                    break
            make_respond(agent_1, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert len(agent_0.commands) == 0
    assert match.round_number == 2
    assert len(match.player_tables[0].team_status) == 0
    check_hp(match, [[6, 4, 7], [10, 10, 10]])
    assert match.player_tables[0].charactors[0].element_application == []
    assert match.player_tables[0].charactors[1].element_application == []
    assert match.player_tables[0].charactors[2].element_application == []
    assert len(match.player_tables[1].team_status) == 1
    assert match.player_tables[1].team_status[0].name == 'Catalyzing Field'
    assert match.player_tables[1].team_status[0].usage == 2

    assert match.match_state != MatchState.ERROR


if __name__ == '__main__':
    test_swirl_with_catalyzing_field()
