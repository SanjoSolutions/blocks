import random
from enum import IntEnum


HEIGHT = 20
WIDTH = 10

POINTS_FOR_CLEARING_4_ROWS = 800


class Rotation(IntEnum):
    Default = 0
    Rotated90DegreeClockwise = 1
    Rotated180DegreeClockwise = 2
    Rotated270DegreeClockwise = 3


default_block_shapes = [
    (
        (True, False),
        (True, False),
        (True, True)
    ),
    (
        (False, True),
        (False, True),
        (True, True)
    ),
    (
        (True, True),
        (True, True)
    ),
    (
        (False, True, True),
        (True, True, False)
    ),
    (
        (True, True, False),
        (False, True, True)
    ),
    (
        (True,),
        (True,),
        (True,),
        (True,)
    )
]


def rotate_90_degree_clockwise(block_shape):
    block_shape_width = len(block_shape[0])
    block_shape_height = len(block_shape)
    rotated_block_shape_width = block_shape_height
    rotated_block_shape_height = block_shape_width
    rotated_block_shape = [None] * rotated_block_shape_height
    for row in range(rotated_block_shape_height):
        rotated_block_shape[row] = [False] * rotated_block_shape_width
    for row in range(block_shape_height):
        for column in range(block_shape_width):
            rotated_block_shape_row = column
            rotated_block_shape_column = block_shape_height - row - 1
            rotated_block_shape[rotated_block_shape_row][rotated_block_shape_column] = block_shape[row][column]
    return rotated_block_shape


def rotate_180_degree_clockwise(block_shape):
    return rotate_clockwise(block_shape, 180)


def rotate_270_degree_clockwise(block_shape):
    return rotate_clockwise(block_shape, 270)


def rotate_clockwise(block_shape, degree):
    rotated_block_shape = block_shape
    for i in range(0, int(degree / 90)):
        rotated_block_shape = rotate_90_degree_clockwise(rotated_block_shape)
    return rotated_block_shape


block_shapes = [
    [
        default_block_shape,
        rotate_90_degree_clockwise(default_block_shape),
        rotate_180_degree_clockwise(default_block_shape),
        rotate_270_degree_clockwise(default_block_shape)
    ]
    for default_block_shape
    in default_block_shapes
]


def choose_random_block():
    return random.choice(list(range(len(block_shapes))))


def add_random_block(blocks):
    block = choose_random_block()
    blocks.append(block)


# TODO: Feature: Hold queue

class Blocks:
    @staticmethod
    def create():
        grid = [None] * HEIGHT
        for index in range(len(grid)):
            grid[index] = [False] * WIDTH
        blocks = []
        for i in range(4):
            add_random_block(blocks)
        score = 0
        return Blocks(grid, blocks, score)

    def __init__(self, grid, blocks, score):
        self.grid = grid
        self.blocks = blocks
        self.score = score

    def determine_available_actions(self):
        available_actions = []
        grid_width = len(self.grid[0])
        grid_height = len(self.grid)
        block = self.blocks[0]
        for rotation in Rotation:
            block_shape = block_shapes[block][int(rotation)]
            block_shape_width = len(block_shape[0])
            block_shape_height = len(block_shape)
            for row in range(grid_height - block_shape_height + 1):
                for column in range(grid_width - block_shape_width + 1):
                    position = (row, column)
                    if self._can_put_block_shape_into_position(block_shape, position):
                        action = (position, rotation)
                        available_actions.append(action)
        return available_actions

    def _can_put_block_shape_into_position(self, block_shape, position):
        return (
            # TODO: Consider putting into in from the side
            self._is_space_free(block_shape, position) and
            self._can_fall_there(block_shape, position)
        )

    def _is_space_free(self, block_shape, position):
        block_shape_width = len(block_shape[0])
        block_shape_height = len(block_shape)
        for block_shape_row in range(block_shape_height):
            for block_shape_column in range(block_shape_width):
                block_shape_cell_value = block_shape[block_shape_row][block_shape_column]
                grid_cell_value = self.grid[position[0] + block_shape_row][position[1] + block_shape_column]
                if block_shape_cell_value and grid_cell_value:
                    return False
        return True

    def _can_fall_there(self, block_shape, position):
        block_shape_width = len(block_shape[0])
        grid_height = len(self.grid)
        for block_shape_column in range(block_shape_width):
            bottom_row_of_block_shape = self._determine_bottom_row_of_block_shape_in_column(
                block_shape,
                block_shape_column
            )
            position_of_bottom_of_block_shape = position[0] + bottom_row_of_block_shape
            position_below_bottom_of_block_shape = position_of_bottom_of_block_shape + 1
            position_above_bottom_of_block_shape = position_of_bottom_of_block_shape - 1
            column = position[1] + block_shape_column
            if (
                (
                    position_below_bottom_of_block_shape >= grid_height or
                    self.grid[position_below_bottom_of_block_shape][column]
                ) and
                all(self.grid[row][column] is False for row in range(0, position_above_bottom_of_block_shape + 1))
            ):
                return True
        return False

    def _determine_bottom_row_of_block_shape_in_column(self, block_shape, column):
        block_shape_height = len(block_shape)
        for row in range(block_shape_height - 1, -1, -1):
            if block_shape[row][column]:
                return row
        raise Exception(
            'There seems to be no block in the column of the block_shape. ' +
            'Please check the block_shape data.'
        )

    def step(self, action):
        position, rotation = action
        block = self.blocks[0]
        block_shape = block_shapes[block][int(rotation)]
        block_shape_width = len(block_shape[0])
        block_shape_height = len(block_shape)
        grid = copy_grid(self.grid)
        for block_shape_row in range(block_shape_height):
            for block_shape_column in range(block_shape_width):
                block_shape_cell_value = block_shape[block_shape_row][block_shape_column]
                if block_shape_cell_value:
                    row = position[0] + block_shape_row
                    column = position[1] + block_shape_column
                    grid[row][column] = True

        grid, number_of_lines_cleared = self._clear_lines(grid)
        score = self.score + self._determine_score_for_lines_cleared(number_of_lines_cleared)

        blocks = self.blocks[1:]
        add_random_block(blocks)
        state = Blocks(grid, blocks, score)

        return state

    def _clear_lines(self, grid):
        number_of_lines_cleared = 0
        width = len(grid[0])
        height = len(grid)
        grid = copy_grid(grid)
        row = height - 1
        while row >= 0:
            if self._row_is_full(grid[row]):
                grid.pop(row)
                grid.insert(0, [False] * width)
                number_of_lines_cleared += 1
                if number_of_lines_cleared > 4:
                    print('.')
            else:
                row -= 1

        return grid, number_of_lines_cleared

    def _row_is_full(self, row):
        return all(cell for cell in row)

    def _determine_score_for_lines_cleared(self, number_of_lines_cleared):
        if number_of_lines_cleared == 0:
            return 0
        elif number_of_lines_cleared == 1:
            return 100
        elif number_of_lines_cleared == 2:
            return 300
        elif number_of_lines_cleared == 3:
            return 500
        elif number_of_lines_cleared == 4:
            return POINTS_FOR_CLEARING_4_ROWS

    def is_done(self):
        return len(self.determine_available_actions()) == 0


def copy_grid(grid):
    grid = grid.copy()
    for index in range(len(grid)):
        grid[index] = grid[index].copy()
    return grid


def print_state(state):
    for row in state.grid:
        row = [(1 if cell else 0) for cell in row]
        print(row)
    print('')
