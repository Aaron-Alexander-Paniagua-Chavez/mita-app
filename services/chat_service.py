"""Cliente de chat por MQTT para MITA.

Reglas duras:
- Nunca se transmite información clínica (diagnósticos, medicamentos, IMC, etc.).
- Funciona con internet (broker público) o sólo red local (broker configurable).
- Si no hay red ni broker, el chat se desactiva de forma silenciosa.
"""
from __future__ import annotations

import json
import logging
import socket
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from config.settings import MQTT_HOST, MQTT_PORT, MQTT_TLS, MQTT_TOPIC


LOG = logging.getLogger(__name__)

BROKER_PUBLICO = "broker.hivemq.com"
BROKER_PUBLICO_PORTA = 1883
TOPIC_POR_DEFECTO = "mita_chat_general_2026"


@dataclass(frozen=True)
class EstadoChat:
    disponible: bool
    motivo: str

    @property
    def descripcion(self) -> str:
        if self.disponible:
            return "Chat disponible"
        return f"Chat no disponible: {self.motivo}"


class ClienteChatMITA:
    """Wrapper de paho-mqtt que abstrae broker público y local."""

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
        self.client.on_message = self._cuando_llega_mensaje
        self._lock = threading.Lock()
        self._conectado = False
        self._host = ""
        self._port = 0
        self._tls = False

        if usar_tls or MQTT_TLS:
            try:
                self.client.tls_set()
            except Exception as exc:  # noqa: BLE001
                LOG.warning("No se pudo activar TLS en MQTT: %s", exc)

        self._hosts_a_probar: list[tuple[str, int, bool]] = []
        if host and port:
            self._hosts_a_probar.append((host, int(port), bool(usar_tls)))
        elif MQTT_HOST:
            self._hosts_a_probar.append((MQTT_HOST, MQTT_PORT or 8883, MQTT_TLS))
        # Siempre se ofrece el broker público como último recurso si hay internet.
        self._hosts_a_probar.append((BROKER_PUBLICO, BROKER_PUBLICO_PORTA, False))

    # ------------------------------------------------------------------
    def estado(self) -> EstadoChat:
        if self._conectado:
            return EstadoChat(True, "conectado")
        return EstadoChat(False, "sin conexión")

    def iniciar(self) -> bool:
        for host, port, usar_tls in self._hosts_a_probar:
            if not _host_alcanzable(host, port, timeout=1.0):
                continue
            try:
                self.client.connect(host, port, keepalive=30)
                self.client.loop_start()
                self._host, self._port, self._tls = host, port, usar_tls
                return True
            except Exception as exc:  # noqa: BLE001
                LOG.info("Fallo conectando a %s:%s — %s", host, port, exc)
                continue
        LOG.info("No se pudo conectar a ningún broker MQTT.")
        return False

    def detener(self) -> None:
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:  # noqa: BLE001
            pass
        self._conectado = False

    def enviar(self, texto: str) -> bool:
        texto = (texto or "").strip()
        if not texto or not self._conectado:
            return False
        payload = json.dumps(
            {"nick": self.nickname, "msg": texto, "ts": int(time.time())},
            ensure_ascii=False,
        )
        try:
            self.client.publish(self.topic, payload)
            return True
        except Exception as exc:  # noqa: BLE001
            LOG.warning("No se pudo publicar el mensaje: %s", exc)
            return False

    # ------------------------------------------------------------------
    def _cuando_conecta(self, client, userdata, flags, reason_code, properties=None):
        if reason_code != 0:
            LOG.info("MQTT conectó con código de error: %s", reason_code)
            return
        with self._lock:
            self._conectado = True
        try:
            client.subscribe(self.topic)
        except Exception as exc:  # noqa: BLE001
            LOG.warning("No se pudo suscribir al tópico: %s", exc)

    def _cuando_llega_mensaje(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            nick = str(data.get("nick", "Anónimo"))[:30]
            texto = str(data.get("msg", ""))
            if texto and self.on_mensaje:
                self.on_mensaje(nick, texto)
        except (ValueError, UnicodeDecodeError):
            texto_crudo = msg.payload.decode("utf-8", errors="ignore")
            if texto_crudo and self.on_mensaje:
                self.on_mensaje("Anónimo", texto_crudo)


def _host_alcanzable(host: str, port: int, timeout: float = 1.0) -> bool:
    """Prueba rápida y silenciosa; no transmite datos."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False
