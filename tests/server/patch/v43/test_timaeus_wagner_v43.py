import os
from src.lpsim import MatchState
from tests.utils_for_test import (
    check_usage,
    get_test_id_from_command,
    make_respond,
    set_16_omni,
    read_from_log_json,
)


def test_timaeus_wagner_v43_draw_card():
    match, agent_0, agent_1 = read_from_log_json(
        os.path.join(os.path.dirname(__file__), "jsons", "test_timaeus_wagner.json")
    )
    # add omnipotent guide
    set_16_omni(match)
    match.start()
    match.step()
    new_commands = [[], []]

    while True:
        if match.need_respond(0):
            agent = agent_0
            nc = new_commands[0]
        elif match.need_respond(1):
            agent = agent_1
            nc = new_commands[1]
        else:
            raise AssertionError("No need respond.")
        # do tests
        while True:
            nc.append(agent.commands[0])
            cmd = agent.commands[0].strip().split(" ")
            test_id = get_test_id_from_command(agent)
            if test_id == 0:
                # id 0 means current command is not a test command.
                break
            elif test_id == 3:
                pidx = int(cmd[2][1])
                check_usage(match.player_tables[pidx].supports, cmd[3:])
            elif test_id == 6:
                pidx = int(cmd[2][1])
                assert len(match.player_tables[pidx].hands) == int(cmd[3])
            else:
                raise AssertionError(f"Unknown test id {test_id}")
        # respond
        make_respond(agent, match)
        if len(agent_1.commands) == 0 and len(agent_0.commands) == 0:
            break

    # simulate ends, check final state
    assert match.state != MatchState.ERROR


if __name__ == "__main__":
    test_timaeus_wagner_v43_draw_card()
