"""
دستیار املاک - نسخه کامل موبایل (فاز ۱) - طراحی شاد
"""
import json
import sqlite3
import platform
from pathlib import Path
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle


FONT_PATH = Path(__file__).parent / "Vazirmatn-Regular.ttf"
FONT_NAME = "Vazir"

if FONT_PATH.exists():
    LabelBase.register(name=FONT_NAME, fn_regular=str(FONT_PATH))
    print("OK Font loaded")
else:
    print("WARN Font not found")
    FONT_NAME = "Roboto"


def fa(text):
    if not text:
        return ""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)


if platform.system() == "Windows":
    BASE_PATH = Path("C:/realestate_assistant")
else:
    BASE_PATH = Path("/storage/emulated/0/realestate_assistant")

DB_PATH = BASE_PATH / "data" / "realestate.db"
MEDIA_PATH = BASE_PATH / "data" / "media"
try:
    MEDIA_PATH.mkdir(parents=True, exist_ok=True)
except:
    pass


BG_DARK = (0.10, 0.06, 0.18, 1)
BG_CARD = (0.18, 0.11, 0.31, 1)
PINK = (1.0, 0.42, 0.62, 1)
PINK_LIGHT = (1.0, 0.70, 0.82, 1)
TURQUOISE = (0.31, 0.80, 0.77, 1)
GOLD = (1.0, 0.85, 0.24, 1)
PURPLE = (0.72, 0.58, 0.96, 1)
MINT = (0.42, 0.81, 0.50, 1)
CORAL = (1.0, 0.54, 0.40, 1)
LAVENDER = (0.85, 0.70, 0.95, 1)
TEXT_PRIMARY = (1.0, 0.96, 0.98, 1)
TEXT_SECONDARY = (0.83, 0.65, 0.83, 1)
DANGER = (1.0, 0.42, 0.42, 1)

PROPERTY_TYPES = {
    "apartment": "آپارتمان", "villa": "ویلایی",
    "old_house": "کلنگی", "partnership": "مشارکت",
    "office": "اداری", "commercial": "تجاری",
    "warehouse": "انبار", "rent": "رهن و اجاره",
    "rent_commercial": "اجاره اداری", "land": "زمین",
    "garden": "باغ/ویلا",
}

NEIGHBORHOODS = {
    "zafaranieh": "زعفرانیه", "velenjak": "ولنجک",
    "mahmoudieh": "محمودیه", "other": "سایر",
}


def get_db():
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def parse_json_safe(text, default):
    try:
        if not text:
            return default
        return json.loads(text)
    except:
        return default


class ColoredLabel(Label):
    def __init__(self, bg_color=BG_CARD, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        self.refresh()
        self.add_widget(self.layout)
    
    def refresh(self):
        self.layout.clear_widgets()
        header = ColoredLabel(
            text=fa("دستیار املاک"), font_size=sp(26), bold=True,
            size_hint_y=None, height=dp(70),
            color=TEXT_PRIMARY, bg_color=PINK
        )
        self.layout.add_widget(header)
        
        conn = get_db()
        if conn:
            prop_count = len(conn.execute("SELECT id FROM properties WHERE status='active'").fetchall())
            client_count = len(conn.execute("SELECT id FROM clients WHERE status='active'").fetchall())
            conn.close()
            stats_text = str(prop_count) + " فایل  •  " + str(client_count) + " مشتری"
        else:
            stats_text = "دیتابیس پیدا نشد"
        
        stats = ColoredLabel(
            text=fa(stats_text), font_size=sp(16), halign='center',
            size_hint_y=None, height=dp(55),
            bg_color=PURPLE, color=TEXT_PRIMARY
        )
        self.layout.add_widget(stats)
        
        scroll = ScrollView()
        btn_list = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(5))
        btn_list.bind(minimum_height=btn_list.setter('height'))
        
        buttons = [
            ("مشاهده فایل‌ها", PINK, "properties"),
            ("افزودن فایل جدید", TURQUOISE, "add_property"),
            ("مشاهده مشتریان", LAVENDER, "clients"),
            ("افزودن مشتری جدید", MINT, "add_client"),
            ("موتور تطبیق", PURPLE, "matches"),
            ("افزودن از دیوار", CORAL, "add_from_divar"),
        ]
        
        for text, color, screen_name in buttons:
            btn = Button(
                text=fa(text), font_size=sp(17), font_name=FONT_NAME, bold=True,
                size_hint_y=None, height=dp(58),
                background_color=color, background_normal=''
            )
            btn.bind(on_press=lambda x, s=screen_name: setattr(self.manager, 'current', s))
            btn_list.add_widget(btn)
        
        scroll.add_widget(btn_list)
        self.layout.add_widget(scroll)


class PropertiesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("لیست فایل‌ها"), font_size=sp(18), bold=True, bg_color=PINK, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=dp(5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_enter(self):
        self.list_layout.clear_widgets()
        conn = get_db()
        if not conn:
            self.list_layout.add_widget(Label(text=fa("دیتابیس پیدا نشد"), color=DANGER, font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
            return
        props = conn.execute("SELECT * FROM properties WHERE status='active' ORDER BY created_at DESC LIMIT 100").fetchall()
        conn.close()
        if not props:
            self.list_layout.add_widget(Label(text=fa("هیچ فایلی موجود نیست"), color=TEXT_SECONDARY, font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
            return
        for p in props:
            p = dict(p)
            if p.get('property_type') in ['rent', 'rent_commercial']:
                price = "ودیعه {:.0f}م".format(p.get('rent_deposit', 0)/1e9)
            elif p.get('property_type') == 'partnership':
                price = "مالک {:.0f}%".format(p.get('partnership_owner_share') or 0)
            else:
                price = "{:.0f} میلیارد".format(p.get('total_price', 0)/1e9) if p.get('total_price') else "-"
            media = parse_json_safe(p.get('media_files'), [])
            media_icon = " [" + str(len(media)) + "]" if media else ""
            text = PROPERTY_TYPES.get(p['property_type'], '') + " • " + NEIGHBORHOODS.get(p['neighborhood'], '') + "\n" + (p.get('street') or '') + " • " + price + media_icon
            btn = Button(
                text=fa(text), size_hint_y=None, height=dp(85),
                background_color=BG_CARD, background_normal='',
                color=TEXT_PRIMARY, font_size=sp(13), font_name=FONT_NAME,
                halign='right'
            )
            btn.bind(on_press=lambda x, pid=p['id']: self.open_detail(pid))
            self.list_layout.add_widget(btn)
    
    def open_detail(self, prop_id):
        detail = self.manager.get_screen('property_detail')
        detail.load_property(prop_id)
        self.manager.current = 'property_detail'


class PropertyDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_prop = None
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'properties'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("جزئیات فایل"), font_size=sp(18), bold=True, bg_color=PINK, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=dp(10))
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        layout.add_widget(scroll)
        actions = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(6))
        btn_edit = Button(text=fa("ویرایش"), background_color=TURQUOISE, background_normal='', font_name=FONT_NAME, font_size=sp(13), bold=True)
        btn_edit.bind(on_press=lambda x: self.edit_property())
        actions.add_widget(btn_edit)
        btn_sms = Button(text=fa("پیامک"), background_color=GOLD, background_normal='', font_name=FONT_NAME, font_size=sp(13), bold=True)
        btn_sms.bind(on_press=lambda x: self.copy_sms())
        actions.add_widget(btn_sms)
        btn_delete = Button(text=fa("حذف"), background_color=DANGER, background_normal='', font_name=FONT_NAME, font_size=sp(13), bold=True)
        btn_delete.bind(on_press=lambda x: self.delete_property())
        actions.add_widget(btn_delete)
        layout.add_widget(actions)
        self.add_widget(layout)
    
    def load_property(self, prop_id):
        conn = get_db()
        if not conn:
            return
        p = conn.execute("SELECT * FROM properties WHERE id=?", (prop_id,)).fetchone()
        conn.close()
        if not p:
            return
        p = dict(p)
        self.current_prop = p
        self.content.clear_widgets()
        
        def add_label(text, font_size=14, color=TEXT_PRIMARY, height=42, bg=BG_CARD):
            lbl = ColoredLabel(text=fa(text), font_size=sp(font_size), color=color,
                size_hint_y=None, height=dp(height), halign='right', bg_color=bg)
            lbl.bind(size=lambda *a: setattr(lbl, 'text_size', (lbl.width - dp(10), None)))
            self.content.add_widget(lbl)
        
        add_label(PROPERTY_TYPES.get(p['property_type'], '') + " در " + NEIGHBORHOODS.get(p['neighborhood'], ''), font_size=18, color=TEXT_PRIMARY, height=55, bg=PINK)
        add_label("📍 " + (p.get('street') or '-'), height=40)
        
        if p['property_type'] in ['rent', 'rent_commercial']:
            add_label("💰 ودیعه: {:.0f} میلیون".format(p.get('rent_deposit', 0)/1e6), height=38)
            add_label("💵 اجاره: {:.0f} میلیون".format(p.get('rent_monthly', 0)/1e6), height=38)
            add_label("👤 مستأجر: " + (p.get('tenant_name') or '-'), height=38)
            add_label("📞 " + (p.get('tenant_phone') or '-'), height=38)
        elif p['property_type'] == 'partnership':
            add_label("🤝 سهم مالک: {:.0f}%".format(p.get('partnership_owner_share') or 0), height=38, color=LAVENDER)
            add_label("🔨 سهم سازنده: {:.0f}%".format(p.get('partnership_builder_share') or 0), height=38, color=LAVENDER)
        elif p['property_type'] in ['land', 'garden']:
            add_label("📐 متراژ: {:.0f} متر".format(p.get('land_area') or 0), height=38)
            add_label("📋 کاربری: " + (p.get('land_use') or '-'), height=38)
            if p.get('total_price'):
                add_label("💰 قیمت: {:.1f} میلیارد".format(p['total_price']/1e9), font_size=17, color=GOLD, height=48)
        else:
            add_label("📐 متراژ زمین: {:.0f} متر".format(p.get('land_area') or 0), height=38)
            add_label("🏗️ متراژ بنا: {:.0f} متر".format(p.get('building_area') or 0), height=38)
            add_label("📜 سند: " + (p.get('document_status') or '-'), height=38)
            if p.get('total_price'):
                add_label("💰 قیمت: {:.1f} میلیارد".format(p['total_price']/1e9), font_size=17, color=GOLD, height=48)
        
        add_label("👤 مالک: " + (p.get('owner_name') or '-'), height=38)
        add_label("📞 " + (p.get('owner_phone') or '-'), height=38)
        if p.get('caretaker_name'):
            add_label("🔑 سرایدار: " + p['caretaker_name'], height=38)
        amenities = parse_json_safe(p.get('amenities'), {})
        active = [k for k, v in amenities.items() if v]
        if active:
            add_label("✨ امکانات: " + str(len(active)) + " مورد", height=38, color=TURQUOISE)
        media = parse_json_safe(p.get('media_files'), [])
        if media:
            add_label("📷 گالری (" + str(len(media)) + " فایل)", font_size=16, color=PINK_LIGHT, height=45)
            for m in media[:3]:
                try:
                    file_path = BASE_PATH / m['path']
                    if file_path.exists() and m['type'] == 'image':
                        img = Image(source=str(file_path), size_hint_y=None, height=dp(160))
                        self.content.add_widget(img)
                except:
                    pass
        if p.get('notes'):
            add_label("📝 " + p['notes'], height=70, color=TEXT_SECONDARY)
    
    def copy_sms(self):
        if not self.current_prop:
            return
        p = self.current_prop
        if p['property_type'] in ['rent', 'rent_commercial']:
            price = "ودیعه {:.0f} میلیون / اجاره {:.0f} میلیون".format(p.get('rent_deposit', 0)/1e6, p.get('rent_monthly', 0)/1e6)
        else:
            price = "{:.0f} میلیارد تومان".format(p.get('total_price', 0)/1e9) if p.get('total_price') else "تماس بگیرید"
        text = PROPERTY_TYPES.get(p['property_type'], '') + " در " + NEIGHBORHOODS.get(p['neighborhood'], '') + "\n"
        text += "آدرس: " + (p.get('street') or '') + "\n"
        text += "قیمت: " + price + "\n"
        text += "برای هماهنگی بازدید تماس بگیرید."
        Clipboard.copy(text)
        self.show_popup("کپی شد", "متن پیامک کپی شد. در واتساپ paste کن.")
    
    def edit_property(self):
        if not self.current_prop:
            return
        edit_screen = self.manager.get_screen('edit_property')
        edit_screen.load_property(self.current_prop)
        self.manager.current = 'edit_property'
    
    def delete_property(self):
        if not self.current_prop:
            return
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=fa("آیا مطمئنی؟"), font_name=FONT_NAME, color=TEXT_PRIMARY))
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_yes = Button(text=fa("بله"), background_color=DANGER, background_normal='', font_name=FONT_NAME)
        btn_no = Button(text=fa("خیر"), background_color=PURPLE, background_normal='', font_name=FONT_NAME)
        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        content.add_widget(btns)
        popup = Popup(title=fa("تأیید حذف"), content=content, size_hint=(0.85, 0.4), title_color=TEXT_PRIMARY, background_color=BG_CARD)
        def confirm(instance):
            conn = get_db()
            if conn:
                conn.execute("UPDATE properties SET status='archived' WHERE id=?", (self.current_prop['id'],))
                conn.commit()
                conn.close()
            popup.dismiss()
            self.manager.current = 'properties'
        btn_yes.bind(on_press=confirm)
        btn_no.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text=fa(message), font_name=FONT_NAME, color=TEXT_PRIMARY))
        btn = Button(text=fa("باشه"), size_hint_y=None, height=dp(50), font_name=FONT_NAME, background_color=PINK, background_normal='')
        content.add_widget(btn)
        popup = Popup(title=fa(title), content=content, size_hint=(0.8, 0.35), title_color=TEXT_PRIMARY, background_color=BG_CARD)
        btn.bind(on_press=popup.dismiss)
        popup.open()


class EditPropertyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_prop = None
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'property_detail'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("ویرایش فایل"), font_size=sp(18), bold=True, bg_color=PINK, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=dp(8))
        form.bind(minimum_height=form.setter('height'))
        def add_field(label_text, hint):
            form.add_widget(Label(text=fa(label_text), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
            inp = TextInput(hint_text=fa(hint), size_hint_y=None, height=dp(42),
                background_color=BG_CARD, foreground_color=TEXT_PRIMARY,
                font_name=FONT_NAME, halign='right', multiline=False, cursor_color=PINK)
            form.add_widget(inp)
            return inp
        self.street_input = add_field("خیابان", "خیابان ناهید")
        self.area_input = add_field("متراژ زمین", "200")
        self.building_input = add_field("متراژ بنا", "180")
        self.document_input = add_field("سند", "شش‌دانگ")
        self.price_input = add_field("قیمت (میلیارد)", "100")
        self.owner_input = add_field("نام مالک", "آقای رضایی")
        self.phone_input = add_field("تلفن مالک", "0912...")
        self.notes_input = add_field("یادداشت", "")
        scroll.add_widget(form)
        layout.add_widget(scroll)
        btn_save = Button(text=fa("ذخیره تغییرات"), font_size=sp(16), font_name=FONT_NAME, bold=True,
            size_hint_y=None, height=dp(55), background_color=MINT, background_normal='')
        btn_save.bind(on_press=lambda x: self.save_property())
        layout.add_widget(btn_save)
        self.status_label = Label(text="", size_hint_y=None, height=dp(30), font_name=FONT_NAME, color=MINT)
        layout.add_widget(self.status_label)
        self.add_widget(layout)
    
    def load_property(self, p):
        self.current_prop = p
        self.street_input.text = p.get('street') or ""
        self.area_input.text = str(int(p.get('land_area') or 0)) if p.get('land_area') else ""
        self.building_input.text = str(int(p.get('building_area') or 0)) if p.get('building_area') else ""
        self.document_input.text = p.get('document_status') or ""
        self.price_input.text = "{:.1f}".format(p['total_price']/1e9) if p.get('total_price') else ""
        self.owner_input.text = p.get('owner_name') or ""
        self.phone_input.text = p.get('owner_phone') or ""
        self.notes_input.text = p.get('notes') or ""
        self.status_label.text = ""
    
    def save_property(self):
        if not self.current_prop:
            return
        conn = get_db()
        if not conn:
            return
        try:
            area = float(self.area_input.text) if self.area_input.text else None
            building = float(self.building_input.text) if self.building_input.text else None
            price_b = float(self.price_input.text) if self.price_input.text else None
            price = price_b * 1e9 if price_b else None
            conn.execute("""
                UPDATE properties SET street=?, land_area=?, building_area=?, document_status=?,
                    total_price=?, owner_name=?, owner_phone=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (self.street_input.text, area, building, self.document_input.text,
                  price, self.owner_input.text, self.phone_input.text,
                  self.notes_input.text, self.current_prop['id']))
            conn.commit()
            conn.close()
            self.status_label.text = fa("ذخیره شد")
            self.status_label.color = MINT
        except Exception as e:
            self.status_label.text = fa("خطا: ") + str(e)
            self.status_label.color = DANGER


class AddPropertyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("افزودن فایل جدید"), font_size=sp(18), bold=True, bg_color=PINK, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=dp(8))
        form.bind(minimum_height=form.setter('height'))
        form.add_widget(Label(text=fa("نوع ملک"), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
        self.type_spinner = Spinner(text=fa("آپارتمان"), values=[fa(v) for v in PROPERTY_TYPES.values()],
            size_hint_y=None, height=dp(45), background_color=PURPLE, font_name=FONT_NAME)
        form.add_widget(self.type_spinner)
        form.add_widget(Label(text=fa("محله"), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
        self.neighborhood_spinner = Spinner(text=fa("زعفرانیه"), values=[fa(v) for v in NEIGHBORHOODS.values()],
            size_hint_y=None, height=dp(45), background_color=PURPLE, font_name=FONT_NAME)
        form.add_widget(self.neighborhood_spinner)
        def add_field(label_text, hint):
            form.add_widget(Label(text=fa(label_text), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
            inp = TextInput(hint_text=fa(hint), size_hint_y=None, height=dp(42),
                background_color=BG_CARD, foreground_color=TEXT_PRIMARY,
                font_name=FONT_NAME, halign='right', multiline=False, cursor_color=PINK)
            form.add_widget(inp)
            return inp
        self.street_input = add_field("خیابان", "خیابان ناهید")
        self.area_input = add_field("متراژ", "200")
        self.price_input = add_field("قیمت (میلیارد)", "100")
        self.owner_input = add_field("نام مالک", "آقای رضایی")
        self.phone_input = add_field("تلفن مالک", "0912...")
        scroll.add_widget(form)
        layout.add_widget(scroll)
        btn_save = Button(text=fa("ذخیره فایل"), font_size=sp(16), font_name=FONT_NAME, bold=True,
            size_hint_y=None, height=dp(55), background_color=MINT, background_normal='')
        btn_save.bind(on_press=lambda x: self.save_property())
        layout.add_widget(btn_save)
        self.status_label = Label(text="", size_hint_y=None, height=dp(30), font_name=FONT_NAME, color=MINT)
        layout.add_widget(self.status_label)
        self.add_widget(layout)
    
    def save_property(self):
        conn = get_db()
        if not conn:
            self.status_label.text = fa("خطا")
            return
        type_key = "apartment"
        for k, v in PROPERTY_TYPES.items():
            if fa(v) == self.type_spinner.text:
                type_key = k
                break
        neigh_key = "zafaranieh"
        for k, v in NEIGHBORHOODS.items():
            if fa(v) == self.neighborhood_spinner.text:
                neigh_key = k
                break
        try:
            area = float(self.area_input.text) if self.area_input.text else None
            price_b = float(self.price_input.text) if self.price_input.text else None
            price = price_b * 1e9 if price_b else None
            conn.execute("""INSERT INTO properties 
                (property_type, neighborhood, street, land_area, total_price, owner_name, owner_phone, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')""",
                (type_key, neigh_key, self.street_input.text, area, price, self.owner_input.text, self.phone_input.text))
            conn.commit()
            conn.close()
            self.status_label.text = fa("فایل ذخیره شد")
            self.status_label.color = MINT
            self.street_input.text = ""
            self.area_input.text = ""
            self.price_input.text = ""
            self.owner_input.text = ""
            self.phone_input.text = ""
        except Exception as e:
            self.status_label.text = fa("خطا: ") + str(e)
            self.status_label.color = DANGER


class ClientsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("لیست مشتریان"), font_size=sp(18), bold=True, bg_color=PINK, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=dp(5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_enter(self):
        self.list_layout.clear_widgets()
        conn = get_db()
        if not conn:
            return
        clients = conn.execute("SELECT * FROM clients WHERE status='active' ORDER BY created_at DESC LIMIT 100").fetchall()
        conn.close()
        if not clients:
            self.list_layout.add_widget(Label(text=fa("هیچ مشتری موجود نیست"), color=TEXT_SECONDARY, font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
            return
        for c in clients:
            c = dict(c)
            nick = " [" + str(c.get('nickname')) + "]" if c.get('nickname') else ""
            text = str(c['full_name']) + nick + "\n" + str(c['phone'])
            btn = Button(text=fa(text), size_hint_y=None, height=dp(80),
                background_color=BG_CARD, background_normal='', color=TEXT_PRIMARY,
                font_size=sp(13), font_name=FONT_NAME, halign='right')
            self.list_layout.add_widget(btn)


class AddClientScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("افزودن مشتری جدید"), font_size=sp(18), bold=True, bg_color=PINK, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=dp(8))
        form.bind(minimum_height=form.setter('height'))
        def add_field(label_text, hint):
            form.add_widget(Label(text=fa(label_text), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
            inp = TextInput(hint_text=fa(hint), size_hint_y=None, height=dp(42),
                background_color=BG_CARD, foreground_color=TEXT_PRIMARY,
                font_name=FONT_NAME, halign='right', multiline=False, cursor_color=PINK)
            form.add_widget(inp)
            return inp
        self.name_input = add_field("نام مشتری", "آقای محمدی")
        self.nickname_input = add_field("نام مستعار", "محمدی — کلنگی")
        self.phone_input = add_field("تلفن", "0912...")
        form.add_widget(Label(text=fa("نوع تقاضا"), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
        self.type_spinner = Spinner(text=fa("آپارتمان"), values=[fa(v) for v in PROPERTY_TYPES.values()],
            size_hint_y=None, height=dp(45), background_color=PURPLE, font_name=FONT_NAME)
        form.add_widget(self.type_spinner)
        self.budget_input = add_field("بودجه تا (میلیارد)", "150")
        scroll.add_widget(form)
        layout.add_widget(scroll)
        btn_save = Button(text=fa("ذخیره مشتری"), font_size=sp(16), font_name=FONT_NAME, bold=True,
            size_hint_y=None, height=dp(55), background_color=MINT, background_normal='')
        btn_save.bind(on_press=lambda x: self.save_client())
        layout.add_widget(btn_save)
        self.status_label = Label(text="", size_hint_y=None, height=dp(30), font_name=FONT_NAME, color=MINT)
        layout.add_widget(self.status_label)
        self.add_widget(layout)
    
    def save_client(self):
        conn = get_db()
        if not conn:
            return
        type_key = "apartment"
        for k, v in PROPERTY_TYPES.items():
            if fa(v) == self.type_spinner.text:
                type_key = k
                break
        try:
            budget_b = float(self.budget_input.text) if self.budget_input.text else None
            budget = budget_b * 1e9 if budget_b else None
            conn.execute("""INSERT INTO clients (full_name, nickname, phone, demand_type, budget_max, status)
                VALUES (?, ?, ?, ?, ?, 'active')""",
                (self.name_input.text, self.nickname_input.text, self.phone_input.text, type_key, budget))
            conn.commit()
            conn.close()
            self.status_label.text = fa("مشتری ذخیره شد")
            self.status_label.color = MINT
            self.name_input.text = ""
            self.nickname_input.text = ""
            self.phone_input.text = ""
            self.budget_input.text = ""
        except Exception as e:
            self.status_label.text = fa("خطا: ") + str(e)
            self.status_label.color = DANGER


class AddFromDivarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("افزودن از دیوار"), font_size=sp(18), bold=True, bg_color=CORAL, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        info = Label(text=fa("اطلاعات آگهی را از پنل دیوارت کپی کن:"),
            size_hint_y=None, height=dp(40), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12))
        layout.add_widget(info)
        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=dp(8))
        form.bind(minimum_height=form.setter('height'))
        def add_field(label_text, hint):
            form.add_widget(Label(text=fa(label_text), size_hint_y=None, height=dp(22), font_name=FONT_NAME, color=PINK_LIGHT, font_size=sp(12)))
            inp = TextInput(hint_text=fa(hint), size_hint_y=None, height=dp(42),
                background_color=BG_CARD, foreground_color=TEXT_PRIMARY,
                font_name=FONT_NAME, halign='right', multiline=False, cursor_color=PINK)
            form.add_widget(inp)
            return inp
        self.link_input = add_field("لینک آگهی", "https://divar.ir/...")
        self.title_input = add_field("عنوان آگهی", "کلنگی ۳۲۰ متری")
        self.price_input = add_field("قیمت (میلیارد)", "120")
        self.area_input = add_field("متراژ", "320")
        self.street_input = add_field("خیابان", "خیابان ناهید")
        self.owner_input = add_field("نام مالک", "")
        self.phone_input = add_field("تلفن مالک", "")
        scroll.add_widget(form)
        layout.add_widget(scroll)
        btn_check = Button(text=fa("بررسی و تطبیق"), font_size=sp(16), font_name=FONT_NAME, bold=True,
            size_hint_y=None, height=dp(55), background_color=CORAL, background_normal='')
        btn_check.bind(on_press=lambda x: self.check_and_add())
        layout.add_widget(btn_check)
        self.result_label = Label(text="", size_hint_y=None, height=dp(80), font_name=FONT_NAME, color=TEXT_PRIMARY)
        layout.add_widget(self.result_label)
        self.add_widget(layout)
    
    def check_and_add(self):
        conn = get_db()
        if not conn:
            return
        area = float(self.area_input.text) if self.area_input.text else None
        price_b = float(self.price_input.text) if self.price_input.text else None
        price = price_b * 1e9 if price_b else None
        street = self.street_input.text
        similar = []
        if street:
            similar = conn.execute("SELECT * FROM properties WHERE status='active' AND street LIKE ?", ("%" + street + "%",)).fetchall()
        if similar:
            msg = "⚠️ مشابه " + str(len(similar)) + " فایل مال توست:\n"
            for s in similar[:3]:
                msg += "• " + (s['street'] or '') + " - " + str(int(s['land_area'] or 0)) + " متر\n"
            msg += "\nممکنه همکار داره فایل تو رو آگهی می‌کنه!"
        else:
            msg = "✅ این آگهی جدیده."
        self.result_label.text = fa(msg)
        try:
            conn.execute("""INSERT INTO properties 
                (property_type, neighborhood, street, land_area, total_price, owner_name, owner_phone, notes, status)
                VALUES ('old_house', 'zafaranieh', ?, ?, ?, ?, ?, ?, 'active')""",
                (street, area, price, self.owner_input.text, self.phone_input.text, "دیوار - " + self.link_input.text))
            conn.commit()
        except:
            pass
        conn.close()


class MatchesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        btn_back = Button(text=fa("بازگشت"), size_hint_x=None, width=dp(90),
            background_color=PURPLE, background_normal='', font_name=FONT_NAME, font_size=sp(14))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        title = ColoredLabel(text=fa("موتور تطبیق"), font_size=sp(18), bold=True, bg_color=PURPLE, color=TEXT_PRIMARY)
        header.add_widget(title)
        layout.add_widget(header)
        self.client_spinner = Spinner(text=fa("انتخاب مشتری"), values=[],
            size_hint_y=None, height=dp(50), background_color=PINK, font_name=FONT_NAME)
        self.client_spinner.bind(text=self.on_client_selected)
        layout.add_widget(self.client_spinner)
        scroll = ScrollView()
        self.results_layout = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=dp(5))
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        scroll.add_widget(self.results_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)
        self.clients_map = {}
    
    def on_enter(self):
        conn = get_db()
        if not conn:
            return
        clients = conn.execute("SELECT id, full_name, phone FROM clients WHERE status='active'").fetchall()
        conn.close()
        self.clients_map = {}
        vals = []
        for c in clients:
            key = c['full_name'] + " — " + c['phone']
            self.clients_map[key] = c['id']
            vals.append(key)
        self.client_spinner.values = [fa(v) for v in vals]
    
    def on_client_selected(self, spinner, text):
        self.results_layout.clear_widgets()
        cid = None
        for k, v in self.clients_map.items():
            if fa(k) == text:
                cid = v
                break
        if not cid:
            return
        conn = get_db()
        if not conn:
            return
        client = conn.execute("SELECT * FROM clients WHERE id=?", (cid,)).fetchone()
        props = conn.execute("SELECT * FROM properties WHERE status='active'").fetchall()
        conn.close()
        if not client:
            return
        client = dict(client)
        results = []
        for p in props:
            p = dict(p)
            score = 0
            if p.get('property_type') == client.get('demand_type'):
                score += 30
            if p.get('total_price') and client.get('budget_max'):
                if p['total_price'] <= client['budget_max']:
                    score += 30
                elif p['total_price'] <= client['budget_max'] * 1.2:
                    score += 15
            if score > 0:
                results.append((p, score))
        results.sort(key=lambda x: x[1], reverse=True)
        if not results:
            self.results_layout.add_widget(Label(text=fa("فایلی مناسب پیدا نشد"), color=TEXT_SECONDARY, font_name=FONT_NAME, size_hint_y=None, height=dp(50)))
            return
        for p, score in results[:20]:
            icon = "🟢" if score >= 60 else "🟡" if score >= 40 else "🔴"
            text = icon + " " + str(score) + " — " + (p.get('street') or '') + " — " + PROPERTY_TYPES.get(p['property_type'], '')
            btn = Button(text=fa(text), size_hint_y=None, height=dp(70),
                background_color=BG_CARD, background_normal='', color=TEXT_PRIMARY,
                font_size=sp(13), font_name=FONT_NAME, halign='right')
            self.results_layout.add_widget(btn)


class RealEstateMobileApp(App):
    def build(self):
        self.title = "دستیار املاک"
        Window.clearcolor = BG_DARK
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(PropertiesScreen(name='properties'))
        sm.add_widget(PropertyDetailScreen(name='property_detail'))
        sm.add_widget(EditPropertyScreen(name='edit_property'))
        sm.add_widget(AddPropertyScreen(name='add_property'))
        sm.add_widget(ClientsScreen(name='clients'))
        sm.add_widget(AddClientScreen(name='add_client'))
        sm.add_widget(AddFromDivarScreen(name='add_from_divar'))
        sm.add_widget(MatchesScreen(name='matches'))
        return sm


if __name__ == "__main__":
    RealEstateMobileApp().run()