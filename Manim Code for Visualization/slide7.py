from manim import *
import pandas as pd
import random

# Define cell dimensions
CELL_WIDTH = 0.7
CELL_HEIGHT = 0.4

class ReferenceMatrix(Scene):

    

    def replace_state_with_dates(self, df):
        """
        Replace 'State/Province' with dates from 'Ops Est Open' in MM.YY format.
        """
        d = df.copy()
        d["State/Province"] = pd.to_datetime(d["Ops Est Open"]).dt.strftime("%m.%y")
        return d

    def random_zero_dates(self, df, p=0.3):
        """
        Randomly replace ~p% of 'State/Province' entries with '0'.
        """
        d = df.copy()
        for i in range(len(d)):
            if random.random() < p:
                d.at[d.index[i], "State/Province"] = "0"
        return d

    def create_reference_matrix(self, df, add_markers=False, max_display=12):
        """
        Create the reference matrix with optional markers.
        """
        scenarios = df["Scenario"].astype(str).tolist()
        stores    = df["Store No."].astype(str).tolist()
        states    = df["State/Province"].astype(str).tolist()

        if len(states) > max_display:
            half = max_display // 2
            scenarios = scenarios[:half] + ["..."] + scenarios[-(max_display-half-1):]
            stores    = stores[:half]    + ["..."] + stores[-(max_display-half-1):]
            states    = states[:half]    + ["..."] + states[-(max_display-half-1):]

        row_items = VGroup(*[Tex(s, font_size=12) for s in states])
        row_items.arrange(RIGHT, buff=0.5).to_edge(UP, buff=1)

        labels = VGroup()
        for sc, stno in zip(scenarios, stores):
            lbl = Tex(rf"\textbf{{{sc}|{stno}}}", font_size=11)
            labels.add(lbl)
        labels.arrange(RIGHT, buff=0.5)
        for lbl, itm in zip(labels, row_items):
            lbl.next_to(itm, UP, buff=0.2)
            lbl.rotate(45*DEGREES, about_point=lbl.get_bottom())

        markers = VGroup()
        if add_markers and len(states) > 0:
            desired_indices = [2, 5, -1, -4, -5]
            n = len(states)
            for idx in desired_indices:
                real_idx = idx if idx >= 0 else (n + idx)
                if 0 <= real_idx < n:
                    line = Line(
                        row_items[real_idx].get_bottom(),
                        row_items[real_idx].get_top(),
                        color=YELLOW, stroke_width=2
                    )
                    line.shift(RIGHT*0.25)
                    markers.add(line)

        lb = Tex(r"\textbf{[}", font_size=16).next_to(row_items, LEFT, buff=0.15)
        rb = Tex(r"\textbf{]}", font_size=16).next_to(row_items, RIGHT, buff=0.23)

        return row_items, labels, markers, lb, rb

    def create_cluster_matrix_rect_grid(self, df, max_rows=8, max_cols=10):
        """
        Create a pinned rectangular grid for cluster matrices.
        """
        self.grid_data = []  # To store cell data for highlighting

        scens = list(dict.fromkeys(df["Scenario"]))
        if len(scens) > max_rows:
            half = max_rows // 2
            scens = scens[:half] + ["..."] + scens[-(max_rows - half - 1):]

        all_rows = VGroup()

        for row_i, scn in enumerate(scens):
            if scn == "...":
                # Scenario ellipsis row
                sc_label = Tex(r"\textbf{...}", font_size=11)
                rect = Rectangle(width=CELL_WIDTH, height=CELL_HEIGHT, stroke_opacity=0)
                t = Tex("...", font_size=12).move_to(rect.get_center())
                cell = VGroup(rect, t)
                row_final = VGroup(sc_label, cell).arrange(RIGHT, buff=0.5)
                row_info = {"scenario": "...", "cells": [(t, None)]}
                self.grid_data.append(row_info)
                all_rows.add(row_final)
                continue

            sub = df[df["Scenario"] == scn].reset_index(drop=True)
            if len(sub) > (max_cols - 1):
                # Show first 6, '...', last 3
                first6 = sub.iloc[:6].copy()
                last3  = sub.iloc[-3:].copy()
                middle = pd.DataFrame([{"State/Province":"...", "Lon":"...", "Ops Est Open":"..."}])
                sub_short = pd.concat([first6, middle, last3], ignore_index=True)
            else:
                sub_short = sub.copy()

            squares = VGroup()
            texts   = VGroup()
            cell_info_list = []

            for col_i in range(max_cols):
                rect = Rectangle(width=CELL_WIDTH, height=CELL_HEIGHT, stroke_opacity=0)
                squares.add(rect)
                txt_str = ""
                row_data = None
                if col_i < len(sub_short):
                    row_data = sub_short.iloc[col_i].to_dict()
                    txt_str = str(row_data.get("State/Province",""))
                txt_mob = Tex(txt_str, font_size=12)
                texts.add(txt_mob)
                cell_info_list.append((txt_mob, row_data))

            squares.arrange(RIGHT, buff=0.1)
            for col_i in range(max_cols):
                texts[col_i].move_to(squares[col_i].get_center())

            row_of_cells = VGroup(squares, texts).arrange(OUT, buff=0)

            scenario_label = Tex(rf"\textbf{{{scn}}}", font_size=11)
            row_main = VGroup(scenario_label, row_of_cells).arrange(RIGHT, buff=0.5)

            # Shift top labels further right by adding a blank at the start
            if row_i == 0:
                top_labels = VGroup()
                # Add a blank label for the first cell to offset labels
                top_labels.add(Tex("", font_size=1))
                for col_i in range(1, max_cols):
                    data_idx = col_i - 1
                    if data_idx < len(sub_short):
                        rd = sub_short.iloc[data_idx].to_dict()
                        sc_  = rd.get("Scenario", "")
                        stno = rd.get("Store No.", "")
                        # Avoid adding labels for "..."
                        if sc_ == "..." or stno == "...":
                            label_txt = Tex("", font_size=1)
                        else:
                            label_txt = Tex(rf"\textbf{{{sc_}|{stno}}}", font_size=11)
                            label_txt.next_to(squares[col_i], UP, buff=0.1)
                            label_txt.rotate(45*DEGREES, about_point=label_txt.get_bottom())
                            # Further shift right to prevent overlap
                            label_txt.shift(RIGHT*0.2)
                        top_labels.add(label_txt)
                    else:
                        top_labels.add(Tex("", font_size=1))

                top_labels.arrange(RIGHT, buff=0.5)
                row_main = VGroup(top_labels, row_main).arrange(DOWN, buff=0.4, aligned_edge=RIGHT)

            row_info = {"scenario": scn, "cells": cell_info_list}
            self.grid_data.append(row_info)
            all_rows.add(row_main)

        all_rows.arrange(DOWN, buff=0.1)
        
        return VGroup(all_rows)

    def highlight_and_transform(self):
        """
        Perform the highlighting and transformation steps with pauses.
        This method executes each step sequentially with appropriate pauses.
        """
        # Step 1: Highlight zeros in blue (only if they have qualifying neighbors)
        blue_highlights = VGroup()
        zero_cells = []  # To store info about zeros for further steps
        neighbors_info = {}  # Mapping from zero cell to its neighbors

        max_cols = len(self.grid_data[0]["cells"])  # Assuming all rows have the same number of columns

        for row_idx, row_info in enumerate(self.grid_data):
            cells = row_info["cells"]  # list of (Text mob, row_data)
            for col_idx, (txt_mob, rd) in enumerate(cells):
                if rd is None:
                    continue
                if rd.get("State/Province", "") == "0":
                    # Determine neighbors based on column conditions
                    adjusted_col_idx = col_idx if col_idx >= 0 else max_cols + col_idx

                    # Initialize list of neighbor indices to highlight
                    target_indices = []

                    # Define column conditions
                    if adjusted_col_idx in [0, 3, max_cols - 3]:
                        # Only right neighbor
                        if (col_idx + 1) < max_cols:
                            target_indices.append(col_idx + 1)
                    elif adjusted_col_idx in [2, 5, max_cols - 1]:
                        # Only left neighbor
                        if (col_idx - 1) >= 0:
                            target_indices.append(col_idx - 1)
                    else:
                        # Both left and right neighbors
                        if (col_idx - 1) >= 0:
                            target_indices.append(col_idx - 1)
                        if (col_idx + 1) < max_cols:
                            target_indices.append(col_idx + 1)

                    # Collect valid neighbors based on the conditions
                    valid_neighbors = []
                    for nbr_idx in target_indices:
                        nbr_txt, nbr_rd = self.grid_data[row_idx]["cells"][nbr_idx]
                        val = str(nbr_rd.get("State/Province", ""))

                        # Skip neighbors that are "0" or "..."
                        if val in ["0", "..."]:
                            continue

                        # Create red square for the neighbor
                        red_sq = Rectangle(width=0.6, height=0.3)
                        red_sq.set_stroke(color=RED, width=3, opacity=0.5)
                        red_sq.set_fill(opacity=0)
                        red_sq.move_to(nbr_txt.get_center())

                        # Add the red square to the collection
                        #blue_highlights.add(red_sq)

                        # Store neighbor information for later use
                        valid_neighbors.append((nbr_idx, nbr_txt, nbr_rd, red_sq))

                    # Only add blue square if there are qualifying neighbors
                    if valid_neighbors:
                        blue_sq = Rectangle(width=0.6, height=0.3)
                        blue_sq.set_stroke(color=BLUE, width=3, opacity=1)
                        blue_sq.set_fill(opacity=0)
                        blue_sq.move_to(txt_mob.get_center())
                        blue_highlights.add(blue_sq)

                        # Append to zero_cells for transformation steps
                        zero_cells.append((row_idx, col_idx, txt_mob, rd))

                        # Map the valid neighbors to the current zero cell
                        neighbors_info[(row_idx, col_idx)] = valid_neighbors

        # Play step 1: Highlight zeros in blue
        if len(blue_highlights) > 0:
            self.play(FadeIn(blue_highlights))
        self.wait(6)  # Pause after step 1

        # Step 2: Highlight neighbors in red
        red_highlights = VGroup()
        for neighbors in neighbors_info.values():
            for _, _, _, red_sq in neighbors:
                red_highlights.add(red_sq)

        # Play step 2: Highlight neighbors in red
        if len(red_highlights) > 0:
            self.play(FadeIn(red_highlights))
        self.wait(6)  # Pause after step 2

        # Step 3: Choose closer neighbor based on Lon, adjust red squares
        transformations = []  # List to store transformation animations

        for (row_idx, col_idx, txt_mob, rd) in zero_cells:
            neighbors = neighbors_info.get((row_idx, col_idx), [])
            if not neighbors:
                continue
            # Extract Lon for zero
            zero_lon_raw = rd.get("Lon", None)
            try:
                zero_lon = float(zero_lon_raw)
            except:
                zero_lon = None

            # Calculate distances
            neighbor_distances = []
            for (nbr_idx, nbr_txt, nbr_rd, red_sq) in neighbors:
                nbr_lon_raw = nbr_rd.get("Lon", None)
                try:
                    nbr_lon = float(nbr_lon_raw)
                except:
                    nbr_lon = None
                if zero_lon is not None and nbr_lon is not None:
                    dist = abs(zero_lon - nbr_lon)
                else:
                    dist = float('inf')
                neighbor_distances.append((dist, (nbr_txt, nbr_rd, red_sq)))

            if not neighbor_distances:
                continue

            # Sort neighbors by distance
            neighbor_distances.sort(key=lambda x: x[0])

            # Best neighbor is first
            best_neighbor = neighbor_distances[0][1]
            best_nbr_txt, best_nbr_rd, best_red_sq = best_neighbor

            # Set opacity to 1 for best neighbor
            transformations.append(best_red_sq.animate.set_stroke(opacity=1))

            # Remove other neighbors' red squares
            for _, (nbr_txt, nbr_rd, red_sq) in neighbor_distances[1:]:
                transformations.append(FadeOut(red_sq))

        # Play step 3: Adjust red squares based on Lon
        if transformations:
            self.play(*transformations)
        self.wait(6)  # Pause after step 3

        # Step 4: Transform zero into neighbor's date
        transforms = []  # List to store transformation animations

        for (row_idx, col_idx, txt_mob, rd) in zero_cells:
            neighbors = neighbors_info.get((row_idx, col_idx), [])
            if not neighbors:
                continue
            # Extract Lon for zero
            zero_lon_raw = rd.get("Lon", None)
            try:
                zero_lon = float(zero_lon_raw)
            except:
                zero_lon = None

            # Calculate distances again to find the best neighbor
            neighbor_distances = []
            for (nbr_idx, nbr_txt, nbr_rd, red_sq) in neighbors:
                nbr_lon_raw = nbr_rd.get("Lon", None)
                try:
                    nbr_lon = float(nbr_lon_raw)
                except:
                    nbr_lon = None
                if zero_lon is not None and nbr_lon is not None:
                    dist = abs(zero_lon - nbr_lon)
                else:
                    dist = float('inf')
                neighbor_distances.append((dist, (nbr_txt, nbr_rd, red_sq)))

            if not neighbor_distances:
                continue

            # Sort neighbors by distance
            neighbor_distances.sort(key=lambda x: x[0])

            # Best neighbor is first
            best_neighbor = neighbor_distances[0][1]
            best_nbr_txt, best_nbr_rd, best_red_sq = best_neighbor

            # Get the date from the best neighbor
            best_date = best_nbr_rd.get("State/Province", "")
            if best_date not in ["0", "..."] and best_date != "":
                new_text = Tex(best_date, font_size=12).move_to(txt_mob.get_center())
                transforms.append(Transform(txt_mob, new_text))

        # Play step 4: Transform zeros into dates
        if transforms:
            self.play(*transforms)
        self.wait(6)  # Pause after step 4

    
    def construct(self):
        # Load your DataFrame
        df = pd.read_csv("output_with_metropolitan.csv")
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

        
        selected_scenario = 0 
        df_filtered = filter_data(df, scenario=selected_scenario)
        dots = dot(df_filtered)
        dots.shift(LEFT*1.2, DOWN)

        self.play(FadeIn(dots))
        self.wait(5)


        # STEP 1: Reference matrix sorted by Scenario and Store No.
        data1 = df.sort_values(["Scenario", "Store No."])
        r1, lab1, mk1, lb1, rb1 = self.create_reference_matrix(data1, add_markers=False)
        txt_ref = Tex("Reference =", font_size=18).next_to(r1, LEFT, buff=0.5)
        row_name = Tex("Scenario|Store", font_size=11).rotate(45*DEGREES, about_point=txt_ref.get_bottom())
        row_name.next_to(txt_ref, UP, buff=0.15)
        self.play(
            FadeIn(r1), FadeIn(lab1), FadeIn(mk1),
            FadeIn(lb1), FadeIn(rb1),
            FadeIn(txt_ref), FadeIn(row_name)
        )
        self.wait(6)  # Pause after step 1
        self.play(FadeOut(dots))
        step_1 =Tex("- Sort by State. Mark the boundaries of the states.", font_size=18)
        step_1.to_edge(LEFT, buff=1)
        step_1.shift(RIGHT, UP)
        self.play(Write(step_1))
        self.wait()

        # STEP 2: Sort by Scenario and State/Province with markers
        data2 = df.sort_values(["Scenario", "State/Province"])
        r2, lab2, mk2, lb2, rb2 = self.create_reference_matrix(data2, add_markers=True)
        self.play(
            TransformMatchingShapes(r1, r2),
            TransformMatchingShapes(lab1, lab2),
            TransformMatchingShapes(mk1, mk2),
            TransformMatchingShapes(lb1, lb2),
            TransformMatchingShapes(rb1, rb2)
        )
        self.wait(6)  # Pause after step 2

        step_2 =Tex("- Within the states, sort by ascending latitudes.", font_size=18)
        step_2.to_edge(LEFT, buff=1)
        step_2.shift(RIGHT, UP*0.45)
        self.play(Write(step_2))
        self.wait(2)

        # STEP 3: Sort by Scenario, State/Province, then Lat
        data3 = df.sort_values(["Scenario", "State/Province", "Lat"])
        r3, lab3, mk3, lb3, rb3 = self.create_reference_matrix(data3, add_markers=True)
        self.play(
            TransformMatchingShapes(r2, r3),
            TransformMatchingShapes(lab2, lab3),
            TransformMatchingShapes(mk2, mk3),
            TransformMatchingShapes(lb2, lb3),
            TransformMatchingShapes(rb2, rb3)
        )
        self.wait(6)  # Pause after step 3
        self.play(FadeOut(step_1,step_2))

        # STEP 4: Create cluster_states with pinned rectangular grid
        cluster_states = self.create_cluster_matrix_rect_grid(data3, max_rows=8, max_cols=10)
        cluster_states.next_to(r3, DOWN, buff=0.8)
        self.play(FadeIn(cluster_states))
        self.wait(6)  # Pause after step 4

        # STEP 5: Replace states with dates and create cluster_dates
        data_dates = self.replace_state_with_dates(data3)
        cluster_dates = self.create_cluster_matrix_rect_grid(data_dates, max_rows=8, max_cols=10)
        cluster_dates.move_to(cluster_states)
        self.play(TransformMatchingShapes(cluster_states, cluster_dates))
        self.wait(6)  # Pause after step 5

        # STEP 6: Replace some dates with zeros and create cluster_zeros
        data_zeroed = self.random_zero_dates(data_dates, p=0.35)  # 35% chance to become '0' for demonstration
        cluster_zeros = self.create_cluster_matrix_rect_grid(data_zeroed, max_rows=8, max_cols=10)
        cluster_zeros.move_to(cluster_dates)
        self.play(TransformMatchingShapes(cluster_dates, cluster_zeros))
        self.wait(6)  # Pause after step 6

        # STEP 7: Highlight zeros, handle neighbors, and transform
        self.highlight_and_transform()
        self.wait(3)  # Final pause
