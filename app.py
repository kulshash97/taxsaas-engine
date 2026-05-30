import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os

class KSPManagementConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("KSP Unified Console - Management Node v3.0")
        
        # FIXED: Geometry strings in Tkinter must use 'x' instead of a comma
        self.root.geometry("1000x700")
        self.root.configure(bg="#0F172A") # Deep Slate Navy
        
        # Color Palette Settings
        self.bg_dark = "#0F172A"
        self.accent_purple = "#6D28D9"
        self.text_light = "#F8FAFC"
        self.card_bg = "#1E293B"
        
        self.setup_styles()
        self.create_layout()
        self.load_initial_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=self.bg_dark, foreground=self.text_light)
        style.configure('TLabel', background=self.bg_dark, foreground=self.text_light, font=('Helvetica', 10))
        style.configure('TFrame', background=self.bg_dark)
        style.configure('Heading.TLabel', font=('Helvetica', 14, 'bold'), foreground=self.accent_purple)
        
        # Notebook/Tabs custom styling
        style.configure('TNotebook', background=self.bg_dark, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.card_bg, foreground=self.text_light, padding=[15, 5], font=('Helvetica', 10))
        style.map('TNotebook.Tab', background=[('selected', self.accent_purple)], foreground=[('selected', self.text_light)])

    def create_layout(self):
        # Top Header Banner
        header_frame = tk.Frame(self.root, bg=self.card_bg, height=70)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        title_lbl = tk.Label(header_frame, text="KULKARNI STRATEGIC PARTNERS", font=('Helvetica', 16, 'bold'), bg=self.card_bg, fg=self.text_light)
        title_lbl.pack(side='left', padx=20, pady=10)
        
        subtitle_lbl = tk.Label(header_frame, text="Unified Operations & Growth Engine", font=('Helvetica', 10, 'italic'), bg=self.card_bg, fg="#94A3B8")
        subtitle_lbl.pack(side='left', pady=15)
        
        # Master Tab Control Node
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Build individual functional tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_leads = ttk.Frame(self.notebook)
        self.tab_social = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard, text="📊 Platform Dashboard")
        self.notebook.add(self.tab_leads, text="📡 Target Lead Matrix")
        self.notebook.add(self.tab_social, text="📱 Social Trust Grid")
        
        self.build_dashboard_tab()
        self.build_leads_tab()
        self.build_social_tab()

    def build_dashboard_tab(self):
        # Main Container
        main_frame = tk.Frame(self.tab_dashboard, bg=self.bg_dark)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        lbl = ttk.Label(main_frame, text="Operational Runway & Parameters", style='Heading.TLabel')
        lbl.pack(anchor='w', pady=(0, 15))
        
        # Stat Cards Layout
        stats_frame = tk.Frame(main_frame, bg=self.bg_dark)
        stats_frame.pack(fill='x', pady=10)
        
        # Configured column configurations for grid auto-distribution
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        
        self.create_stat_card(stats_frame, "Monthly Income Target", "INR 2,00,000", 0)
        self.create_stat_card(stats_frame, "Daily Run-Rate Required", "INR 6,666.67 / Day", 1)
        self.create_stat_card(stats_frame, "Configured Gateway Node", "shashankkulkarni228@gmail.com", 2)
        
        # Platform Tier Details Area
        tier_frame = tk.LabelFrame(main_frame, text=" Software Subscription Multi-Tenant Architecture ", font=('Helvetica', 10, 'bold'), bg=self.bg_dark, fg=self.text_light, bd=1, relief='solid')
        tier_frame.pack(fill='both', expand=True, pady=20)
        
        tiers_txt = (
            "🟢 STARTER SOLO TIER (INR 1,999 / mo):\n"
            "   -> Includes Module 1 (Smart ITR Filing Engine) & Module 2 (Incorporation Strategy Matrix).\n"
            "   -> Value Vector: Automatically optimizes presumptive tax declarations under Sec 44ADA to protect bank underwriting.\n\n"
            "🔵 GROWTH PRACTICE TIER (INR 4,999 / mo):\n"
            "   -> Includes Modules 1, 2, 5 (GST Command Center Core), and Module 6 (Predictive Fractional CFO Model).\n"
            "   -> Value Vector: Empowers junior articles to smoothly run localized INR 25k - 75k recurring monthly advisory retainers.\n\n"
            "👑 ELITE PARTNER TIER (INR 9,999 / mo):\n"
            "   -> Full 6-Module Infrastructure Infrastructure Suite (Includes Valuation Modeler & Venture Pitch Deck Architect).\n"
            "   -> Value Vector: Instantly executes institutional capital evaluation algorithms to command INR 50,000+ corporate fees."
        )
        
        display_box = scrolledtext.ScrolledText(tier_frame, wrap=tk.WORD, bg=self.card_bg, fg=self.text_light, font=('Consolas', 10), insertbackground=self.text_light, bd=0)
        display_box.insert(tk.END, tiers_txt)
        display_box.configure(state='disabled')
        display_box.pack(fill='both', expand=True, padx=10, pady=10)

    def build_leads_tab(self):
        main_frame = tk.Frame(self.tab_leads, bg=self.bg_dark)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        top_bar = tk.Frame(main_frame, bg=self.bg_dark)
        top_bar.pack(fill='x', pady=(0, 10))
        
        lbl = ttk.Label(top_bar, text="Deduplicated B2B Lead Grid", style='Heading.TLabel')
        lbl.pack(side='left')
        
        refresh_btn = tk.Button(top_bar, text="🔄 Reload Active Leads", bg=self.accent_purple, fg=self.text_light, font=('Helvetica', 9, 'bold'), bd=0, padx=10, pady=4, command=self.load_leads_matrix)
        refresh_btn.pack(side='right')

        # Treeview Ledger Table Design
        columns = ('name', 'location', 'phone', 'email', 'tier')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('name', text='Firm Corporate Name')
        self.tree.heading('location', text='Primary Location Node')
        self.tree.heading('phone', text='Contact Phone')
        self.tree.heading('email', text='Delivery Terminal Inbox')
        self.tree.heading('tier', text='Target Category Vector')
        
        self.tree.column('name', width=250, anchor='w')
        self.tree.column('location', width=150, anchor='center')
        self.tree.column('phone', width=120, anchor='center')
        self.tree.column('email', width=200, anchor='w')
        self.tree.column('tier', width=180, anchor='center')
        
        # Style treeview items to dark theme standards
        style = ttk.Style()
        style.configure("Treeview", background=self.card_bg, fieldbackground=self.card_bg, foreground=self.text_light, rowheight=28)
        style.map("Treeview", background=[('selected', self.accent_purple)])
        
        self.tree.pack(fill='both', expand=True)

    def build_social_tab(self):
        main_frame = tk.Frame(self.tab_social, bg=self.bg_dark)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        lbl = ttk.Label(main_frame, text="Evergreen 9-Post Trust Grid Content Engine Blueprint", style='Heading.TLabel')
        lbl.pack(anchor='w', pady=(0, 10))
        
        # Scrolled Text panel to read the generated marketing scripts hands-free
        self.social_text_box = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, bg=self.card_bg, fg=self.text_light, font=('Consolas', 10), insertbackground=self.text_light, bd=0)
        self.social_text_box.pack(fill='both', expand=True)
        
        load_blueprint_btn = tk.Button(main_frame, text="📖 Stream Social Blueprint Data", bg=self.accent_purple, fg=self.text_light, font=('Helvetica', 10, 'bold'), bd=0, pady=6, command=self.load_social_blueprint)
        load_blueprint_btn.pack(fill='x', pady=(10, 0))

    # COMPLETED: Implementation for structural stat card visual injection
    def create_stat_card(self, parent, title, value, column):
        card = tk.Frame(parent, bg=self.card_bg, bd=1, relief='solid', highlightbackground="#475569")
        card.grid(row=0, column=column, padx=10, pady=5, sticky='nsew')
        
        lbl_title = tk.Label(card, text=title.upper(), font=('Helvetica', 8, 'bold'), bg=self.card_bg, fg="#94A3B8")
        lbl_title.pack(anchor='w', padx=15, pady=(12, 2))
        
        lbl_val = tk.Label(card, text=value, font=('Consolas', 12, 'bold'), bg=self.card_bg, fg=self.text_light)
        lbl_val.pack(anchor='w', padx=15, pady=(0, 12))

    # COMPLETED: Safe Initialization Pipeline
    def load_initial_data(self):
        self.load_leads_matrix()
        self.load_social_blueprint()

    # COMPLETED: Data Processing for Target B2B Lead Grid
    def load_leads_matrix(self):
        # Flush out existing tree records to avoid overlapping duplicates
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Standard Mock B2B Ledger Array
        mock_leads = [
            ("Kulkarni & Associates", "Mumbai Corporate HQ", "+91 98765 43210", "contact@kulkarnicorporate.in", "👑 ELITE PARTNER"),
            ("Alpha Digital Ventures", "Bangalore Hub", "+91 87654 32109", "ops@alphadigital.co", "🔵 GROWTH PRACTICE"),
            ("Nikhil Freelance Logistics", "Pune Node", "+91 76543 21098", "nikhil@freelancelog.in", "🟢 STARTER SOLO"),
            ("Apex Tax Consultants", "Hyderabad Site", "+91 65432 10987", "info@apextax.com", "🔵 GROWTH PRACTICE"),
