from manim import *
import pandas as pd
import numpy as np

def load_data(file_path):
    return pd.read_csv(file_path)

def normalize_coordinates(lat, lon):
    x = (lon + 125) / (125 - 66) * 10 - 5
    y = (lat - 25) / (49 - 25) * 6 - 3
    return np.array([x * 0.7 + 2, y * 0.7, 0])

def create_dots(filtered_df, opacity=0.3, radius=0.03):
    return VGroup(
        *[
            Dot(normalize_coordinates(row.Lat, row.Lon), color="#E6E6FA", radius=radius)
            .set_opacity(opacity)
            for _, row in filtered_df.iterrows()
        ]
    )

atl_zipcodes = [
    30002, 30030, 30032, 30033, 30067, 30079, 30080, 30084, 30303, 30305, 30306,
    30307, 30308, 30309, 30310, 30311, 30312, 30313, 30314, 30315, 30316, 30317,
    30318, 30319, 30324, 30326, 30327, 30328, 30329, 30337, 30338, 30339, 30340,
    30341, 30342, 30344, 30345, 30346, 30354, 30360, 30363
]

class PlotGAFilteredPoints(ThreeDScene):
    def construct(self):
        file_path = "output_with_metropolitan.csv"
        data = load_data(file_path)
        scenario_0_points = data[data["Scenario"] == 0]
        dots = create_dots(scenario_0_points)
        self.add(dots)
        self.wait(1)

        ga_points = scenario_0_points[scenario_0_points["State/Province"] == "GA"]
        ga_dots = create_dots(ga_points, opacity=0.3, radius=0.03)
        non_ga_dots = VGroup(*[dot for dot in dots if dot not in ga_dots])

        atl_points = scenario_0_points[
            (scenario_0_points["State/Province"] == "GA")
            & (scenario_0_points["Zipcode"].isin(atl_zipcodes))
        ]
        atl_dots = create_dots(atl_points, opacity=0.4, radius=0.01)
        atl_dots2 = create_dots(atl_points, opacity=0.4, radius=0.002)

        non_atl_points = scenario_0_points[
            (scenario_0_points["State/Province"] == "GA")
            & (~scenario_0_points["Zipcode"].isin(atl_zipcodes))
        ]
        non_atl_dots = create_dots(non_atl_points, opacity=0.4, radius=0.01)

        self.play(
            non_ga_dots.animate.set_opacity(0),
            FadeIn(ga_dots),
            FadeIn(atl_dots),
            FadeIn(non_atl_dots),
            run_time=4
        )
        self.wait(1)

        all_dots = VGroup(atl_dots, non_atl_dots, atl_dots2)
        tex1 = Tex("Georgia", font_size=24, color=WHITE).shift([0, -2, 0])
        self.play(Write(tex1))

        self.play(
            ga_dots.animate.scale(5).move_to([0, 0.2, 0]).set_opacity(0),
            all_dots.animate.scale(5).move_to([0, 0.2, 0]),
            run_time=2
        )
        self.wait(1)

        tex2 = Tex("Atlanta", font_size=24, color=WHITE).shift([0, -2, 0])
        self.play(
            Transform(tex1, tex2),
            non_atl_dots.animate.set_opacity(0),
            run_time=2
        )
        self.wait(0.5)

        self.play(
            atl_dots.animate.scale(5).move_to(ORIGIN).set_opacity(0),
            atl_dots2.animate.scale(5).move_to(ORIGIN),
        )
        self.wait(3)

        self.play(atl_dots2.animate.rotate_about_origin(-PI/2), run_time=2)
        self.play(atl_dots2.animate.move_to(2 * UP + 3 * LEFT), run_time=2)
        self.wait(3)
