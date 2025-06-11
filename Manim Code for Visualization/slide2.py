from manim import *
import json
import numpy as np

def load_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def normalize_coordinates(lat, lon):
    x = (lon + 125) / (125 - 66) * 10 - 5
    y = (lat - 25) / (49 - 25) * 6 - 3
    return np.array([x * 0.7 + 2, y * 0.7, 0])

def create_dots_for_year(positions, all_points_set):
    """
    Creates Dot mobjects for positions that have not
    yet appeared in all_points_set.
    `positions` is expected to be a list of (lat, lon) pairs.
    """
    new_positions = []
    for entry in positions:
        # We assume these are just (lat, lon)
        if len(entry) >= 2:
            lat, lon = entry[:2]
            # Only add if not already in our set
            if (lat, lon) not in all_points_set:
                new_positions.append(normalize_coordinates(lat, lon))
                all_points_set.add((lat, lon))

    return VGroup(
        *[Dot(pos, color="#E6E6FA", radius=0.03).set_opacity(0.5)
          for pos in new_positions]
    )

def create_first_three_lines():
    return VGroup(
        Tex("\\textbf{50 Scenarios}", font_size=24),
        Tex("\\textbf{751 Projects per Scenario}", font_size=24),
        Tex("\\textbf{Features:}", font_size=24).set_color(YELLOW),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(LEFT, buff=1.0).shift(UP)

def create_features_text(baseline):
    features = VGroup(
        Tex("- Latitude, Longitude", font_size=20).shift(RIGHT * 0.5),
        Tex("- Opening Time (5-year period)", font_size=20).shift(RIGHT * 0.5),
        Tex("- Number of Rooms", font_size=20).shift(RIGHT * 0.5),
        Tex("- State/Province", font_size=20).shift(RIGHT * 0.5),
        Tex("- Binary: Metropolitan Area (Yes/No)", font_size=20).shift(RIGHT * 0.5),
        Tex("- Other attributes: Store Number, Zipcode, etc.", font_size=20).shift(RIGHT * 0.5),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    features.next_to(baseline, DOWN, aligned_edge=LEFT, buff=0.3)
    return features

def create_title():
    return Tex("\\textbf{Output of Demand Scenarios}", font_size=32).to_edge(UP, buff=0.5)

def filter_points_by_state(positions, state, all_points_set):
    """
    Filters positions for a specific state. If an entry doesn't have a
    state, it is simply skipped.
    Expected format: (lat, lon, st)
    """
    filtered_positions = []
    for entry in positions:
        # Only process if we truly have three elements
        if len(entry) == 3:
            lat, lon, current_state = entry
            if current_state == state and (lat, lon) not in all_points_set:
                filtered_positions.append(normalize_coordinates(lat, lon))
                all_points_set.add((lat, lon))

    return VGroup(
        *[Dot(pos, color="#FFA07A", radius=0.05).set_opacity(0.5)
          for pos in filtered_positions]
    )

def plot_filtered_points(scene, grouped_by_year):
    """
    This function attempts to show GA-only points. It assumes each
    year's positions may have the format (lat, lon, state). If they
    don't, the filtering step will simply skip them.
    """
    all_points_set = set()
    year_label_position = np.array([2.45, -3.25, 0])
    previous_year_text = None
    for year, positions in grouped_by_year.items():
        filtered_dots = filter_points_by_state(positions, "GA", all_points_set)
        year_text = Tex(f"\\textbf{{GA Only\\\\Year {year}}}", font_size=24).move_to(year_label_position)
        scene.play(
            FadeIn(filtered_dots, run_time=1.5),
            Write(year_text) if not previous_year_text else ReplacementTransform(previous_year_text, year_text),
        )
        previous_year_text = year_text
        # stop at 2030, if that's your intention
        if int(year) == 2030:
            break
    scene.add(previous_year_text)

class USMapDemandScenarios(ThreeDScene):
    def construct(self):
        grouped_by_year = load_data("grouped_points.json")
        first_three_lines = create_first_three_lines().shift(UP * 0.5)
        title = create_title()

        def plot_title():
            self.play(FadeIn(title, run_time=1.5))
            self.wait(1.0)

        def plot_first_three_lines():
            for line in first_three_lines:
                self.play(FadeIn(line, run_time=0.5))
                self.wait(0.5)

        def plot_features_text():
            features_text = create_features_text(first_three_lines[-1])
            features_text.shift(RIGHT * 0.5)
            self.play(FadeIn(features_text, run_time=1.5))
            return features_text

        def plot_points():
            all_points_set = set()
            all_points_group = VGroup()
            year_label_position = np.array([2.45, -2.75, 0])
            previous_year_text = None
            for year, positions in grouped_by_year.items():
                new_dots = create_dots_for_year(positions, all_points_set)
                year_text = Tex(f"\\textbf{{Scenario 0\\\\Year {year}}}", font_size=24).move_to(year_label_position)
                self.play(
                    FadeIn(new_dots, run_time=1.5),
                    Write(year_text) if not previous_year_text else ReplacementTransform(previous_year_text, year_text),
                )
                previous_year_text = year_text
                all_points_group.add(new_dots)
                if int(year) == 2030:
                    break
            self.add(previous_year_text)
            return all_points_group, previous_year_text

        # -----------------------------------------------
        #    Actual animation sequence
        # -----------------------------------------------
        plot_title()
        plot_first_three_lines()
        self.wait(2.0)
        features_text = plot_features_text()
        self.wait(5.0)
        points_group, year_text = plot_points()
        self.wait(7)

        
        self.add_fixed_in_frame_mobjects(first_three_lines, title, features_text, year_text)

    
        #plot_filtered_points(self, grouped_by_year)
