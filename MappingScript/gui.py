import tkinter as tk
import customtkinter as ctk
import folium
import os
import webbrowser
import serial
import serial.tools.list_ports
import threading
import time
import re


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TrashMapperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KAMPAGA MAP PLOTTER")
        self.root.geometry("1000x700") 

        self.serial_port = None
        self.is_monitoring = False
        self.monitor_thread = None

        # File paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = current_dir if os.path.basename(current_dir) == ".venv" else os.path.join(current_dir, ".venv")
        self.txt_file = os.path.join(self.data_dir, "coordinates.txt")
        self.map_file = os.path.join(self.data_dir, "plotted_locations.html")

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self._create_widgets()
        self.refresh_ports()


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
        self.sidebar = ctk.CTkFrame(self.content_frame, width=220, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)

        # Bluetooth Section
        self.bt_label = ctk.CTkLabel(self.sidebar, text="BLUETOOTH MONITOR", font=ctk.CTkFont(size=13, weight="bold"))
        self.bt_label.pack(pady=(20, 5), padx=10)

        self.port_combobox = ctk.CTkComboBox(self.sidebar, values=["Scanning..."], font=ctk.CTkFont(size=11))
        self.port_combobox.pack(pady=5, padx=10, fill="x")

        self.refresh_btn = ctk.CTkButton(
            self.sidebar, text="Refresh Ports", command=self.refresh_ports, 
            height=24, font=ctk.CTkFont(size=11), fg_color="#3a3a3a"
        )
        self.refresh_btn.pack(pady=5, padx=10, fill="x")

        self.start_btn = ctk.CTkButton(
            self.sidebar, text="Begin Monitoring", command=self.start_monitoring,
            fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(size=12, weight="bold")
        )
        self.start_btn.pack(pady=(15, 5), padx=10, fill="x")

        self.stop_btn = ctk.CTkButton(
            self.sidebar, text="End Monitoring", command=self.stop_monitoring,
            fg_color="#dc3545", hover_color="#c82333", font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled"
        )
        self.stop_btn.pack(pady=5, padx=10, fill="x")

        # Separator-like label
        ctk.CTkLabel(self.sidebar, text="───────────────────", text_color="#3a3a3a").pack(pady=10)

        # Plotting Section
        self.save_btn = ctk.CTkButton(
            self.sidebar, 
            text="Save & Plot", 
            command=self.save_and_plot,
            corner_radius=10,
            fg_color="#007acc",
            hover_color="#005fa3",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.save_btn.pack(fill="x", pady=5, padx=10)

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
        self.count_label.pack(side="bottom", pady=20)


        # RIGHT INPUT BOX
        self.coords_text = ctk.CTkTextbox(
            self.content_frame, 
            corner_radius=15,
            font=ctk.CTkFont(family="Consolas", size=13),
            border_width=1,
            border_color="#3e3e42"
        )
        self.coords_text.pack(side="left", fill="both", expand=True)

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
        if self.is_monitoring:
            self.status_var.set("❌ Error: End monitoring before opening the map!")
            return

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
        
        # We'll use a state machine that handles separate Date and Time lines
        # and buffers numbers until they form valid pairs.
        candidate_numbers = []
        current_ts = "N/A"
        date_buff = ""
        time_buff = ""
        
        for line in content.split('\n'):
            line = line.strip()
            if not line: continue
            
            # 1. Identify Timestamp components in this line
            b_match = re.search(r"\[(.*?)\]", line)
            dt_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", line)
            tm_match = re.search(r"(\d{2}:\d{2}(?::\d{2})?)", line)
            
            found_new_ts = False
            if b_match:
                current_ts = b_match.group(1)
                found_new_ts = True
            elif dt_match or tm_match:
                if dt_match: date_buff = dt_match.group(1)
                if tm_match: time_buff = tm_match.group(1)
                
                # Combine what we have so far
                if date_buff and time_buff:
                    current_ts = f"{date_buff} {time_buff}"
                elif date_buff:
                    current_ts = date_buff
                else: 
                    current_ts = time_buff
                found_new_ts = True

            # If we just found/updated a timestamp, retroactively apply it to any "N/A" candidates
            # (This is crucial for the Lat \n Long \n Date \n Time sequence)
            if found_new_ts:
                for cand in reversed(candidate_numbers):
                    if cand['ts'] == "N/A": 
                        cand['ts'] = current_ts
                    else: 
                        break

            # 2. Extract numbers while ignoring the timestamp strings themselves
            clean_line = line
            if b_match: clean_line = clean_line.replace(b_match.group(0), "")
            if dt_match: clean_line = clean_line.replace(dt_match.group(0), "")
            if tm_match: clean_line = clean_line.replace(tm_match.group(0), "")
            
            # Look for coordinate-like numbers
            nums = re.findall(r"[-+]?\d+\.\d+", clean_line) # Priority on decimals
            if not nums:
                nums = re.findall(r"[-+]?\d+", clean_line)
            
            for n in nums:
                try:
                    candidate_numbers.append({'val': float(n), 'ts': current_ts})
                except: pass
        
        # 3. Process candidate pool into coordinate pairs
        i = 0
        while i < len(candidate_numbers) - 1:
            v1, v2 = candidate_numbers[i]['val'], candidate_numbers[i+1]['val']
            
            # Philippines coordinate logic (Approx Lat: 4 to 22, Lon: 114 to 130)
            lat, lon = v1, v2
            if 114 < abs(v1) < 130: lat, lon = v2, v1
            elif 114 < abs(v2) < 130: lat, lon = v1, v2
            
            # Strict filter for Philippines area to ignore junk data like 27.5 or 3.0
            if 4 <= lat <= 22 and 114 <= lon <= 130:
                # Use the latest timestamp available for this set
                ts = candidate_numbers[i+1]['ts'] if candidate_numbers[i+1]['ts'] != "N/A" else candidate_numbers[i]['ts']
                coords_list.append((lat, lon, ts))
                i += 2 # Move to next pair
            else:
                i += 1 # Shift and try next combination
                
        return coords_list

    def save_and_plot(self):
        coords = self.parse_coordinates()
        if not coords:
            self.status_var.set("❌ Error: No coordinates to save!")
            return

        try:
            self.status_var.set("Saving data to txt...")
            with open(self.txt_file, "w", encoding="utf-8") as file:
                for lat, lon, ts in coords:
                    file.write(f"[{ts}] {lat}, {lon}\n")
            
            self.status_var.set("Generating folium map...")
            # Use the LAST coordinate to center the map (most recent location)
            last_lat, last_lon = coords[-1][0], coords[-1][1]
            
            # Using 'OpenStreetMap' for better visibility of terrain and streets
            world_map = folium.Map(location=[last_lat, last_lon], zoom_start=18, tiles='OpenStreetMap')
            
            for lat, lon, ts in coords:
                popup_text = (
                    f"<div style='font-family: Arial; color: #333;'>"
                    f"<b>Time:</b> {ts}<br>"
                    f"<b>Lat:</b> {lat:.6f}<br>"
                    f"<b>Lon:</b> {lon:.6f}"
                    f"</div>"
                )
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    weight=2,
                    color="#333",
                    fill=True,
                    fill_color="#ff3b30", # Vibrant red
                    fill_opacity=0.9,
                    popup=folium.Popup(popup_text, max_width=250),
                    tooltip=f"Time: {ts}"
                ).add_to(world_map)

            # Add a Title/Header to the map
            title_html = f'''
                 <h3 align="center" style="font-size:16px; color:white; background-color:rgba(0,0,0,0.6); 
                 padding:10px; border-radius:10px; position:fixed; top:10px; left:50%; 
                 transform:translateX(-50%); z-index:9999; font-family: 'Segoe UI', Arial; border: 1px solid #444;">
                 <b>KAMPAJAGA Trash Mapping Data</b><br>
                 <span style="font-size:12px; font-weight: normal;">Latest Plot: {coords[-1][2]}</span>
                 </h3>
                 '''
            world_map.get_root().html.add_child(folium.Element(title_html))
            
            world_map.save(self.map_file)
            self.count_var.set(f"LOCATIONS\nPLOTTED: {len(coords)}")
            self.status_var.set(f"✅ Success! Last Plot: {last_lat:.4f}, {last_lon:.4f}")
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")

    # --- Bluetooth Monitoring Logic ---
    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [f"{p.device} ({p.description})" for p in ports]
        
        if not port_list:
            self.port_combobox.configure(values=["No Ports Found"])
            self.port_combobox.set("No Ports Found")
        else:
            self.port_combobox.configure(values=port_list)
            self.port_combobox.set(port_list[0])

    def start_monitoring(self):
        selected = self.port_combobox.get()
        if "No Ports" in selected or "Scanning" in selected:
            self.status_var.set("❌ Error: Select a valid COM port!")
            return

        port_name = selected.split(" ")[0]
        try:
            self.serial_port = serial.Serial(port_name, 9600, timeout=1)
            self.is_monitoring = True
            
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.port_combobox.configure(state="disabled")
            self.refresh_btn.configure(state="disabled")
            
            self.status_var.set(f"📡 Monitoring {port_name}...")
            
            self.monitor_thread = threading.Thread(target=self.read_serial_loop, daemon=True)
            self.monitor_thread.start()
        except Exception as e:
            self.status_var.set(f"❌ Connection Error: {str(e)}")

    def stop_monitoring(self):
        self.is_monitoring = False
        if self.serial_port:
            try:
                self.serial_port.close()
            except:
                pass
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.port_combobox.configure(state="normal")
        self.refresh_btn.configure(state="normal")
        self.status_var.set("🛑 Monitoring stopped. You can now view the map.")

    def read_serial_loop(self):
        while self.is_monitoring:
            if self.serial_port and self.serial_port.is_open:
                try:
                    if self.serial_port.in_waiting > 0:
                        raw_data = self.serial_port.readline().decode('utf-8', errors='replace')
                        if raw_data.strip():
                            # Auto-add timestamp only if NOT a coordinate, date, or time-only line
                            if not re.search(r"\[.*?\]|\d{4}[-/]\d{2}[-/]\d{2}|\d{2}:\d{2}(?::\d{2})?", raw_data):
                                timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
                                data = f"{timestamp} {raw_data}"
                            else:
                                data = raw_data
                            self.root.after(0, self.update_coords_from_serial, data)
                except Exception as e:
                    self.root.after(0, lambda msg=str(e): self.status_var.set(f"❌ Read Error: {msg}"))
                    self.root.after(0, self.stop_monitoring)
                    break
            time.sleep(0.01)

    def update_coords_from_serial(self, data):
        # Insert the data EXACTLY as it comes from Bluetooth
        self.coords_text.insert("end", data)
        self.coords_text.see("end")
        
        # Update plotted count in real-time
        coords = self.parse_coordinates()
        self.count_var.set(f"LOCATIONS\nPLOTTED: {len(coords)}")
        self.status_var.set(f"📡 Receiving: {data.strip()}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = TrashMapperUI(root)
    root.mainloop()
