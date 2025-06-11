from manim import *
import pandas as pd
import numpy as np

def scenario_dfs(path):
    data = pd.read_csv(path)
    scenarios = data.groupby('Scenario')
    dfs = {
        s: {
            "store": {st: g for st, g in grp.groupby('Store No.')},
            "year": {yr: g for yr, g in grp.groupby('year')},
        }
        for s, grp in scenarios
    }
    return dfs

def normalize_coordinates(lat, lon):
    x = (lon + 125) / (125 - 66) * 10 - 5
    y = (lat - 25) / (49 - 25) * 6 - 3
    return np.array([x * 17.5, y * 17.5, 0])

def filter_data(df, scenario=None, year=None, store=None):
    filtered = df.copy()
    if scenario is not None:
        filtered = filtered[filtered["Scenario"] == scenario]
    if year is not None:
        filtered = filtered[filtered["year"] == year]
    if store is not None:
        filtered = filtered[filtered["Store No."] == store]
    return filtered

def dot(filtered_df, color="#E6E6FA", x_adjust=0, y_adjust=0, opacity=0.4, radius=0.05):
    return VGroup(
        *[
            Dot(
                normalize_coordinates(row.Lat, row.Lon) + np.array([x_adjust, y_adjust, 0]),
                color=color,
                radius=radius,
                opacity=opacity
            ).set_opacity(opacity)
            for _, row in filtered_df.iterrows()
        ]
    )

def combined_df(scenario_data):
    return pd.concat(scenario_data["store"].values())

def dot(filtered_df, color=WHITE, opacity=0.3, radius=0.05, shift=ORIGIN, rotation=-PI / 2):
    dots = VGroup(
        *[
            Dot(normalize_coordinates(row.Lat, row.Lon), color=color, radius=radius).set_opacity(opacity)
            for _, row in filtered_df.iterrows()
        ]
    )
    return dots.move_to(shift).rotate_about_origin(rotation)

def create_dots_group(df, year, scenarios, color=BLUE, radius=0.03, opacity=0.8, x_shift=3 * LEFT):
    dots_group = VGroup()
    for i, scenario in enumerate(scenarios):
        filtered_df = filter_data(df, year=year, scenario=scenario)
        if not filtered_df.empty:
            dots = dot(filtered_df, color=color, radius=radius, opacity=opacity)
            dots.shift((2 - i) * UP + x_shift)
            dots_group.add(dots)
    return dots_group

class DisplayTransformations(ThreeDScene):
    def construct(self):
        df = pd.read_csv("Atlanta.csv")
        all_dots = VGroup()
        for i in range(5):
            df_i = filter_data(df, scenario=i)
            dots = dot(df_i)
            dots.shift((2 - i) * UP + 3 * LEFT)
            self.add(dots)
            all_dots.add(dots)
            centroid = np.array([-2.98442898, 2.04385786, 0.0])
            label_position = centroid + 2.2 * LEFT - np.array([0, i, 0])
            label = Tex(f"Scenario \\textbf{i}", font_size=24, color=WHITE).move_to(label_position)
            self.play(FadeIn(dots, label))

        self.wait(2)
        self.play(all_dots.animate.set_opacity(0.1))
        previous_year_text = None
        centroid = np.array([-2.98442898, 2.04385786, 0.0])
        year_label_position = centroid + 5.25 * DOWN

        for year in range(2025, 2031):
            year_text = Tex(f"\\textbf{{Year {year}}}", font_size=26, color=YELLOW).move_to(year_label_position)
            new_dots = VGroup(
                *[
                    dots[i]
                    for dots, (_, scenario_data) in zip(all_dots, df.groupby("Scenario"))
                    for i, (_, row) in enumerate(scenario_data.iterrows())
                    if row["year"] == year
                ]
            )
            self.play(
                *[
                    dots[i].animate.set_color(YELLOW).set_opacity(0.5)
                    for dots, (_, scenario_data) in zip(all_dots, df.groupby("Scenario"))
                    for i, (_, row) in enumerate(scenario_data.iterrows())
                    if row["year"] == year
                ],
                Write(year_text) if not previous_year_text else ReplacementTransform(previous_year_text, year_text),
                run_time=1
            )
            previous_year_text = year_text
            self.wait(1)
            if year == 2030:
                break

        matrix = VGroup()
        start_position = np.array([0, 2.04385786, 0.0])
        cell_width = 0.4
        cell_height = 0.4
        store_count = 11
        scenarios = range(5)
        row_animations = []

        for i, scenario in enumerate(scenarios):
            row = VGroup()
            for j in range(store_count):
                cell = Rectangle(width=cell_width, height=cell_height, color=WHITE)
                cell.move_to(start_position + np.array([j * 0.5, -i, 0]))
                row.add(cell)
            matrix.add(row)
            row_animations.append(FadeIn(row, lag_ratio=0.1))

        scenario_labels = VGroup(*[Tex(f"{scenario}", font_size=18).next_to(matrix[i], LEFT)
                                   for i, scenario in enumerate(scenarios)])
        store_labels = VGroup(*[Tex(f"Store {j+1}", font_size=18).next_to(matrix[0][j], UP, buff=0.1)
                                for j in range(store_count)])
        matrix.add(scenario_labels, store_labels)

        left_brace = Brace(matrix, LEFT, buff=0.2).set_color(WHITE)
        right_brace = Brace(matrix, RIGHT, buff=0.2).set_color(WHITE)
        self.add(left_brace, right_brace)
        self.play(AnimationGroup(*row_animations, lag_ratio=0.5))
