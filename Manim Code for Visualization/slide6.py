from manim import *
import pandas as pd
import numpy as np

def normalize_coordinates(lat, lon):
    # Normalize coordinates to fit into the scene's coordinate system
    x = (lon + 125) / (125 - 66) * 10 - 5
    y = (lat - 25) / (49 - 25) * 6 - 3
    return np.array([x * 0.7 + 2, y * 0.7, 0])

def create_dots_for_year(positions, all_points_set):
    # Create new dots for unique latitude and longitude positions
    new_positions = [
        normalize_coordinates(lat, lon)
        for lat, lon in positions
        if (lat, lon) not in all_points_set
    ]
    all_points_set.update((lat, lon) for lat, lon in positions)
    return VGroup(*[Dot(pos, color="#E6E6FA", radius=0.02).set_opacity(0.4) for pos in new_positions])

def filter_data(df, scenario):
    # Filter data for a specific scenario
    return df[df["Scenario"] == scenario]

def dot(filtered_data):
    # Create dots for the filtered data
    positions = list(zip(filtered_data["Lat"], filtered_data["Lon"]))
    all_points_set = set()
    return create_dots_for_year(positions, all_points_set)

class ReferenceMatrix(Scene):
    def create_reference_matrix(
        self,
        data: pd.DataFrame,
        max_display: int = 10,
        add_markers: bool = False,
        font_size_states: int = 12,
        font_size_labels: int = 11,
        buff_between_items: float = 0.5,
    ):
        """
        Create a horizontal 'matrix' (really just a row) of text elements
        for the states, plus a corresponding row of angled labels (scenario|store).
        
        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing 'Scenario', 'Store No.', and 'State/Province'.
        max_display : int
            Limit the number of entries (show first and last with an ellipsis in between).
        add_markers : bool
            Whether or not to add boundary markers between state changes.
        font_size_states : int
            Font size for the states row.
        font_size_labels : int
            Font size for the angled scenario|store labels.
        buff_between_items : float
            Spacing between adjacent items in the row.

        Returns
        -------
        tuple(VGroup, VGroup, VGroup)
            Returns (states_row, labels_row, markers_group)
            markers_group can be empty if add_markers=False.
        """

        # Extract relevant columns
        scenario_numbers = data["Scenario"].astype(str).tolist()
        store_numbers = data["Store No."].astype(str).tolist()
        states = data["State/Province"].astype(str).tolist()

        # Limit how many we show, placing an ellipsis in the middle if needed
        if len(states) > max_display:
            scenario_numbers = scenario_numbers[:6] + ["..."] + scenario_numbers[-(max_display - 6) :]
            store_numbers    = store_numbers[:6] + ["..."] + store_numbers[-(max_display - 6) :]
            states           = states[:6] + ["..."] + states[-(max_display - 6) :]

        # Create the row of states
        states_row = VGroup(*[
            Text(state, font_size=font_size_states) for state in states
        ])
        states_row.arrange(RIGHT, buff=buff_between_items)
        states_row.to_edge(UP, buff=1)

        # Create angled scenario|store labels
        labels_row = VGroup()
        for scenario, store in zip(scenario_numbers, store_numbers):
            label_text = Tex(rf"\textbf{{{scenario}|{store}}}", font_size=font_size_labels)
            labels_row.add(label_text)

        labels_row.arrange(RIGHT, buff=buff_between_items)
        for label, entry in zip(labels_row, states_row):
            label.next_to(entry, UP, buff=0.2)
            label.rotate(45 * DEGREES, about_point=label.get_bottom())

        # Optionally add boundary markers where state changes
        markers_group = VGroup()
        if add_markers:
            state_end_indices = []
            if states:  # only if we actually have any states
                prev_state = states[0]
                for i, state in enumerate(states):
                    if state != prev_state:
                        state_end_indices.append(i - 1)
                        prev_state = state
                state_end_indices.append(len(states) - 1)

            for idx in state_end_indices:
                # Draw a vertical line across the top/bottom of that entry
                marker = Line(
                    start=states_row[idx].get_bottom(),
                    end=states_row[idx].get_top(),
                    stroke_width=2,
                    color=YELLOW,
                )
                # shift a small amount to the right so it doesn't overlap text
                marker.shift(RIGHT * 0.25)
                markers_group.add(marker)

        return states_row, labels_row, markers_group
    
