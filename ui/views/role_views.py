"""Vistas por rol — adulto mayor, familiar, cuidador y admin."""
import threading
from typing import Callable, Optional

import customtkinter as ctk

from config.settings import (
    ACCENT_GREEN,
    BG_COLOR,
    DARK_TEXT,
    DISABLED_SURFACE,
    SOFT_GREEN,
    SOFT_PURPLE,
    SURFACE_COLOR,
    TEXT_GRAY,
)
from core.messages import MensajeMITA
from core.session import SessionManager
from models.actividad import Actividad, AdaptadorEjercicios
from models.progreso import GestorProgreso, PanelCuidador, ReporteCuidador, SistemaLogros
from models.usuario import AdultoMayor
from ui.components import ComponenteUI, LogoMITA, NotificationService


class VistaMixin:
    """Utilidades compartidas entre vistas."""

    def boton_volver(self, parent, command: Callable) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            parent,
            text="⬅ Volver al Menú",
            fg_color="transparent",
            text_color=ACCENT_GREEN,
            font=ComponenteUI.fuente(16, bold=True),
            hover_color=SOFT_GREEN,
            command=command,
        )
        btn.pack(anchor="nw", pady=(0, 16))
        return btn

    def barra_nav_inferior(self, parent, activo: str, callbacks: dict) -> None:
        nav = ctk.CTkFrame(parent, fg_color=SURFACE_COLOR, corner_radius=20, height=84)
        nav.pack(fill="x", padx=32, side="bottom", pady=16)
        nav.pack_propagate(False)
        items = [
            ("Inicio", "🏠", "inicio"),
            ("Progreso", "📊", "progreso"),
            ("Comunidad", "👥", "comunidad"),
            ("Logros", "⭐", "logros"),
        ]
        for texto, icono, key in items:
            active = activo == key
            ctk.CTkButton(
                nav,
                text=f"{icono}\n{texto}",
                fg_color="transparent",
                text_color=ACCENT_GREEN if active else TEXT_GRAY,
                font=ComponenteUI.fuente(16, bold=active),
                hover_color=SOFT_GREEN,
                command=callbacks.get(key),
            ).pack(side="left", expand=True, fill="both", pady=4)


