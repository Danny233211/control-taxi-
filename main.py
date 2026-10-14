import json
import os
from datetime import datetime

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

Window.softinput_mode = 'resize'

ARCHIVO_DATOS = "control_taxi.json"
IMAGEN_FONDO = "fondo.jpg"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r") as f:
                datos = json.load(f)
                if "turno_activo" not in datos: datos["turno_activo"] = None
                if "turnos" not in datos: datos["turnos"] = []
                if "mantenimientos" not in datos: datos["mantenimientos"] = []
                if "pin" not in datos: datos["pin"] = "1234"
                if "clave_maestra" not in datos: datos["clave_maestra"] = "dany"
                return datos
        except Exception:
            pass
    return {
        "turno_activo": None, 
        "turnos": [], 
        "mantenimientos": [], 
        "pin": "1234",
        "clave_maestra": "dany"
    }

def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w") as f:
            json.dump(datos, f, indent=4)
    except Exception:
        pass

class EntradaTextoFija(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.foreground_color = (0, 0, 0, 1)
        self.cursor_color = (0, 0, 0, 1)
        self.background_color = (1, 1, 1, 1)
        self.bind(size=self.actualizar_padding, font_size=self.actualizar_padding)

    def actualizar_padding(self, *args):
        padding_y = (self.height - self.line_height) / 2
        self.padding = [14, max(4, padding_y), 14, max(4, padding_y)]

class CampoClaveConOjito(BoxLayout):
    def __init__(self, tam_fuente='22sp', **kwargs):
        super().__init__(orientation='horizontal', spacing=8, **kwargs)
        
        self.txt_input = EntradaTextoFija(
            password=True,
            font_size=tam_fuente,
            size_hint_x=0.72,
            size_hint_y=1
        )
        
        self.btn_ojito = Button(
            text="[b]VER[/b]",
            markup=True,
            font_size='15sp',
            size_hint_x=0.28,
            size_hint_y=1,
            background_color=(0.2, 0.4, 0.6, 0.95),
            color=(1, 1, 1, 1)
        )
        self.btn_ojito.bind(on_release=self.alternar_visibilidad)
        
        self.add_widget(self.txt_input)
        self.add_widget(self.btn_ojito)

    def alternar_visibilidad(self, instance):
        self.txt_input.password = not self.txt_input.password
        if self.txt_input.password:
            self.btn_ojito.text = "[b]VER[/b]"
            self.btn_ojito.background_color = (0.2, 0.4, 0.6, 0.95)
            self.btn_ojito.color = (1, 1, 1, 1)
        else:
            self.btn_ojito.text = "[b]OCULTAR[/b]"
            self.btn_ojito.background_color = (0.8, 0.4, 0.1, 0.95)
            self.btn_ojito.color = (1, 1, 1, 1)

    @property
    def text(self):
        return self.txt_input.text

    @text.setter
    def text(self, valor):
        self.txt_input.text = valor

class PantallaConFondo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = FloatLayout()
        
        if os.path.exists(IMAGEN_FONDO):
            bg = Image(
                source=IMAGEN_FONDO,
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1),
                pos_hint={'x': 0, 'y': 0}
            )
            self.root_layout.add_widget(bg)
        
        self.contenido_principal = BoxLayout(orientation='vertical')
        self.root_layout.add_widget(self.contenido_principal)
        self.add_widget(self.root_layout)

class BotonRedondo(Button):
    def __init__(self, color_bg=(0.2, 0.6, 1, 1), radio=12, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color_bg = color_bg
        self.radio = radio
        self.bind(pos=self.actualizar_canvas, size=self.actualizar_canvas)

    def actualizar_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color_bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radio])

