from agents.interaction_agent import (
    InteractionAgent_V1_0, InteractionAgent
)
from agents.nothing_agent import NothingAgent
from server.match import Match, MatchState
from server.deck import Deck
from tests.utils_for_test import (
    check_hp, get_test_id_from_command, make_respond, get_random_state, 
    set_16_omni
)
from server.interaction import UseSkillRequest


def test_small_elemental_artifacts():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent_V1_0(
        version = '1.0',
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 1 2 3 4 5 6 7",
            "card 4 0 pyro geo",
            # cost decrease
            "skill 0 dendro hydro",
            # check skill cost after first attack (should no cost decrease)
            "tune hydro 1",
            "card 1 0 dendro dendro",
            # after equip second artifact, can use A but not E 
            # (cost is dendro + any)
            "skill 0 omni omni",
            "end",
            "reroll 0 1 2 3 4 5 6 7",
            "card 0 0 anemo",
            "tune hydro 0",
            # next run after tune, 3 skills are available but only normal 
            # any decrease
            "skill 1 dendro dendro omni",
            "tune pyro 0",
            # after skill 1 and tune, still have 1-1 normal attack
            "card 0 0 electro electro",
            "tune hydro 0",
            "skill 2 dendro dendro",
            "end",
            "reroll",
            "sw_char 1 anemo",
            "sw_char 2 anemo",
            "tune dendro 0",
            "skill 0 electro dendro dendro",
            "tune pyro 0",
            "skill 0 electro cryo cryo",
            "end"
            # 85 10 10 99 10 10
        ],
        only_use_command = True
    )
    match = Match(version = '0.0.1', random_state = get_random_state())
    deck = {
        'name': 'Deck',
        'charactors': [
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
                'hp': 99,
                'max_hp': 99,
            },
            {
                'name': 'DendroMobMage',
                'element': 'DENDRO',
            },
            {
                'name': 'ElectroMobMage',
                'element': 'ELECTRO',
            },
        ],
        'cards': [
            {
                'name': 'Wine-Stained Tricorne',
            }
        ] * 10 + [
            {
                'name': 'Laurel Coronet',
            }
        ] * 10 + [
            {
                'name': 'Strategize',
            }
        ] * 10,
    }
    deck = Deck(**deck)
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    assert match.start()
    match.step()

    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):

            # asserts
            if len(agent_1.commands) == 22:
                # cost decrease
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 2
                assert skills[0].cost.elemental_dice_number == 0
                assert skills[0].cost.any_dice_number == 2
                assert skills[1].cost.elemental_dice_number == 2
                assert skills[1].cost.any_dice_number == 0
            elif len(agent_1.commands) == 21:
                # check skill cost after first attack (should no cost decrease)
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 2
                assert skills[0].cost.elemental_dice_number == 1
                assert skills[0].cost.any_dice_number == 2
                assert skills[1].cost.elemental_dice_number == 3
                assert skills[1].cost.any_dice_number == 0
            elif len(agent_1.commands) == 19:
                # after equip second artifact, can use A but not E 
                # (cost is dendro + any)
                skills = [x for x in match.requests
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 1
                skill: UseSkillRequest = skills[0]
                assert skill.cost.elemental_dice_number == 1
                assert skill.cost.any_dice_number == 1
            elif len(agent_1.commands) == 14:
                # next run after tune, 3 skills are available but only normal 
                # any decrease
                skills = [x for x in match.requests 
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 3
                skills.sort(key = lambda x: x.skill_idx)
                assert skills[0].cost.elemental_dice_number == 1
                assert skills[0].cost.any_dice_number == 1
                assert skills[1].cost.elemental_dice_number == 3
                assert skills[1].cost.any_dice_number == 0
                assert skills[2].cost.elemental_dice_number == 3
                assert skills[2].cost.any_dice_number == 0
            elif len(agent_1.commands) == 12:
                # after skill 1 and tune, still have 1-1 normal attack
                skills = [x for x in match.requests 
                          if x.name == 'UseSkillRequest']
                assert len(skills) == 1
                skill: UseSkillRequest = skills[0]
                assert skill.cost.elemental_dice_number == 1
                assert skill.cost.any_dice_number == 1

            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0
    assert match.round_number == 4
    check_hp(match, [[85, 10, 10], [99, 10, 10]])
    assert match.player_tables[1].charactors[0].artifact is not None

    assert match.state != MatchState.ERROR


def test_create_small_element_artifacts():
    deck = Deck.from_str(
        """
        charactor:Nahida*3
        Broken Rime's Echo*4
        Laurel Coronet*4
        Mask of Solitude Basalt*4
        Thunder Summoner's Crown*4
        Viridescent Venerer's Diadem*4
        Wine-Stained Tricorne*4
        Witch's Scorching Hat*4
        Strategize*2
        """
    )
    match = Match()
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 4
    match.config.max_hand_size = 30
    match.config.initial_hand_size = 30
    match.start()
    match.step()

    assert match.state != MatchState.ERROR


def test_old_version_elemental_artifacts():
    agent_0 = NothingAgent(player_idx = 0)
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "reroll 1 4",
            "TEST 1 all card can use",
            "sw_char 1 4",
            "TEST 1 all card can use",
            "sw_char 2 0",
            "TEST 2 3 card can use, 0 and 4 cannot",
            "end"
        ],
        only_use_command = True
    )
    deck = Deck.from_str(
        '''
        charactor:Fischl
        charactor:Mona
        charactor:Nahida
        Wine-Stained Tricorne*12
        Timmie*2
        Rana*2
        Strategize*2
        # Timmie*22
        '''
    )
    old_wine = {'name': 'Wine-Stained Tricorne', 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old_wine] * 12
    deck = Deck(**deck_dict)
    match = Match(random_state = get_random_state())
    match.config.max_same_card_number = 30
    match.set_deck([deck, deck])
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    counter = 0
                    for request in match.requests:
                        if request.name == 'UseCardRequest':
                            counter += 1
                    assert counter == 5
                elif test_id == 2:
                    counter = []
                    for request in match.requests:
                        if request.name == 'UseCardRequest':
                            counter.append(request.card_idx)
                    assert len(counter) == 3
                    assert 0 not in counter
                    assert 4 not in counter
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0:
            break

    assert len(agent_1.commands) == 0

    assert match.state != MatchState.ERROR