class VistaAdultoMayor(VistaMixin):
    """Experiencia principal para adultos mayores — UI amplia y simple."""

    def __init__(self, app) -> None:
        self.app = app

    def dashboard(self, feedback: str = None) -> None:
        self.app.limpiar_pantalla()
        usuario = SessionManager().usuario_actual
        nombre = usuario.nombre if usuario else "Usuario"

        header = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        header.pack(fill="x", padx=36, pady=(16, 8))
        LogoMITA(header, size=56).pack(side="left", padx=(0, 12))
        ComponenteUI.titulo(header, f"Hola, {nombre.split()[0]}").pack(side="left")
        ComponenteUI.boton(
            header, "Cerrar sesión", self.app.cerrar_sesion,
            ancho=160, grande=False, color="#C62828",
        ).pack(side="right")

        if feedback:
            NotificationService.mostrar(self.app.main_container, feedback)

        cards = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        cards.pack(fill="x", padx=36, pady=8)

        card_f = ctk.CTkFrame(cards, fg_color=SOFT_GREEN, corner_radius=16, height=190)
        card_f.pack(side="left", expand=True, fill="both", padx=(0, 8))
        card_f.pack_propagate(False)
        ComponenteUI.titulo(card_f, "🏃 Ejercicio físico").pack(anchor="w", padx=20, pady=(20, 8))
        ComponenteUI.boton(card_f, "Ver catálogo", self.ejercicios_fisicos, ancho=200).pack(anchor="w", padx=20)

        card_c = ctk.CTkFrame(cards, fg_color=SOFT_PURPLE, corner_radius=16, height=190)
        card_c.pack(side="right", expand=True, fill="both", padx=(8, 0))
        card_c.pack_propagate(False)
        ComponenteUI.titulo(card_c, "🧠 Ejercicio cognitivo").pack(anchor="w", padx=20, pady=(20, 8))
        ComponenteUI.boton(
            card_c, "Ver actividades", self.ejercicios_cognitivos,
            ancho=200, color="#8975B4",
        ).pack(anchor="w", padx=20)

        # Accesibilidad rápida
        acc_frame = ctk.CTkFrame(self.app.main_container, fg_color=SURFACE_COLOR, corner_radius=12)
        acc_frame.pack(fill="x", padx=36, pady=8)
        ComponenteUI.subtitulo(acc_frame, "Accesibilidad:").pack(side="left", padx=16, pady=12)
        self.app.font_scale = getattr(self.app, "font_scale", 1.0)
        ctk.CTkButton(
            acc_frame, text="A+ Texto", width=100, command=lambda: self.app.ajustar_texto(1.1),
            fg_color=ACCENT_GREEN,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            acc_frame, text="A- Texto", width=100, command=lambda: self.app.ajustar_texto(0.9),
            fg_color=ACCENT_GREEN,
        ).pack(side="left", padx=4)

        self.barra_nav_inferior(
            self.app.main_container,
            "inicio",
            {
                "inicio": lambda: self.dashboard(),
                "progreso": self.progreso,
                "comunidad": self.comunidad,
                "logros": self.logros,
            },
        )

    def ejercicios_fisicos(self) -> None:
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)
        self.boton_volver(frame, self.dashboard)
        LogoMITA(frame, size=48).pack(anchor="w")

        usuario = SessionManager().usuario_actual
        limitaciones = "Ninguna"
        movilidad = "Normal"
        if isinstance(usuario, AdultoMayor):
            limitaciones = usuario.limitaciones_movilidad
            movilidad = usuario.nivel_movilidad

        actividades, msj = AdaptadorEjercicios.filtrar_fisicos(limitaciones, movilidad)
        NotificationService.mostrar(frame, msj)
        ComponenteUI.titulo(frame, "Ejercicios físicos").pack(anchor="w", pady=(0, 12))

        for ej in actividades:
            card = ctk.CTkFrame(frame, fg_color=SURFACE_COLOR, corner_radius=10)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(
                card, text=f"🏃 {ej.titulo} [{ej.impacto}]",
                font=ComponenteUI.fuente(18), text_color=DARK_TEXT,
            ).pack(side="left", padx=16, pady=14)
            ComponenteUI.boton(
                card, "Instrucciones", lambda e=ej: self.instrucciones(e),
                ancho=160,
            ).pack(side="right", padx=16, pady=8)

    def ejercicios_cognitivos(self) -> None:
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)
        self.boton_volver(frame, self.dashboard)
        ComponenteUI.titulo(frame, "Actividades cognitivas").pack(anchor="w", pady=(0, 12))

        for ej in AdaptadorEjercicios.cognitivos():
            card = ctk.CTkFrame(frame, fg_color=SURFACE_COLOR, corner_radius=10)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(
                card, text=f"🧠 {ej.titulo}",
                font=ComponenteUI.fuente(18), text_color=DARK_TEXT,
            ).pack(side="left", padx=16, pady=14)
            ComponenteUI.boton(
                card, "Instrucciones", lambda e=ej: self.instrucciones(e),
                ancho=160, color="#8975B4",
            ).pack(side="right", padx=16, pady=8)

    def instrucciones(self, actividad: Actividad) -> None:
        self.app.actividad_actual = actividad
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)
        self.boton_volver(frame, self.dashboard)
        NotificationService.mostrar(frame, MensajeMITA.SIGUE_PASOS.value)

        ComponenteUI.titulo(frame, actividad.titulo).pack(pady=(0, 12))
        box = ctk.CTkFrame(frame, fg_color=SURFACE_COLOR, corner_radius=14)
        box.pack(fill="both", expand=True, pady=8)

        for paso in actividad.instrucciones:
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=8)
            ctk.CTkLabel(row, text=paso.icono, font=ComponenteUI.fuente(24)).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(
                row, text=f"{paso.orden}. {paso.texto}",
                font=ComponenteUI.fuente(18), justify="left", wraplength=620,
            ).pack(side="left", fill="x")

        ComponenteUI.boton(
            frame, "▶ COMENZAR ACTIVIDAD",
            lambda: self._completar(actividad),
            grande=True, ancho=400,
        ).pack(pady=16)

    def _completar(self, actividad: Actividad) -> None:
        def tarea():
            actividad.iniciar()
            actividad.ejecutar()
            actividad.finalizar()
            pts, msj = self.app.gestor_progreso.registrar_actividad(actividad)
            usuario = SessionManager().usuario_actual
            if usuario and usuario.id:
                self.app.progreso_repo.guardar_progreso(usuario.id, self.app.gestor_progreso.to_dict())
                self.app.progreso_repo.registrar_historial(
                    usuario.id, actividad.categoria, actividad.titulo, actividad.calcular_puntuacion(),
                )
                self.app.analytics_service.registrar_resultado_actividad(
                    usuario.id,
                    actividad.titulo,
                    actividad.categoria,
                    intentos=1,
                    aciertos=1,
                    errores=0,
                    nivel=getattr(actividad, "nivel_dificultad", 1),
                    puntaje=actividad.calcular_puntuacion(),
                    duracion=0,
                )
            desbloqueado, msj_logro = self.app.sistema_logros.evaluar(self.app.gestor_progreso)
            self.app.after(0, lambda: self._post_completar(msj, desbloqueado, msj_logro))

        threading.Thread(target=tarea, daemon=True).start()

    def _post_completar(self, msj: str, desbloqueado: bool, msj_logro: str) -> None:
        NotificationService.mostrar(self.app.main_container, msj)
        if desbloqueado:
            self.app.after(900, lambda: NotificationService.mostrar(self.app.main_container, msj_logro))
        self.dashboard(MensajeMITA.ACTIVIDAD_COMPLETADA.value)

    def progreso(self) -> None:
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)
        self.boton_volver(frame, self.dashboard)
        gp = self.app.gestor_progreso
        ComponenteUI.titulo(frame, "Tu progreso").pack(anchor="w", pady=(0, 12))
        stats = ctk.CTkFrame(frame, fg_color=SURFACE_COLOR, corner_radius=14)
        stats.pack(fill="x", pady=8)
        ctk.CTkLabel(
            stats, text=f"Puntos: {gp.puntos}",
            font=ComponenteUI.fuente(22, bold=True), text_color=ACCENT_GREEN,
        ).pack(pady=(16, 6))
        ctk.CTkLabel(
            stats, text=f"🔥 Racha: {gp.racha_dias} días seguidos",
            font=ComponenteUI.fuente(18),
        ).pack(pady=(0, 16))
        nivel = min(10, 1 + gp.puntos // 20)
        ctk.CTkLabel(stats, text=f"Nivel {nivel}", font=ComponenteUI.fuente(18)).pack(pady=4)
        bar = ctk.CTkProgressBar(stats, progress_color=ACCENT_GREEN, height=14)
        bar.set(min(1.0, (gp.puntos % 20) / 20))
        bar.pack(fill="x", padx=40, pady=(4, 16))

    def logros(self) -> None:
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)
        self.boton_volver(frame, self.dashboard)
        ComponenteUI.titulo(frame, "Mis logros").pack(anchor="w", pady=(0, 12))
        for logro in self.app.sistema_logros.logros:
            card = ctk.CTkFrame(
                frame,
                fg_color=SOFT_GREEN if logro.desbloqueado else DISABLED_SURFACE,
                corner_radius=10,
            )
            card.pack(fill="x", pady=6)
            estado = "Desbloqueado" if logro.desbloqueado else "Bloqueado"
            ctk.CTkLabel(
                card, text=f"{logro.icono} {logro.titulo} — {estado}",
                font=ComponenteUI.fuente(18, bold=True),
            ).pack(anchor="w", padx=16, pady=(12, 4))
            ctk.CTkLabel(
                card, text=logro.descripcion,
                font=ComponenteUI.fuente(16), text_color=TEXT_GRAY,
            ).pack(anchor="w", padx=16, pady=(0, 12))

    def comunidad(self) -> None:
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)
        self.boton_volver(frame, self.dashboard)
        posts, msj = self.app.comunidad_service.obtener_publicaciones()
        NotificationService.mostrar(frame, msj)
        ComponenteUI.titulo(frame, "Comunidad MITA").pack(anchor="w", pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=8)
        for autor, texto in posts:
            card = ctk.CTkFrame(scroll, fg_color=SURFACE_COLOR, corner_radius=10)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=f"{autor}:", font=ComponenteUI.fuente(16, bold=True), text_color=ACCENT_GREEN).pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(card, text=texto, font=ComponenteUI.fuente(16), wraplength=700).pack(anchor="w", padx=12, pady=(4, 10))

        inp_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inp_frame.pack(fill="x", pady=8)
        entry = ComponenteUI.entrada(inp_frame, "Escribe un mensaje...", ancho=500)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def enviar():
            u = SessionManager().usuario_actual
            res = self.app.comunidad_service.enviar_mensaje(u.id or 0, u.nombre, entry.get())
            NotificationService.mostrar(frame, res, es_error=res == MensajeMITA.CAMPOS_OBLIGATORIOS.value)
            if res == MensajeMITA.MENSAJE_ENVIADO.value:
                self.comunidad()

        ComponenteUI.boton(inp_frame, "Enviar ➔", enviar, ancho=120).pack(side="right")


