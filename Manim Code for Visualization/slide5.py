from manim import *
import pandas as pd
import numpy as np
import random

LAVENDER = YELLOW

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

def dot(filtered_df, color=WHITE, opacity=0.3, radius=0.05, shift=ORIGIN, rotation=-PI / 2):
    dots = VGroup(
        *[
            Dot(normalize_coordinates(row.Lat, row.Lon), color=color, radius=radius).set_opacity(opacity)
            for _, row in filtered_df.iterrows()
        ]
    )
    return dots.move_to(shift).rotate_about_origin(rotation)

def process_points_across_scenarios(scene, df, all_dots, matrix):
    """
    Gradually animate whether each point is "kept" (high opacity, blue) or "excluded"
    (low opacity, white) for the first 5 scenarios. Display the exclusion text 
    ("Some projects don't happen in some scenarios.") before the changes occur.
    """
    points_decision = []

    # Display exclusion text
    exclusion_text = Tex("Some projects don't happen in some scenarios.", font_size=24).to_edge(DOWN)
    scene.play(FadeIn(exclusion_text), run_time=1)
    scene.wait(5)

    # Iterate through each scenario
    for i, dots_group in enumerate(all_dots[:5]):
        if len(dots_group) == 0:  # Skip empty dot groups
            continue

        decisions = []

        # Process all dots and cells for the current scenario together
        dot_animations = []
        cell_animations = []

        for j, dot_obj in enumerate(dots_group):
            if j >= len(matrix[i]):  # Ensure the index is valid for the matrix
                continue

            # Randomly decide to keep or exclude
            keep = random.choice([True, False])
            decisions.append(keep)

            # Define animations based on the decision
            if keep:
                dot_animation = dot_obj.animate.set_color(LAVENDER).set_opacity(0.8)
                cell_animation = matrix[i][j].animate.set_opacity(0).set_stroke(color=WHITE, opacity=1)
            else:
                dot_animation = dot_obj.animate.set_opacity(0.1).set_color(WHITE)
                cell_animation = matrix[i][j].animate.set_opacity(0).set_stroke(color=WHITE, opacity=0.5)

            dot_animations.append(dot_animation)
            cell_animations.append(cell_animation)

        # Play all animations for the current scenario together
        scene.play(*dot_animations, *cell_animations, run_time=1)
        points_decision.append(decisions)

    # Fade out exclusion text after all animations
    scene.play(FadeOut(exclusion_text), run_time=1)

    return points_decision






def highlight_points_and_matrix_by_sorted_store(
    scene, df, all_dots, matrix, points_decision, sorted_store_numbers
):
    """
    - If keep==True => bounding boxes + short date in cell + bottom text (Rooms, Banner, Month dd, yyyy).
    - If keep==False => bounding boxes + "0" in cell + bottom text "---".
    """
    previous_store_info = None

    # Precompute store index mapping for efficiency
    store_index_map = {store_no: idx for idx, store_no in enumerate(sorted_store_numbers)}

    for store_no in sorted_store_numbers:
        for scenario_index in range(min(5, len(points_decision))):
            df_row = df[
                (df["Store No."] == store_no)
                & (df["Scenario"] == scenario_index)
            ]
            if df_row.empty:
                continue

            store_index = store_index_map[store_no]
            if (
                store_index >= len(matrix[scenario_index])
                or store_index >= len(all_dots[scenario_index])
            ):
                continue

            keep = points_decision[scenario_index][store_index]
            dot_obj = all_dots[scenario_index][store_index]
            cell = matrix[scenario_index][store_index]

            dot_box = SurroundingRectangle(dot_obj, color=BLUE, buff=0.1)
            cell_box = SurroundingRectangle(cell, color=BLUE, buff=0.1)

            # "0" or "mm.yy" in the cell
            if keep:
                date_val = pd.to_datetime(df_row.iloc[0]["Ops Est Open"])
                short_date_str = date_val.strftime("%m.%y") 
                    
            else:
                short_date_str = "0"

            cell_text = Tex(short_date_str, font_size=16).move_to(cell.get_center())

            # Bottom text:
            if keep:
                date_val_full = pd.to_datetime(df_row.iloc[0]["Ops Est Open"])
                date_str_full = date_val_full.strftime("%B %d, %Y")
                store_info = Tex(
                    rf"\textbf{{{df_row.iloc[0]['Banner'].replace('&', r'\&')}}}, "
                    rf"Rooms: \textbf{{{df_row.iloc[0]['Project Rooms']}}}, "
                    rf"Open: \textbf{{{date_str_full}}}",
                    font_size=24
                ).to_edge(DOWN)
            else:
                store_info = Tex(
                    rf"This project doesn't happen in scenario \textbf{{{df_row.iloc[0]['Scenario']}}} ",
                    font_size=24
                ).to_edge(DOWN)

            # Animate bounding boxes, cell text, and bottom text together
            if previous_store_info is None:
                scene.play(
                    Create(dot_box),
                    Create(cell_box),
                    Write(cell_text),
                    Write(store_info),
                    run_time=1
                )
            else:
                scene.play(
                    Create(dot_box),
                    Create(cell_box),
                    Write(cell_text),
                    ReplacementTransform(previous_store_info, store_info),
                    run_time=1
                )

            previous_store_info = store_info

            # Fade out bounding boxes, keep cell text and bottom text
            scene.play(FadeOut(dot_box), FadeOut(cell_box), run_time=0.5)

    # Fade out the last store info
    if previous_store_info:
        scene.play(FadeOut(previous_store_info))


