import customtkinter as ctk

# ==========================================
#            BACKEND ARRAY CLASS 
# ==========================================

class MitaInABox:
    def __init__(self):
        self.array = []
        self.capacity = 0
        self.data_type = "String" # Default data type

    # Validates and converts input based on current data type
    def validate_and_convert(self, value):
        # Clean the input
        value = str(value).strip()
        
        if self.data_type == "Integer":
            # Check if it's a valid integer (handles negatives)
            if value.lstrip('-').isdigit(): 
                return True, int(value)
            return False, None
            
        elif self.data_type == "Boolean":
            val_lower = value.lower()
            
            # Define accepted True/False variations
            true_values = {'true', '1', 'yes', 'on', 't', 'y'}
            false_values = {'false', '0', 'no', 'off', 'f', 'n'}

            if val_lower in true_values:
                return True, True
            if val_lower in false_values:
                return True, False
            
            # If it doesn't match any known boolean flag
            return False, None
            
        else: # String (Accepts anything)
            return True, value

    # Creates array with initial data and type validation
    def create_array(self, capacity_input, raw_data_string, selected_type):
        try:
            self.capacity = int(capacity_input) if capacity_input else 1
        except ValueError:
            self.capacity = 1

        self.data_type = selected_type
        self.array = []
        
        if raw_data_string and raw_data_string.strip():
            raw_items = [x.strip() for x in raw_data_string.split(',')]
            valid_items = []
            
            # Validate all initial items
            for item in raw_items:
                is_valid, converted = self.validate_and_convert(item)
                if not is_valid:
                    return False, f"'{item}' is not a valid {self.data_type}"
                valid_items.append(converted)
            
            # Truncate if too long
            self.array = valid_items[:self.capacity]
            
        return True, "Success"

    # Check if array is full
    def is_full(self):
        return len(self.array) >= self.capacity

    # Insert without resizing
    def insert(self, item):
        is_valid, converted = self.validate_and_convert(item)
        if not is_valid:
            return False
        self.array.append(converted)
        return True

    # Resize and insert (dynamic array behavior)
    def resize_and_insert(self, item):
        is_valid, converted = self.validate_and_convert(item)
        if not is_valid:
            return False
        
        self.capacity *= 2
        self.array.append(converted)
        return True

    # Accessors
    def get_data(self):
        return self.array
    
    def get_capacity(self):
        return self.capacity
    
    def get_value_at(self, index):
        return self.array[index] if 0 <= index < len(self.array) else None
    
    def get_first_value(self):
        return self.array[0] if self.array else None
    
    def get_last_value(self):
        return self.array[-1] if self.array else None
    
    def get_length(self): 
        return len(self.array)
    
    def clear(self):
        self.array = []
    
    # Modify value at specific index
    def modify_at_index(self, index, value):
        is_valid, converted = self.validate_and_convert(value)
        if not is_valid:
            return "TYPE_ERROR"

        if 0 <= index < len(self.array):
            self.array[index] = converted
            return True
        return "INDEX_ERROR"
    
    # Delete at specific index    
    def delete_at_index(self, index):
        if 0 <= index < len(self.array):
            self.array.pop(index)
            return True
        return "INDEX_ERROR"
    
    # Insert at specific index
    def insert_at_specific_index(self, index, value):
        if len(self.array) >= self.capacity:
            return "FULL"
        
        is_valid, converted = self.validate_and_convert(value)
        if not is_valid:
            return "TYPE_ERROR"

        if 0 <= index <= len(self.array):
            self.array.insert(index, converted)
            return True
        return "INDEX_ERROR"
    
    # Search for value in the array
    def search(self, value):
        is_bool_mode = self.data_type == "Boolean" or (len(self.array) > 0 and isinstance(self.array[0], bool))

        if is_bool_mode:
            val_str = str(value).lower()
            true_values = {'true', '1', 'yes', 'on', 't', 'y'}
            false_values = {'false', '0', 'no', 'off', 'f', 'n'}

            target = None
            if val_str in true_values:
                target = True
            elif val_str in false_values:
                target = False

            if target is not None:
                try:
                    return self.array.index(target)
                except ValueError:
                    return -1
            else:
                return -1

        is_valid, converted = self.validate_and_convert(value)
        if not is_valid: return -1
        try:
            return self.array.index(converted)
        except ValueError:
            return -1