class VistaFamiliar(VistaMixin):
    """Vista simplificada — solo seguimiento sin datos sensibles."""

    def __init__(self, app) -> None:
        self.app = app

    def dashboard(self, feedback: str = None) -> None:
        self.app.limpiar_pantalla()
        usuario = SessionManager().usuario_actual
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=24)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x")
        LogoMITA(top, size=48).pack(side="left")
        ComponenteUI.titulo(top, f"Panel Familiar — {usuario.nombre}").pack(side="left", padx=12)
        ComponenteUI.boton(top, "Cerrar sesión", self.app.cerrar_sesion, ancho=150, color="#C62828").pack(side="right")

        if feedback:
            NotificationService.mostrar(frame, feedback)

        ComponenteUI.subtitulo(
            frame,
            "Aquí puedes ver el progreso de tu familiar (sin información médica sensible).",
        ).pack(anchor="w", pady=12)

        adultos = self.app.user_repo.listar_por_rol("Adulto Mayor")
        vinculado = getattr(usuario, "id_adulto_vinculado", None)

        for adulto in adultos:
            if vinculado and adulto["id"] != vinculado:
                continue
            resumen, msj = self.app.permiso_service.obtener_resumen_familiar(
                usuario.id, adulto["id"], self.app.progreso_repo,
            )
            if resumen:
                card = ctk.CTkFrame(frame, fg_color=SURFACE_COLOR, corner_radius=12)
                card.pack(fill="x", pady=8)
                ctk.CTkLabel(card, text=resumen, font=ComponenteUI.fuente(16), justify="left").pack(padx=16, pady=16)
                NotificationService.mostrar(card, msj)

        ComponenteUI.boton(
            frame, "Registrar nuevo adulto mayor",
            self.app.mostrar_registro_adulto_familiar,
            ancho=360, grande=True,
        ).pack(pady=20)


