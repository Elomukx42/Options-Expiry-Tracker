import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import json
import os

class OptionsExpiryWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Dev's Options Expiry Tracker")
        
        self.config_file = "widget_config.json"
        self.load_config()
        
        # Window properties
        self.root.geometry(f"620x700+{self.window_x}+{self.window_y}")
        self.root.wm_attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")
        
        # NSE Holidays
        self.nse_holidays = [
            (datetime(2025, 12, 25), "Christmas"),
            (datetime(2026, 1, 26), "Republic Day"),
            (datetime(2026, 3, 6), "Holi"),
            (datetime(2026, 4, 2), "Ram Navami"),
            (datetime(2026, 4, 10), "Mahavir Jayanti"),
            (datetime(2026, 4, 14), "Dr. Ambedkar Jayanti"),
            (datetime(2026, 5, 1), "Maharashtra Day"),
            (datetime(2026, 8, 15), "Independence Day"),
            (datetime(2026, 10, 2), "Gandhi Jayanti"),
            (datetime(2026, 11, 9), "Diwali"),
            (datetime(2026, 12, 25), "Christmas"),
        ]
        
        self.instruments = {
            "NIFTY": {"exchange": "NSE", "expiry_day": 1},
            "BANKNIFTY": {"exchange": "NSE", "expiry_day": 1},
            "FINNIFTY": {"exchange": "NSE", "expiry_day": 1},
            "MIDCPNIFTY": {"exchange": "NSE", "expiry_day": 1},
            "SENSEX": {"exchange": "BSE", "expiry_day": 3},
            "BANKEX": {"exchange": "BSE", "expiry_day": 3},
        }
        
        # All NSE stocks with F&O - 180+ stocks
        self.stocks_list = [
            "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS",
            "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL",
            "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE",
            "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT",
            "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "BSOFT",
            "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL",
            "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR",
            "DELTACORP", "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND",
            "FEDERALBNK", "GAIL", "GLENMARK", "GMRINFRA", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES",
            "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE",
            "HEROMOTOCO", "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "ICICIBANK", "ICICIGI",
            "ICICIPRULI", "IDEA", "IDFC", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM",
            "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC",
            "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "LALPATHLAB",
            "LAURUSLABS", "LICHSGFIN", "LT", "LTIM", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", 
            "MARICO", "MARUTI", "MCDOWELL-N", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS", 
            "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", 
            "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PEL", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", 
            "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", 
            "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SUNPHARMA",
            "SUNTV", "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER",
            "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR",
            "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE"
        ]
        
        self.expiry_labels = {}
        self.expiry_dates = {}
        self.selected_stock = None
        self.stock_expiry_date = None
        self.dropdown_visible = False
        
        self.create_widgets()
        self.setup_dragging()
        self.ensure_topmost()
        
        try:
            self.update_all_expiries()
        except Exception as e:
            print(f"Error: {e}")
        
        self.realtime_update()
        
    def get_upcoming_holidays(self, count=2):
        today = datetime.now()
        upcoming = [(hd, hn, (hd - today).days) for hd, hn in self.nse_holidays if hd > today]
        upcoming.sort(key=lambda x: x[0])
        return upcoming[:count]
        
    def create_widgets(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg="#2d2d2d", height=35)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="⚡Dev's Options Expiry Tracker", 
                fg="#00ff88", bg="#2d2d2d", 
                font=("Segoe UI", 11, "bold")).pack(side="left", padx=10)
        
        tk.Button(title_frame, text="✕", fg="white", bg="#2d2d2d",
                 font=("Arial", 12, "bold"), bd=0, 
                 command=self.on_close, cursor="hand2",
                 activebackground="#ff4444").pack(side="right", padx=8)
        
        self.datetime_label = tk.Label(title_frame, text="", 
                                       fg="#aaaaaa", bg="#2d2d2d",
                                       font=("Segoe UI", 9))
        self.datetime_label.pack(side="right", padx=10)
        
        # STOCK SELECTOR WITH DROPDOWN LIST
        stock_section = tk.Frame(self.root, bg="#2a2a2a")
        stock_section.pack(fill="x", padx=10, pady=(10, 5))
        
        tk.Label(stock_section, text="📈 SELECT STOCK", 
                fg="#ffaa00", bg="#2a2a2a", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(8, 5))
        
        # Dropdown button
        dropdown_btn_frame = tk.Frame(stock_section, bg="#3a3a3a", cursor="hand2")
        dropdown_btn_frame.pack(fill="x", padx=10, pady=(0, 5))
        dropdown_btn_frame.bind("<Button-1>", self.toggle_dropdown)
        
        self.dropdown_label = tk.Label(dropdown_btn_frame, 
                                       text="▼ Click to select stock...",
                                       bg="#3a3a3a", fg="white",
                                       font=("Segoe UI", 11),
                                       anchor="w", cursor="hand2")
        self.dropdown_label.pack(fill="x", padx=15, pady=12)
        self.dropdown_label.bind("<Button-1>", self.toggle_dropdown)
        
        # Scrollable stock list (hidden by default)
        self.stock_list_frame = tk.Frame(stock_section, bg="#3a3a3a")
        
        list_container = tk.Frame(self.stock_list_frame, bg="#3a3a3a")
        list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        list_scrollbar = tk.Scrollbar(list_container)
        list_scrollbar.pack(side="right", fill="y")
        
        self.stock_listbox = tk.Listbox(list_container,
                                        bg="#3a3a3a", fg="white",
                                        font=("Segoe UI", 10),
                                        selectbackground="#00aaff",
                                        selectforeground="white",
                                        bd=0, highlightthickness=0,
                                        yscrollcommand=list_scrollbar.set,
                                        height=12)
        self.stock_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.config(command=self.stock_listbox.yview)
        
        # Populate listbox
        for stock in self.stocks_list:
            self.stock_listbox.insert(tk.END, stock)
        
        self.stock_listbox.bind("<<ListboxSelect>>", self.on_stock_select)
        
        # Stock expiry display
        expiry_display = tk.Frame(stock_section, bg="#2a2a2a")
        expiry_display.pack(fill="x", padx=10, pady=(5, 10))
        
        left_col = tk.Frame(expiry_display, bg="#2a2a2a")
        left_col.pack(side="left", fill="both", expand=True)
        
        self.stock_name_label = tk.Label(left_col, text="No stock selected", 
                                         fg="#888888", bg="#2a2a2a",
                                         font=("Segoe UI", 10, "bold"),
                                         anchor="w")
        self.stock_name_label.pack(anchor="w", pady=2)
        
        self.stock_exchange_label = tk.Label(left_col, text="", 
                                            fg="#888888", bg="#2a2a2a",
                                            font=("Segoe UI", 8),
                                            anchor="w")
        self.stock_exchange_label.pack(anchor="w")
        
        right_col = tk.Frame(expiry_display, bg="#2a2a2a")
        right_col.pack(side="left", fill="both", expand=True)
        
        self.stock_date_label = tk.Label(right_col, text="", 
                                        fg="white", bg="#2a2a2a",
                                        font=("Segoe UI", 10, "bold"),
                                        anchor="w")
        self.stock_date_label.pack(anchor="w", pady=2)
        
        self.stock_countdown_label = tk.Label(right_col, text="", 
                                             fg="#ffaa00", bg="#2a2a2a",
                                             font=("Segoe UI", 9),
                                             anchor="w")
        self.stock_countdown_label.pack(anchor="w")
        
        # Scrollable area
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(main_container, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e1e")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        content = tk.Frame(self.scrollable_frame, bg="#1e1e1e")
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Holidays
        holidays_section = tk.Frame(content, bg="#3a2a2a")
        holidays_section.pack(fill="x", pady=(0, 10))
        
        tk.Label(holidays_section, text="🗓️ UPCOMING HOLIDAYS", 
                fg="#ff6666", bg="#3a2a2a", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(8, 5))
        
        self.holidays_frame = tk.Frame(holidays_section, bg="#3a2a2a")
        self.holidays_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.update_holidays_display()
        
        tk.Frame(content, bg="#444444", height=2).pack(fill="x", pady=5)
        
        # Indices
        tk.Label(content, text="📊 INDICES", 
                fg="#00aaff", bg="#1e1e1e", 
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        hdr = tk.Frame(content, bg="#2a2a2a", height=35)
        hdr.pack(fill="x", pady=(0, 2))
        hdr.pack_propagate(False)
        
        tk.Label(hdr, text="INSTRUMENT", fg="#00ff88", bg="#2a2a2a",
                font=("Segoe UI", 9, "bold"), width=15, anchor="w").pack(side="left", padx=10)
        tk.Label(hdr, text="EXPIRY DATE", fg="#00aaff", bg="#2a2a2a",
                font=("Segoe UI", 9, "bold"), width=45, anchor="w").pack(side="left", padx=5)
        
        indices_frame = tk.Frame(content, bg="#1e1e1e")
        indices_frame.pack(fill="x")
        
        for idx, inst in enumerate(self.instruments.keys()):
            self.create_row(indices_frame, inst, idx)
        
        # Footer
        footer = tk.Frame(content, bg="#1e1e1e")
        footer.pack(fill="x", pady=(10, 0))
        
        self.update_label = tk.Label(footer, text="Initializing...", 
                                     fg="#666666", bg="#1e1e1e",
                                     font=("Segoe UI", 8))
        self.update_label.pack()
        
        tk.Button(footer, text="🔄 Refresh", fg="white", bg="#444444",
                 font=("Segoe UI", 9), bd=0, command=self.update_all_expiries,
                 cursor="hand2", padx=20, pady=6).pack(pady=(5, 10))
    
    def toggle_dropdown(self, event=None):
        """Show or hide the stock dropdown list"""
        if self.dropdown_visible:
            self.stock_list_frame.pack_forget()
            self.dropdown_label.config(text="▼ Click to select stock...")
            self.dropdown_visible = False
        else:
            self.stock_list_frame.pack(fill="x", padx=10, pady=(0, 5))
            self.dropdown_label.config(text="▲ Select from list below:")
            self.dropdown_visible = True
    
    def on_stock_select(self, event=None):
        """Handle stock selection"""
        selection = self.stock_listbox.curselection()
        if selection:
            stock_name = self.stock_listbox.get(selection[0])
            self.select_stock(stock_name)
            self.toggle_dropdown()  # Close dropdown after selection
    
    def select_stock(self, stock_name):
        """Display selected stock expiry"""
        self.selected_stock = stock_name
        self.stock_expiry_date = self.calculate_stock_expiry(stock_name)
        
        self.stock_name_label.config(text=stock_name, fg="white")
        self.stock_exchange_label.config(text="NSE - Monthly Stock Options")
        
        date_str = self.stock_expiry_date.strftime("%d %b %Y (%A)")
        time_str = self.stock_expiry_date.strftime("%I:%M %p")
        full_str = f"{date_str} {time_str}"
        
        color = self.get_color(self.stock_expiry_date)
        self.stock_date_label.config(text=full_str, fg=color)
        
        ct, cc = self.format_countdown(self.stock_expiry_date)
        self.stock_countdown_label.config(text=ct, fg=cc)
        
        self.dropdown_label.config(text=f"▼ Selected: {stock_name}")
        
        self.save_config()
    
    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        
    def update_holidays_display(self):
        for w in self.holidays_frame.winfo_children():
            w.destroy()
        
        for hd, hn, da in self.get_upcoming_holidays(2):
            hr = tk.Frame(self.holidays_frame, bg="#3a2a2a")
            hr.pack(fill="x", pady=2)
            
            tk.Label(hr, text=hd.strftime("%d %b %Y"), fg="#ffcccc", bg="#3a2a2a",
                    font=("Segoe UI", 9, "bold"), width=15, anchor="w").pack(side="left")
            tk.Label(hr, text=hn, fg="white", bg="#3a2a2a",
                    font=("Segoe UI", 9), anchor="w").pack(side="left", padx=5)
            
            if da == 0:
                txt, col = "TODAY", "#ff4444"
            elif da == 1:
                txt, col = "TOMORROW", "#ffaa00"
            else:
                txt, col = f"in {da}d", "#888888"
            
            tk.Label(hr, text=txt, fg=col, bg="#3a2a2a",
                    font=("Segoe UI", 8)).pack(side="right")
        
    def create_row(self, parent, name, idx):
        bg = "#252525" if idx % 2 == 0 else "#2a2a2a"
        
        row = tk.Frame(parent, bg=bg, height=55)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        
        left = tk.Frame(row, bg=bg, width=130)
        left.pack(side="left", fill="y", padx=8)
        left.pack_propagate(False)
        
        tk.Label(left, text=name, fg="white", bg=bg,
                font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w", pady=(8, 2))
        
        tk.Label(left, text=self.instruments[name]['exchange'], fg="#888888", bg=bg,
                font=("Segoe UI", 7), anchor="w").pack(anchor="w")
        
        right = tk.Frame(row, bg=bg)
        right.pack(side="left", fill="both", expand=True, padx=8)
        
        dl = tk.Label(right, text="Calculating...", fg="white", bg=bg,
                     font=("Segoe UI", 9, "bold"), anchor="w")
        dl.pack(anchor="w", pady=(6, 2))
        
        cl = tk.Label(right, text="...", fg="#ffaa00", bg=bg,
                     font=("Segoe UI", 8), anchor="w")
        cl.pack(anchor="w")
        
        self.expiry_labels[name] = {'date': dl, 'countdown': cl}
        
    def calculate_stock_expiry(self, stock):
        """All stocks expire on LAST THURSDAY of the month at 3:30 PM"""
        today = datetime.now()
        
        # Get next month
        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
        
        # Get last day of current month
        last_day = next_month - timedelta(days=1)
        
        # Find last Thursday
        while last_day.weekday() != 3:  # 3 = Thursday
            last_day -= timedelta(days=1)
        
        expiry = last_day.replace(hour=15, minute=30, second=0, microsecond=0)
        expiry = self.get_trading_day(expiry)
        
        # If already expired, get next month's expiry
        if expiry < today:
            if today.month == 12:
                next_next_month = today.replace(year=today.year+1, month=2, day=1)
            elif today.month == 11:
                next_next_month = today.replace(year=today.year+1, month=1, day=1)
            else:
                next_next_month = today.replace(month=today.month+2, day=1)
            
            last_day = next_next_month - timedelta(days=1)
            while last_day.weekday() != 3:
                last_day -= timedelta(days=1)
            
            expiry = last_day.replace(hour=15, minute=30, second=0, microsecond=0)
            expiry = self.get_trading_day(expiry)
        
        return expiry
        
    def setup_dragging(self):
        widgets = []
        for w in self.root.winfo_children():
            if isinstance(w, tk.Frame) and w.cget('bg') == '#2d2d2d':
                widgets.append(w)
                for c in w.winfo_children():
                    if not isinstance(c, tk.Button):
                        widgets.append(c)
        
        for w in widgets:
            w.bind("<Button-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)
            
    def start_move(self, e):
        self.x = e.x_root - self.root.winfo_x()
        self.y = e.y_root - self.root.winfo_y()
        
    def do_move(self, e):
        self.root.geometry(f"+{e.x_root - self.x}+{e.y_root - self.y}")
        
    def ensure_topmost(self):
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(2000, self.ensure_topmost)
        
    def get_trading_day(self, dt):
        cd = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        while cd.weekday() in [5, 6] or any(cd.date() == h[0].date() for h in self.nse_holidays):
            cd -= timedelta(days=1)
        return cd.replace(hour=dt.hour, minute=dt.minute, second=dt.second)
        
    def calculate_next_expiry(self, inst):
        cfg = self.instruments[inst]
        ed = cfg["expiry_day"]
        today = datetime.now()
        et = today.replace(hour=15, minute=30, second=0, microsecond=0)
        da = ed - today.weekday()
        
        if da == 0 and today.hour < 15:
            ne = et
        elif da <= 0:
            ne = (today + timedelta(days=da+7)).replace(hour=15, minute=30, second=0, microsecond=0)
        else:
            ne = (today + timedelta(days=da)).replace(hour=15, minute=30, second=0, microsecond=0)
        
        return self.get_trading_day(ne)
        
    def get_color(self, exp):
        now = datetime.now()
        if exp.date() == now.date():
            return "#ff4444"
        elif (exp - now).days <= 1:
            return "#ffaa00"
        return "#00ff88"
            
    def format_countdown(self, exp):
        diff = exp - datetime.now()
        if diff.total_seconds() < 0:
            return "⚠️ EXPIRED", "#ff4444"
        
        ts = int(diff.total_seconds())
        d, h, m, s = ts//86400, (ts%86400)//3600, (ts%3600)//60, ts%60
        
        if exp.date() == datetime.now().date():
            return f"⏰ TODAY - {h:02d}:{m:02d}:{s:02d}", "#ff4444"
        elif d == 0:
            return f"⏰ TOMORROW - {h}h {m}m", "#ffaa00"
        return f"⏳ {d}d {h}h", "#00ff88"
            
    def update_all_expiries(self):
        try:
            for inst in self.instruments.keys():
                exp = self.calculate_next_expiry(inst)
                self.expiry_dates[inst] = exp
                if inst in self.expiry_labels:
                    self.expiry_labels[inst]['date'].config(
                        text=exp.strftime("%d %b %Y (%A) %I:%M %p"), 
                        fg=self.get_color(exp))
                    ct, cc = self.format_countdown(exp)
                    self.expiry_labels[inst]['countdown'].config(text=ct, fg=cc)
            
            if self.selected_stock:
                self.select_stock(self.selected_stock)
            
            self.update_holidays_display()
            self.update_label.config(text=f"Updated: {datetime.now().strftime('%I:%M:%S %p')}")
        except Exception as e:
            self.update_label.config(text=f"Error: {e}")
        
    def realtime_update(self):
        try:
            for inst in self.instruments.keys():
                if inst in self.expiry_dates and inst in self.expiry_labels:
                    exp = self.expiry_dates[inst]
                    ct, cc = self.format_countdown(exp)
                    self.expiry_labels[inst]['countdown'].config(text=ct, fg=cc)
                    self.expiry_labels[inst]['date'].config(fg=self.get_color(exp))
            
            if self.stock_expiry_date:
                ct, cc = self.format_countdown(self.stock_expiry_date)
                self.stock_countdown_label.config(text=ct, fg=cc)
                self.stock_date_label.config(fg=self.get_color(self.stock_expiry_date))
            
            now = datetime.now()
            self.datetime_label.config(text=f"{now.strftime('%d %b %Y')} | {now.strftime('%I:%M:%S %p')}")
        except:
            pass
        
        self.root.after(1000, self.realtime_update)
        
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    c = json.load(f)
                    self.window_x = c.get('x', 1000)
                    self.window_y = c.get('y', 50)
                    saved_stock = c.get('selected_stock', '')
                    if saved_stock:
                        self.root.after(1000, lambda: self.select_stock(saved_stock))
            except:
                self.window_x, self.window_y = 1000, 50
        else:
            self.window_x, self.window_y = 1000, 50
        
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({
                    'x': self.root.winfo_x(), 
                    'y': self.root.winfo_y(),
                    'selected_stock': self.selected_stock if self.selected_stock else ''
                }, f)
        except:
            pass
            
    def on_close(self):
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OptionsExpiryWidget(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
