"""Cliente MQTT de mensajes generales para MITA.

No transmite información clínica ni credenciales. Para usarlo por Internet se
debe configurar un broker propio con TLS y autenticación; en red local se puede
usar un broker confiable con TLS desactivado de forma explícita.
"""
from __future__ import annotations

import json
import logging
import socket
import threading
import time
from dataclasses import dataclass
from typing import Callable

import paho.mqtt.client as mqtt

from config.settings import MQTT_HOST, MQTT_PASSWORD, MQTT_PORT, MQTT_TLS, MQTT_TOPIC, MQTT_USERNAME


LOG = logging.getLogger(__name__)
TOPIC_POR_DEFECTO = "mita/chat/general"


@dataclass(frozen=True)
class EstadoChat:
    disponible: bool
    motivo: str

    @property
    def descripcion(self) -> str:
        return "Chat disponible" if self.disponible else f"Chat no disponible: {self.motivo}"


class ClienteChatMITA:
    """Cliente MQTT que confirma conexión y suscripción antes de permitir envíos."""

    def __init__(
        self,
        nickname: str,
        on_mensaje: Callable[[str, str], None],
        host: str = "",
        port: int = 0,
        topic: str = "",
        usar_tls: bool = False,
    ) -> None:
        self.nickname = (nickname or "Anónimo").strip()[:30]
        self.on_mensaje = on_mensaje
        self.topic = topic or MQTT_TOPIC or TOPIC_POR_DEFECTO
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"mita-{self.nickname}-{int(time.time())}",
        )
        self.client.on_connect = self._cuando_conecta
        self.client.on_disconnect = self._cuando_desconecta
        self.client.on_message = self._cuando_llega_mensaje
        if MQTT_USERNAME:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        self._lock = threading.Lock()
        self._conexion_evento = threading.Event()
        self._conectado = False
        self._motivo = "sin conexión"
        self._host = ""
        self._port = 0
        self._tls = False
        self._hosts_a_probar: list[tuple[str, int, bool]] = []
        if host and port:
            self._hosts_a_probar.append((host, int(port), bool(usar_tls)))
        elif MQTT_HOST:
            self._hosts_a_probar.append((MQTT_HOST, MQTT_PORT or 8883, MQTT_TLS))

        if any(configuracion[2] for configuracion in self._hosts_a_probar):
            try:
                self.client.tls_set()
            except Exception as exc:  # noqa: BLE001
                self._motivo = "no se pudo activar TLS"
                LOG.warning("No se pudo activar TLS en MQTT: %s", exc)

    def estado(self) -> EstadoChat:
        return EstadoChat(self._conectado, "conectado" if self._conectado else self._motivo)

    def iniciar(self) -> bool:
        if not self._hosts_a_probar:
            self._motivo = "falta configurar MQTT_HOST"
            return False
        for host, port, usar_tls in self._hosts_a_probar:
            if not _host_alcanzable(host, port, timeout=1.0):
                self._motivo = "el broker no responde"
                continue
            try:
                self._conexion_evento.clear()
                self.client.connect(host, port, keepalive=30)
                self.client.loop_start()
                self._host, self._port, self._tls = host, port, usar_tls
                if self._conexion_evento.wait(timeout=4.0) and self._conectado:
                    return True
                self.client.loop_stop()
                self.client.disconnect()
            except Exception as exc:  # noqa: BLE001
                self._motivo = "no fue posible conectar con el broker"
                LOG.info("Fallo conectando a %s:%s: %s", host, port, exc)
        return False

    def detener(self) -> None:
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:  # noqa: BLE001
            pass
        self._conectado = False
        self._motivo = "desconectado"

    def enviar(self, texto: str) -> bool:
        texto = (texto or "").strip()[:500]
        if not texto or not self._conectado:
            return False
        payload = json.dumps(
            {"nick": self.nickname, "msg": texto, "ts": int(time.time())},
            ensure_ascii=False,
        )
        try:
            resultado = self.client.publish(self.topic, payload, qos=1)
            return resultado.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as exc:  # noqa: BLE001
            LOG.warning("No se pudo publicar el mensaje: %s", exc)
            return False

    def _cuando_conecta(self, client, userdata, flags, reason_code, properties=None):
        if reason_code != 0:
            self._motivo = f"el broker rechazó la conexión ({reason_code})"
            self._conexion_evento.set()
            return
        with self._lock:
            self._conectado = True
            self._motivo = "conectado"
        try:
            client.subscribe(self.topic, qos=1)
        except Exception as exc:  # noqa: BLE001
            self._conectado = False
            self._motivo = "no fue posible suscribirse al canal"
            LOG.warning("No se pudo suscribir al tópico: %s", exc)
        finally:
            self._conexion_evento.set()

    def _cuando_desconecta(self, client, userdata, disconnect_flags, reason_code, properties=None):
        with self._lock:
            self._conectado = False
            if self._motivo != "desconectado":
                self._motivo = "conexión con el broker interrumpida"

    def _cuando_llega_mensaje(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            nick = str(data.get("nick", "Anónimo"))[:30]
            texto = str(data.get("msg", ""))[:500]
        except (ValueError, UnicodeDecodeError):
            nick = "Anónimo"
            texto = msg.payload.decode("utf-8", errors="ignore")[:500]
        if texto and self.on_mensaje:
            self.on_mensaje(nick, texto)


def _host_alcanzable(host: str, port: int, timeout: float = 1.0) -> bool:
    """Prueba rápida y silenciosa de accesibilidad del broker."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
