from manim import *

START_VALUE = 0

BIT_WIDTH = 4

RUN_TIME = 0.9 #1.5
STEP_PAUSE = 0.15


def binary_count(start_value, bit_width):

    initial_bits = format(start_value, f"0{bit_width}b")
    bits = list(initial_bits)
    yield "".join(bits)

    while True:
        bit_index = bit_width - 1
        while bit_index >= 0 and bits[bit_index] == "1":
            bits[bit_index] = "0"
            bit_index -= 1

        # A carry beyond the lastleft bit means counting is complete.
        if bit_index < 0:
            return

        bits[bit_index] = "1"
        yield "".join(bits)


class BinaryCounterScene(Scene):
    def construct(self):
        cell_size = min(1.5, 10/BIT_WIDTH)
        states = binary_count(START_VALUE, BIT_WIDTH)
        initial_bits = next(states)

        squares = []
        digits = []
        cells = VGroup()

        for bit_index in range(BIT_WIDTH):
            square = Square(side_length=cell_size, color=BLUE_B, fill_opacity=0.15)
            digit = Text(initial_bits[bit_index], font_size=48)
            digit.move_to(square.get_center())
            cells.add(VGroup(square, digit))

            squares.append(square)
            digits.append(digit)

        cells.arrange(RIGHT, buff=0.5)  #  try 1
        cells.move_to(ORIGIN)

        decimal_text = Text(f"Decimal: {START_VALUE}", font_size=40)
        decimal_text.next_to(cells, UP, buff=0.8)

        self.play(FadeIn(cells), Write(decimal_text), run_time=2)
        self.wait(0.3)

        previous_bits = initial_bits
        for next_bits in states:
            next_value = int(next_bits, 2)
            changed_indices = []
            for bit_index in range(BIT_WIDTH):
                if previous_bits[bit_index] != next_bits[bit_index]:
                    changed_indices.append(bit_index)

            bit_animations = None
            for bit_index in changed_indices:
                new_digit = Text(next_bits[bit_index], font_size=48)
                new_digit.move_to(digits[bit_index].get_center())
                digit_animation = Transform(
                    digits[bit_index],
                    new_digit,
                    run_time=RUN_TIME,
                    rate_func=smooth,
                )
                highlight_animation = Indicate(
                    squares[bit_index],
                    color=YELLOW,
                    run_time=RUN_TIME,
                )
                current_bit_animation = AnimationGroup(
                    digit_animation,
                    highlight_animation,
                    lag_ratio=0,
                )
                # Combine changed bits so they animate at the same instance.
                if bit_animations is None:
                    bit_animations = current_bit_animation
                else:
                    bit_animations = AnimationGroup(
                        bit_animations,
                        current_bit_animation,
                        lag_ratio=0,
                    )

            new_decimal = Text(f"Decimal:  {next_value}", font_size=40)
            new_decimal.move_to(decimal_text.get_center())
            decimal_animation = Transform(
                decimal_text,
                new_decimal,
                run_time=RUN_TIME,
                rate_func=smooth,
            )
            self.play(bit_animations, decimal_animation)
            self.wait(STEP_PAUSE)
            previous_bits = next_bits

        self.wait(1)
        self.play(FadeOut(cells), FadeOut(decimal_text), run_time=1)
        self.wait(1)