# ==========================================
#        GUI CLASS (FRONTEND)
# ==========================================

class ArrayCard(ctk.CTkFrame):
    def __init__(self, master, text="", width=60, height=85, **kwargs):
        text_color = kwargs.pop("text_color", "black")
        text_color_disabled = kwargs.pop("text_color_disabled", "black")
        
        super().__init__(master, width=width, height=height, **kwargs)
        self.pack_propagate(False)

        self.label = ctk.CTkLabel(
            self, 
            text=str(text), 
            font=("Arial", 14, "bold"),
            text_color=text_color
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

    def configure(self, **kwargs):
        if "text" in kwargs:
            self.label.configure(text=str(kwargs.pop("text")))
        if "text_color" in kwargs:
            self.label.configure(text_color=kwargs.pop("text_color"))
        if "text_color_disabled" in kwargs:
            self.label.configure(text_color=kwargs.pop("text_color_disabled"))

        super().configure(**kwargs)

class MitaVisualizer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.backend = MitaInABox()
        self.current_box_objects = [] 

        self._setup_layout()

    # --- NEW: CUSTOM POPUP FUNCTION ---
    def show_popup(self, title, message, is_error=False):
        # Create a Toplevel window (popup)
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("350x180")
        popup.resizable(False, False)
        
        # Ensure it stays on top and grabs focus (Modal)
        popup.attributes("-topmost", True)
        popup.grab_set() 
        
        # Determine text color based on error state
        msg_color = "#FF5555" if is_error else "#2CC985" # Red or Green
        
        # Message Label
        label = ctk.CTkLabel(popup, text=message, font=("Arial", 16, "bold"), 
                             wraplength=300, text_color=msg_color)
        label.pack(expand=True, padx=20, pady=20)
        
        # OK Button
        btn = ctk.CTkButton(popup, text="OK", command=popup.destroy, width=100, fg_color=msg_color, text_color="white")
        btn.pack(pady=(0, 20))

    def _setup_layout(self):
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(anchor="n", padx=20, pady=10, fill="x")

        # 1. LEFT FRAME (Setup)
        left_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(left_frame, text="Setup Array", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        def arrlength_validation(P):
            return P == "" or (P.isdigit() and 1 <= int(P) <= 10)
        vcmd = (self.register(arrlength_validation), '%P')
        self.array_length_var = ctk.StringVar(value="5")

        ctk.CTkLabel(left_frame, text="Capacity (1-10):").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(left_frame, width=140, validate="key", validatecommand=vcmd, textvariable=self.array_length_var).pack(anchor="w")

        self.data_type_menu = ctk.CTkOptionMenu(left_frame, values=["String", "Integer", "Boolean"])
        self.data_type_menu.set("String")
        self.data_type_menu.pack(anchor="w", pady=(5, 0))

        ctk.CTkLabel(left_frame, text="Initial Data:").pack(anchor="w", pady=(5,0))
        self.data_entry = ctk.CTkEntry(left_frame, width=140, placeholder_text="e.g. A, B")
        self.data_entry.pack(anchor="w")

        ctk.CTkButton(left_frame, text="Create / Reset", command=self.create_array, fg_color="green").pack(anchor="w", pady=(15, 0))

        ctk.CTkFrame(controls_frame, width=2, fg_color="gray80").pack(side="left", fill="y", padx=20, pady=10)

        # 2. MIDDLE FRAME
        middle_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        middle_frame.pack(side="left", fill="both", expand=True)

        inspect_frame = ctk.CTkFrame(middle_frame, fg_color="transparent")
        inspect_frame.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(inspect_frame, text="Array Operations", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0,5))
        ctk.CTkButton(inspect_frame, text="Access Index", command=self.access, fg_color="#8E44AD", width=120).pack(pady=2)
        ctk.CTkButton(inspect_frame, text="First Value", command=self.get_first, fg_color="#D68910", width=120).pack(pady=2)
        ctk.CTkButton(inspect_frame, text="Last Value", command=self.get_last, fg_color="#D68910", width=120).pack(pady=2)
        ctk.CTkButton(inspect_frame, text="Array Length", command=self.get_arr_length, fg_color="#D68910", width=120).pack(pady=2)
        self.search_btn = ctk.CTkButton(inspect_frame, text="Search Value", command=self.search_value, fg_color="#D35400", width=120)
        self.search_btn.pack(pady=2)

        ctk.CTkFrame(middle_frame, width=2, fg_color="gray80").pack(side="left", fill="y", padx=15, pady=10)

        modify_frame = ctk.CTkFrame(middle_frame, fg_color="transparent")
        modify_frame.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(modify_frame, text="Modify Array", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0,5))
        ctk.CTkButton(modify_frame, text="Insert at Index", command=self.insert_at_idx, fg_color="#8E44AD", width=120).pack(pady=2)
        ctk.CTkButton(modify_frame, text="Modify Index", command=self.modify_idx, fg_color="#D68910", width=120).pack(pady=2)
        ctk.CTkButton(modify_frame, text="Delete Index", command=self.delete_index, fg_color="#C0392B", width=120).pack(pady=2)
        ctk.CTkButton(modify_frame, text="Clear Elements", command=self.clear_elements, fg_color="#7F8C8D", width=120).pack(pady=2)

        ctk.CTkFrame(controls_frame, width=2, fg_color="gray80").pack(side="left", fill="y", padx=20, pady=10)

        # 3. RIGHT FRAME
        right_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(right_frame, text="Append / Resize", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.insert_entry = ctk.CTkEntry(right_frame, placeholder_text="Value to Append")
        self.insert_entry.pack(anchor="w", pady=(5,0))

        self.resize_toggle_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(right_frame, text="Dynamic Resizing", variable=self.resize_toggle_var).pack(anchor="w", pady=(10,0))

        self.insert_btn = ctk.CTkButton(right_frame, text="Append Element", command=self.insert_element)
        self.insert_btn.pack(anchor="w", pady=(10,0))

        # 4. VISUALIZATION FRAME AREA 
        self.visual_frame = ctk.CTkFrame(self, fg_color=("white", "#2B2B2B"), corner_radius=10)
        self.visual_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # REMOVED: self.status_label

        self.visual_inner_frame = ctk.CTkFrame(self.visual_frame, fg_color="transparent")
        self.visual_inner_frame.pack(fill="x", padx=20, pady=20)


    # VISUAL FUNCTIONS
    def render_array(self, target_frame, data_list, capacity, label_text="Current Array"):
        for widget in target_frame.winfo_children():
            widget.destroy()

        lbl = ctk.CTkLabel(target_frame, text=label_text, font=("Arial", 12, "bold"))
        lbl.pack(anchor="center", pady=(0, 10))

        box_container = ctk.CTkFrame(target_frame, fg_color="transparent")
        box_container.pack(anchor="center")

        created_boxes = [] 
        MAX_COLS = 10 

        for i in range(capacity):
            row_num = i // MAX_COLS
            col_num = i % MAX_COLS
            is_filled = i < len(data_list)
            
            if is_filled:
                box_color = "#3B8ED0" 
                text_val = str(data_list[i])
                text_color = "white"
                border_color = "#2c6e91"
            else:
                box_color = ("gray90", "#3A3A3A") 
                text_val = ""
                text_color = ("gray60", "gray60") 
                border_color = ("gray70", "#505050")

            card = ArrayCard(
                box_container, text=text_val, width=60, height=85,      
                fg_color=box_color, border_width=2, border_color=border_color,
                corner_radius=8, text_color=text_color, text_color_disabled=text_color 
            )
            card.grid(row=row_num, column=col_num, padx=5, pady=(0, 30)) 
            created_boxes.append(card)
            
            idx_color = ("gray40", "gray80")
            idx_lbl = ctk.CTkLabel(box_container, text=str(i), font=("Arial", 11, "bold"), text_color=idx_color)
            idx_lbl.place(in_=card, relx=0.5, rely=1.0, y=14, anchor="center")
            
        return created_boxes

    def highlight_box(self, index, color="#F1C40F"):
        if index is not None and 0 <= index < len(self.current_box_objects):
            target_box = self.current_box_objects[index]
            target_box.configure(fg_color=color)
            self.after(1000, lambda: target_box.configure(fg_color="#3B8ED0"))

    def animate_resize(self, new_item):
        is_valid, _ = self.backend.validate_and_convert(new_item)
        if not is_valid:
            self.show_popup("Error", f"Invalid {self.backend.data_type} format.", is_error=True)
            return

        self.insert_btn.configure(state="disabled")
        # Notify user (Optional: could be a popup but might be annoying)
        # self.show_popup("Resizing", "Array Full! Resizing started...")
        
        current_data = self.backend.get_data()
        current_cap = self.backend.get_capacity()
        new_capacity = current_cap * 2
        
        resize_frame = ctk.CTkFrame(self.visual_frame, fg_color="transparent")
        resize_frame.pack(pady=20, fill="x")
        
        new_box_objects = self.render_array(resize_frame, [], new_capacity, "New Array (Resized)")
        old_box_objects = list(self.current_box_objects)

        def copy_step(index):
            try:
                if index < len(current_data):
                    # Visual Only (No Text Update)
                    if index < len(old_box_objects) and old_box_objects[index].winfo_exists():
                        old_box_objects[index].configure(fg_color="#E5AA00") 
                    
                    def fill_new_box():
                        try:
                            val_to_copy = current_data[index]
                            if index < len(new_box_objects) and new_box_objects[index].winfo_exists():
                                new_box_objects[index].configure(fg_color="#3B8ED0", text=str(val_to_copy), text_color_disabled="white")
                            if index < len(old_box_objects) and old_box_objects[index].winfo_exists():
                                old_box_objects[index].configure(fg_color="gray90")
                            self.after(600, lambda: copy_step(index + 1))
                        except Exception:
                            self.insert_btn.configure(state="normal")
                    self.after(600, fill_new_box)
                else:
                    if len(current_data) < len(new_box_objects):
                        target_box = new_box_objects[len(current_data)]
                        target_box.configure(fg_color="#2CC985", text=str(new_item), text_color_disabled="white")
                    
                    def finalize():
                        try:
                            self.backend.resize_and_insert(new_item)
                            if resize_frame.winfo_exists(): resize_frame.destroy()
                            self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
                            self.show_popup("Success", "Resizing Complete.\nCapacity Doubled.")
                            self.insert_btn.configure(state="normal")
                        except Exception: pass
                    self.after(1200, finalize)
            except Exception:
                self.insert_btn.configure(state="normal")

        copy_step(0)

    # ==========================================
    #        LOGIC FOR BUTTON ACTIONS
    # ==========================================

    def create_array(self):
        selected_type = self.data_type_menu.get()
        success, message = self.backend.create_array(self.array_length_var.get(), self.data_entry.get(), selected_type)
        
        if success:
            self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
            self.show_popup("Success", f"Created {selected_type} Array.")
        else:
            self.show_popup("Error", message, is_error=True)

    def insert_element(self):
        val = self.insert_entry.get()
        if not val: return

        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return

        if self.backend.is_full():
            if self.resize_toggle_var.get():
                self.animate_resize(val)
            else:
                self.show_popup("Error", "Array is full!", is_error=True)
        else:
            success = self.backend.insert(val)
            if success:
                self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
                self.show_popup("Success", f"Inserted '{val}'")
            else:
                self.show_popup("Error", f"Invalid {self.backend.data_type} format.", is_error=True)
        
        self.insert_entry.delete(0, 'end')

    def access(self):
        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return
            
        if self.backend.get_length() == 0:
            self.show_popup("Error", "Array is empty!", is_error=True)
            return
        
        dialog = ctk.CTkInputDialog(text="Enter index to access:", title="Access Index")
        s = dialog.get_input()
        if not s: return
            
        if not s.lstrip('-').isdigit():
            self.show_popup("Error", "Please enter a valid integer.", is_error=True)
            return
            
        idx = int(s)
        val = self.backend.get_value_at(idx)
        if val is not None:
            self.highlight_box(idx, "#F1C40F")
            self.show_popup("Success", f"Value at {idx} is '{val}'")
        else:
            self.show_popup("Error", f"Index {idx} out of bounds.", is_error=True)

    def get_first(self):
        val = self.backend.get_first_value()
        if val is not None:
            self.highlight_box(0, "#2CC985")
            self.show_popup("Success", f"First Value: '{val}'")
        else:
            self.show_popup("Error", "Array empty.", is_error=True)

    def get_last(self):
        val = self.backend.get_last_value()
        if val is not None:
            idx = len(self.backend.get_data()) - 1
            self.highlight_box(idx, "#9B59B6")
            self.show_popup("Success", f"Last Value: '{val}'")
        else:
            self.show_popup("Error", "Array empty.", is_error=True)

    def get_arr_length(self):
        l = self.backend.get_length()
        # Highlight all
        for i in range(l):
            if i < len(self.current_box_objects):
                b = self.current_box_objects[i]
                b.configure(fg_color="#1ABC9C")
                self.after(1000, lambda box=b: box.configure(fg_color="#3B8ED0"))
        
        self.show_popup("Info", f"Current Length: {l}")

    def search_value(self):
        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return
            
        if self.backend.get_length() == 0:
            self.show_popup("Error", "Array is empty!", is_error=True)
            return
        
        dialog = ctk.CTkInputDialog(text=f"Search Value ({self.backend.data_type}):", title="Search")
        target = dialog.get_input()
        if not target: return
        
        is_valid, converted = self.backend.validate_and_convert(target)
        if not is_valid:
            self.show_popup("Error", f"'{target}' is not a valid {self.backend.data_type}.", is_error=True)
            return
        
        # 1. GET RESULT FROM BACKEND
        found_idx = self.backend.search(target)

        self.search_btn.configure(state="disabled")
        data = self.backend.get_data()
        
        # 2. VISUAL ANIMATION
        def scan(i):
            if i < len(data):
                if i < len(self.current_box_objects):
                    self.current_box_objects[i].configure(fg_color="#E67E22")
                    # No text update, just visual color
                    
                def next_step():
                    if i != found_idx and i < len(self.current_box_objects):
                        self.current_box_objects[i].configure(fg_color="#3B8ED0")
                    
                    if i == found_idx: 
                        if i < len(self.current_box_objects):
                            self.current_box_objects[i].configure(fg_color="#2ECC71")
                        
                        # Show Popup Result
                        self.show_popup("Found!", f"'{target}' found at index {i}.")
                        
                        self.after(2000, lambda: self.current_box_objects[i].configure(fg_color="#3B8ED0") if i < len(self.current_box_objects) else None)
                        self.search_btn.configure(state="normal")
                    else:
                        scan(i + 1)

                self.after(400, next_step)
            else:
                self.show_popup("Not Found", f"'{target}' not found.", is_error=True)
                self.search_btn.configure(state="normal")
        
        scan(0)

    def clear_elements(self):
        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return
            
        self.backend.clear()
        self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
        self.show_popup("Success", "Array cleared.")

    def delete_index(self):
        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return
            
        dialog = ctk.CTkInputDialog(text="Index to delete:", title="Delete")
        s = dialog.get_input()
        if not s: return
            
        if not s.lstrip('-').isdigit():
            self.show_popup("Error", "Please enter a valid number.", is_error=True)
            return
            
        idx = int(s)
        result = self.backend.delete_at_index(idx)
        
        if result == True:
            self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
            self.show_popup("Success", f"Deleted element at index {idx}.")
        elif result == "INDEX_ERROR":
            self.show_popup("Error", f"Index {idx} out of bounds.", is_error=True)
        else:
            self.show_popup("Error", "Unable to delete.", is_error=True)
        
    def insert_at_idx(self):
        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return
        
        if len(self.backend.get_data()) >= self.backend.get_capacity():
            self.show_popup("Error", "Array is full!", is_error=True)
            return
            
        dialog = ctk.CTkInputDialog(text="Index to insert at:", title="Insert Index")
        s = dialog.get_input()
        if not s: return
            
        if not s.lstrip('-').isdigit():
            self.show_popup("Error", "Please enter a valid number.", is_error=True)
            return
            
        idx = int(s)
        if not (0 <= idx <= len(self.backend.get_data())):
            self.show_popup("Error", f"Index {idx} out of bounds.", is_error=True)
            return
        
        dialog2 = ctk.CTkInputDialog(text=f"Value for index {idx}:", title="Insert Value")
        val = dialog2.get_input()
        if not val: return

        result = self.backend.insert_at_specific_index(idx, val)
        
        if result == True:
            self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
            self.highlight_box(idx, "#2CC985")
            self.show_popup("Success", f"Inserted '{val}' at index {idx}.")
        elif result == "TYPE_ERROR":
            self.show_popup("Error", f"'{val}' is not a valid {self.backend.data_type}.", is_error=True)
        elif result == "FULL":
            self.show_popup("Error", "Array is full!", is_error=True)
        elif result == "INDEX_ERROR":
            self.show_popup("Error", f"Index {idx} out of bounds.", is_error=True)
        else:
            self.show_popup("Error", "Unable to insert.", is_error=True)

    def modify_idx(self):
        if self.backend.get_capacity() == 0:
            self.show_popup("Error", "Create array first!", is_error=True)
            return
            
        if self.backend.get_length() == 0:
            self.show_popup("Error", "Array is empty!", is_error=True)
            return
        
        idx_dialog = ctk.CTkInputDialog(text="Enter Index to modify:", title="Modify Index")
        idx_str = idx_dialog.get_input()
        if not idx_str: return
            
        if not idx_str.lstrip('-').isdigit():
            self.show_popup("Error", "Please enter a valid number.", is_error=True)
            return
            
        idx = int(idx_str)
        if not (0 <= idx < len(self.backend.get_data())):
            self.show_popup("Error", f"Index {idx} out of bounds.", is_error=True)
            return

        val_dialog = ctk.CTkInputDialog(text=f"Enter New Value for index {idx}:", title="Modify Value")
        val = val_dialog.get_input()
        if not val: return

        result = self.backend.modify_at_index(idx, val)
        
        if result == True:
            self.current_box_objects = self.render_array(self.visual_inner_frame, self.backend.get_data(), self.backend.get_capacity())
            self.highlight_box(idx, "#F39C12") 
            self.show_popup("Success", f"Modified index {idx} to '{val}'.")
        elif result == "TYPE_ERROR":
            self.show_popup("Error", f"'{val}' is not a valid {self.backend.data_type}.", is_error=True)
        elif result == "INDEX_ERROR":
            self.show_popup("Error", f"Index {idx} out of bounds.", is_error=True)
        else:
            self.show_popup("Error", "Unable to modify.", is_error=True)
            
# ==========================================
#           WINDOW EXECUTION
# ==========================================

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Array Visualizer")
    root.geometry("1000x650")

    app_instance = MitaVisualizer(master=root)
    app_instance.pack(fill="both", expand=True)

    root.mainloop()
