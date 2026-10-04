"""
Metrics and Scientific Telemetry Panel.
Displays live analytical calculations: fringe spacing, angular separation,
central envelope width, Michelson visibility, missing orders, and data export buttons.
Fully styled with Vazirmatn and Space Grotesk typography.
"""

from typing import Dict, Any, Callable, Optional
import customtkinter as ctk

from utils.localization import LocalizationService
from utils.font_manager import FontManager

class MetricsPanel(ctk.CTkFrame):
    """
    Displays real-time analytical calculations, statistical counters, and export buttons.
    """

    def __init__(
        self,
        master,
        on_export_csv: Callable[[], None],
        on_export_plot: Callable[[], None],
        on_export_obj: Optional[Callable[[], None]] = None,
        on_export_zip: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.on_export_csv = on_export_csv
        self.on_export_plot = on_export_plot
        self.on_export_obj = on_export_obj
        self.on_export_zip = on_export_zip

        self.labels: Dict[str, ctk.CTkLabel] = {}
        self.title_labels: Dict[str, ctk.CTkLabel] = {}

        self.metrics_keys = [
            ("fringe_spacing", "Δy = 2.531 mm", "#00F0FF", 0, 0),
            ("angular_separation", "θ = 2.53 mrad", "#38BDF8", 0, 1),
            ("central_width", "Env = 25.31 mm", "#FBBF24", 0, 2),
            ("visibility", "V = 1.000", "#10B981", 0, 3),
            ("missing_orders", "Missing: None", "#A78BFA", 1, 0),
            ("detected_hits", "Hits: N = 0", "#4ADE80", 1, 1),
            ("chi_square", "χ²_red = 1.00", "#F472B6", 1, 2),
        ]

        self._create_widgets()

    def _create_widgets(self):
        """Constructs metric readout tiles and action buttons."""
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        is_fa = LocalizationService.current_language() == "fa"

        # Metrics rows: 4 columns across bottom
        for key, default_text, color, r, c in self.metrics_keys:
            tile = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=6, border_width=1, border_color="#27272A")
            tile.grid(row=r, column=c, padx=3, pady=2, sticky="nsew")

            title = ctk.CTkLabel(
                tile,
                text=LocalizationService.get(key),
                font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
                text_color="#A1A1AA",
                anchor="e" if is_fa else "w"
            )
            title.pack(anchor="e" if is_fa else "w", padx=6, pady=(3, 0), fill="x")
            self.title_labels[key] = title

            val = ctk.CTkLabel(
                tile,
                text=default_text,
                font=FontManager.get_number_font(12, "bold"),
                text_color=color,
                anchor="w"
            )
            val.pack(anchor="w", padx=6, pady=(0, 3))
            self.labels[key] = val

        # Export Buttons Tile in (row 1, col 3)
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=1, column=3, padx=3, pady=2, sticky="nsew")
        action_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_csv = ctk.CTkButton(
            action_frame,
            text=LocalizationService.get("export_csv"),
            command=self.on_export_csv,
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=28,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_csv.grid(row=0, column=0, padx=1, pady=1, sticky="ew")

        self.btn_plot = ctk.CTkButton(
            action_frame,
            text=LocalizationService.get("export_plot"),
            command=self.on_export_plot,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            height=28,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_plot.grid(row=0, column=1, padx=1, pady=1, sticky="ew")

        self.btn_obj = ctk.CTkButton(
            action_frame,
            text=LocalizationService.get("export_obj"),
            command=self._handle_export_obj,
            fg_color="#059669",
            hover_color="#047857",
            height=28,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_obj.grid(row=0, column=2, padx=1, pady=1, sticky="ew")

        self.btn_zip = ctk.CTkButton(
            action_frame,
            text=LocalizationService.get("export_zip"),
            command=self._handle_export_zip,
            fg_color="#D97706",
            hover_color="#B45309",
            height=28,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_zip.grid(row=0, column=3, padx=1, pady=1, sticky="ew")

    def _handle_export_obj(self):
        if self.on_export_obj:
            self.on_export_obj()

    def _handle_export_zip(self):
        if self.on_export_zip:
            self.on_export_zip()

    def refresh_language(self):
        """Refreshes text and fonts when language toggles."""
        is_fa = LocalizationService.current_language() == "fa"

        for key, _, _, _, _ in self.metrics_keys:
            if key in self.title_labels:
                lbl = self.title_labels[key]
                lbl.configure(
                    text=LocalizationService.get(key),
                    font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
                    anchor="e" if is_fa else "w"
                )
                lbl.pack(anchor="e" if is_fa else "w")

        csv_txt = LocalizationService.get("export_csv")
        plot_txt = LocalizationService.get("export_plot")
        obj_txt = LocalizationService.get("export_obj")
        zip_txt = LocalizationService.get("export_zip")

        self.btn_csv.configure(
            text=csv_txt,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_plot.configure(
            text=plot_txt,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_obj.configure(
            text=obj_txt,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )
        self.btn_zip.configure(
            text=zip_txt,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
        )

    def update_metrics(
        self,
        features: Dict[str, Any],
        total_hits: int = 0,
        chi2_dict: Dict[str, float] | None = None
    ):
        """Updates all analytical readout tiles."""
        # 1. Fringe Spacing Δy
        dy_mm = features.get("fringe_spacing_dy_mm", 0.0)
        if dy_mm < 0.1:
            self.labels["fringe_spacing"].configure(text=f"Δy = {dy_mm * 1000.0:.2f} µm")
        else:
            self.labels["fringe_spacing"].configure(text=f"Δy = {dy_mm:.3f} mm")

        # 2. Angular Separation θ
        theta_mrad = features.get("angular_separation_rad", 0.0) * 1000.0
        self.labels["angular_separation"].configure(text=f"θ = {theta_mrad:.3f} mrad")

        # 3. Central Envelope Width
        env_mm = features.get("central_envelope_width_mm", 0.0)
        self.labels["central_width"].configure(text=f"Width = {env_mm:.2f} mm")

        # 4. Visibility V
        v = features.get("visibility", 1.0)
        self.labels["visibility"].configure(text=f"V = {v:.3f}")

        # 5. Missing Orders
        miss = features.get("missing_orders", [])
        if miss:
            pos_m = [str(abs(m)) for m in miss if m > 0][:3]
            txt = "m = ±" + ", ±".join(pos_m)
        else:
            txt = LocalizationService.get("missing_none")
        self.labels["missing_orders"].configure(text=f"{txt}")

        # 6. Detected Hits
        self.labels["detected_hits"].configure(text=f"N = {total_hits:,}")

        # 7. Chi-Square / Convergence
        if chi2_dict and total_hits > 50:
            c2_red = chi2_dict.get("chi2_reduced", 1.0)
            qual = chi2_dict.get("convergence_quality", 1.0) * 100.0
            self.labels["chi_square"].configure(text=f"χ² = {c2_red:.2f} ({qual:.0f}%)")
        else:
            self.labels["chi_square"].configure(text="χ² = Ready")
