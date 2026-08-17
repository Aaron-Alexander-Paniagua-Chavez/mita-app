"""Componentes UI accesibles — Material Design adaptado (RNF01–RNF03)."""
import os
import tkinter as tk
from io import BytesIO
from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image

from config.settings import (
    ACCENT_GREEN,
    ACCENT_GREEN_LIGHT,
    ACCENT_TERRACOTA,
    BG_COLOR,
    BUTTON_HEIGHT,
    BUTTON_HEIGHT_LARGE,
    DARK_TEXT,
    ENTRY_HEIGHT,
    FONT_FAMILY,
    FONT_SIZE_BODY,
    FONT_SIZE_BUTTON,
    FONT_SIZE_SUBTITLE,
    FONT_SIZE_TITLE,
    SOFT_GREEN,
    TEXT_GRAY,
    WHITE,
)
from ui.i18n import traducir


class ComponenteUI:
    """Clase base que garantiza lineamientos de accesibilidad."""

    _acento = ACCENT_GREEN
    _acento_hover = ACCENT_GREEN_LIGHT

    @classmethod
    def establecer_tema(cls, tema: str) -> None:
        """Acentos adicionales conservando los modos claro/oscuro de MITA."""
        temas = {
            "clasico": (ACCENT_GREEN, ACCENT_GREEN_LIGHT),
            "oceano": (("#226A8A", "#68BDE0"), ("#18526B", "#4A9ABF")),
            "lavanda": (("#715A9C", "#B8A4D8"), ("#594779", "#927AB8")),
            "calido": (("#A85A3B", "#E09B7A"), ("#80432B", "#BF7659")),
        }
        cls._acento, cls._acento_hover = temas.get(tema, temas["clasico"])

    @staticmethod
    def fuente(tamano: int, bold: bool = False) -> ctk.CTkFont:
        return ctk.CTkFont(family=FONT_FAMILY, size=max(tamano, 16), weight="bold" if bold else "normal")

    @staticmethod
    def boton(
        parent,
        texto: str,
        command: Callable,
        primario: bool = True,
        grande: bool = False,
        ancho: Optional[int] = None,
        color: Optional[str] = None,
    ) -> ctk.CTkButton:
        h = BUTTON_HEIGHT_LARGE if grande else BUTTON_HEIGHT
        return ctk.CTkButton(
            parent,
            text=texto,
            command=command,
            width=ancho or 320,
            height=h,
            fg_color=color or ComponenteUI._acento,
            hover_color=ComponenteUI._acento_hover,
            corner_radius=12,
            font=ComponenteUI.fuente(FONT_SIZE_BUTTON, bold=True),
            text_color=WHITE,
        )

    @staticmethod
    def entrada(parent, placeholder: str, ancho: int = 380, password: bool = False) -> ctk.CTkEntry:
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            width=ancho,
            height=ENTRY_HEIGHT,
            corner_radius=10,
            font=ComponenteUI.fuente(FONT_SIZE_BODY),
            show="*" if password else "",
        )

    @staticmethod
    def titulo(parent, texto: str, tamano: int = FONT_SIZE_TITLE) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent,
            text=texto,
            font=ComponenteUI.fuente(tamano, bold=True),
            text_color=DARK_TEXT,
        )

    @staticmethod
    def subtitulo(parent, texto: str) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent,
            text=texto,
            font=ComponenteUI.fuente(FONT_SIZE_SUBTITLE),
            text_color=TEXT_GRAY,
        )