class VistaCuidador(VistaMixin):
    """Panel profesional — múltiples pacientes, registro completo."""

    def __init__(self, app) -> None:
        self.app = app

    def dashboard(self, feedback: str = None) -> None:
        self.app.limpiar_pantalla()
        usuario = SessionManager().usuario_actual
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=20)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x")
        LogoMITA(top, size=48).pack(side="left")
        ComponenteUI.titulo(top, f"Panel Médico — {usuario.nombre}").pack(side="left", padx=12)
        ComponenteUI.boton(top, "Cerrar sesión", self.app.cerrar_sesion, ancho=150, color="#C62828").pack(side="right")

        if feedback:
            NotificationService.mostrar(frame, feedback)

        pacientes = self.app.user_repo.listar_por_rol("Adulto Mayor")
        ids = [p["id"] for p in pacientes]
        metricas_list = self.app.progreso_repo.metricas_pacientes(ids) if ids else []
        metricas, msj = PanelCuidador.recopilar_metricas(metricas_list)
        NotificationService.mostrar(frame, msj)

        stats = ctk.CTkFrame(frame, fg_color=SURFACE_COLOR, corner_radius=12)
        stats.pack(fill="x", pady=8)
        ctk.CTkLabel(
            stats,
            text=f"Pacientes: {metricas['total_pacientes']} | Actividades totales: {metricas['total_actividades']} | Racha prom.: {metricas['promedio_racha']} días",
            font=ComponenteUI.fuente(16),
        ).pack(padx=16, pady=14)

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill="x", pady=8)
        ComponenteUI.boton(btns, "➕ Registrar adulto mayor", self.app.mostrar_registro_adulto_medico, ancho=280).pack(side="left", padx=4)
        ComponenteUI.boton(btns, "➕ Registrar familiar", self.app.mostrar_registro_familiar_medico, ancho=220).pack(side="left", padx=4)

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", height=320)
        scroll.pack(fill="both", expand=True, pady=8)
        reporte = ReporteCuidador()
        for p in pacientes:
            gp = GestorProgreso()
            gp.cargar_desde_db(self.app.progreso_repo.obtener_progreso(p["id"]))
            adulto = self.app.user_repo.dict_a_usuario(p)
            card = ctk.CTkFrame(scroll, fg_color=SOFT_GREEN, corner_radius=10)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(
                card, text=reporte.generar_resumen(adulto, gp),
                font=ComponenteUI.fuente(15), justify="left",
            ).pack(padx=14, pady=12)