# --- PANTALLA MENÚ PRINCIPAL ---
class PantallaMenu(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        titulo = Label(
            text="[b]CONTROL DE TAXI[/b]", 
            markup=True,
            font_size='22sp', 
            size_hint_y=0.15
        )
        layout.add_widget(titulo)
        
        btn_iniciar = BotonRedondo(
            text="1. INICIAR TURNO", 
            color_bg=(0.1, 0.5, 0.9, 0.9),
            font_size='15sp',
            size_hint_y=0.16
        )
        btn_iniciar.bind(on_release=lambda x: setattr(self.manager, 'current', 'iniciar_turno'))
        
        btn_finalizar = BotonRedondo(
            text="2. FINALIZAR TURNO", 
            color_bg=(0.1, 0.7, 0.3, 0.9),
            font_size='15sp',
            size_hint_y=0.16
        )
        btn_finalizar.bind(on_release=lambda x: setattr(self.manager, 'current', 'finalizar_turno'))
        
        btn_mantenimiento = BotonRedondo(
            text="3. REGISTRAR MANTENIMIENTO", 
            color_bg=(0.9, 0.5, 0.2, 0.9),
            font_size='15sp',
            size_hint_y=0.16
        )
        btn_mantenimiento.bind(on_release=lambda x: self.solicitar_clave('mantenimiento'))
        
        btn_alertas = BotonRedondo(
            text="4. ALERTAS DE REPUESTOS", 
            color_bg=(0.9, 0.7, 0.1, 0.9),
            font_size='15sp',
            size_hint_y=0.16
        )
        btn_alertas.bind(on_release=lambda x: self.solicitar_clave('alertas'))
        
        btn_reportes = BotonRedondo(
            text="5. CONSULTAR REPORTES", 
            color_bg=(0.7, 0.3, 0.8, 0.9),
            font_size='15sp',
            size_hint_y=0.16
        )
        btn_reportes.bind(on_release=lambda x: self.solicitar_clave('reportes'))
        
        layout.add_widget(btn_iniciar)
        layout.add_widget(btn_finalizar)
        layout.add_widget(btn_mantenimiento)
        layout.add_widget(btn_alertas)
        layout.add_widget(btn_reportes)
        
        self.contenido_principal.add_widget(layout)
        
        self.capa_bloqueo = FloatLayout(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        
        with self.capa_bloqueo.canvas.before:
            Color(0, 0, 0, 0.8)
            self.rect_oscuro = RoundedRectangle(pos=self.capa_bloqueo.pos, size=self.capa_bloqueo.size)
        self.capa_bloqueo.bind(pos=self._actualizar_rect_oscuro, size=self._actualizar_rect_oscuro)

        self.tarjeta_modal = BoxLayout(
            orientation='vertical',
            padding=[16, 14, 16, 14],
            spacing=8,
            size_hint=(0.94, 0.38),
            pos_hint={'center_x': 0.5, 'top': 0.82}
        )
        
        with self.tarjeta_modal.canvas.before:
            Color(0.12, 0.12, 0.12, 0.98)
            self.rect_tarjeta = RoundedRectangle(pos=self.tarjeta_modal.pos, size=self.tarjeta_modal.size, radius=[16])
        self.tarjeta_modal.bind(pos=self._actualizar_rect_tarjeta, size=self._actualizar_rect_tarjeta)

        lbl_titulo_modal = Label(
            text="[b][color=#00FFFF]ACCESO PRIVADO[/color][/b]",
            markup=True,
            font_size='20sp',
            size_hint_y=0.16,
            halign='center',
            valign='middle'
        )
        lbl_titulo_modal.bind(size=lbl_titulo_modal.setter('text_size'))
        
        lbl_instruccion = Label(
            text="[b][color=#FFD700]Ingrese la Clave de Acceso:[/color][/b]",
            markup=True,
            font_size='16sp',
            size_hint_y=0.15,
            halign='center',
            valign='middle'
        )
        lbl_instruccion.bind(size=lbl_instruccion.setter('text_size'))
        
        self.txt_clave_modal = CampoClaveConOjito(tam_fuente='22sp', size_hint_y=0.24)
        
        self.lbl_error_modal = Label(text="", color=(1, 0.3, 0.3, 1), font_size='13sp', size_hint_y=0.08, halign='center')
        self.lbl_error_modal.bind(size=self.lbl_error_modal.setter('text_size'))
        
        box_opciones = BoxLayout(spacing=10, size_hint_y=0.14)
        btn_cambiar = Button(
            text="[color=#00FFFF][u]¿Cambiar contraseña?[/u][/color]",
            markup=True,
            background_color=(0, 0, 0, 0),
            font_size='13sp'
        )
        btn_olvido = Button(
            text="[color=#FF8C00][u]¿Olvidó su contraseña?[/u][/color]",
            markup=True,
            background_color=(0, 0, 0, 0),
            font_size='13sp'
        )
        box_opciones.add_widget(btn_cambiar)
        box_opciones.add_widget(btn_olvido)
        
        box_botones = BoxLayout(spacing=12, size_hint_y=0.23)
        btn_cancelar = BotonRedondo(
            text="[b]Cancelar[/b]",
            markup=True,
            color_bg=(0.4, 0.4, 0.4, 0.95),
            font_size='16sp'
        )
        btn_ingresar = BotonRedondo(
            text="[b]Ingresar[/b]",
            markup=True,
            color_bg=(0.1, 0.6, 0.9, 0.95),
            font_size='16sp'
        )
        box_botones.add_widget(btn_cancelar)
        box_botones.add_widget(btn_ingresar)
        
        self.tarjeta_modal.add_widget(lbl_titulo_modal)
        self.tarjeta_modal.add_widget(lbl_instruccion)
        self.tarjeta_modal.add_widget(self.txt_clave_modal)
        self.tarjeta_modal.add_widget(self.lbl_error_modal)
        self.tarjeta_modal.add_widget(box_opciones)
        self.tarjeta_modal.add_widget(box_botones)
        
        self.capa_bloqueo.add_widget(self.tarjeta_modal)
        
        btn_cancelar.bind(on_release=self.ocultar_modal)
        btn_ingresar.bind(on_release=self.verificar_pin_modal)
        btn_cambiar.bind(on_release=lambda x: self.navegar_y_ocultar('cambiar_clave'))
        btn_olvido.bind(on_release=lambda x: self.navegar_y_ocultar('recuperar_clave'))

    def _actualizar_rect_oscuro(self, instance, value):
        self.rect_oscuro.pos = instance.pos
        self.rect_oscuro.size = instance.size

    def _actualizar_rect_tarjeta(self, instance, value):
        self.rect_tarjeta.pos = instance.pos
        self.rect_tarjeta.size = instance.size

    def solicitar_clave(self, pantalla_destino):
        self.pantalla_destino_actual = pantalla_destino
        self.txt_clave_modal.text = ""
        self.lbl_error_modal.text = ""
        if self.capa_bloqueo not in self.root_layout.children:
            self.root_layout.add_widget(self.capa_bloqueo)

    def ocultar_modal(self, *args):
        if self.capa_bloqueo in self.root_layout.children:
            self.root_layout.remove_widget(self.capa_bloqueo)

    def navegar_y_ocultar(self, pantalla_destino):
        self.ocultar_modal()
        self.manager.current = pantalla_destino

    def verificar_pin_modal(self, *args):
        datos = cargar_datos()
        pin_actual = datos.get("pin", "1234")
        if self.txt_clave_modal.text.strip() == pin_actual:
            self.ocultar_modal()
            self.manager.current = self.pantalla_destino_actual
        else:
            self.lbl_error_modal.text = "Clave incorrecta. Intente de nuevo."
            self.txt_clave_modal.text = ""

# --- PANTALLA COMPLETA: RECUPERAR CONTRASEÑA ---
class PantallaRecuperarClave(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[15, 10, 15, 15], spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp')
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]RECUPERAR CONTRASEÑA[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        grid = GridLayout(cols=2, spacing=15, size_hint_y=None, height=220, padding=[10, 0, 10, 0])
        
        lbl_maestra = Label(text="[b][color=#00FFFF]Palabra Maestra:[/color][/b]", markup=True, font_size='15sp', halign='left', valign='middle')
        lbl_maestra.bind(size=lbl_maestra.setter('text_size'))
        self.txt_maestra = CampoClaveConOjito()
        
        lbl_nueva = Label(text="[b][color=#00FFFF]Nueva Clave:[/color][/b]", markup=True, font_size='15sp', halign='left', valign='middle')
        lbl_nueva.bind(size=lbl_nueva.setter('text_size'))
        self.txt_nueva = CampoClaveConOjito()
        
        grid.add_widget(lbl_maestra)
        grid.add_widget(self.txt_maestra)
        grid.add_widget(lbl_nueva)
        grid.add_widget(self.txt_nueva)
        
        layout.add_widget(grid)
        
        self.lbl_info = Label(
            text="Ingrese la Palabra Maestra para restablecer la contraseña.", 
            size_hint_y=1, 
            font_size='14sp', 
            color=(0.3, 0.8, 1, 1), 
            markup=True,
            halign='left',
            valign='top'
        )
        self.lbl_info.bind(size=self.lbl_info.setter('text_size'))
        layout.add_widget(self.lbl_info)
        
        box_boton_restablecer = BoxLayout(size_hint_y=None, height=100, padding=[0, 0, 0, 30])
        btn_restablecer = Button(
            text="[b][color=#00FF7F]RESTABLECER CLAVE[/color][/b]", 
            markup=True,
            background_color=(0, 0, 0, 0),
            font_size='20sp'
        )
        btn_restablecer.bind(on_release=self.restablecer_clave)
        box_boton_restablecer.add_widget(btn_restablecer)
        layout.add_widget(box_boton_restablecer)
        
        self.contenido_principal.add_widget(layout)

    def on_pre_enter(self):
        self.txt_maestra.text = ""
        self.txt_nueva.text = ""
        self.lbl_info.text = "Ingrese la Palabra Maestra para restablecer la contraseña."

    def restablecer_clave(self, instance):
        datos = cargar_datos()
        clave_maestra = datos.get("clave_maestra", "dany")
        
        maestra_ingresada = self.txt_maestra.text.strip().lower()
        nueva_clave = self.txt_nueva.text.strip()
        
        if maestra_ingresada != clave_maestra.lower():
            self.lbl_info.text = "[color=#FF5555]Error: Palabra Maestra incorrecta.[/color]"
            return
        if not nueva_clave:
            self.lbl_info.text = "[color=#FF5555]Error: Ingrese la nueva clave.[/color]"
            return
            
        datos["pin"] = nueva_clave
        guardar_datos(datos)
        
        self.txt_maestra.text = ""
        self.txt_nueva.text = ""
        self.manager.current = 'menu'

# --- PANTALLA COMPLETA: CAMBIAR CONTRASEÑA ---
class PantallaCambiarClave(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[15, 10, 15, 15], spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp')
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]CAMBIAR CONTRASEÑA[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        grid = GridLayout(cols=2, spacing=12, size_hint_y=None, height=310, padding=[10, 0, 10, 0])
        
        lbl_act = Label(text="[b][color=#00FFFF]Clave Actual:[/color][/b]", markup=True, font_size='15sp', halign='left', valign='middle')
        lbl_act.bind(size=lbl_act.setter('text_size'))
        self.txt_act = CampoClaveConOjito()
        
        lbl_nue = Label(text="[b][color=#00FFFF]Nueva Clave:[/color][/b]", markup=True, font_size='15sp', halign='left', valign='middle')
        lbl_nue.bind(size=lbl_nue.setter('text_size'))
        self.txt_nue = CampoClaveConOjito()
        
        lbl_conf = Label(text="[b][color=#00FFFF]Confirmar Clave:[/color][/b]", markup=True, font_size='15sp', halign='left', valign='middle')
        lbl_conf.bind(size=lbl_conf.setter('text_size'))
        self.txt_conf = CampoClaveConOjito()
        
        grid.add_widget(lbl_act)
        grid.add_widget(self.txt_act)
        grid.add_widget(lbl_nue)
        grid.add_widget(self.txt_nue)
        grid.add_widget(lbl_conf)
        grid.add_widget(self.txt_conf)
        
        layout.add_widget(grid)
        
        self.lbl_info = Label(
            text="Ingrese su clave actual y la nueva clave deseada.", 
            size_hint_y=1, 
            font_size='14sp', 
            color=(0.3, 0.8, 1, 1), 
            markup=True,
            halign='left',
            valign='top'
        )
        self.lbl_info.bind(size=self.lbl_info.setter('text_size'))
        layout.add_widget(self.lbl_info)
        
        box_boton_guardar = BoxLayout(size_hint_y=None, height=100, padding=[0, 0, 0, 30])
        btn_guardar = Button(
            text="[b][color=#00FF7F]GUARDAR CLAVE[/color][/b]", 
            markup=True,
            background_color=(0, 0, 0, 0),
            font_size='20sp'
        )
        btn_guardar.bind(on_release=self.guardar_nueva_clave)
        box_boton_guardar.add_widget(btn_guardar)
        layout.add_widget(box_boton_guardar)
        
        self.contenido_principal.add_widget(layout)

    def on_pre_enter(self):
        self.txt_act.text = ""
        self.txt_nue.text = ""
        self.txt_conf.text = ""
        self.lbl_info.text = "Ingrese su clave actual y la nueva clave deseada."

    def guardar_nueva_clave(self, instance):
        datos = cargar_datos()
        pin_actual = datos.get("pin", "1234")
        
        act = self.txt_act.text.strip()
        nue = self.txt_nue.text.strip()
        conf = self.txt_conf.text.strip()
        
        if act != pin_actual:
            self.lbl_info.text = "[color=#FF5555]Error: La clave actual es incorrecta.[/color]"
            return
        if not nue:
            self.lbl_info.text = "[color=#FF5555]Error: Ingrese la nueva clave.[/color]"
            return
        if nue != conf:
            self.lbl_info.text = "[color=#FF5555]Error: Las claves nuevas no coinciden.[/color]"
            return
            
        datos["pin"] = nue
        guardar_datos(datos)
        
        self.txt_act.text = ""
        self.txt_nue.text = ""
        self.txt_conf.text = ""
        self.manager.current = 'menu'

# --- PANTALLA 1: INICIAR TURNO ---
class PantallaIniciarTurno(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[15, 10, 15, 15], spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp')
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]INICIO DE JORNADA[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        grid = GridLayout(cols=2, spacing=15, size_hint_y=None, height=200, padding=[10, 0, 10, 0])
        
        lbl_chofer = Label(text="[b][color=#00FFFF]Chofer / Conductor:[/color][/b]", markup=True, font_size='16sp', halign='left', valign='middle')
        lbl_chofer.bind(size=lbl_chofer.setter('text_size'))
        self.txt_chofer = EntradaTextoFija(font_size='18sp', size_hint_y=None, height=85)
        
        lbl_km_ini = Label(text="[b][color=#00FFFF]Km INICIAL:[/color][/b]", markup=True, font_size='16sp', halign='left', valign='middle')
        lbl_km_ini.bind(size=lbl_km_ini.setter('text_size'))
        self.txt_km_ini = EntradaTextoFija(input_filter='float', font_size='18sp', size_hint_y=None, height=85)
        
        grid.add_widget(lbl_chofer)
        grid.add_widget(self.txt_chofer)
        grid.add_widget(lbl_km_ini)
        grid.add_widget(self.txt_km_ini)
        
        layout.add_widget(grid)
        
        self.lbl_info = Label(text="", size_hint_y=1, font_size='15sp', color=(0.3, 0.8, 1, 1), markup=True, halign='left', valign='top')
        self.lbl_info.bind(size=self.lbl_info.setter('text_size'))
        layout.add_widget(self.lbl_info)
        
        box_boton_abrir = BoxLayout(size_hint_y=None, height=110, padding=[0, 0, 0, 40])
        btn_guardar = Button(text="[b][color=#00FF7F]ABRIR TURNO[/color][/b]", markup=True, background_color=(0, 0, 0, 0), font_size='22sp')
        btn_guardar.bind(on_release=self.abrir_turno)
        box_boton_abrir.add_widget(btn_guardar)
        layout.add_widget(box_boton_abrir)
        
        self.contenido_principal.add_widget(layout)

    def on_pre_enter(self):
        datos = cargar_datos()
        if datos.get("turno_activo"):
            t = datos["turno_activo"]
            self.lbl_info.text = f"[b][color=#FF5555]ATENCION: YA HAY UN TURNO ABIERTO[/color][/b]\nChofer: {t['chofer']} | Inicio: {t['hora_inicio']}"
        else:
            self.lbl_info.text = "Ingrese los datos para abrir el turno."

    def abrir_turno(self, instance):
        datos = cargar_datos()
        if datos.get("turno_activo"):
            self.lbl_info.text = "[color=#FF5555]Error: Debe finalizar el turno activo.[/color]"
            return

        chofer = self.txt_chofer.text.strip() or "No especificado"
        km_ini_text = self.txt_km_ini.text.strip()

        if not km_ini_text:
            self.lbl_info.text = "[color=#FF5555]Error: Por favor ingrese el Km Inicial.[/color]"
            return

        try:
            km_ini = float(km_ini_text)
            hora_inicio = datetime.now().strftime("%I:%M %p")
            fecha = datetime.now().strftime("%d-%m-%Y")

            datos["turno_activo"] = {
                "fecha": fecha,
                "chofer": chofer,
                "hora_inicio": hora_inicio,
                "km_inicio": km_ini
            }
            guardar_datos(datos)

            self.txt_chofer.text = ""
            self.txt_km_ini.text = ""
            self.manager.current = 'menu'
        except ValueError:
            self.lbl_info.text = "[color=#FF5555]Error: Kilometraje invalido.[/color]"

# --- PANTALLA 2: FINALIZAR TURNO ---
class PantallaFinalizarTurno(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[12, 10, 12, 12], spacing=5)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp')
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=20))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]CIERRE DE JORNADA[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=50,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=25))
        
        self.lbl_datos_inicio = Label(
            text="", 
            size_hint_y=None, 
            height=45, 
            font_size='14sp', 
            markup=True, 
            halign='center',
            valign='middle'
        )
        self.lbl_datos_inicio.bind(size=self.lbl_datos_inicio.setter('text_size'))
        layout.add_widget(self.lbl_datos_inicio)
        
        layout.add_widget(Widget(size_hint_y=None, height=15))
        
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        
        box_contenido_scroll = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        box_contenido_scroll.bind(minimum_height=box_contenido_scroll.setter('height'))
        
        grid = GridLayout(cols=2, spacing=12, size_hint_y=None, height=1350, padding=[10, 5, 10, 5])
        
        def agregar_campo_expandido(texto_label, color_hex, def_val="", es_numero=True, hint=""):
            lbl = Label(text=f"[b][color={color_hex}]{texto_label}[/color][/b]", markup=True, font_size='15sp', halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            
            if es_numero:
                txt = EntradaTextoFija(text=def_val, input_filter='float', font_size='18sp', size_hint_y=None, height=85)
            else:
                txt = EntradaTextoFija(text=def_val, hint_text=hint, font_size='16sp', size_hint_y=None, height=85)
            grid.add_widget(lbl)
            grid.add_widget(txt)
            return txt

        self.txt_km_fin = agregar_campo_expandido("Km FINAL:", "#00FFFF")
        self.txt_efectivo = agregar_campo_expandido("Efectivo:", "#33FF33", "0")
        self.txt_datafono = agregar_campo_expandido("Datáfono:", "#33FF33", "0")
        self.txt_sinpe = agregar_campo_expandido("Sinpe Móvil:", "#33FF33", "0")
        
        self.txt_boletas_coop = agregar_campo_expandido("Boletas Coop (12%):", "#FF8C00", "0")
        self.txt_boletas_taxi18 = agregar_campo_expandido("Boletas Taxizarias (18%):", "#FF8C00", "0")
        self.txt_boletas_taxi10 = agregar_campo_expandido("Boletas Taxizarias (10%):", "#FF8C00", "0")
        
        self.txt_combustible = agregar_campo_expandido("Combustible:", "#FF8C00", "0")
        self.txt_lavado = agregar_campo_expandido("Lavado:", "#FF8C00", "0")
        self.txt_peajes = agregar_campo_expandido("Peajes:", "#FF8C00", "0")
        self.txt_viaticos = agregar_campo_expandido("Viáticos:", "#FF8C00", "0")
        self.txt_gastos_extras = agregar_campo_expandido("Monto Extras:", "#FF8C00", "0")
        self.txt_motivo_extras = agregar_campo_expandido("Motivo Extra:", "#FF8C00", "", es_numero=False, hint="ej: Llanta, Bombillo")
        
        box_contenido_scroll.add_widget(grid)
        
        self.lbl_resumen_vivo = Label(text="", markup=True, font_size='15sp', size_hint_y=None, height=0, line_height=1.3, halign='left')
        self.lbl_resumen_vivo.bind(width=lambda img, val: setattr(self.lbl_resumen_vivo, 'text_size', (val, None)))
        self.lbl_resumen_vivo.bind(texture_size=lambda img, val: setattr(self.lbl_resumen_vivo, 'height', val[1]))
        box_contenido_scroll.add_widget(self.lbl_resumen_vivo)
        
        self.scroll.add_widget(box_contenido_scroll)
        layout.add_widget(self.scroll)
        
        self.lbl_resultado = Label(text="", size_hint_y=None, height=20, font_size='13sp', color=(1, 0.3, 0.3, 1))
        layout.add_widget(self.lbl_resultado)
        
        box_botones = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=40, padding=[10, 5, 10, 40])
        
        btn_calcular = Button(text="[b][color=#00BFFF]CALCULAR / VER RESUMEN[/color][/b]", markup=True, background_color=(0, 0, 0, 0), size_hint_y=None, height=48, font_size='20sp')
        btn_calcular.bind(on_release=self.calcular_resumen_vivo)
        
        btn_cerrar = Button(text="[b][color=#00FF7F]CERRAR Y GUARDAR TURNO[/color][/b]", markup=True, background_color=(0, 0, 0, 0), size_hint_y=None, height=48, font_size='20sp')
        btn_cerrar.bind(on_release=self.cerrar_turno)
        
        box_botones.add_widget(btn_calcular)
        box_botones.add_widget(btn_cerrar)
        layout.add_widget(box_botones)
        
        self.contenido_principal.add_widget(layout)

    def calcular_resumen_vivo(self, instance):
        datos = cargar_datos()
        if not datos.get("turno_activo"):
            self.lbl_resultado.text = "Error: No hay turno activo para calcular."
            return

        try:
            t_ini = datos["turno_activo"]
            km_ini = t_ini["km_inicio"]
            km_fin = float(self.txt_km_fin.text or 0)
            
            if km_fin < km_ini:
                self.lbl_resultado.text = "Error: El Km Final debe ser mayor al Inicial."
                return

            km_recorridos = km_fin - km_ini
            hora_fin_actual = datetime.now().strftime("%I:%M %p")

            efectivo = float(self.txt_efectivo.text or 0)
            datafono = float(self.txt_datafono.text or 0)
            sinpe = float(self.txt_sinpe.text or 0)
            
            b_coop_bruto = float(self.txt_boletas_coop.text or 0)
            b_coop_neto = b_coop_bruto * 0.88

            b_taxi18_bruto = float(self.txt_boletas_taxi18.text or 0)
            b_taxi18_neto = b_taxi18_bruto * 0.82

            b_taxi10_bruto = float(self.txt_boletas_taxi10.text or 0)
            b_taxi10_neto = b_taxi10_bruto * 0.90

            total_boletas_neto = b_coop_neto + b_taxi18_neto + b_taxi10_neto

            combustible = float(self.txt_combustible.text or 0)
            lavado = float(self.txt_lavado.text or 0)
            peajes = float(self.txt_peajes.text or 0)
            viaticos = float(self.txt_viaticos.text or 0)
            gastos_extras = float(self.txt_gastos_extras.text or 0)
            motivo_extras = self.txt_motivo_extras.text.strip() or "Sin detallar"

            total_ingresos = efectivo + datafono + sinpe + total_boletas_neto
            comision_chofer = total_ingresos * 0.30
            total_gastos = combustible + lavado + peajes + viaticos + gastos_extras
            ganancia_neta = total_ingresos - comision_chofer - total_gastos

            res = f"[size=18sp][b][color=#FFD700]=====================================[/color][/b][/size]\n"
            res += f"[size=18sp][b][color=#FFD700]      RESUMEN Y DESGLOSE EN VIVO[/color][/b][/size]\n"
            res += f"[size=18sp][b][color=#FFD700]=====================================[/color][/b][/size]\n\n\n"
            
            res += f"• [color=#AAAAAA]Chofer:[/color] [b]{t_ini['chofer']}[/b]\n"
            res += f"• [color=#AAAAAA]Horario Turno:[/color] {t_ini['hora_inicio']} - {hora_fin_actual}\n"
            res += f"• [color=#00FFFF]Kilómetros Recorridos:[/color] [b]{km_recorridos:.1f} km[/b] (Ini: {km_ini:.1f} | Fin: {km_fin:.1f})\n\n\n"
            
            res += f"• [color=#FFFFFF]Ingreso Bruto Total Real:[/color] [b][color=#33FF33]Colones {total_ingresos:,.2f}[/color][/b]\n\n"
            
            res += f"  [b][color=#00BFFF]PAGOS INGRESADOS:[/color][/b]\n"
            res += f"    - Efectivo: [color=#33FF33]Colones {efectivo:,.2f}[/color]\n"
            res += f"    - Datáfono: [color=#33FF33]Colones {datafono:,.2f}[/color]\n"
            res += f"    - Sinpe Móvil: [color=#33FF33]Colones {sinpe:,.2f}[/color]\n"
            
            if b_coop_bruto > 0:
                res += f"    - Boletas Coop (-12%): [color=#FF8C00]Colones {b_coop_neto:,.2f}[/color] [color=#888888](Bruto: {b_coop_bruto:,.2f})[/color]\n"
            if b_taxi18_bruto > 0:
                res += f"    - Boletas Taxizarias (-18%): [color=#FF8C00]Colones {b_taxi18_neto:,.2f}[/color] [color=#888888](Bruto: {b_taxi18_bruto:,.2f})[/color]\n"
            if b_taxi10_bruto > 0:
                res += f"    - Boletas Taxizarias (-10%): [color=#FF8C00]Colones {b_taxi10_neto:,.2f}[/color] [color=#888888](Bruto: {b_taxi10_bruto:,.2f})[/color]\n"
            
            res += f"\n\n• [color=#FFFFFF]COMISIÓN CHÓFER (30%):[/color] [b][color=#FFD700]Colones {comision_chofer:,.2f}[/color][/b]\n\n\n"
            
            res += f"• [color=#FFFFFF]GASTOS REGISTRADOS:[/color] [b][color=#FF5555]Colones {total_gastos:,.2f}[/color][/b]\n"
            res += f"    - Combustible: [color=#FF5555]Colones {combustible:,.2f}[/color]\n"
            res += f"    - Lavado: [color=#FF5555]Colones {lavado:,.2f}[/color]\n"
            res += f"    - Peajes: [color=#FF5555]Colones {peajes:,.2f}[/color]\n"
            res += f"    - Viáticos: [color=#FF5555]Colones {viaticos:,.2f}[/color]\n"
            res += f"    - Gastos Extras ({motivo_extras}): [color=#FF5555]Colones {gastos_extras:,.2f}[/color]\n\n\n"
            
            res += f"[color=#333333]--------------------------------------------------[/color]\n"
            res += f"• [b][color=#FFFFFF]NETO A ENTREGAR AL TAXI:[/color] [color=#00FF7F]Colones {ganancia_neta:,.2f}[/color][/b]\n"
            res += f"[color=#333333]--------------------------------------------------[/color]\n"

            self.lbl_resumen_vivo.text = res
            self.lbl_resultado.text = ""
            self.scroll.scroll_y = 0
        except ValueError:
            self.lbl_resultado.text = "Error: Ingrese números válidos para calcular."

    def limpiar_formulario(self):
        self.txt_km_fin.text = ""
        self.txt_efectivo.text = "0"
        self.txt_datafono.text = "0"
        self.txt_sinpe.text = "0"
        self.txt_boletas_coop.text = "0"
        self.txt_boletas_taxi18.text = "0"
        self.txt_boletas_taxi10.text = "0"
        self.txt_combustible.text = "0"
        self.txt_lavado.text = "0"
        self.txt_peajes.text = "0"
        self.txt_viaticos.text = "0"
        self.txt_gastos_extras.text = "0"
        self.txt_motivo_extras.text = ""
        self.lbl_resultado.text = ""
        self.lbl_resumen_vivo.text = ""
        self.scroll.scroll_y = 1

    def on_pre_enter(self):
        self.limpiar_formulario()
        datos = cargar_datos()
        if not datos.get("turno_activo"):
            self.lbl_datos_inicio.text = "[color=#FF5555][b]ATENCION: NO HAY NINGUN TURNO ABIERTO.[/b][/color]\n"
        else:
            t = datos["turno_activo"]
            self.lbl_datos_inicio.text = f"[color=#FFD700]Chofer:[/color] {t['chofer']}  |  [color=#FFD700]Inicio:[/color] {t['hora_inicio']}  |  [color=#FFD700]Km Ini:[/color] {t['km_inicio']:.1f} km"

    def cerrar_turno(self, instance):
        datos = cargar_datos()
        if not datos.get("turno_activo"):
            self.lbl_resultado.text = "Error: No hay turno abierto para cerrar."
            return

        try:
            t_ini = datos["turno_activo"]
            km_ini = t_ini["km_inicio"]
            km_fin = float(self.txt_km_fin.text or 0)
            
            if km_fin < km_ini:
                self.lbl_resultado.text = "Error: El Km Final debe ser mayor al Inicial."
                return

            efectivo = float(self.txt_efectivo.text or 0)
            datafono = float(self.txt_datafono.text or 0)
            sinpe = float(self.txt_sinpe.text or 0)
            
            b_coop_bruto = float(self.txt_boletas_coop.text or 0)
            b_coop_neto = b_coop_bruto * 0.88

            b_taxi18_bruto = float(self.txt_boletas_taxi18.text or 0)
            b_taxi18_neto = b_taxi18_bruto * 0.82

            b_taxi10_bruto = float(self.txt_boletas_taxi10.text or 0)
            b_taxi10_neto = b_taxi10_bruto * 0.90

            total_boletas_neto = b_coop_neto + b_taxi18_neto + b_taxi10_neto

            combustible = float(self.txt_combustible.text or 0)
            lavado = float(self.txt_lavado.text or 0)
            peajes = float(self.txt_peajes.text or 0)
            viaticos = float(self.txt_viaticos.text or 0)
            gastos_extras = float(self.txt_gastos_extras.text or 0)
            motivo_extras = self.txt_motivo_extras.text.strip() or "Sin detallar"

            hora_fin_auto = datetime.now().strftime("%I:%M %p")
            km_recorridos = km_fin - km_ini
            total_ingresos = efectivo + datafono + sinpe + total_boletas_neto
            comision_chofer = total_ingresos * 0.30
            total_gastos = combustible + lavado + peajes + viaticos + gastos_extras
            ganancia_neta = total_ingresos - comision_chofer - total_gastos

            registro_completo = {
                "fecha": t_ini["fecha"],
                "chofer": t_ini["chofer"],
                "hora_inicio": t_ini["hora_inicio"],
                "hora_fin": hora_fin_auto,
                "km_inicio": km_ini,
                "km_fin": km_fin,
                "km_recorridos": km_recorridos,
                "efectivo": efectivo,
                "datafono": datafono,
                "sinpe": sinpe,
                "boletas_coop_bruto": b_coop_bruto,
                "boletas_coop_neto": b_coop_neto,
                "boletas_taxi18_bruto": b_taxi18_bruto,
                "boletas_taxi18_neto": b_taxi18_neto,
                "boletas_taxi10_bruto": b_taxi10_bruto,
                "boletas_taxi10_neto": b_taxi10_neto,
                "total_ingresos": total_ingresos,
                "comision_chofer": comision_chofer,
                "combustible": combustible,
                "lavado": lavado,
                "peajes": peajes,
                "viaticos": viaticos,
                "gastos_extras": gastos_extras,
                "motivo_extras": motivo_extras,
                "total_gastos": total_gastos,
                "ganancia_neta": ganancia_neta
            }

            datos["turnos"].append(registro_completo)
            datos["turno_activo"] = None
            guardar_datos(datos)

            self.limpiar_formulario()
            self.manager.current = 'menu'
        except ValueError:
            self.lbl_resultado.text = "Error: Ingrese números válidos."

# --- PANTALLA 3: REGISTRAR MANTENIMIENTO ---
class PantallaMantenimiento(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[15, 10, 15, 15], spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp')
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=30))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]REGISTRAR REPUESTO[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=35))
        
        grid = GridLayout(cols=2, spacing=15, size_hint_y=None, height=380, padding=[10, 0, 10, 0])
        
        lbl_item = Label(text="[b][color=#00FFFF]Pieza / Servicio:[/color][/b]", markup=True, font_size='16sp', halign='left', valign='middle')
        lbl_item.bind(size=lbl_item.setter('text_size'))
        self.txt_item = EntradaTextoFija(hint_text="ej: Aceite, Fibras", font_size='18sp', size_hint_y=None, height=80)
        
        lbl_km_act = Label(text="[b][color=#00FFFF]Km Actual Taxi:[/color][/b]", markup=True, font_size='16sp', halign='left', valign='middle')
        lbl_km_act.bind(size=lbl_km_act.setter('text_size'))
        self.txt_km_act = EntradaTextoFija(input_filter='float', font_size='18sp', size_hint_y=None, height=80)
        
        lbl_km_prox = Label(text="[b][color=#00FFFF]Km Proximo Cambio:[/color][/b]", markup=True, font_size='16sp', halign='left', valign='middle')
        lbl_km_prox.bind(size=lbl_km_prox.setter('text_size'))
        self.txt_km_prox = EntradaTextoFija(input_filter='float', font_size='18sp', size_hint_y=None, height=80)
        
        lbl_costo = Label(text="[b][color=#00FFFF]Costo (Colones):[/color][/b]", markup=True, font_size='16sp', halign='left', valign='middle')
        lbl_costo.bind(size=lbl_costo.setter('text_size'))
        self.txt_costo = EntradaTextoFija(input_filter='float', text="0", font_size='18sp', size_hint_y=None, height=80)
        
        grid.add_widget(lbl_item)
        grid.add_widget(self.txt_item)
        grid.add_widget(lbl_km_act)
        grid.add_widget(self.txt_km_act)
        grid.add_widget(lbl_km_prox)
        grid.add_widget(self.txt_km_prox)
        grid.add_widget(lbl_costo)
        grid.add_widget(self.txt_costo)
        
        layout.add_widget(grid)
        
        self.lbl_status = Label(text="", size_hint_y=1, font_size='15sp', color=(0.2, 1, 0.2, 1), markup=True, halign='left', valign='top')
        self.lbl_status.bind(size=self.lbl_status.setter('text_size'))
        layout.add_widget(self.lbl_status)
        
        box_boton_guardar = BoxLayout(size_hint_y=None, height=110, padding=[0, 0, 0, 40])
        btn_guardar = Button(text="[b][color=#FF8C00]GUARDAR MANTENIMIENTO[/color][/b]", markup=True, background_color=(0, 0, 0, 0), font_size='22sp')
        btn_guardar.bind(on_release=self.guardar_mantenimiento)
        box_boton_guardar.add_widget(btn_guardar)
        layout.add_widget(box_boton_guardar)
        
        self.contenido_principal.add_widget(layout)

    def guardar_mantenimiento(self, instance):
        item = self.txt_item.text.strip()
        try:
            km_act = float(self.txt_km_act.text or 0)
            km_prox = float(self.txt_km_prox.text or 0)
            costo = float(self.txt_costo.text or 0)
            fecha = datetime.now().strftime("%d-%m-%Y")

            if not item:
                self.lbl_status.text = "[color=#FF5555]Error: Ingrese la pieza o servicio.[/color]"
                return

            datos = cargar_datos()
            datos["mantenimientos"].append({
                "fecha": fecha,
                "item": item,
                "km_realizado": km_act,
                "km_proximo": km_prox,
                "costo": costo
            })
            guardar_datos(datos)

            self.txt_item.text = ""
            self.txt_km_act.text = ""
            self.txt_km_prox.text = ""
            self.txt_costo.text = "0"
            self.lbl_status.text = "[color=#33FF33]Mantenimiento guardado con éxito.[/color]"
        except ValueError:
            self.lbl_status.text = "[color=#FF5555]Error: Ingrese números válidos.[/color]"

