from server.interaction import SwitchCardResponse
from tests.utils_for_test import make_respond
from agents.interaction_agent import InteractionAgent
from agents.nothing_agent import NothingAgent
from server.match import Match
from server.deck import Deck


def test_draw_card():
    """
    when all card same, should raise no error and hand number right
    """
    deck = Deck.from_str(
        '''
        charactor:Nahida*3
        Strategize*30
        '''
    )
    match = Match()
    match.set_deck([deck, deck])
    match.config.max_same_card_number = 30
    match.config.random_first_player = False
    match.start()
    match.step()
    agent_0 = NothingAgent(player_id = 0)
    agent_1 = InteractionAgent(
        player_id = 1,
        commands = [
            'sw_card 1 2 3 4',
        ],
        only_use_command = True
    )
    while True:
        if match.need_respond(0):
            make_respond(agent_0, match)
        elif match.need_respond(1):
            make_respond(agent_1, match)
        else:
            break
        if len(agent_1.commands) == 0:
            break
    assert len(agent_1.commands) == 0
    assert len(match.player_tables[1].hands) == 5

    """
    when two types of cards, should become another type in all hand
    """
    deck = Deck.from_str(
        '''
        charactor:Nahida*3
        Strategize*15
        Rana*15
        '''
    )
    for _ in range(100):
        match = Match()
        match.set_deck([deck, deck])
        match.config.max_same_card_number = 30
        match.config.random_first_player = False
        match.start()
        match.step()
        agent_0 = NothingAgent(player_id = 0)
        while True:
            if match.need_respond(0):
                make_respond(agent_0, match)
            elif match.need_respond(1):
                assert len(match.requests) == 1
                assert match.requests[0].name == 'SwitchCardRequest'
                req = match.requests[0]
                ids = []
                for id, name in enumerate(req.card_names):
                    if name == 'Strategize':
                        ids.append(id)
                resp: SwitchCardResponse = SwitchCardResponse(
                    request = req,
                    card_ids = ids,
                )
                match.respond(resp)
                match.step()
                break
            else:
                break
        assert len(match.player_tables[1].hands) == 5
        for card in match.player_tables[1].hands:
            assert card.name == 'Rana'


if __name__ == '__main__':
    test_draw_card()