class ReferenceMatrix(Scene):
    def construct(self):
        # Load the dataset
        df = pd.read_csv("output_with_metropolitan.csv")

        # Extract relevant columns
        scenario_numbers = df["Scenario"].astype(str).tolist()
        store_numbers = df["Store No."].astype(str).tolist()
        states = df["State/Province"].astype(str).tolist()

        # Limit the number of entries displayed
        max_display = 10
        if len(states) > max_display:
            scenario_numbers = scenario_numbers[:6] + ["..."] + scenario_numbers[-7:]
            store_numbers = store_numbers[:6] + ["..."] + store_numbers[-7:]
            states = states[:6] + ["..."] + states[-7:]

        # Create a group for the Reference matrix elements (states)
        reference_matrix_1 = VGroup(*[
            Text(state, font_size=12) for state in states
        ])
        reference_matrix_1.arrange(RIGHT, buff=0.5)
        reference_matrix_1.to_edge(UP, buff=1)

        # Create labels (Scenario/Store No.) above each matrix entry
        labels = VGroup()
        for scenario, store in zip(scenario_numbers, store_numbers):
            label_text = Tex(rf"\textbf{{{scenario}|{store}}}", font_size=11)
            labels.add(label_text)

        labels.arrange(RIGHT, buff=0.5)
        for label, entry in zip(labels, reference_matrix_1):
            label.next_to(entry, UP, buff=0.2)
            label.rotate(45 * DEGREES, about_point=label.get_bottom())

        # Add braces to the matrix
        left_brace = Tex(r"\textbf{[}", font_size=16)
        right_brace = Tex(r"\textbf{]}", font_size=16)
        left_brace.next_to(reference_matrix_1, LEFT, buff=0.15)
        right_brace.next_to(reference_matrix_1, RIGHT, buff=0.23)

        # Label the matrix as "Reference"
        reference_label = Text("Reference =", font_size=18, color=WHITE)
        reference_label.next_to(reference_matrix_1, LEFT, buff=0.5)
        row_name = Tex("Scenario|Store", font_size=11, color=WHITE)
        row_name.rotate(45 * DEGREES, about_point=reference_label.get_bottom())
        row_name.next_to(reference_label, UP, buff=0.15)

        

        selected_scenario = 0 
        df_filtered = filter_data(df, scenario=selected_scenario)
        dots = dot(df_filtered)
        dots.next_to(reference_matrix_1, DOWN, buff=0.2)
        dots.shift(LEFT*1.2, UP)

        self.play(FadeIn(dots))
        self.wait(5)

        # Animate the creation of the reference matrix
        self.play(
            LaggedStartMap(FadeIn, labels, lag_ratio=0.1),  # Fade in labels with a lag
            FadeIn(reference_label),  # Fade in the reference label
            FadeIn(row_name),  # Fade in the row name
            FadeIn(left_brace),  # Fade in the left brace
            FadeIn(right_brace),  # Fade in the right brace
            LaggedStartMap(FadeIn, reference_matrix_1, lag_ratio=0.1),  # Fade in the matrix with a lag
        )


        

        self.wait(6)
        self.play(FadeOut(dots))
        step_1 =Tex("- Sort by State. Mark the boundaries of the states.", font_size=18)
        step_1.next_to(reference_label, DOWN, buff=1)
        step_1.shift(RIGHT)
        self.play(Write(step_1))
        self.wait()
        
        grouped = df.groupby("Scenario")
        sorted_data = (
            grouped.apply(lambda group: group.sort_values("State/Province"))
            .reset_index(drop=True)
        )

        # Extract relevant columns
        scenario_numbers = sorted_data["Scenario"].astype(str).tolist()
        store_numbers = sorted_data["Store No."].astype(str).tolist()
        states = sorted_data["State/Province"].astype(str).tolist()

        # Limit the number of entries displayed
        max_display = 10
        if len(states) > max_display:
            scenario_numbers = scenario_numbers[:6] + ["..."] + scenario_numbers[-7:]
            store_numbers = store_numbers[:6] + ["..."] + store_numbers[-7:]
            states = states[:6] + ["..."] + states[-7:]

        reference_matrix_2 = VGroup(*[Text(state, font_size=12) for state in states])
        reference_matrix_2.arrange(RIGHT, buff=0.5)
        reference_matrix_2.to_edge(UP, buff=1)

        labels_2 = VGroup()
        for scenario, store in zip(scenario_numbers, store_numbers):
            label_text = Tex(rf"\textbf{{{scenario}|{store}}}", font_size=11)
            labels_2.add(label_text)

        labels_2.arrange(RIGHT, buff=0.5)
        for label, entry in zip(labels_2, reference_matrix_2):
            label.next_to(entry, UP, buff=0.2)
            label.rotate(45 * DEGREES, about_point=label.get_bottom())

    
        state_end_indices = []
        prev_state = states[0]
        for i, state in enumerate(states):
            if state != prev_state:
                state_end_indices.append(i - 1) 
                prev_state = state

        
        state_end_indices.append(len(states) - 1)

        
        markers = VGroup()
        for idx in state_end_indices:
            marker = Line(
                start=reference_matrix_2[idx].get_bottom(),
                end=reference_matrix_2[idx].get_top(),
                stroke_width=2,
                color=YELLOW,
            )
            marker.shift(RIGHT * 0.25)
            markers.add(marker)

        self.play(
            Transform(reference_matrix_1, reference_matrix_2),
            Transform(labels, labels_2),
            FadeIn(markers)
        )
        self.wait(2)

        step_2 =Tex("- Within the states, sort by ascending latitudes.", font_size=18)
        step_2.next_to(step_1, DOWN, buff=1)
        self.play(Write(step_2))
        self.wait(2)

        sorted_data_by_scenario_state_latitude = (
            df.sort_values(["Scenario", "State/Province", "Lat"])
            .reset_index(drop=True)
        )

        # Extract relevant columns
        scenarios = sorted_data_by_scenario_state_latitude["Scenario"].astype(str).tolist()
        states = sorted_data_by_scenario_state_latitude["State/Province"].astype(str).tolist()
        latitudes = sorted_data_by_scenario_state_latitude["Lat"].astype(str).tolist()
        store_numbers = sorted_data_by_scenario_state_latitude["Store No."].astype(str).tolist()

        # Limit the number of entries displayed
        max_display = 10
        if len(states) > max_display:
            scenarios = scenarios[:6] + ["..."] + scenarios[-7:]
            states = states[:6] + ["..."] + states[-7:]
            store_numbers = store_numbers[:6] + ["..."] + store_numbers[-7:]
            latitudes = latitudes[:6] + ["..."] + latitudes[-7:]

        # Create the sorted matrix (reference_matrix_3)
        reference_matrix_3 = VGroup(*[Text(state, font_size=12) for state in states])
        reference_matrix_3.arrange(RIGHT, buff=0.5)
        reference_matrix_3.to_edge(UP, buff=1)

        # Create labels for the sorted matrix
        labels_3 = VGroup()
        for scenario, store, latitude in zip(scenarios, store_numbers, latitudes):
            label_text = Tex(rf"\textbf{{{scenario}|{store}}}", font_size=11)
            labels_3.add(label_text)

        labels_3.arrange(RIGHT, buff=0.5)
        for label, entry in zip(labels_3, reference_matrix_3):
            label.next_to(entry, UP, buff=0.2)
            label.rotate(45 * DEGREES, about_point=label.get_bottom())

        # Identify where state and scenario groups end for markers
        group_end_indices = []
        prev_scenario = scenarios[0]
        prev_state = states[0]
        for i, (scenario, state) in enumerate(zip(scenarios, states)):
            if scenario != prev_scenario or state != prev_state:
                group_end_indices.append(i - 1)  # Mark the last index of the group
                prev_scenario = scenario
                prev_state = state

        # Add the final group end if not already included
        group_end_indices.append(len(states) - 1)

        # Add markers (lines) for the scenario and state boundaries
        markers = VGroup()
        for idx in group_end_indices:
            marker = Tex(r"$\triangle$", font_size=16, color=YELLOW)
            marker.next_to(reference_matrix_3[idx], UP, buff=0.1)
            markers.add(marker)

        # Add the sorted matrix to the scene
        self.play(
            Transform(reference_matrix_2, reference_matrix_3),
            Transform(labels_2, labels_3),
            FadeIn(markers)
        )
        self.wait(2)


