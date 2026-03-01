import tkinter as tk
import customtkinter as ctk
import folium
import os
import webbrowser

# Set basic appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TrashMapperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KAMPAGA MAP PLOTTER")
        self.root.geometry("800x650")

        # File paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = current_dir if os.path.basename(current_dir) == ".venv" else os.path.join(current_dir, ".venv")
        self.txt_file = os.path.join(self.data_dir, "coordinates.txt")
        self.map_file = os.path.join(self.data_dir, "plotted_locations.html")

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)


        self._create_widgets()

    def _create_widgets(self):
        # Header (Top Frame)
        self.header = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#333333")
        self.header.pack(side="top", fill="x")

        self.title_label = ctk.CTkLabel(
            self.header, 
            text="LCC-D KAMPJAGA MAP PLOTTER", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="white"
        )
        self.title_label.pack(pady=(15, 2))

        self.desc_label = ctk.CTkLabel(
            self.header, 
            text="Data analysis software for the Research Project KAMPAJAGA SalvaBoat", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="white"
        )
        self.desc_label.pack(pady=(0, 2))

        self.branding = ctk.CTkLabel(
            self.header, 
            text="coded by @jwsephdev", 
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color="white"
        )
        self.branding.pack(pady=(0, 15))

        # Main Workspace
        self.workspace = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.workspace.pack(fill="both", expand=True, padx=30, pady=20)

        # Content Frame (Splits Sidebar and Text)
        self.content_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # LEFT SIDEBAR
        self.sidebar = ctk.CTkFrame(self.content_frame, width=160, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)

        self.save_btn = ctk.CTkButton(
            self.sidebar, 
            text="Save & Plot", 
            command=self.save_and_plot,
            corner_radius=10,
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.save_btn.pack(fill="x", pady=(20, 5), padx=10)

        self.open_btn = ctk.CTkButton(
            self.sidebar, 
            text="View Map", 
            command=self.open_external,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.open_btn.pack(fill="x", pady=5, padx=10)

        self.clear_btn = ctk.CTkButton(
            self.sidebar, 
            text="Clear List", 
            command=self.clear_entries,
            corner_radius=10,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.clear_btn.pack(fill="x", pady=5, padx=10)

        # Locations Plotted Counter
        self.count_var = tk.StringVar(value="LOCATIONS\nPLOTTED: 0")
        self.count_label = ctk.CTkLabel(
            self.sidebar, 
            textvariable=self.count_var,
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.count_label.pack(side="top", pady=(30, 10))

        # RIGHT INPUT BOX
        self.coords_text = ctk.CTkTextbox(
            self.content_frame, 
            corner_radius=15,
            font=ctk.CTkFont(family="Consolas", size=13),
            border_width=1,
            border_color="#3e3e42"
        )
        self.coords_text.pack(side="left", fill="both", expand=True)
        self.coords_text.insert("1.0", "14.111700992815708, 122.95587958866973\n14.111520204762945, 122.9559231745658\n14.111666526039748, 122.95563282544262\n14.11165286939122, 122.95551346714257")

        # BOTTOM STATUS
        self.status_var = tk.StringVar(value="Status: Software is Idle")
        self.status_label = ctk.CTkLabel(
            self.workspace, 
            textvariable=self.status_var,
            text_color="#007acc",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.status_label.pack(side="bottom", pady=(15, 0))

    def clear_entries(self):
        self.coords_text.delete("1.0", "end")
        self.count_var.set("LOCATIONS\nPLOTTED: 0")
        self.status_var.set("Status: List cleared. Software is Idle")

    def open_external(self):
        coords = self.parse_coordinates()
        if not coords:
            self.status_var.set("❌ Error: Enter coordinates before viewing the map!")
            return

        if os.path.exists(self.map_file):
            file_path = os.path.abspath(self.map_file)
            webbrowser.open(f"file:///{file_path}")
            self.status_var.set("✅ Map opened in external browser.")
        else:
            self.status_var.set("❌ Error: Map file not found. Click 'Save & Plot' first!")

    def parse_coordinates(self):
        content = self.coords_text.get("1.0", "end-1c").strip()
        if not content: return []
        coords_list = []
        for line in content.split('\n'):
            line = line.strip().lstrip('(').rstrip(')')
            if not line: continue
            try:
                parts = line.split(',')
                if len(parts) == 2:
                    coords_list.append((float(parts[0].strip()), float(parts[1].strip())))
            except ValueError: continue
        return coords_list

    def save_and_plot(self):
        coords = self.parse_coordinates()
        if not coords:
            self.status_var.set("❌ Error: No coordinates to save!")
            return

        try:
            self.status_var.set("Saving data to txt...")
            with open(self.txt_file, "w", encoding="utf-8") as file:
                for lat, lon in coords:
                    file.write(f"Trash Detected at: ({lat}, {lon})\n")
            
            self.status_var.set("Generating folium map...")
            world_map = folium.Map(location=coords[0], zoom_start=20, tiles='CartoDB positron')
            for lat, lon in coords:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    weight=0,
                    fill=True,
                    fill_color="red",
                    fill_opacity=1
                ).add_to(world_map)
            
            world_map.save(self.map_file)
            self.count_var.set(f"LOCATIONS\nPLOTTED: {len(coords)}")
            self.status_var.set(f"✅ Success! Saved to: {self.txt_file}")
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = TrashMapperUI(root)
    root.mainloop()
