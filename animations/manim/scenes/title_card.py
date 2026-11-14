"""Stage 0 smoke-test scene: proves the Manim pipeline renders in CI.

Uses Text (not MathTex) so it needs no LaTeX install. Stage 1 adds the
"why resistance vanishes" scene.

Render:  manim -ql scenes/title_card.py TitleCard
"""

from manim import BLUE_B, DOWN, FadeIn, GREY_B, Scene, Text, Write


class TitleCard(Scene):
    def construct(self) -> None:
        title = Text("Ambient Superconductivity Lab", font_size=48, color=BLUE_B)
        tagline = Text("Prove every step. Score every claim.", font_size=28, color=GREY_B)
        tagline.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(tagline, shift=0.2 * DOWN))
        self.wait(0.5)
