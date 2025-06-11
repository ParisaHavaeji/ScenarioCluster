from manim import *
import json
import numpy as np

# Helper functions
def load_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def normalize_coordinates(lat, lon):
    x = (lon + 125) / (125 - 66) * 10 - 5
    y = (lat - 25) / (49 - 25) * 6 - 3
    return np.array([x * 0.7 + 2, y * 0.7, 0])

def create_dots_for_year(positions, all_points_set):
    new_positions = [
        normalize_coordinates(lat, lon)
        for lat, lon in positions
        if (lat, lon) not in all_points_set
    ]
    all_points_set.update((lat, lon) for lat, lon in positions)
    return VGroup(*[Dot(pos, color="#E6E6FA", radius=0.05).set_opacity(0.3) for pos in new_positions])

def create_first_three_lines():
    """Create the first three lines of text."""
    return VGroup(
        Tex("\\textbf{50 Scenarios}", font_size=24),
        Tex("\\textbf{751 Projects per Scenario}", font_size=24),
        Tex("\\textbf{Features:}", font_size=24).set_color(YELLOW),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(LEFT, buff=1.0).shift(UP * 1)

def create_features_text(baseline):
    """Create the remaining lines of text under 'Features'."""
    features = VGroup(
        Tex("- Latitude, Longitude", font_size=20).shift(RIGHT * 0.5),
        Tex("- Opening Time (5-year period)", font_size=20).shift(RIGHT * 0.5),
        Tex("- Number of Rooms", font_size=20).shift(RIGHT * 0.5),
        Tex("- State/Province", font_size=20).shift(RIGHT * 0.5),
        Tex("- Binary: Metropolitan Area (Yes/No)", font_size=20).shift(RIGHT * 0.5),
        Tex("- Other attributes: Store Number, Zipcode, etc.", font_size=20).shift(RIGHT * 0.5),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    features.next_to(baseline, DOWN, aligned_edge=LEFT, buff=0.3)  # Position relative to 'Features'
    return features

def create_title():
    return Tex("\\textbf{Output of Demand Scenarios}", font_size=32).to_edge(UP, buff=0.5)

class USMapDemandScenarios(Scene):
    def construct(self):
        # Load data
        preprocessed_file = "grouped_points.json"
        grouped_by_year = load_data(preprocessed_file)

        # Create components
        first_three_lines = create_first_three_lines().shift(UP * 0.5)  # Shift text up slightly
        title = create_title()

        # Plot the title
        def plot_title():
            self.play(FadeIn(title, run_time=1.5))
            self.wait(1.0)  # Add a short pause after the title appears

        # Plot first three lines of text function
        def plot_first_three_lines():
            for line in first_three_lines:
                self.play(FadeIn(line, run_time=0.5))
                self.wait(0.5)

        # Plot remaining features text function
        def plot_features_text():
            # Dynamically create the features text relative to the last line ('Features')
            features_text = create_features_text(first_three_lines[-1])
            features_text.shift(RIGHT * 0.5)  # Shift features text slightly to the right
            self.play(FadeIn(features_text, run_time=1.5))

        # Plot points function
        def plot_points():
            all_points_set = set()
            all_points_group = VGroup()
            year_label_position = np.array([2.45, -2.75, 0])  # Fixed position beneath points
            previous_year_text = None

            for year, positions in grouped_by_year.items():
                new_dots = create_dots_for_year(positions, all_points_set)
                year_text = Tex(f"\\textbf{{Scenario 0\\\\Year {year}}}", font_size=24).move_to(year_label_position)

                # Plot dots and year text
                self.play(
                    FadeIn(new_dots, run_time=1.5),
                    Write(year_text) if not previous_year_text else ReplacementTransform(previous_year_text, year_text),
                )
                previous_year_text = year_text
                all_points_group.add(new_dots)

                # Stop early if year is 2030
                if int(year) == 2030:
                    break

            # Keep the last year text static
            self.add(previous_year_text)

        # Execute the animations in the desired order
        plot_title()  # Plot the title first
        plot_first_three_lines()  # Plot the first three lines sequentially
        self.wait(2.0)
        plot_features_text()  # Plot the features text simultaneously

        # Add a delay before the points start
        self.wait(5.0)  # Longer lag before points appear

        plot_points()  # Plot the points after all the text is done

        # Wait at the end
        self.wait(7)