# --- PANTALLA 4: ALERTAS DE REPUESTOS ---
class PantallaAlertas(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[15, 10, 15, 15], spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp')
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=30))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]ALERTAS DE REPUESTOS[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=35))
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        
        box_contenido = BoxLayout(orientation='vertical', size_hint_y=None, padding=[0, 5, 0, 10])
        box_contenido.bind(minimum_height=box_contenido.setter('height'))
        
        self.lbl_alertas = Label(text="", size_hint_y=None, font_size='15sp', markup=True, halign='left', valign='top')
        self.lbl_alertas.bind(width=lambda img, val: setattr(self.lbl_alertas, 'text_size', (val, None)))
        self.lbl_alertas.bind(texture_size=lambda img, val: setattr(self.lbl_alertas, 'height', val[1]))
        
        box_contenido.add_widget(self.lbl_alertas)
        scroll.add_widget(box_contenido)
        
        layout.add_widget(scroll)
        self.contenido_principal.add_widget(layout)

    def on_pre_enter(self):
        datos = cargar_datos()
        mantenimientos = datos.get("mantenimientos", [])
        
        if not mantenimientos:
            self.lbl_alertas.text = "[color=#AAAAAA]No hay registros de mantenimientos.[/color]"
            return

        ultimo_km = 0
        if datos.get("turnos"):
            ultimo_km = datos["turnos"][-1]["km_fin"]

        res = f"[b][color=#FFFFFF]Último Km en Turnos:[/color][/b] [b][color=#00FFFF]{ultimo_km:.1f} km[/color][/b]\n"
        res += "[color=#444444]--------------------------------------------------[/color]\n\n"

        for m in mantenimientos:
            faltan = m["km_proximo"] - ultimo_km
            res += f"• [b][color=#FFE082]{m['item'].capitalize()}[/color][/b] [color=#CCCCCC](Hecho el {m['fecha']} a los {m['km_realizado']:.1f} km)[/color]\n"
            res += f"  [color=#FFFFFF]Próximo cambio:[/color] [color=#00FFFF]{m['km_proximo']:.1f} km[/color]\n"
            
            if ultimo_km > 0:
                if faltan <= 0:
                    res += f"  [b][color=#FF5555]ALERTA! Pasado por {abs(faltan):.1f} km[/color][/b]\n"
                elif faltan <= 500:
                    res += f"  [b][color=#FFD700]ATENCIÓN! Quedan {faltan:.1f} km[/color][/b]\n"
                else:
                    res += f"  [b][color=#33FF33]Faltan {faltan:.1f} km[/color][/b]\n"
            res += "[color=#444444]--------------------------------------------------[/color]\n\n"

        self.lbl_alertas.text = res

