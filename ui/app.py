"""Aplicación principal MITA — CustomTkinter con roles y accesibilidad."""
import tkinter as tk

import customtkinter as ctk

from config.settings import (
    ACCENT_GREEN,
    ADMIN_SECRET_COMBO,
    BG_COLOR,
    BG_WARM,
    DARK_TEXT,
    FONT_SIZE_HERO,
    SOFT_GREEN,
    SURFACE_COLOR,
    TEXT_GRAY,
)
from core.database import DatabaseManager
from core.messages import MensajeMITA
from core.session import SessionManager
from core.sync import GestorSincronizacionLocal
from models.progreso import GestorProgreso, SistemaLogros
from repositories.comunidad_repository import ComunidadRepository
from repositories.estadistica_repository import EstadisticaRepository
from repositories.progreso_repository import ProgresoRepository
from repositories.usuario_repository import UsuarioRepository
from services.admin_service import AdministradorUsuarios
from services.auth_service import AuthService
from services.comunidad_service import ComunidadService, PermisoSeguimiento
from services.analytics_service import AnalyticsService
from ui.components import ComponenteUI, LogoMITA, NotificationService
from ui.i18n import IDIOMAS, establecer_idioma, idioma_actual, traducir
from ui.views.role_views import VistaAdmin, VistaAdultoMayor, VistaCuidador, VistaFamiliar

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class MitaApp(ctk.CTk):
    """Ventana principal — orquesta servicios, navegación y vistas por rol."""

    def __init__(self) -> None:
        super().__init__()
        self.title("MITA — Ayuda a evitar y cuidar el envejecimiento")
        self.geometry("980x720")
        self.minsize(900, 650)
        self.configure(fg_color=BG_COLOR)
        self.font_scale = 1.0
        self.tema_oscuro = ctk.BooleanVar(value=False)
        self.actividad_actual = None
        self.rol_seleccionado = None

        # Capa de servicios (SRP / RNF08)
        self.db_service = DatabaseManager()
        self.user_repo = UsuarioRepository(self.db_service)
        self.progreso_repo = ProgresoRepository(self.db_service)
        self.comunidad_repo = ComunidadRepository(self.db_service)
        self.estadistica_repo = EstadisticaRepository(self.db_service)
        self.auth_service = AuthService(self.user_repo)
        self.admin_service = AdministradorUsuarios(self.user_repo, self.db_service)
        self.comunidad_service = ComunidadService(self.comunidad_repo)
        self.permiso_service = PermisoSeguimiento(self.user_repo)
        self.analytics_service = AnalyticsService(self.estadistica_repo)
        self.mongo_session_id = None
        self.sync_service = GestorSincronizacionLocal(self.db_service)
        self.gestor_progreso = GestorProgreso()
        self.sistema_logros = SistemaLogros()

        # Vistas por rol
        self.vista_adulto = VistaAdultoMayor(self)
        self.vista_familiar = VistaFamiliar(self)
        self.vista_cuidador = VistaCuidador(self)
        self.vista_admin = VistaAdmin(self)

        self._crear_barra_accesibilidad()
        self.main_container = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.main_container.pack(fill="both", expand=True)

        self.bind(ADMIN_SECRET_COMBO, self._abrir_admin_secreto)
        self.mostrar_bienvenida()

    def limpiar_pantalla(self) -> None:
        for w in self.main_container.winfo_children():
            w.destroy()
        self.after_idle(self.aplicar_idioma_actual)

    def ajustar_texto(self, factor: float) -> None:
        self.font_scale = max(0.8, min(1.5, self.font_scale * factor))
        ctk.set_widget_scaling(self.font_scale)
        NotificationService.mostrar(
            self.main_container,
            f"Tamaño de texto ajustado ({int(self.font_scale * 100)}%)",
        )

    def _crear_barra_accesibilidad(self) -> None:
        """Controles persistentes, disponibles antes y después del inicio de sesión."""
        barra = ctk.CTkFrame(self, fg_color=SURFACE_COLOR, corner_radius=0, height=48)
        barra.pack(fill="x", side="top")
        barra.pack_propagate(False)
        self._texto_accesibilidad = ctk.CTkLabel(
            barra, text="Accesibilidad", font=ComponenteUI.fuente(14, bold=True), text_color=DARK_TEXT,
        )
        self._texto_accesibilidad.pack(side="left", padx=(18, 8), pady=7)
        ctk.CTkButton(
            barra, text="A−", width=42, height=32, command=lambda: self.ajustar_texto(0.9),
            font=ComponenteUI.fuente(16, bold=True), fg_color=ACCENT_GREEN,
        ).pack(side="left", padx=2, pady=7)
        ctk.CTkButton(
            barra, text="A+", width=42, height=32, command=lambda: self.ajustar_texto(1.1),
            font=ComponenteUI.fuente(16, bold=True), fg_color=ACCENT_GREEN,
        ).pack(side="left", padx=2, pady=7)
        self._switch_tema = ctk.CTkSwitch(
            barra, text="Modo oscuro", variable=self.tema_oscuro, command=self.cambiar_tema,
            font=ComponenteUI.fuente(14), progress_color=ACCENT_GREEN,
        )
        self._switch_tema.pack(side="left", padx=16, pady=7)
        self._texto_idioma = ctk.CTkLabel(
            barra, text="Idioma", font=ComponenteUI.fuente(14), text_color=DARK_TEXT,
        )
        self._texto_idioma.pack(side="right", padx=(8, 4), pady=7)
        self._selector_idioma = ctk.CTkOptionMenu(
            barra, values=list(IDIOMAS.values()), command=self.cambiar_idioma,
            width=150, height=32, font=ComponenteUI.fuente(14), fg_color=ACCENT_GREEN,
        )
        self._selector_idioma.set(IDIOMAS[idioma_actual()])
        self._selector_idioma.pack(side="right", padx=(4, 18), pady=7)

    def cambiar_tema(self) -> None:
        ctk.set_appearance_mode("dark" if self.tema_oscuro.get() else "light")

    def cambiar_idioma(self, etiqueta: str) -> None:
        codigo = next((key for key, value in IDIOMAS.items() if value == etiqueta), "es")
        establecer_idioma(codigo)
        self._actualizar_textos_barra()
        self.aplicar_idioma_actual()

    def _actualizar_textos_barra(self) -> None:
        self._texto_accesibilidad.configure(text=traducir("Accesibilidad"))
        self._switch_tema.configure(text=traducir("Modo oscuro"))
        self._texto_idioma.configure(text=traducir("Idioma"))

    def aplicar_idioma_actual(self) -> None:
        """Actualiza texto y placeholders de la pantalla sin perder su estado."""
        def recorrer(widget) -> None:
            try:
                texto = widget.cget("text")
                if texto:
                    origen = getattr(widget, "_mita_texto_origen", texto)
                    widget._mita_texto_origen = origen
                    widget.configure(text=traducir(origen))
            except (AttributeError, ValueError, tk.TclError):
                pass
            try:
                placeholder = widget.cget("placeholder_text")
                if placeholder:
                    origen_placeholder = getattr(widget, "_mita_placeholder_origen", placeholder)
                    widget._mita_placeholder_origen = origen_placeholder
                    widget.configure(placeholder_text=traducir(origen_placeholder))
            except (AttributeError, ValueError, tk.TclError):
                pass
            for hijo in widget.winfo_children():
                recorrer(hijo)

        recorrer(self.main_container)

    def _abrir_admin_secreto(self, _event=None) -> None:
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        LogoMITA(frame, size=64).pack(pady=(0, 12))
        ComponenteUI.titulo(frame, "Acceso Administrador").pack()
        entry_u = ComponenteUI.entrada(frame, "Usuario admin")
        entry_u.pack(pady=8)
        entry_p = ComponenteUI.entrada(frame, "Contraseña", password=True)
        entry_p.pack(pady=8)

        def intentar():
            ok, msj, user = self.auth_service.login(entry_u.get(), entry_p.get(), "Administrador")
            if ok and user and user.rol == "Administrador":
                self.vista_admin.dashboard()
            else:
                NotificationService.mostrar(frame, "Acceso denegado", es_error=True)

        ComponenteUI.boton(frame, "Entrar", intentar, ancho=300).pack(pady=16)
        ComponenteUI.boton(frame, "Volver", self.mostrar_bienvenida, ancho=200, color=TEXT_GRAY).pack()

    # ------------------------------------------------------------------
    # PANTALLA BIENVENIDA — 3 opciones de rol
    # ------------------------------------------------------------------
    def mostrar_bienvenida(self, feedback: str = None) -> None:
        SessionManager().cerrar_sesion()
        self.limpiar_pantalla()

        left = ctk.CTkFrame(self.main_container, width=380, corner_radius=20, fg_color=BG_WARM)
        left.pack(side="left", fill="y", padx=20, pady=20)
        LogoMITA(left, size=120).pack(pady=(40, 8))
        ctk.CTkLabel(
            left, text="MITA",
            font=ComponenteUI.fuente(FONT_SIZE_HERO, bold=True),
            text_color=ACCENT_GREEN,
        ).pack()
        ctk.CTkLabel(
            left,
            text="Ayuda a evitar y cuidar\nel envejecimiento",
            font=ComponenteUI.fuente(18),
            text_color=ACCENT_GREEN,
            justify="center",
        ).pack(pady=8)

        right = ctk.CTkFrame(self.main_container, fg_color=BG_COLOR)
        right.pack(side="right", fill="both", expand=True, padx=36, pady=36)

        if feedback:
            NotificationService.mostrar(right, feedback)
        else:
            NotificationService.mostrar(right, MensajeMITA.BIENVENIDA.value)
        for warning in self.db_service.startup_warnings:
            NotificationService.mostrar(right, warning, duracion=6500)

        ComponenteUI.titulo(right, "¿Quién eres?").pack(pady=(10, 20))

        ComponenteUI.boton(
            right,
            "👴 Soy adulto mayor",
            lambda: self.mostrar_login_rol("Adulto Mayor"),
            grande=True,
            ancho=420,
        ).pack(pady=10)

        ComponenteUI.boton(
            right,
            "👨‍👩‍👧 Soy familiar o encargado",
            lambda: self.mostrar_login_rol("Familiar"),
            ancho=380,
            color="#628272",
        ).pack(pady=8)

        ComponenteUI.boton(
            right,
            "🩺 Soy médico, enfermero o cuidador",
            lambda: self.mostrar_login_rol("Cuidador"),
            ancho=340,
            color="#9CA18D",
        ).pack(pady=8)

        ctk.CTkLabel(
            right,
            text="Tip: Ctrl+Shift+A — panel de administrador (desarrolladores)",
            font=ComponenteUI.fuente(12),
            text_color=TEXT_GRAY,
        ).pack(side="bottom", pady=8)

    # ------------------------------------------------------------------
    # LOGIN POR ROL
    # ------------------------------------------------------------------
    def mostrar_login_rol(self, rol: str) -> None:
        self.rol_seleccionado = rol
        SessionManager().rol_entrada = rol
        self.limpiar_pantalla()

        frame = ctk.CTkFrame(self.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=40, pady=40)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkButton(
            top, text="⬅ Volver", fg_color="transparent", text_color=ACCENT_GREEN,
            command=self.mostrar_bienvenida,
        ).pack(side="left")
        LogoMITA(top, size=56).pack(side="right")

        titulos = {
            "Adulto Mayor": "Iniciar sesión — Adulto Mayor",
            "Familiar": "Iniciar sesión — Familiar",
            "Cuidador": "Iniciar sesión — Personal de salud",
        }
        ComponenteUI.titulo(frame, titulos.get(rol, "Iniciar sesión")).pack(pady=(20, 12))

        if rol == "Adulto Mayor":
            ctk.CTkLabel(
                frame,
                text="Usa las credenciales que te dio tu médico o familiar.",
                font=ComponenteUI.fuente(16),
                text_color=TEXT_GRAY,
            ).pack(pady=(0, 12))

        self.entry_usuario = ComponenteUI.entrada(frame, "Correo o nombre completo")
        self.entry_usuario.pack(pady=8)
        self.entry_pass = ComponenteUI.entrada(frame, "Contraseña", password=True)
        self.entry_pass.pack(pady=8)

        ComponenteUI.boton(frame, "Entrar", self.ejecutar_login, ancho=380, grande=True).pack(pady=20)

        if rol == "Adulto Mayor":
            ctk.CTkButton(
                frame,
                text="¿No tienes médico? Regístrate tú mismo",
                fg_color="transparent",
                text_color=TEXT_GRAY,
                hover_color=SOFT_GREEN,
                font=ComponenteUI.fuente(14),
                command=self.mostrar_registro_adulto_solo,
            ).pack(pady=4)
        elif rol == "Familiar":
            ctk.CTkButton(
                frame,
                text="¿Primera vez? Crear cuenta de familiar",
                fg_color="transparent",
                text_color=TEXT_GRAY,
                command=self.mostrar_registro_familiar_solo,
            ).pack(pady=4)
        elif rol == "Cuidador":
            ctk.CTkButton(
                frame,
                text="¿No tienes cuenta? Registro profesional",
                fg_color="transparent",
                text_color=TEXT_GRAY,
                command=self.mostrar_registro_cuidador,
            ).pack(pady=4)

    def ejecutar_login(self) -> None:
        u = self.entry_usuario.get().strip()
        p = self.entry_pass.get().strip()
        ok, msj, usuario = self.auth_service.login(u, p, self.rol_seleccionado)
        if ok:
            self.mongo_session_id = self.analytics_service.registrar_login(usuario.id or 0)
            self._cargar_progreso_usuario(usuario)
            self._ir_a_panel(usuario, msj)
        else:
            NotificationService.mostrar(self.main_container, msj, es_error=True)

    def _cargar_progreso_usuario(self, usuario) -> None:
        if usuario and usuario.id:
            datos = self.progreso_repo.obtener_progreso(usuario.id)
            self.gestor_progreso = GestorProgreso()
            self.gestor_progreso.cargar_desde_db(datos)

    def _ir_a_panel(self, usuario, feedback: str) -> None:
        destino = usuario.panel_destino()
        self.analytics_service.registrar_cambio_pantalla(usuario.id, destino)
        if destino == "adulto":
            self.vista_adulto.dashboard(feedback)
        elif destino == "familiar":
            self.vista_familiar.dashboard(feedback)
        elif destino == "cuidador":
            self.vista_cuidador.dashboard(feedback)
        elif destino == "admin":
            self.vista_admin.dashboard()
        else:
            self.vista_adulto.dashboard(feedback)

    def cerrar_sesion(self) -> None:
        usuario = SessionManager().usuario_actual
        self.analytics_service.registrar_logout(
            usuario.id if usuario else None, self.mongo_session_id
        )
        self.mongo_session_id = None
        SessionManager().cerrar_sesion()
        self.mostrar_bienvenida(MensajeMITA.SESION_CERRADA.value)

    # ------------------------------------------------------------------
    # REGISTROS
    # ------------------------------------------------------------------
    def _formulario_registro(self, titulo: str, campos_extra: list, on_guardar, rol_default: str) -> None:
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=28)
        ctk.CTkButton(
            frame, text="⬅ Volver", fg_color="transparent", text_color=ACCENT_GREEN,
            command=lambda: self.mostrar_login_rol(rol_default),
        ).pack(anchor="nw")
        ComponenteUI.titulo(frame, titulo).pack(pady=(0, 16))

        entries = {}
        for label, key, is_pass in campos_extra:
            if label:
                ctk.CTkLabel(frame, text=label, font=ComponenteUI.fuente(14)).pack(anchor="w")
            entries[key] = ComponenteUI.entrada(frame, key.replace("_", " ").title(), password=is_pass)
            entries[key].pack(pady=6)

        def guardar():
            datos = {k: e.get().strip() for k, e in entries.items()}
            on_guardar(datos)

        ComponenteUI.boton(frame, "Guardar", guardar, ancho=360, grande=True).pack(pady=20)

    def mostrar_registro_adulto_solo(self) -> None:
        def guardar(d):
            res = self.auth_service.registrar_usuario({
                "nombre": d.get("nombre", ""),
                "correo": d.get("correo", ""),
                "password": d.get("contraseña", ""),
                "rol": "Adulto Mayor",
                "limitaciones_movilidad": d.get("limitaciones", "Ninguna"),
                "nivel_movilidad": d.get("movilidad", "Normal"),
                "acepto_privacidad": 1,
            })
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                self.mostrar_login_rol("Adulto Mayor")
                NotificationService.mostrar(self.main_container, res)
            else:
                NotificationService.mostrar(self.main_container, res, es_error=True)

        self._formulario_registro(
            "Registro personal — Adulto Mayor",
            [
                ("", "nombre", False),
                ("", "correo", False),
                ("", "contraseña", True),
                ("Limitaciones (ej. rodilla, ninguna)", "limitaciones", False),
                ("Nivel movilidad (Normal/Reducida)", "movilidad", False),
            ],
            guardar,
            "Adulto Mayor",
        )

    def mostrar_registro_familiar_solo(self) -> None:
        def guardar(d):
            res = self.auth_service.registrar_usuario({
                "nombre": d["nombre"], "correo": d["correo"],
                "password": d["contraseña"], "rol": "Familiar",
            })
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                self.mostrar_login_rol("Familiar")
                NotificationService.mostrar(self.main_container, res)
            else:
                NotificationService.mostrar(self.main_container, res, es_error=True)

        self._formulario_registro(
            "Registro — Familiar",
            [("", "nombre", False), ("", "correo", False), ("", "contraseña", True)],
            guardar,
            "Familiar",
        )

    def mostrar_registro_cuidador(self) -> None:
        def guardar(d):
            res = self.auth_service.registrar_usuario({
                "nombre": d["nombre"], "correo": d["correo"],
                "password": d["contraseña"], "rol": "Cuidador",
                "cedula_medica": d.get("cedula", "MED-0000"),
            })
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                self.mostrar_login_rol("Cuidador")
                NotificationService.mostrar(self.main_container, res)
            else:
                NotificationService.mostrar(self.main_container, res, es_error=True)

        self._formulario_registro(
            "Registro — Personal de salud",
            [
                ("", "nombre", False), ("", "correo", False),
                ("", "contraseña", True), ("Cédula profesional", "cedula", False),
            ],
            guardar,
            "Cuidador",
        )

    def mostrar_registro_adulto_medico(self) -> None:
        medico = SessionManager().usuario_actual

        def guardar(d):
            res = self.auth_service.registrar_usuario({
                "nombre": d["nombre"], "correo": d["correo"],
                "password": d["contraseña"], "rol": "Adulto Mayor",
                "limitaciones_movilidad": d.get("limitaciones", "Ninguna"),
                "alergias": d.get("alergias", "Ninguna"),
                "imc": float(d.get("imc") or 22),
                "nivel_movilidad": d.get("movilidad", "Normal"),
                "dificultades_cognitivas": d.get("cognitivas", "Ninguna"),
                "perfil_medico": d.get("perfil_medico", ""),
                "creado_por": medico.id if medico else None,
                "acepto_privacidad": 1,
            })
            msg = res
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                msg = f"{res}\nCredenciales: {d['correo']} / {d['contraseña']}"
            NotificationService.mostrar(self.main_container, msg, es_error=res != MensajeMITA.REGISTRO_EXITOSO.value)
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                self.vista_cuidador.dashboard()

        self._formulario_registro(
            "Registrar paciente — Adulto Mayor",
            [
                ("", "nombre", False), ("", "correo", False), ("Contraseña para el adulto", "contraseña", True),
                ("Alergias", "alergias", False), ("IMC", "imc", False),
                ("Movilidad", "movilidad", False), ("Limitaciones", "limitaciones", False),
                ("Dificultades cognitivas", "cognitivas", False), ("Perfil médico", "perfil_medico", False),
            ],
            guardar,
            "Cuidador",
        )

    def mostrar_registro_familiar_medico(self) -> None:
        medico = SessionManager().usuario_actual

        def guardar(d):
            res = self.auth_service.registrar_usuario({
                "nombre": d["nombre"], "correo": d["correo"],
                "password": d["contraseña"], "rol": "Familiar",
                "id_adulto_vinculado": int(d.get("id_adulto") or 0) or None,
                "creado_por": medico.id if medico else None,
            })
            NotificationService.mostrar(
                self.main_container, res,
                es_error=res != MensajeMITA.REGISTRO_EXITOSO.value,
            )
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                self.vista_cuidador.dashboard()

        self._formulario_registro(
            "Registrar familiar vinculado",
            [
                ("", "nombre", False), ("", "correo", False), ("", "contraseña", True),
                ("ID del adulto mayor vinculado", "id_adulto", False),
            ],
            guardar,
            "Cuidador",
        )

    def mostrar_registro_adulto_familiar(self) -> None:
        familiar = SessionManager().usuario_actual

        def guardar(d):
            res = self.auth_service.registrar_usuario({
                "nombre": d["nombre"], "correo": d["correo"],
                "password": d["contraseña"], "rol": "Adulto Mayor",
                "limitaciones_movilidad": d.get("limitaciones", "Ninguna"),
                "creado_por": familiar.id if familiar else None,
                "id_familiar_vincular": familiar.id if familiar else None,
            })
            NotificationService.mostrar(
                self.main_container,
                f"{res} — Comparte: {d['correo']} / {d['contraseña']}" if res == MensajeMITA.REGISTRO_EXITOSO.value else res,
                es_error=res != MensajeMITA.REGISTRO_EXITOSO.value,
            )
            if res == MensajeMITA.REGISTRO_EXITOSO.value:
                self.vista_familiar.dashboard()

        self._formulario_registro(
            "Registrar adulto mayor (familiar)",
            [
                ("", "nombre", False), ("", "correo", False),
                ("Contraseña para el adulto", "contraseña", True),
                ("Limitaciones", "limitaciones", False),
            ],
            guardar,
            "Familiar",
        )


def main() -> None:
    app = MitaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
