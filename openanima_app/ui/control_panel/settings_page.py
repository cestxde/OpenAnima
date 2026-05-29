import sys
from pathlib import Path

from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox, QGroupBox, QLabel, QPushButton, 
    QVBoxLayout, QWidget, QComboBox, QHBoxLayout
)

from ...runtime.startup import set_startup_enabled, startup_enabled


def discover_available_languages() -> list[tuple[str, str, str]]:
    """
    Scans i18n directory and returns a list of tuples: 
    (lang_code, display_name, svg_path_str_or_empty)
    """
    i18n_dir = Path(__file__).parent.parent.parent / "i18n"
    
    en_svg = i18n_dir / "en.svg"
    en_icon_path = str(en_svg) if en_svg.exists() else ""
    languages = [("en", "English", en_icon_path)]
    
    if not i18n_dir.exists():
        return languages

    for qm_file in i18n_dir.glob("app_*.qm"):
        lang_code = qm_file.stem.split("_")[1]
        if lang_code == "en":
            continue
            
        locale = QLocale(lang_code)
        native_name = locale.nativeLanguageName().capitalize()
        
        svg_file = i18n_dir / f"{lang_code}.svg"
        icon_path = str(svg_file) if svg_file.exists() else ""
        
        languages.append((lang_code, native_name, icon_path))
        
    return languages


def build_settings_page(panel):
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    title = QLabel("Settings")
    title.setObjectName("SectionTitle")
    subtitle = QLabel("Application preferences, asset location, and recovery actions.")
    subtitle.setObjectName("SubtleLabel")
    subtitle.setWordWrap(True)

    asset_group = QGroupBox("Assets")
    asset_layout = QVBoxLayout(asset_group)
    asset_layout.setContentsMargins(14, 18, 14, 14)
    asset_layout.setSpacing(8)
    panel.settings_asset_root_label = QLabel()
    panel.settings_asset_root_label.setObjectName("SubtleLabel")
    panel.settings_asset_root_label.setWordWrap(True)
    change_root_button = QPushButton("Change Assets Folder")
    change_root_button.clicked.connect(panel.change_asset_root)
    asset_layout.addWidget(panel.settings_asset_root_label)
    asset_layout.addWidget(change_root_button, 0, Qt.AlignLeft)

    app_group = QGroupBox("Startup")
    app_layout = QVBoxLayout(app_group)
    app_layout.setContentsMargins(14, 18, 14, 14)
    panel.startup_check = QCheckBox("Start on system boot")
    panel.startup_check.setEnabled(False)
    if hasattr(panel.startup_check, "setVisible"):
        panel.startup_check.setVisible(sys.platform == "win32")
        if sys.platform == "win32":
            panel.startup_check.setEnabled(True)
            panel.startup_check.setChecked(startup_enabled())
            panel.startup_check.toggled.connect(set_startup_enabled)
    app_layout.addWidget(panel.startup_check)

    lang_layout = QHBoxLayout()
    lang_label = QLabel("Language:")
    
    panel.language_combo = QComboBox()
    panel.language_combo.setMinimumWidth(200)
    
    i18n_dir = Path(__file__).parent.parent.parent / "i18n"
    globe_svg = i18n_dir / "globe.svg"
    
    if globe_svg.exists():
        panel.language_combo.addItem(QIcon(str(globe_svg)), "Auto", "")
    else:
        panel.language_combo.addItem("Auto", "")

    available_langs = discover_available_languages()
    for code, display, icon_path in available_langs:
        if icon_path:
            panel.language_combo.addItem(QIcon(icon_path), display, code)
        else:
            panel.language_combo.addItem(display, code)
        
    from ...runtime.config import load_config_data
    
    try:
        current_lang = load_config_data().get("ui", {}).get("language", "")
    except Exception:
        current_lang = ""
            
    index = panel.language_combo.findData(current_lang)
    if index >= 0:
        panel.language_combo.setCurrentIndex(index)
        
    panel.language_combo.currentIndexChanged.connect(panel.change_language)
    
    lang_layout.addWidget(lang_label)
    lang_layout.addWidget(panel.language_combo, 0, Qt.AlignLeft)
    lang_layout.addStretch()
    app_layout.addLayout(lang_layout)

    recovery_group = QGroupBox("Recovery")
    recovery_layout = QVBoxLayout(recovery_group)
    recovery_layout.setContentsMargins(14, 18, 14, 14)
    recovery_layout.setSpacing(8)

    center_all_button = QPushButton("Center All")
    disable_click_button = QPushButton("Disable Click-Through Mode")
    unlock_all_button = QPushButton("Unlock All")
    panel.prepare_button(center_all_button, 96, "Bring all overlays to center")
    panel.prepare_button(disable_click_button, 172)
    panel.prepare_button(unlock_all_button, 96, "Unlock all overlays")
    center_all_button.clicked.connect(panel.bring_all_overlays_to_center)
    disable_click_button.clicked.connect(panel.disable_click_through_for_all)
    unlock_all_button.clicked.connect(panel.unlock_all_overlays)

    recovery_show_button = QPushButton("Show All")
    recovery_hide_button = QPushButton("Hide All")
    clear_session_button = QPushButton("Clear saved session")
    panel.prepare_button(recovery_show_button, 92, "Show all overlays")
    panel.prepare_button(recovery_hide_button, 92, "Hide all overlays")
    panel.prepare_button(clear_session_button, 140)
    recovery_show_button.clicked.connect(panel.show_all_overlays)
    recovery_hide_button.clicked.connect(panel.hide_all_overlays)
    clear_session_button.clicked.connect(panel.clear_saved_session)
    recovery_layout.addWidget(
        panel.button_flow(
            center_all_button,
            disable_click_button,
            unlock_all_button,
            recovery_show_button,
            recovery_hide_button,
            clear_session_button,
        )
    )

    layout.addWidget(title)
    layout.addWidget(subtitle)
    layout.addWidget(asset_group)
    layout.addWidget(app_group)
    layout.addWidget(recovery_group)
    layout.addStretch()
    panel.add_page("Settings", panel.scroll_page(tab))