# --- PANTALLA 5: REPORTES ---
class PantallaReportes(PantallaConFondo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=[12, 10, 12, 12], spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=42)
        btn_atras = BotonRedondo(text="< Volver", color_bg=(0.3, 0.3, 0.3, 0.9), size_hint_x=0.28, font_size='13sp', radio=10)
        btn_atras.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(btn_atras)
        top_bar.add_widget(Label(size_hint_x=0.72))
        layout.add_widget(top_bar)
        
        layout.add_widget(Widget(size_hint_y=None, height=20))
        
        lbl_titulo = Label(
            text="[b][color=#FFD700]CONSULTA DE REPORTES[/color][/b]", 
            markup=True, 
            font_size='18sp',
            size_hint_y=None,
            height=50,
            halign='center',
            valign='middle'
        )
        lbl_titulo.bind(size=lbl_titulo.setter('text_size'))
        layout.add_widget(lbl_titulo)
        
        layout.add_widget(Widget(size_hint_y=None, height=20))
        
        self.box_contenedor_tarjeta = BoxLayout(orientation='vertical', size_hint_y=None, height=320)
        
        self.box_tarjeta = BoxLayout(
            orientation='vertical', 
            padding=[15, 20, 15, 15], 
            spacing=10, 
            size_hint=(0.94, 1), 
            pos_hint={'center_x': 0.5}
        )
        
        with self.box_tarjeta.canvas.before:
            Color(0.18, 0.18, 0.18, 0.95)
            self.rect_bg = RoundedRectangle(pos=self.box_tarjeta.pos, size=self.box_tarjeta.size, radius=[14])
        self.box_tarjeta.bind(pos=lambda obj, val: setattr(self.rect_bg, 'pos', val), size=lambda obj, val: setattr(self.rect_bg, 'size', val))
        
        self.lbl_aviso_tarjeta = Label(
            text="[b][color=#FFD700]Ingrese la fecha:[/color][/b]", 
            markup=True, 
            font_size='18sp', 
            size_hint_y=0.20,
            halign='center',
            valign='middle'
        )
        self.lbl_aviso_tarjeta.bind(size=self.lbl_aviso_tarjeta.setter('text_size'))
        self.box_tarjeta.add_widget(self.lbl_aviso_tarjeta)
        
        box_entradas = BoxLayout(size_hint_y=0.52, spacing=10)
        
        col_dia = BoxLayout(orientation='vertical', spacing=2)
        self.txt_dia = EntradaTextoFija(hint_text="DD", input_filter='int', font_size='20sp', halign='center')
        lbl_dia = Label(text="[b][color=#00FFFF]Día[/color][/b]", markup=True, font_size='14sp', size_hint_y=0.35, halign='center')
        col_dia.add_widget(self.txt_dia)
        col_dia.add_widget(lbl_dia)
        
        col_mes = BoxLayout(orientation='vertical', spacing=2)
        self.txt_mes = EntradaTextoFija(hint_text="MM", input_filter='int', font_size='20sp', halign='center')
        lbl_mes = Label(text="[b][color=#00FFFF]Mes[/color][/b]", markup=True, font_size='14sp', size_hint_y=0.35, halign='center')
        col_mes.add_widget(self.txt_mes)
        col_mes.add_widget(lbl_mes)
        
        col_ano = BoxLayout(orientation='vertical', spacing=2)
        self.txt_ano = EntradaTextoFija(text="2026", input_filter='int', font_size='20sp', halign='center')
        lbl_ano = Label(text="[b][color=#00FFFF]Año[/color][/b]", markup=True, font_size='14sp', size_hint_y=0.35, halign='center')
        col_ano.add_widget(self.txt_ano)
        col_ano.add_widget(lbl_ano)
        
        box_entradas.add_widget(col_dia)
        box_entradas.add_widget(col_mes)
        box_entradas.add_widget(col_ano)
        self.box_tarjeta.add_widget(box_entradas)
        
        btn_aceptar = BotonRedondo(
            text="[b]Aceptar[/b]", 
            markup=True,
            color_bg=(0.1, 0.5, 0.9, 0.95), 
            size_hint_y=0.28, 
            font_size='17sp',
            radio=10
        )
        btn_aceptar.bind(on_release=self.consultar)
        self.box_tarjeta.add_widget(btn_aceptar)
        
        self.box_contenedor_tarjeta.add_widget(self.box_tarjeta)
        layout.add_widget(self.box_contenedor_tarjeta)
        
        self.btn_nueva_busqueda = Button(
            text="[b][color=#00FFFF]NUEVA CONSULTA[/color][/b]", 
            markup=True,
            background_color=(0, 0, 0, 0),
            size_hint_y=None, 
            height=0, 
            opacity=0,
            font_size='18sp'
        )
        self.btn_nueva_busqueda.bind(on_release=self.mostrar_tarjeta)
        layout.add_widget(self.btn_nueva_busqueda)

        scroll = ScrollView(size_hint=(1, 1))
        self.lbl_reporte = Label(text="", size_hint_y=None, font_size='14sp', line_height=1.2, markup=True)
        self.lbl_reporte.bind(width=lambda img, val: setattr(self.lbl_reporte, 'text_size', (val, None)))
        self.lbl_reporte.bind(texture_size=lambda img, val: setattr(self.lbl_reporte, 'height', val[1]))
        scroll.add_widget(self.lbl_reporte)
        layout.add_widget(scroll)
        
        box_flotante = BoxLayout(size_hint_y=None, height=90, padding=[15, 5, 15, 30])
        btn_volver_abajo = Button(
            text="[b][color=#00FF7F]VOLVER AL MENU[/color][/b]", 
            markup=True,
            background_color=(0, 0, 0, 0),
            font_size='20sp'
        )
        btn_volver_abajo.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        box_flotante.add_widget(btn_volver_abajo)
        
        layout.add_widget(box_flotante)
        self.contenido_principal.add_widget(layout)

    def on_pre_enter(self):
        self.mostrar_tarjeta()

    def mostrar_tarjeta(self, *args):
        self.txt_dia.text = ""
        self.txt_mes.text = ""
        self.txt_ano.text = "2026"
        self.lbl_aviso_tarjeta.text = "[b][color=#FFD700]Ingrese la fecha:[/color][/b]"
        self.lbl_reporte.text = ""
        
        self.btn_nueva_busqueda.height = 0
        self.btn_nueva_busqueda.opacity = 0
        
        self.box_contenedor_tarjeta.height = 320
        self.box_contenedor_tarjeta.opacity = 1

    def consultar(self, instance):
        dia = self.txt_dia.text.strip()
        mes = self.txt_mes.text.strip()
        ano = self.txt_ano.text.strip() or "2026"
        
        if not mes:
            self.lbl_aviso_tarjeta.text = "[color=#FF5555][b]¡Ingrese el Mes (MM)![/b][/color]"
            return

        if dia and len(dia) == 1: dia = f"0{dia}"
        if len(mes) == 1: mes = f"0{mes}"

        if dia:
            consulta = f"{dia}-{mes}-{ano}"
        else:
            consulta = f"{mes}-{ano}"

        datos = cargar_datos()
        turnos_filtrados = [t for t in datos["turnos"] if t["fecha"] == consulta or t["fecha"].endswith(consulta)]
        
        if not turnos_filtrados:
            self.lbl_aviso_tarjeta.text = f"[color=#FF5555][b]Sin registros en {consulta}[/b][/color]"
            return

        tot_km = sum(t["km_recorridos"] for t in turnos_filtrados)
        tot_ing = sum(t["total_ingresos"] for t in turnos_filtrados)
        tot_com_chofer = sum(t.get("comision_chofer", t["total_ingresos"] * 0.30) for t in turnos_filtrados)
        tot_gas = sum(t["total_gastos"] for t in turnos_filtrados)
        tot_net = tot_ing - tot_com_chofer - tot_gas
        
        # Espacio inicial alto para no chocar con el botón NUEVA CONSULTA
        res = "\n\n"
        res += f"[b][color=#FFD700]========================================[/color][/b]\n"
        res += f"[b][color=#FFD700]  RESUMEN GENERAL: {consulta}[/color][/b]\n"
        res += f"[b][color=#FFD700]========================================[/color][/b]\n\n"
        res += f"[color=#FFFFFF]Km Recorridos:[/color] [b][color=#00FFFF]{tot_km:.1f} km[/color][/b]\n"
        res += f"[color=#FFFFFF]INGRESOS BRUTOS REALES:[/color] [b][color=#33FF33]Colones {tot_ing:,.2f}[/color][/b]\n"
        res += f"[color=#FFFFFF]COMISIÓN CHÓFER (30%):[/color] [b][color=#FFD700]Colones {tot_com_chofer:,.2f}[/color][/b]\n"
        res += f"[color=#FFFFFF]GASTOS TOTALES:[/color] [b][color=#FF5555]Colones {tot_gas:,.2f}[/color][/b]\n"
        res += f"[color=#FFFFFF]GANANCIA NETA (TAXI):[/color] [b][color=#00FF7F]Colones {tot_net:,.2f}[/color][/b]\n\n"
        res += f"[color=#555555]--------------------------------------------------[/color]\n\n"
        res += f"[b][color=#00BFFF]DESGLOSE DETALLADO POR TURNO:[/color][/b]\n\n"
        
        for idx, t in enumerate(turnos_filtrados, 1):
            com_chof = t.get("comision_chofer", t["total_ingresos"] * 0.30)
            g_extras = t.get("gastos_extras", 0)
            m_extras = t.get("motivo_extras", "Sin detallar")
            res += f"[b][color=#FFD700]#{idx} TURNO | Fecha: {t['fecha']}[/color][/b]\n"
            res += f"[color=#AAAAAA]Chofer:[/color] [b]{t['chofer']}[/b]\n"
            res += f"[color=#AAAAAA]Horario:[/color] {t['hora_inicio']} - {t['hora_fin']}\n"
            res += f"[color=#AAAAAA]Km Recorridos:[/color] [b][color=#00FFFF]{t['km_recorridos']:.1f} km[/color][/b]\n\n"
            
            res += f"  • [color=#FFFFFF]Ingreso Bruto Real:[/color] [b][color=#33FF33]Colones {t['total_ingresos']:,.2f}[/color][/b]\n"
            res += f"  • [color=#FFFFFF]Comisión Chófer (30%):[/color] [b][color=#FFD700]Colones {com_chof:,.2f}[/color][/b]\n"
            res += f"  • [color=#FFFFFF]Ganancia Neta (Taxi):[/color] [b][color=#00FF7F]Colones {t['ganancia_neta']:,.2f}[/color][/b]\n\n"
            
            res += f"  [b][color=#00BFFF]PAGOS RECIBIDOS:[/color][/b]\n"
            res += f"    - Efectivo: [b][color=#33FF33]Colones {t['efectivo']:,.2f}[/color][/b]\n"
            res += f"    - Datáfono: [b][color=#33FF33]Colones {t['datafono']:,.2f}[/color][/b]\n"
            res += f"    - Sinpe Móvil: [b][color=#33FF33]Colones {t['sinpe']:,.2f}[/color][/b]\n"
            
            if t.get("boletas_coop_bruto", 0) > 0:
                res += f"    - Boletas Coop (-12%): [b][color=#FF8C00]Colones {t['boletas_coop_neto']:,.2f}[/color][/b] [color=#AAAAAA](Bruto: {t['boletas_coop_bruto']:,.2f})[/color]\n"
            if t.get("boletas_taxi18_bruto", 0) > 0:
                res += f"    - Boletas Taxizarias (-18%): [b][color=#FF8C00]Colones {t['boletas_taxi18_neto']:,.2f}[/color][/b] [color=#AAAAAA](Bruto: {t['boletas_taxi18_bruto']:,.2f})[/color]\n"
            if t.get("boletas_taxi10_bruto", 0) > 0:
                res += f"    - Boletas Taxizarias (-10%): [b][color=#FF8C00]Colones {t['boletas_taxi10_neto']:,.2f}[/color][/b] [color=#AAAAAA](Bruto: {t['boletas_taxi10_bruto']:,.2f})[/color]\n"
            
            res += f"\n  [b][color=#FF5555]GASTOS DEL TURNO:[/color][/b]\n"
            res += f"    - Combustible: [b][color=#FF5555]Colones {t['combustible']:,.2f}[/color][/b]\n"
            res += f"    - Lavado: [b][color=#FF5555]Colones {t['lavado']:,.2f}[/color][/b]\n"
            res += f"    - Peajes: [b][color=#FF5555]Colones {t['peajes']:,.2f}[/color][/b]\n"
            res += f"    - Viáticos: [b][color=#FF5555]Colones {t['viaticos']:,.2f}[/color][/b]\n"
            res += f"    - Gastos Extras ({m_extras}): [b][color=#FF5555]Colones {g_extras:,.2f}[/color][/b]\n\n"
            res += f"[color=#333333]--------------------------------------------------[/color]\n\n"
            
        self.lbl_reporte.text = res

        self.box_contenedor_tarjeta.height = 0
        self.box_contenedor_tarjeta.opacity = 0
        
        self.btn_nueva_busqueda.height = 50
        self.btn_nueva_busqueda.opacity = 1

# --- ADMINISTRADOR DE PANTALLAS ---
class TaxiApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaMenu(name='menu'))
        sm.add_widget(PantallaIniciarTurno(name='iniciar_turno'))
        sm.add_widget(PantallaFinalizarTurno(name='finalizar_turno'))
        sm.add_widget(PantallaMantenimiento(name='mantenimiento'))
        sm.add_widget(PantallaAlertas(name='alertas'))
        sm.add_widget(PantallaReportes(name='reportes'))
        sm.add_widget(PantallaRecuperarClave(name='recuperar_clave'))
        sm.add_widget(PantallaCambiarClave(name='cambiar_clave'))
        return sm

if __name__ == "__main__":
    TaxiApp().run()