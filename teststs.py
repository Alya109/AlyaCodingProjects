import customtkinter as ctk

# ==========================================
#               BACKEND LOGIC
# ==========================================
class ArrayBackend:
    def __init__(self):
        self.arr, self.cap, self.type = [], 0, "String"

    def validate(self, val):
        val = str(val).strip()
        if self.type == "Integer":
            return (True, int(val)) if val.lstrip('-').isdigit() else (False, None)
        elif self.type == "Boolean":
            if val.lower() in {'true', '1', 'yes', 'on', 't', 'y'}: return True, True
            if val.lower() in {'false', '0', 'no', 'off', 'f', 'n'}: return True, False
            return False, None
        return True, val

    def create(self, cap_input, raw_data, dtype):
        try: self.cap = int(cap_input) if cap_input else 1
        except ValueError: self.cap = 1
        self.type, self.arr = dtype, []
        
        if raw_data and raw_data.strip():
            for item in raw_data.split(','):
                valid, val = self.validate(item)
                if not valid: return False, f"'{item.strip()}' invalid for {dtype}"
                self.arr.append(val)
            self.arr = self.arr[:self.cap]
        return True, "Success"

    def insert(self, item, resize=False):
        valid, val = self.validate(item)
        if not valid: return False, "TYPE_ERROR"
        if len(self.arr) >= self.cap:
            if not resize: return False, "FULL"
            self.cap *= 2
        self.arr.append(val)
        return True, "Success"

    def modify(self, idx, val):
        if not (0 <= idx < len(self.arr)): return "INDEX_ERROR"
        valid, conv = self.validate(val)
        if not valid: return "TYPE_ERROR"
        self.arr[idx] = conv
        return True

    def insert_at(self, idx, val):
        if len(self.arr) >= self.cap: return "FULL"
        # Check Valid Bounds (0 to Capacity-1) for UI safety
        if idx < 0 or idx >= self.cap: return "INDEX_ERROR"
        
        valid, conv = self.validate(val)
        if not valid: return "TYPE_ERROR"
        
        # Standard insert behavior (appends if idx > current length)
        self.arr.insert(idx, conv)
        return True

    def delete(self, idx):
        if 0 <= idx < len(self.arr): return self.arr.pop(idx) is not None
        return False

    def search(self, val):
        valid, target = self.validate(val)
        if not valid: return -1
        try: return self.arr.index(target)
        except ValueError: return -1

