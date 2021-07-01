import time

from main import Blocks, print_state, block_shapes, POINTS_FOR_CLEARING_4_ROWS


def main():
    state = Blocks.create()
    print_state(state)
    while not state.is_done():
        action = choose_action(state)
        state = state.step(action)
        print_state(state)
    print('Game over!')


def choose_action(state):
    action = tree_search(state, duration=10)
    return action


def tree_search(state, duration):
    start_time = time.time()
    current_node = Node(None, state)

    node = current_node

    block = node.state.blocks[0]
    if block == 5:
        available_actions = node.state.determine_available_actions()
        for action in available_actions:
            if can_clear_4_rows(node, action):
                return action

    nodes = [node]

    depth = 0
    highest_evaluation = None
    node_with_highest_evaluation = None

    while depth < len(current_node.state.blocks) and time.time() - start_time < duration:
        depth += 1
        next_nodes = []
        for node in nodes:
            available_actions = node.state.determine_available_actions()

            block = node.state.blocks[0]
            available_actions = filter_actions_which_leaves_most_right_column_free(
                node.state.grid,
                block,
                available_actions
            )
            node.children = [
                create_child_node(node, action)
                for action
                in available_actions
            ]
            next_nodes += node.children

            for node in node.children:
                node_evaluation = evaluate(node)
                if highest_evaluation is None or node_evaluation > highest_evaluation:
                    highest_evaluation = node_evaluation
                    node_with_highest_evaluation = node

            if time.time() - start_time >= duration:
                break
        nodes = next_nodes

    node = node_with_highest_evaluation
    while node.parent and node.parent.parent:
        node = node.parent

    return node.action


def filter_actions_which_leaves_most_right_column_free(grid, block, actions):
    return [action for action in actions if is_action_which_leaves_most_right_column_free(grid, block, action)]


def is_action_which_leaves_most_right_column_free(grid, block, action):
    position, rotation = action
    shape = block_shapes[block][rotation]
    shape_width = len(shape[0])
    grid_width = len(grid[0])
    return position[1] + shape_width <= grid_width - 1


def can_clear_4_rows(node, action):
    state = node.state
    after_state = state.step(action)
    return after_state.score - state.score >= POINTS_FOR_CLEARING_4_ROWS


def create_child_node(parent, action):
    return Node(action, parent.state.step(action), parent)


def evaluate(node):
    percentage_of_filled_out = determine_percentage_of_filled_out(node)
    percentage_of_rows_empty = determine_percentage_of_rows_empty(node)
    return percentage_of_filled_out * percentage_of_rows_empty


def determine_percentage_of_rows_empty(node):
    number_of_rows_empty = determine_number_of_rows_empty(node)
    number_of_rows = len(node.state.grid)
    return number_of_rows_empty / float(number_of_rows)


def determine_number_of_rows_empty(node):
    height = determine_height_of_rows_with_block(node)
    grid_height = len(node.state.grid)
    return grid_height - height


def determine_percentage_of_filled_out(node):
    number_of_gaps = determine_number_of_gaps(node)
    width = len(node.state.grid[0])
    height = determine_height_of_rows_with_block(node) - 1
    if height <= 0:
        return 0
    area = width * height
    return (area - number_of_gaps) / float(area)


def determine_height_of_rows_with_block(node):
    state = node.state
    grid = state.grid
    height = 0
    grid_height = len(grid)
    row = grid_height - 1
    while row >= 0 and has_blocks_in_row(grid[row]):
        height += 1
        row -= 1
    return height


def has_blocks_in_row(row):
    return any(cell for cell in row)


def determine_number_of_gaps(node):
    state = node.state
    grid = state.grid
    gaps = 0
    grid_height = len(grid)
    height = determine_height_of_rows_with_block(node)
    top_row_with_blocks = grid_height - height
    for row in range(top_row_with_blocks + 1, grid_height):
        gaps += count_gaps_in_row(grid, row)
    return gaps


def count_gaps_in_row(grid, row):
    count = 0
    grid_width = len(grid[0])
    for column in range(grid_width):
        if (
            grid[row][column] is False and
            (row - 1 >= 0 and grid[row - 1][column] is True) and
            (column - 1 >= 0 and grid[row][column - 1] is True) and
            (column + 1 < grid_width and grid[row][column + 1] is True)
        ):
            count += 1
    return count


class Node:
    def __init__(self, action, state, parent=None):
        self.action = action
        self.state = state
        self.playouts = 0
        self.parent = parent
        self.children = set()


if __name__ == '__main__':
    main()