def test_gambler():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "end",
            "choose 1",
            "choose 2",
            "choose 3",
            "choose 4",
            "choose 5",
            "choose 6",
            "skill 0 0 1 2",
            "choose 7",
            "card 0 0 0",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 9 15",
            "end",
            "skill 0 0 1 2",
            "TEST 1 13 15",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 11 15",
            "end",
            "TEST 2 p0c7 usage2",
            "end"
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 1 1",
            "skill 0 0 1 2",
            "TEST 1 16 12",
            "card 0 0 1",
            "skill 0 0 1 2",
            "TEST 1 16 10",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 16 8",
            "skill 0 0 1 2",
            "TEST 1 16 5",
            "card 0 0 0",
            "skill 0 0 1 2",
            "TEST 1 16 3",
            "card 0 2 0",
            "end",
            "choose 1",
            "skill 0 0 1 2",
            "choose 2",
            "TEST 1 11 15",
            "end",
            "choose 3",
            "choose 4",
            "card 0 0 0",
            "end",
            "choose 5",
            "choose 6",
            "end"
        ],
        only_use_command = True
    )
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        # charactor:Nahida
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        Gambler's Earrings*30
        '''
    )
    # old_wine = {'name': 'Wine-Stained Tricorne', 'version': '3.3'}
    # deck_dict = deck.dict()
    # deck_dict['cards'] += [old_wine] * 12
    # deck = Deck(**deck_dict)
    for charactor in deck.charactors:
        charactor.hp = 1
        charactor.max_hp = 1
    match = Match(random_state = get_random_state())
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    match.set_deck([deck, deck])
    set_16_omni(match)
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            while True:
                cmd = agent_0.commands[0]
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                elif test_id == 2:
                    charactor = match.player_tables[0].charactors[7]
                    assert charactor.artifact is not None
                    assert charactor.artifact.name == "Gambler's Earrings"
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                cmd = agent_1.commands[0]
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0 and len(agent_0.commands) == 0

    assert match.state != MatchState.ERROR


def test_old_gambler():
    agent_0 = InteractionAgent(
        player_idx = 0,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "end",
            "choose 1",
            "choose 2",
            "choose 3",
            "choose 4",
            "choose 5",
            "choose 6",
        ],
        only_use_command = True
    )
    agent_1 = InteractionAgent(
        player_idx = 1,
        verbose_level = 0,
        commands = [
            "sw_card",
            "choose 0",
            "card 0 1 1",
            "skill 0 0 1 2",
            "TEST 1 16 12",
            "card 0 0 1",
            "skill 0 0 1 2",
            "TEST 1 16 10",
            "skill 0 0 1 2",
            "skill 0 0 1 2",
            "TEST 1 16 8",
            "skill 0 0 1 2",
            "TEST 1 16 7",
            "skill 0 0 1 2",
            "TEST 1 16 6",
            "end",
        ],
        only_use_command = True
    )
    deck = Deck.from_str(
        '''
        # charactor:Fischl
        # charactor:Mona
        # charactor:Nahida
        charactor:Nahida*10
        # Gambler's Earrings*2
        # Wine-Stained Tricorne*2
        # Timmie*2
        # Rana*2
        # Strategize*2
        # The Bestest Travel Companion!*2
        # Covenant of Rock
        # Gambler's Earrings*30
        '''
    )
    old_gambler = {'name': "Gambler's Earrings", 'version': '3.3'}
    deck_dict = deck.dict()
    deck_dict['cards'] += [old_gambler] * 30
    deck = Deck(**deck_dict)
    for charactor in deck.charactors:
        charactor.hp = 1
        charactor.max_hp = 1
    match = Match(random_state = get_random_state())
    match.config.max_same_card_number = 30
    match.config.charactor_number = 10
    match.config.random_first_player = False
    match.set_deck([deck, deck])
    set_16_omni(match)
    match.start()
    match.step()
    while True:
        if match.need_respond(0):
            while True:
                cmd = agent_0.commands[0]
                test_id = get_test_id_from_command(agent_0)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                elif test_id == 2:
                    charactor = match.player_tables[0].charactors[7]
                    assert charactor.artifact is not None
                    assert charactor.artifact.name == "Gambler's Earrings"
                else:
                    break
            make_respond(agent_0, match)
        elif match.need_respond(1):
            while True:
                cmd = agent_1.commands[0]
                test_id = get_test_id_from_command(agent_1)
                if test_id == 1:
                    number = [int(x) for x in cmd.strip().split(' ')[-2:]]
                    assert number[0] == len(match.player_tables[0].dice.colors)
                    assert number[1] == len(match.player_tables[1].dice.colors)
                else:
                    break
            make_respond(agent_1, match)
        else:
            raise AssertionError('No need respond.')
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    assert len(agent_1.commands) == 0 and len(agent_0.commands) == 0

    assert match.state != MatchState.ERROR


if __name__ == '__main__':
    # test_small_elemental_artifacts()
    # test_create_small_element_artifacts()
    # test_old_version_artifacts()
    # test_gambler()
    test_old_gambler()