# ==========================================
#               FRONTEND GUI
# ==========================================
class ArrayVisualizer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bk = ArrayBackend()
        self.boxes = []
        self.setup_ui()

    # --- UI HELPERS ---
    def setup_ui(self):
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=10)

        # Setup Section
        self.add_section(ctrl, "Setup Array", [
            ("lbl", "Capacity (1-10):"),
            ("entry_var", "cap", "5"),
            ("menu", ["String", "Integer", "Boolean"]),
            ("entry", "init_data", "e.g. A, B"),
            ("btn", "Create / Reset", self.create_array, "green")
        ])
        
        # Operations Section
        self.add_section(ctrl, "Inspect", [
             ("btn", "Access Index", self.access_idx, "#8E44AD"),
             ("btn", "First Value", lambda: self.access_special(0), "#D68910"),
             ("btn", "Last Value", lambda: self.access_special(-1), "#D68910"),
             ("btn", "Length", self.show_len, "#D68910"),
             ("btn", "Search", self.search_val, "#D35400")
        ], div=True)

        # Modification Section
        self.add_section(ctrl, "Modify", [
            ("btn", "Insert At", self.insert_at_idx, "#8E44AD"),
            ("btn", "Modify Idx", self.modify_idx, "#D68910"),
            ("btn", "Delete Idx", self.del_idx, "#C0392B"),
            ("btn", "Clear", self.clear_arr, "#7F8C8D")
        ], div=True)

        # Append Section
        self.add_section(ctrl, "Append", [
            ("entry", "append_val", "Value"),
            ("switch", "Dynamic Resize", "resize_mode"),
            ("btn", "Append", self.append_el, None)
        ], div=True)

        self.vis_frame = ctk.CTkFrame(self, fg_color=("white", "#2B2B2B"))
        self.vis_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.status = ctk.CTkLabel(self.vis_frame, text="", font=("Arial", 14))
        self.status.pack(pady=10)
        self.box_frame = ctk.CTkFrame(self.vis_frame, fg_color="transparent")
        self.box_frame.pack(fill="x", padx=20)

    def add_section(self, parent, title, widgets, div=False):
        if div: ctk.CTkFrame(parent, width=2, fg_color="gray60").pack(side="left", fill="y", padx=10, pady=5)
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", fill="y", padx=5)
        ctk.CTkLabel(f, text=title, font=("Arial", 12, "bold")).pack(anchor="w")
        
        for w in widgets:
            w_type = w[0]
            if w_type == "btn":
                ctk.CTkButton(f, text=w[1], command=w[2], fg_color=w[3] if w[3] else "blue", width=110, height=24).pack(pady=2)
            elif w_type == "entry_var":
                vcmd = (self.register(lambda P: P == "" or (P.isdigit() and 1 <= int(P) <= 10)), '%P')
                setattr(self, w[1], ctk.StringVar(value=w[2]))
                ctk.CTkEntry(f, width=110, textvariable=getattr(self, w[1]), validate="key", validatecommand=vcmd).pack(pady=2)
            elif w_type == "entry":
                e = ctk.CTkEntry(f, width=110, placeholder_text=w[2])
                e.pack(pady=2); setattr(self, w[1], e)
            elif w_type == "menu":
                self.dtype = ctk.CTkOptionMenu(f, values=w[1], width=110); self.dtype.pack(pady=2)
            elif w_type == "switch":
                setattr(self, w[2], ctk.BooleanVar(value=False))
                ctk.CTkSwitch(f, text=w[1], variable=getattr(self, w[2])).pack(pady=5)
            elif w_type == "lbl":
                ctk.CTkLabel(f, text=w[1], font=("Arial", 10)).pack(pady=(2,0), anchor="w")

    # CORE ACTIONS 
    def update_status(self, msg, color="black"):
        self.status.configure(text=msg, text_color=color)

    def refresh(self, frame=None, title="Current Array"):
        tgt = frame if frame else self.box_frame
        for w in tgt.winfo_children(): w.destroy()
        
        ctk.CTkLabel(tgt, text=title, font=("Arial", 12, "bold")).pack(pady=(0, 10))
        cont = ctk.CTkFrame(tgt, fg_color="transparent"); cont.pack()
        
        self.boxes = []
        for i in range(self.bk.cap):
            filled = i < len(self.bk.arr)
            card = ctk.CTkFrame(cont, width=50, height=70, corner_radius=6, border_width=2,
                                fg_color="#3B8ED0" if filled else ("gray90", "#3A3A3A"),
                                border_color="#2c6e91" if filled else ("gray70", "#505050"))
            card.grid(row=i//10, column=i%10, padx=4, pady=(0, 25))
            card.pack_propagate(False)
            
            ctk.CTkLabel(card, text=str(self.bk.arr[i]) if filled else "", font=("Arial", 12, "bold"),
                         text_color="white" if filled else "gray60").place(relx=0.5, rely=0.5, anchor="c")
            ctk.CTkLabel(cont, text=str(i), font=("Arial", 10), text_color="gray60").place(in_=card, relx=0.5, rely=1.0, y=10, anchor="c")
            self.boxes.append(card)
        return self.boxes

    def get_input(self, prompt, cast_int=False):
        if not self.bk.cap: return self.update_status("Error: Create array first!", "red")
        val = ctk.CTkInputDialog(text=prompt, title="Input").get_input()
        if not val: return None
        if cast_int:
            return int(val) if val.lstrip('-').isdigit() else (self.update_status("Invalid Number", "red"), None)[1]
        return val

    # OPERATION HANDLERS 
    def create_array(self):
        s, msg = self.bk.create(self.cap.get(), self.init_data.get(), self.dtype.get())
        if s: self.refresh(); self.update_status(f"Created {self.bk.type} Array", "green")
        else: self.update_status(f"Error: {msg}", "red")

    def append_el(self):
        val = self.append_val.get()
        if not val: return
        if self.bk.cap > 0 and len(self.bk.arr) >= self.bk.cap:
            if self.resize_mode.get(): self.animate_resize(val)
            else: self.update_status("Array Full!", "red")
        else:
            s, msg = self.bk.insert(val)
            if s: self.refresh(); self.update_status(f"Inserted '{val}'", "blue"); self.append_val.delete(0, 'end')
            else: self.update_status(f"Error: {msg}", "red")

    def access_idx(self):
        idx = self.get_input("Enter Index:", True)
        if idx is None: return
        val = self.bk.arr[idx] if 0 <= idx < len(self.bk.arr) else None
        if val is not None:
            self.update_status(f"Value at {idx}: {val}", "green")
            self.flash(idx, "#F1C40F")
        else: self.update_status("Index out of bounds", "red")

    def access_special(self, i):
        if not self.bk.arr: return self.update_status("Empty Array", "red")
        actual_i = i if i >= 0 else len(self.bk.arr) + i
        self.update_status(f"{'First' if i==0 else 'Last'}: {self.bk.arr[actual_i]}", "green")
        self.flash(actual_i, "#F1C40F")

    def show_len(self):
        self.update_status(f"Length: {len(self.bk.arr)}", "blue")
        for i in range(len(self.bk.arr)): self.flash(i, "#1ABC9C")

    # ==========================================
    #  UPDATED: CHECKS BEFORE INPUT
    # ==========================================
    def insert_at_idx(self):
        # 1. CHECK FULL BEFORE INPUT
        if len(self.bk.arr) >= self.bk.cap:
            return self.update_status("Error: Array is Full! Cannot Insert.", "red")

        idx = self.get_input("Index to insert:", True)
        if idx is None: return
        
        # 2. Capacity Bound Check
        if idx >= self.bk.cap:
            return self.update_status(f"Error: Index {idx} out of bounds (0-{self.bk.cap - 1})", "red")

        val = self.get_input(f"Value for index {idx}:")
        if not val: return
        
        res = self.bk.insert_at(idx, val)
        if res == True: 
            self.refresh()
            final_idx = min(idx, len(self.bk.arr)-1) 
            self.update_status(f"Inserted at {final_idx}", "green")
            self.flash(final_idx, "#2CC985")
        elif res == "FULL": self.update_status("Array is Full (Cannot shift)", "red")
        else: self.update_status(f"Error: {res}", "red")

    def modify_idx(self):
        # 1. CHECK EMPTY BEFORE INPUT
        if not self.bk.arr:
             return self.update_status("Error: Array is empty!", "red")

        idx = self.get_input("Index to modify:", True)
        if idx is None: return

        if not (0 <= idx < len(self.bk.arr)):
             return self.update_status(f"Error: Index {idx} out of bounds (0-{len(self.bk.arr)-1})", "red")

        val = self.get_input(f"New Value for {idx}:")
        if not val: return

        res = self.bk.modify(idx, val)
        if res == True: self.refresh(); self.update_status(f"Modified {idx}", "green"); self.flash(idx, "#F39C12")
        else: self.update_status(f"Error: {res}", "red")

    def del_idx(self):
        # 1. CHECK EMPTY BEFORE INPUT
        if not self.bk.arr:
             return self.update_status("Error: Array is empty!", "red")

        idx = self.get_input("Index to delete:", True)
        if idx is None: return

        if not (0 <= idx < len(self.bk.arr)):
             return self.update_status(f"Error: Index {idx} out of bounds (0-{len(self.bk.arr)-1})", "red")

        if self.bk.delete(idx): self.refresh(); self.update_status(f"Deleted index {idx}", "green")
        else: self.update_status("Index Error", "red")

    def clear_arr(self):
        self.bk.arr = []; self.refresh(); self.update_status("Array Cleared", "green")

    # --- ANIMATIONS ---
    def flash(self, i, col):
        if 0 <= i < len(self.boxes):
            b = self.boxes[i]; orig = b.cget("fg_color")
            b.configure(fg_color=col); self.after(800, lambda: b.configure(fg_color=orig))

    def search_val(self):
        target = self.get_input(f"Search Value ({self.bk.type}):")
        if not target: return

        is_valid, _ = self.bk.validate(target)
        if not is_valid:
            self.update_status(f"Type Mismatch: '{target}' is not a {self.bk.type}", "red")
            return 

        found_idx = self.bk.search(target)
        
        def scan(i):
            if i >= len(self.bk.arr): return self.update_status(f"'{target}' not found", "red")
            if i < len(self.boxes): self.boxes[i].configure(fg_color="#E67E22")
            self.update_status(f"Scanning index {i}...")
            
            def next_step():
                if i < len(self.boxes) and i != found_idx: self.boxes[i].configure(fg_color="#3B8ED0")
                if i == found_idx:
                    self.boxes[i].configure(fg_color="#2ECC71")
                    self.update_status(f"Found '{target}' at index {i}!", "green")
                    self.after(2000, lambda: self.boxes[i].configure(fg_color="#3B8ED0"))
                else: scan(i + 1)
            self.after(300, next_step)
        scan(0)

    def animate_resize(self, new_item):
        valid, _ = self.bk.validate(new_item)
        if not valid: return self.update_status("Invalid Type", "red")
        
        self.update_status("Resizing...", "orange")
        pop = ctk.CTkFrame(self.vis_frame); pop.pack(pady=10)
        self.bk.cap *= 2
        new_boxes = self.refresh(pop, "Resizing Array...")
        
        def step(i):
            if i < len(self.bk.arr):
                self.status.configure(text=f"Copying {i}...")
                if i < len(self.boxes): self.boxes[i].configure(fg_color="#E5AA00")
                self.after(400, lambda: [
                    new_boxes[i].configure(fg_color="#3B8ED0", border_color="#2c6e91"),
                    new_boxes[i].winfo_children()[0].configure(text=str(self.bk.arr[i]), text_color="white"),
                    step(i+1)
                ])
            else:
                pop.destroy()
                self.bk.insert(new_item, resize=True)
                self.refresh()
                self.update_status("Resize Complete", "green")
        step(0)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    root = ctk.CTk(); root.title("Array Visualizer"); root.geometry("900x600")
    ArrayVisualizer(root).pack(fill="both", expand=True)
    root.mainloop()