class VistaAdmin(VistaMixin):
    """Panel secreto de superusuario — mantenimiento del sistema."""

    def __init__(self, app) -> None:
        self.app = app

    def dashboard(self) -> None:
        self.app.limpiar_pantalla()
        frame = ctk.CTkFrame(self.app.main_container, fg_color=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=36, pady=20)

        ComponenteUI.titulo(frame, "⚙ Panel Administrador MITA").pack(anchor="w")
        ComponenteUI.subtitulo(frame, "Mantenimiento — datos sensibles enmascarados").pack(anchor="w", pady=(0, 12))

        from core.security import GestorSeguridad

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for u in self.app.admin_service.listar_usuarios():
            card = ctk.CTkFrame(scroll, fg_color=SURFACE_COLOR, corner_radius=8)
            card.pack(fill="x", pady=4)
            texto = f"ID {u['id']} | {u['nombre']} | {u['correo']} | Rol: {u['rol']}"
            ctk.CTkLabel(card, text=texto, font=ComponenteUI.fuente(15)).pack(side="left", padx=12, pady=10)
            ctk.CTkButton(
                card, text="Editar rol", width=90,
                command=lambda uid=u["id"]: self._editar_rol(uid),
            ).pack(side="right", padx=8)

        ComponenteUI.boton(frame, "Comprobar conexión MySQL", self._sync, ancho=260).pack(pady=8)
        ComponenteUI.boton(frame, "Salir del panel admin", self.app.mostrar_bienvenida, ancho=220, color=TEXT_GRAY).pack(pady=4)

    def _editar_rol(self, user_id: int) -> None:
        dialog = ctk.CTkInputDialog(text="Nuevo rol:", title="Modificar rol")
        rol = dialog.get_input()
        if rol:
            admin = SessionManager().usuario_actual
            self.app.admin_service.modificar_usuario(user_id, {"rol": rol}, admin.id if admin else 0)
            self.dashboard()

    def _sync(self) -> None:
        n = self.app.sync_service.sincronizar_pendientes()
        mensaje = "MySQL está conectado; los cambios se comparten en esta red." if n == 0 else (
            "MySQL no está disponible. Inicia el servicio para guardar información."
        )
        NotificationService.mostrar(self.app.main_container, mensaje, es_error=n < 0)