class LogoMITA(ctk.CTkFrame):
    """Logo vectorial convertido a imagen — visible en todas las ventanas."""

    _cache_image = None

    def __init__(self, parent, size: int = 80, **kwargs) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._render_logo(size)

    @classmethod
    def _cargar_imagen(cls, size: int):
        if cls._cache_image and cls._cache_image._size == (size, size):
            return cls._cache_image

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        png_path = os.path.join(base_dir, "assets", "logo_mita.png")
        svg_path = os.path.join(base_dir, "assets", "logo_mita.svg")

        if os.path.exists(svg_path):
            try:
                import cairosvg
                png_data = cairosvg.svg2png(
                    url=svg_path, output_width=size * 2, output_height=size * 2
                )
                img = Image.open(BytesIO(png_data))
                cls._cache_image = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(size, size)
                )
                cls._cache_image._size = (size, size)
                return cls._cache_image
            except Exception:
                pass

        if os.path.exists(png_path):
            img = Image.open(png_path)
            cls._cache_image = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
            cls._cache_image._size = (size, size)
            return cls._cache_image

        # Fallback tipográfico estilizado
        return None

    def _render_logo(self, size: int) -> None:
        img = self._cargar_imagen(size)
        if img:
            ctk.CTkLabel(self, text="", image=img).pack()
        else:
            ctk.CTkLabel(
                self,
                text="♥",
                font=ctk.CTkFont(family=FONT_FAMILY, size=max(22, size // 2), weight="bold"),
                text_color=ACCENT_TERRACOTA,
            ).pack()


class GuiaVisual(ctk.CTkFrame):
    """Dibujo sencillo y animado para acompañar instrucciones sin depender de red."""

    def __init__(self, parent, movimiento: str = "general", animar: bool = True, **kwargs) -> None:
        super().__init__(parent, fg_color=SOFT_GREEN, corner_radius=14, **kwargs)
        self.movimiento = movimiento
        self._fase = 0
        self._animar = animar
        self.canvas = tk.Canvas(self, width=150, height=120, bg="#E8F0E8", highlightthickness=0)
        self.canvas.pack(padx=10, pady=8)
        self._dibujar()
        if animar:
            self.after(700, self._pulso)

    def _dibujar(self) -> None:
        c = self.canvas
        c.delete("all")
        verde, terracota = "#21574A", "#D39B75"
        y = 31 + (2 if self._fase else 0)
        # Cabeza, cuerpo, brazos y piernas: una silueta universal, legible y sin estereotipos.
        c.create_oval(66, y - 18, 84, y, fill=terracota, outline=verde, width=2)
        c.create_line(75, y, 75, y + 45, fill=verde, width=5, capstyle="round")
        if self.movimiento in {"brazos", "hombros", "movimiento"}:
            brazos = (43, y + 10, 106, y + 2) if self._fase else (48, y + 18, 102, y + 18)
        elif self.movimiento in {"respiracion", "sentado"}:
            brazos = (55, y + 21, 95, y + 21)
        else:
            brazos = (51, y + 15, 99, y + 15)
        c.create_line(75, y + 12, brazos[0], brazos[1], fill=verde, width=5, capstyle="round")
        c.create_line(75, y + 12, brazos[2], brazos[3], fill=verde, width=5, capstyle="round")
        if self.movimiento in {"piernas", "rodillas", "caminar", "equilibrio"}:
            c.create_line(75, y + 45, 55, y + 72 + (3 if self._fase else 0), fill=verde, width=5, capstyle="round")
            c.create_line(75, y + 45, 98, y + 70 - (3 if self._fase else 0), fill=verde, width=5, capstyle="round")
        else:
            c.create_line(75, y + 45, 61, y + 74, fill=verde, width=5, capstyle="round")
            c.create_line(75, y + 45, 89, y + 74, fill=verde, width=5, capstyle="round")
        if self.movimiento == "respiracion":
            c.create_arc(105, y + 15, 137, y + 47, start=80, extent=200, style="arc", outline=terracota, width=3)
        c.create_text(75, 106, text="Guía ilustrada", fill="#21574A", font=(FONT_FAMILY, 11, "bold"))

    def _pulso(self) -> None:
        if not self.winfo_exists():
            return
        self._fase = 1 - self._fase
        self._dibujar()
        self.after(700, self._pulso)


class NotificationService:
    """Retroalimentación visual centralizada."""

    @staticmethod
    def mostrar(parent, texto: str, es_error: bool = False, duracion: int = 3500) -> None:
        from config.settings import ERROR_COLOR

        color = ERROR_COLOR if es_error else ACCENT_GREEN
        toast = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        toast.pack(side="top", fill="x", padx=16, pady=8)
        ctk.CTkLabel(
            toast,
            text=traducir(texto),
            text_color=WHITE,
            font=ComponenteUI.fuente(FONT_SIZE_BODY, bold=True),
            wraplength=700,
        ).pack(padx=16, pady=10)
        parent.after(duracion, toast.destroy)


class GestorNavegacion:
    """Router con confirmación para acciones críticas."""

    @staticmethod
    def confirmar(parent, mensaje: str, on_si: Callable) -> None:
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Confirmar")
        dialog.geometry("420x200")
        dialog.transient(parent)
        dialog.grab_set()
        dialog.configure(fg_color=BG_COLOR)
        ComponenteUI.titulo(dialog, "¿Está seguro?").pack(pady=(20, 10))
        ComponenteUI.subtitulo(dialog, mensaje).pack(pady=5)
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(pady=20)
        ComponenteUI.boton(frame, "Sí, continuar", lambda: (on_si(), dialog.destroy()), ancho=160).pack(side="left", padx=8)
        ComponenteUI.boton(
            frame, "Cancelar", dialog.destroy, primario=False,
            color=TEXT_GRAY, ancho=140,
        ).pack(side="left", padx=8)