class YearlyVisualization(Scene):
    def construct(self):
        # 1) Read CSV
        df = pd.read_csv("Atlanta.csv")

        # 2) Sort by scenario ascending, lat descending (adjust to your needs)
        df.sort_values(by=["Scenario", "Lat"], ascending=[True, True], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 3) Build a store list in descending lat order
        store_lat_first = df.groupby("Store No.")["Lat"].first()
        store_lat_first.sort_values(ascending=False, inplace=True)
        sorted_store_numbers = store_lat_first.index.tolist()

        
        max_scenarios = 5
        store_count = len(sorted_store_numbers)
        start_position = np.array([0, 2.04385786, 0.0])
        cell_width = 0.4
        cell_height = 0.4
        previous_store_info = None
        all_dots = VGroup()
        matrix = VGroup()
        store_count = len(sorted_store_numbers)
        max_scenarios = 5
        start_position = np.array([0, 2.04385786, 0.0])
        cell_width = 0.4
        cell_height = 0.4

        for i in range(max_scenarios):
            df_i = filter_data(df, scenario=i)
            dots = dot(df_i)
            dots.shift((2 - i) * UP + 3 * LEFT)
            self.add(dots)
            all_dots.add(dots)

            row = VGroup()
            for j in range(store_count):
                cell = Rectangle(width=cell_width, height=cell_height, color=WHITE)
                cell.move_to(start_position + np.array([j * 0.5, -i, 0]))
                row.add(cell)
            matrix.add(row)

        self.add(matrix)
        left_brace = Brace(matrix, LEFT, buff=0.3).set_color(WHITE)
        right_brace = Brace(matrix, RIGHT, buff=0.3).set_color(WHITE)
        self.add(left_brace, right_brace)

        #######################################################################
        # 3) YELLOW HIGHLIGHT ANIMATION FOR EACH SCENARIO ROW (once only)
        #######################################################################
        for i in range(max_scenarios):
            highlight_dots = all_dots[i].animate.set_color(LAVENDER).set_opacity(1)
            highlight_row = matrix[i].animate.set_fill(LAVENDER, opacity=0.5)
            self.play(highlight_dots, highlight_row, run_time=0.5)

            reset_dots = all_dots[i].animate.set_color(WHITE).set_opacity(0.5)
            reset_row = matrix[i].animate.set_fill(WHITE, opacity=0.1)
            self.play(reset_dots, reset_row, run_time=0.5)

        self.play(all_dots.animate.set_opacity(0.1))

        # 3) Highlight each store index 'j' (original logic)
        for j in range(store_count):
            store_data = df.iloc[j]  # (This is just the j-th row in df)
            store_info = Tex(
                rf"\textbf{{{store_data['Banner'].replace('&', r'\&')}}}, "
                rf"Rooms: \textbf{{{store_data['Project Rooms']}}}, "
                "Date: Miscellaneous",
                font_size=24
            ).to_edge(DOWN)

            highlight_dots = [
                dots[k].animate.set_color(LAVENDER).set_opacity(1)
                for dots in all_dots
                for k in range(len(dots))
                if k == j
            ]
            highlight_cells = [
                row[j].animate.set_stroke(LAVENDER, opacity=1).set_fill(LAVENDER, opacity=0.5)
                for row in matrix
            ]
            dot_positions = [
                dots[k].get_center()
                for dots in all_dots
                for k in range(len(dots))
                if k == j
            ]
            dots_bounding_box = SurroundingRectangle(
                VGroup(*[Dot(pos) for pos in dot_positions]), color=BLUE, buff=0.2
            )
            cell_positions = [
                row[j].get_center()
                for row in matrix
            ]
            cells_bounding_box = SurroundingRectangle(
                VGroup(*[Dot(pos) for pos in cell_positions]), color=BLUE, buff=0.2
            )

            if not previous_store_info:
                self.play(
                    *highlight_dots,
                    *highlight_cells,
                    Create(dots_bounding_box, run_time=1, rate_func=lambda t: t**2),
                    Create(cells_bounding_box, run_time=1, rate_func=lambda t: t**2),
                    Write(store_info),
                )
            else:
                self.play(
                    *highlight_dots,
                    *highlight_cells,
                    Create(dots_bounding_box, run_time=1, rate_func=lambda t: t**2),
                    Create(cells_bounding_box, run_time=1, rate_func=lambda t: t**2),
                    ReplacementTransform(previous_store_info, store_info),
                )

            previous_store_info = store_info
            self.wait(0.1)
            self.play(
                FadeOut(dots_bounding_box, run_time=1.5),
                FadeOut(cells_bounding_box, run_time=1.5),
            )

            reset_dots = [
                dots[k].animate.set_color(WHITE).set_opacity(0.1)
                for dots in all_dots
                for k in range(len(dots))
                if k == j
            ]
            reset_cells = [
                row[j].animate.set_fill(WHITE, opacity=0.1).set_stroke(WHITE, opacity=1)
                for row in matrix
            ]
            self.play(*reset_dots, *reset_cells, run_time=0.2)

        self.play(FadeOut(previous_store_info))

        

        # 6) Example grouping highlight
        group_1 = [0, 1]
        group_2 = [2, 3, 4]
        k_means_text= Tex("Run K-Means, K=2", font_size=28)
        self.play(FadeIn(k_means_text.to_edge(DOWN)))

        def draw_rectangle(scenario_indices, color):
            points_positions = [dot.get_center() for i in scenario_indices for dot in all_dots[i]]
            points_box = SurroundingRectangle(
                VGroup(*[Dot(pos) for pos in points_positions]), color=color, buff=0.1
            )
            cells_positions = [cell.get_center() for i in scenario_indices for cell in matrix[i]]
            cells_box = SurroundingRectangle(
                VGroup(*[Dot(pos) for pos in cells_positions]), color=color, buff=0.25
            )
            return points_box, cells_box

        points_box_green, cells_box_green = draw_rectangle(group_1, GREEN)
        points_box_red, cells_box_red = draw_rectangle(group_2, RED)

        # Show both bounding boxes
        self.play(
            Create(points_box_green),
            Create(cells_box_green),
            Create(points_box_red),
            Create(cells_box_red),
            run_time=1
        )
        self.wait(2)
        
        self.play(*reset_cells)
        self.play(
            FadeOut(points_box_green),
            FadeOut(cells_box_green),
            FadeOut(points_box_red),
            FadeOut(cells_box_red),
            FadeOut(k_means_text),
        
        )
        for row in matrix:
            for cell in row:
                cell.set_opacity(0)


        
        matrix = VGroup()
        for i in range(max_scenarios):
            df_i = filter_data(df, scenario=i)
            dots = dot(df_i).shift((2 - i) * UP + 3 * LEFT)
            #self.add(dots)
            #all_dots.add(dots)

            row = VGroup()
            for j in range(store_count):
                cell = Rectangle(width=0.4, height=0.4, color=WHITE)
                cell.move_to(start_position + np.array([j * 0.5, -i, 0]))
                row.add(cell)
            matrix.add(row)

        self.add(matrix)


        points_decision = process_points_across_scenarios(self, df, all_dots, matrix)

        highlight_points_and_matrix_by_sorted_store(
            self, df, all_dots, matrix, points_decision, sorted_store_numbers
        )
        self.wait(10)
        


        group_1 = [0, 1, 2]
        group_2 = [3, 4]
        k_means_text= Tex("Run K-Means, K=2", font_size=28)
        self.play(FadeIn(k_means_text.to_edge(DOWN)))

        def draw_rectangle(scenario_indices, color):
            points_positions = [dot.get_center() for i in scenario_indices for dot in all_dots[i]]
            points_box = SurroundingRectangle(
                VGroup(*[Dot(pos) for pos in points_positions]), color=color, buff=0.1
            )
            cells_positions = [cell.get_center() for i in scenario_indices for cell in matrix[i]]
            cells_box = SurroundingRectangle(
                VGroup(*[Dot(pos) for pos in cells_positions]), color=color, buff=0.25
            )
            return points_box, cells_box

        points_box_green, cells_box_green = draw_rectangle(group_1, GREEN)
        points_box_red, cells_box_red = draw_rectangle(group_2, RED)

        # Show both bounding boxes
        self.play(
            Create(points_box_green),
            Create(cells_box_green),
            Create(points_box_red),
            Create(cells_box_red),
            run_time=1
        )
        self.wait(5)
        
        self.play(*reset_cells)
        self.play(
            FadeOut(points_box_green),
            FadeOut(cells_box_green),
            FadeOut(points_box_red),
            FadeOut(cells_box_red),
            FadeOut(k_means_text),
        
        )
