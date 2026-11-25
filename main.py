"""
Advanced Pixel Resolution Calculator
A lightweight, offline Windows desktop utility.
"""

from __future__ import annotations

import math
import tkinter as tk
from fractions import Fraction
from tkinter import messagebox, ttk


APP_TITLE = "Advanced Pixel Resolution Calculator"
APP_VERSION = "0.1.0"

ASPECT_RATIOS = {
    "1:1": [(1024, 1024), (1080, 1080), (1440, 1440), (2048, 2048)],
    "4:3": [(800, 600), (1024, 768), (1600, 1200), (2048, 1536)],
    "3:2": [(900, 600), (1200, 800), (1800, 1200), (3000, 2000)],
    "5:4": [(1280, 1024), (1600, 1280), (2560, 2048)],
    "16:10": [(1280, 800), (1440, 900), (1920, 1200), (2560, 1600)],
    "16:9": [(1280, 720), (1600, 900), (1920, 1080), (2560, 1440), (3840, 2160)],
    "21:9": [(1680, 720), (2560, 1080), (3440, 1440), (5120, 2160)],
    "9:16": [(720, 1280), (1080, 1920), (1440, 2560)],
    "2:3": [(600, 900), (800, 1200), (1200, 1800)],
    "3:4": [(600, 800), (768, 1024), (1200, 1600)],
}
RATIO_CHOICES = list(ASPECT_RATIOS) + ["Custom"]


def parse_ratio(value: str) -> tuple[int, int]:
    """Parse a ratio such as 16:9 and return its reduced integer terms."""
    try:
        left, right = value.strip().replace("/", ":").split(":")
        ratio = Fraction(int(left.strip()), int(right.strip()))
    except (ValueError, ZeroDivisionError):
        raise ValueError("Enter an aspect ratio such as 16:9 or 7:5.") from None

    if ratio.numerator <= 0 or ratio.denominator <= 0:
        raise ValueError("Aspect-ratio values must be greater than zero.")
    return ratio.numerator, ratio.denominator


def calculate_resolution(
    total_pixels: int, ratio_width: int, ratio_height: int, even_dimensions: bool
) -> tuple[int, int]:
    """Find the closest integer resolution that preserves the exact target ratio."""
    step = 2 if even_dimensions and (ratio_width % 2 or ratio_height % 2) else 1
    ideal_scale = math.sqrt(total_pixels / (ratio_width * ratio_height))
    scale = max(step, round(ideal_scale / step) * step)
    return ratio_width * scale, ratio_height * scale


class PixelCalculatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_TITLE}  |  v{APP_VERSION}")
        self.root.geometry("760x650")
        self.root.minsize(680, 600)
        self.root.configure(bg="#f3f5f8")

        self.source_ratio = tk.StringVar(value="16:9")
        self.source_preset = tk.StringVar(value="1920 × 1080")
        self.source_width = tk.StringVar(value="1920")
        self.source_height = tk.StringVar(value="1080")
        self.target_ratio = tk.StringVar(value="1:1")
        self.custom_target_ratio = tk.StringVar(value="5:4")
        self.even_dimensions = tk.BooleanVar(value=False)

        self.total_pixels = 0
        self.result_width = 0
        self.result_height = 0

        self._configure_style()
        self._build_interface()
        self._update_source_presets()
        self.calculate()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f5f8")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f3f5f8", foreground="#253247", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#ffffff", foreground="#253247", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#f3f5f8", foreground="#17243a", font=("Segoe UI", 19, "bold"))
        style.configure("Subtitle.TLabel", background="#f3f5f8", foreground="#64748b", font=("Segoe UI", 9))
        style.configure("Section.TLabel", background="#ffffff", foreground="#17243a", font=("Segoe UI", 12, "bold"))
        style.configure("Value.TLabel", background="#ffffff", foreground="#1457b8", font=("Segoe UI", 17, "bold"))
        style.configure("TCombobox", padding=6, font=("Segoe UI", 10))
        style.configure("TEntry", padding=6, font=("Segoe UI", 10))
        style.configure("TButton", padding=(12, 7), font=("Segoe UI", 10))
        style.configure("Accent.TButton", background="#2163c5", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#174fa5")])

    def _build_interface(self) -> None:
        outer = ttk.Frame(self.root, padding=24)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Advanced Pixel Resolution Calculator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Convert an image's pixel count to a different aspect ratio.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 18))

        source_card = ttk.Frame(outer, style="Card.TFrame", padding=18)
        source_card.pack(fill="x", pady=(0, 14))
        ttk.Label(source_card, text="1. Source image", style="Section.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 13)
        )

        ttk.Label(source_card, text="Aspect ratio", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        self.source_ratio_combo = ttk.Combobox(
            source_card, textvariable=self.source_ratio, values=RATIO_CHOICES, state="readonly", width=14
        )
        self.source_ratio_combo.grid(row=2, column=0, sticky="ew", padx=(0, 12))
        self.source_ratio_combo.bind("<<ComboboxSelected>>", self._update_source_presets)

        ttk.Label(source_card, text="Resolution preset", style="Card.TLabel").grid(row=1, column=1, sticky="w")
        self.preset_combo = ttk.Combobox(
            source_card, textvariable=self.source_preset, state="readonly", width=22
        )
        self.preset_combo.grid(row=2, column=1, sticky="ew", padx=(0, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self._select_source_preset)

        dimensions = ttk.Frame(source_card, style="Card.TFrame")
        dimensions.grid(row=2, column=2, columnspan=2, sticky="ew")
        ttk.Label(dimensions, text="Width", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(dimensions, text="Height", style="Card.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.width_entry = ttk.Entry(dimensions, textvariable=self.source_width, width=10)
        self.width_entry.grid(row=1, column=0, sticky="ew")
        self.height_entry = ttk.Entry(dimensions, textvariable=self.source_height, width=10)
        self.height_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        dimensions.columnconfigure((0, 1), weight=1)

        self.source_ratio_note = ttk.Label(
            source_card, text="Choose a preset or enter your own width and height.",
            style="Card.TLabel", foreground="#64748b"
        )
        self.source_ratio_note.grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 0))
        for column in range(4):
            source_card.columnconfigure(column, weight=1)

        target_card = ttk.Frame(outer, style="Card.TFrame", padding=18)
        target_card.pack(fill="x", pady=(0, 14))
        ttk.Label(target_card, text="2. Target aspect ratio", style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 13)
        )
        ttk.Label(target_card, text="Target ratio", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        self.target_ratio_combo = ttk.Combobox(
            target_card, textvariable=self.target_ratio, values=RATIO_CHOICES, state="readonly", width=16
        )
        self.target_ratio_combo.grid(row=2, column=0, sticky="ew", padx=(0, 14))
        self.target_ratio_combo.bind("<<ComboboxSelected>>", self._toggle_custom_ratio)

        ttk.Label(target_card, text="Custom ratio (if selected)", style="Card.TLabel").grid(
            row=1, column=1, sticky="w"
        )
        self.custom_ratio_entry = ttk.Entry(
            target_card, textvariable=self.custom_target_ratio, width=16, state="disabled"
        )
        self.custom_ratio_entry.grid(row=2, column=1, sticky="ew")
        target_card.columnconfigure((0, 1, 2), weight=1)

        options = ttk.Frame(target_card, style="Card.TFrame")
        options.grid(row=3, column=0, columnspan=3, sticky="w", pady=(12, 0))
        ttk.Checkbutton(
            options,
            text="Use even width and height (recommended for some image workflows)",
            variable=self.even_dimensions,
            command=self.calculate,
        ).pack(anchor="w")

        result_card = ttk.Frame(outer, style="Card.TFrame", padding=18)
        result_card.pack(fill="both", expand=True)
        ttk.Label(result_card, text="3. Calculation result", style="Section.TLabel").pack(anchor="w")

        stats = ttk.Frame(result_card, style="Card.TFrame")
        stats.pack(fill="x", pady=(15, 10))
        self.pixel_value = ttk.Label(stats, text="—", style="Value.TLabel")
        self.pixel_value.grid(row=0, column=0, sticky="w")
        ttk.Label(stats, text="Total source pixels", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        stats.columnconfigure(0, weight=1)

        self.result_value = ttk.Label(result_card, text="—", style="Value.TLabel")
        self.result_value.pack(anchor="w", pady=(10, 0))
        ttk.Label(result_card, text="Calculated target resolution", style="Card.TLabel").pack(anchor="w")

        self.difference_value = ttk.Label(
            result_card, text="Pixel-count difference: —", style="Card.TLabel"
        )
        self.difference_value.pack(anchor="w", pady=(12, 0))

        self.status_value = ttk.Label(
            result_card, text="Enter a valid source resolution to calculate.", style="Card.TLabel"
        )
        self.status_value.pack(anchor="w", pady=(5, 0))

        buttons = ttk.Frame(result_card, style="Card.TFrame")
        buttons.pack(fill="x", pady=(18, 0))
        ttk.Button(buttons, text="Calculate", style="Accent.TButton", command=self.calculate).pack(
            side="left"
        )
        ttk.Button(buttons, text="Copy resolution", command=self.copy_result).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(buttons, text="Reset", command=self.reset).pack(side="right")

        footer = ttk.Label(
            outer, text="Works offline • No image files are uploaded or modified",
            style="Subtitle.TLabel"
        )
        footer.pack(anchor="center", pady=(12, 0))

        self.width_entry.bind("<Return>", lambda _event: self.calculate())
        self.height_entry.bind("<Return>", lambda _event: self.calculate())
        self.custom_ratio_entry.bind("<Return>", lambda _event: self.calculate())

    def _update_source_presets(self, _event=None) -> None:
        ratio = self.source_ratio.get()
        presets = ASPECT_RATIOS.get(ratio, [])
        values = [f"{w} × {h}" for w, h in presets] + ["Custom resolution"]
        self.preset_combo.configure(values=values)

        if presets:
            preferred = (1920, 1080) if ratio == "16:9" else presets[0]
            if preferred not in presets:
                preferred = presets[0]
            self.source_preset.set(f"{preferred[0]} × {preferred[1]}")
            self.source_width.set(str(preferred[0]))
            self.source_height.set(str(preferred[1]))
        else:
            self.source_preset.set("Custom resolution")
            self.source_ratio_note.configure(
                text="Custom source ratio selected. Enter any width and height."
            )

        if ratio != "Custom":
            self.source_ratio_note.configure(
                text="Choose a preset or enter your own width and height."
            )
        self.calculate()

    def _select_source_preset(self, _event=None) -> None:
        value = self.source_preset.get()
        if value == "Custom resolution":
            self.width_entry.focus_set()
            self.width_entry.selection_range(0, "end")
            return
        try:
            width, height = value.replace(" ", "").split("×")
            self.source_width.set(width)
            self.source_height.set(height)
            self.calculate()
        except ValueError:
            pass

    def _toggle_custom_ratio(self, _event=None) -> None:
        state = "normal" if self.target_ratio.get() == "Custom" else "disabled"
        self.custom_ratio_entry.configure(state=state)
        self.calculate()

    def _get_target_ratio(self) -> tuple[int, int]:
        value = self.custom_target_ratio.get() if self.target_ratio.get() == "Custom" else self.target_ratio.get()
        return parse_ratio(value)

    def calculate(self) -> None:
        try:
            width = int(self.source_width.get().strip())
            height = int(self.source_height.get().strip())
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be greater than zero.")

            target_w, target_h = self._get_target_ratio()
            pixels = width * height
            result_w, result_h = calculate_resolution(
                pixels, target_w, target_h, self.even_dimensions.get()
            )
        except ValueError as error:
            self.pixel_value.configure(text="—")
            self.result_value.configure(text="—")
            self.difference_value.configure(text="Pixel-count difference: —")
            self.status_value.configure(text=str(error))
            self.total_pixels = 0
            self.result_width = 0
            self.result_height = 0
            return

        result_pixels = result_w * result_h
        difference = result_pixels - pixels
        difference_percent = (difference / pixels) * 100

        self.total_pixels = pixels
        self.result_width = result_w
        self.result_height = result_h

        self.pixel_value.configure(text=f"{pixels:,} pixels  ({pixels / 1_000_000:.3f} MP)")
        self.result_value.configure(text=f"{result_w:,} × {result_h:,}")
        self.difference_value.configure(
            text=(
                f"Result: {result_pixels:,} pixels  |  "
                f"Difference: {difference:+,} pixels ({difference_percent:+.4f}%)"
            )
        )
        self.status_value.configure(
            text=f"Target ratio: {target_w}:{target_h}  •  Original: {width} × {height}"
        )

    def copy_result(self) -> None:
        if not self.result_width or not self.result_height:
            messagebox.showwarning("Nothing to copy", "Please enter a valid resolution first.")
            return
        value = f"{self.result_width}x{self.result_height}"
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.status_value.configure(text=f"Copied {value} to clipboard.")

    def reset(self) -> None:
        self.source_ratio.set("16:9")
        self.source_preset.set("1920 × 1080")
        self.source_width.set("1920")
        self.source_height.set("1080")
        self.target_ratio.set("1:1")
        self.custom_target_ratio.set("5:4")
        self.even_dimensions.set(False)
        self.custom_ratio_entry.configure(state="disabled")
        self._update_source_presets()


def main() -> None:
    root = tk.Tk()
    PixelCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
