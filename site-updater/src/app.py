import sys, os, shutil, re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QFileDialog, QMessageBox, QFormLayout, QSpinBox)

class SiteUpdater(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Site Updater")
        self.setGeometry(100, 100, 600, 700)
        # Define paths
        self.console_dir = r"F:\Projects\KARS\consoles"
        self.games_dir = r"F:\Projects\KARS\games"
        self.artwork_dir = r"F:\Projects\KARS\artwork"
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)
        
        # Startup widget (only buttons visible on startup)
        self.startup_widget = QWidget()
        startup_layout = QHBoxLayout()
        self.startup_widget.setLayout(startup_layout)
        add_btn = QPushButton("Add Game")
        update_btn = QPushButton("Update Game")
        delete_btn = QPushButton("Remove Game")
        add_btn.clicked.connect(self.show_add_game)
        update_btn.clicked.connect(self.show_update_game)
        delete_btn.clicked.connect(self.show_remove_game)
        startup_layout.addWidget(add_btn)
        startup_layout.addWidget(update_btn)
        startup_layout.addWidget(delete_btn)
        self.main_layout.addWidget(self.startup_widget)
        
        # Add Game form (reuse existing form)
        self.add_form = QWidget()
        add_form_layout = QFormLayout()
        self.add_form.setLayout(add_form_layout)
        # Console dropdown
        self.add_console_cb = QComboBox()
        consoles = [f for f in os.listdir(self.console_dir) if f.endswith(".html")]
        self.add_console_cb.addItems([os.path.splitext(f)[0] for f in consoles])
        add_form_layout.addRow("Select Console:", self.add_console_cb)
        # Game name
        self.add_game_name_le = QLineEdit()
        add_form_layout.addRow("Game Name:", self.add_game_name_le)
        # Artwork picker
        hbox = QHBoxLayout()
        self.add_artwork_le = QLineEdit()
        self.add_artwork_btn = QPushButton("Browse...")
        self.add_artwork_btn.clicked.connect(self.browse_artwork)
        hbox.addWidget(self.add_artwork_le)
        hbox.addWidget(self.add_artwork_btn)
        add_form_layout.addRow("Artwork:", hbox)
        # Mirrors count
        self.add_mirror_count_sb = QSpinBox()
        self.add_mirror_count_sb.setRange(1, 5)
        self.add_mirror_count_sb.valueChanged.connect(lambda count: self.update_mirror_fields(count, form="add"))
        add_form_layout.addRow("Number of Download Mirrors:", self.add_mirror_count_sb)
        # Mirrors container
        self.add_mirror_fields = []
        self.add_mirrors_layout = QVBoxLayout()
        add_form_layout.addRow("Download Mirrors:", self.add_mirrors_layout)
        self.update_mirror_fields(self.add_mirror_count_sb.value(), form="add")
        # Complete button
        self.add_complete_btn = QPushButton("Complete")
        self.add_complete_btn.setStyleSheet("background-color: blue; color: white;")
        self.add_complete_btn.clicked.connect(self.complete_add)
        add_form_layout.addRow("", self.add_complete_btn)
        self.main_layout.addWidget(self.add_form)
        self.add_form.hide()
        
        # Update Game form
        self.update_form = QWidget()
        update_form_layout = QVBoxLayout()
        self.update_form.setLayout(update_form_layout)
        # Dropdowns for console and game selection
        top_update = QHBoxLayout()
        self.update_console_cb = QComboBox()
        self.update_console_cb.addItems([os.path.splitext(f)[0] for f in os.listdir(self.console_dir) if f.endswith(".html")])
        self.update_console_cb.currentTextChanged.connect(self.load_game_list)
        self.update_game_cb = QComboBox()
        top_update.addWidget(QLabel("Console:"))
        top_update.addWidget(self.update_console_cb)
        top_update.addWidget(QLabel("Game:"))
        top_update.addWidget(self.update_game_cb)
        load_btn = QPushButton("Load Game")
        load_btn.clicked.connect(self.load_update_game)
        top_update.addWidget(load_btn)
        update_form_layout.addLayout(top_update)
        # Editable fields (similar to add form but without artwork)
        form_update = QFormLayout()
        self.upd_game_name_le = QLineEdit()
        form_update.addRow("Game Name:", self.upd_game_name_le)
        # Mirrors count for update
        self.upd_mirror_count_sb = QSpinBox()
        self.upd_mirror_count_sb.setRange(1, 5)
        self.upd_mirror_count_sb.valueChanged.connect(lambda count: self.update_mirror_fields(count, form="upd"))
        form_update.addRow("Number of Download Mirrors:", self.upd_mirror_count_sb)
        # Mirrors container for update
        self.upd_mirror_fields = []
        self.upd_mirrors_layout = QVBoxLayout()
        form_update.addRow("Download Mirrors:", self.upd_mirrors_layout)
        self.update_mirror_fields(self.upd_mirror_count_sb.value(), form="upd")
        # Complete Update button
        self.upd_complete_btn = QPushButton("Complete Update")
        self.upd_complete_btn.setStyleSheet("background-color: blue; color: white;")
        self.upd_complete_btn.clicked.connect(self.complete_update)
        form_update.addRow("", self.upd_complete_btn)
        update_form_layout.addLayout(form_update)
        self.main_layout.addWidget(self.update_form)
        self.update_form.hide()
        
        # Remove Game form
        self.remove_form = QWidget()
        remove_form_layout = QHBoxLayout()
        self.remove_form.setLayout(remove_form_layout)
        self.rem_console_cb = QComboBox()
        self.rem_console_cb.addItems([os.path.splitext(f)[0] for f in os.listdir(self.console_dir) if f.endswith(".html")])
        self.rem_console_cb.currentTextChanged.connect(self.load_remove_game_list)
        self.rem_game_cb = QComboBox()
        remove_form_layout.addWidget(QLabel("Console:"))
        remove_form_layout.addWidget(self.rem_console_cb)
        remove_form_layout.addWidget(QLabel("Game:"))
        remove_form_layout.addWidget(self.rem_game_cb)
        del_btn = QPushButton("Delete Game")
        del_btn.clicked.connect(self.delete_game)
        remove_form_layout.addWidget(del_btn)
        self.main_layout.addWidget(self.remove_form)
        self.remove_form.hide()

    def show_add_game(self):
        self.startup_widget.hide()
        self.update_form.hide()
        self.remove_form.hide()
        self.add_form.show()

    def show_update_game(self):
        self.startup_widget.hide()
        self.add_form.hide()
        self.remove_form.hide()
        self.update_form.show()
        # Load game list for selected console
        self.load_game_list(self.update_console_cb.currentText())
        
    def show_remove_game(self):
        self.startup_widget.hide()
        self.add_form.hide()
        self.update_form.hide()
        self.remove_form.show()
        self.load_remove_game_list(self.rem_console_cb.currentText())

    def load_game_list(self, console):
        # List files in games/(console)
        self.update_game_cb.clear()
        game_folder = os.path.join(self.games_dir, console)
        if os.path.isdir(game_folder):
            games = [os.path.splitext(f)[0] for f in os.listdir(game_folder) if f.endswith(".html")]
            self.update_game_cb.addItems(games)

    def load_remove_game_list(self, console):
        self.rem_game_cb.clear()
        game_folder = os.path.join(self.games_dir, console)
        if os.path.isdir(game_folder):
            games = [os.path.splitext(f)[0] for f in os.listdir(game_folder) if f.endswith(".html")]
            self.rem_game_cb.addItems(games)

    def load_update_game(self):
        console = self.update_console_cb.currentText()
        game = self.update_game_cb.currentText()
        if not game:
            QMessageBox.warning(self, "Error", "No game selected.")
            return
        game_page_path = os.path.join(self.games_dir, console, f"{game}.html")
        try:
            with open(game_page_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load game file: {e}")
            return
        # Prefill the game name
        self.upd_game_name_le.setText(game)
        # Use regex to extract mirror data from list items
        import re
        mirrors = re.findall(r'<li><a href="([^"]+)" target="_blank">([^<]+)</a></li>', content)
        # Set the mirror count & update mirror fields
        count = len(mirrors) if mirrors else 1
        self.upd_mirror_count_sb.setValue(count)
        self.update_mirror_fields(count, form="upd")
        # Prefill each mirror field: mirror name (group 2) and link (group 1)
        for i, (mlink, mname) in enumerate(mirrors):
            if i < len(self.upd_mirror_fields):
                self.upd_mirror_fields[i][0].setText(mname)
                self.upd_mirror_fields[i][1].setText(mlink)
        QMessageBox.information(self, "Loaded", f"Loaded data for '{game}'.")

    def complete_add(self):
        # ...similar to complete_update() previously used for adding games...
        console = self.add_console_cb.currentText()
        game_name = self.add_game_name_le.text().strip()
        artwork_path = self.add_artwork_le.text().strip()
        if not (console and game_name and artwork_path):
            QMessageBox.warning(self, "Missing Info", "Please fill all required fields.")
            return
        mirrors = []
        for name_field, link_field in self.add_mirror_fields:
            mirror_name = name_field.text().strip()
            mirror_link = link_field.text().strip()
            if mirror_name and mirror_link:
                mirrors.append((mirror_name, mirror_link))
        info = f"Console: {console}\nGame Name: {game_name}\nArtwork: {artwork_path}\nMirrors:\n"
        for i, (mname, mlink) in enumerate(mirrors, start=1):
            info += f"  {i}. {mname}: {mlink}\n"
        reply = QMessageBox.question(self, "Confirm", f"Are You Sure?\n\n{info}", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        new_artwork_path = os.path.join(self.artwork_dir, f"{game_name}.png")
        shutil.copy(artwork_path, new_artwork_path)
        game_console_folder = os.path.join(self.games_dir, console)
        os.makedirs(game_console_folder, exist_ok=True)
        game_page_path = os.path.join(game_console_folder, f"{game_name}.html")
        game_page_content = self.generate_game_page(game_name, mirrors)
        with open(game_page_path, "w", encoding="utf-8") as f:
            f.write(game_page_content)
        console_path = os.path.join(self.console_dir, f"{console}.html")
        self.update_console_page(console_path, console, game_name)
        QMessageBox.information(self, "Success", "Game added successfully!")
        self.reset_to_startup()

    def complete_update(self):
        # Similar to add but update existing game data using the update form fields.
        console = self.update_console_cb.currentText()
        old_game = self.update_game_cb.currentText()
        new_game_name = self.upd_game_name_le.text().strip()
        if not (console and old_game and new_game_name):
            QMessageBox.warning(self, "Missing Info", "Please fill required fields.")
            return
        mirrors = []
        for name_field, link_field in self.upd_mirror_fields:
            mirror_name = name_field.text().strip()
            mirror_link = link_field.text().strip()
            if mirror_name and mirror_link:
                mirrors.append((mirror_name, mirror_link))
        # Overwrite the game HTML file with updated data
        game_console_folder = os.path.join(self.games_dir, console)
        game_page_path = os.path.join(game_console_folder, f"{old_game}.html")
        new_game_page_path = os.path.join(game_console_folder, f"{new_game_name}.html")
        game_page_content = self.generate_game_page(new_game_name, mirrors)
        with open(game_page_path, "w", encoding="utf-8") as f:
            f.write(game_page_content)
        # Rename file if game name changed
        if old_game != new_game_name:
            os.rename(game_page_path, new_game_page_path)
        QMessageBox.information(self, "Success", "Game updated successfully!")
        self.reset_to_startup()

    def delete_game(self):
        console = self.rem_console_cb.currentText()
        game = self.rem_game_cb.currentText()
        if not game:
            QMessageBox.warning(self, "Error", "No game selected.")
            return
        reply = QMessageBox.question(self, "Confirm", f"Are you sure you want to delete '{game}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        # Delete game HTML file
        game_page_path = os.path.join(self.games_dir, console, f"{game}.html")
        if os.path.exists(game_page_path):
            os.remove(game_page_path)
        # Delete artwork image
        artwork_path = os.path.join(self.artwork_dir, f"{game}.png")
        if os.path.exists(artwork_path):
            os.remove(artwork_path)
        # Remove reference from console page
        console_path = os.path.join(self.console_dir, f"{console}.html")
        with open(console_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Assume game item block contains the game name
        new_content = re.sub(rf'\s*<div class="game-item".*?{re.escape(game)}.*?</div>\s*', '', content, flags=re.DOTALL)
        with open(console_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        QMessageBox.information(self, "Deleted", f"'{game}' deleted successfully!")
        self.reset_to_startup()

    def update_mirror_fields(self, count, form="add"):
        # form parameter: "add" or "upd"
        if form == "add":
            layout = self.add_mirrors_layout
            fields = self.add_mirror_fields
        else:
            layout = self.upd_mirrors_layout
            fields = self.upd_mirror_fields
        # Clear existing mirror widgets
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        fields.clear()
        for i in range(count):
            hbox = QHBoxLayout()
            mirror_name = QLineEdit()
            mirror_link = QLineEdit()
            hbox.addWidget(QLabel(f"Mirror {i+1} Name:"))
            hbox.addWidget(mirror_name)
            hbox.addWidget(QLabel("Link:"))
            hbox.addWidget(mirror_link)
            container = QWidget()
            container.setLayout(hbox)
            layout.addWidget(container)
            fields.append((mirror_name, mirror_link))

    def browse_artwork(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Artwork", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Set for both add form (update form does not change image)
            self.add_artwork_le.setText(file_path)

    def generate_game_page(self, game_name, mirrors):
        mirror_list_html = ""
        for mname, mlink in mirrors:
            mirror_list_html += f'				<li><a href="{mlink}" target="_blank">{mname}</a></li>\n'
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>{game_name} - KARS</title>
	<link rel="stylesheet" href="../../style.css">
	<link rel="icon" href="../../img/favicon.ico">
</head>
<body>
	<div id="sideMenu" class="sidemenu">
		<button class="closebtn" onclick="toggleMenu()">×</button>
		<a href="../../consoles/nintendo-switch.html">Nintendo Switch</a>
		<a href="../../consoles/playstation-4.html">PlayStation 4</a>
		<a href="../../consoles/xbox-one.html">Xbox One</a>
	</div>
	<header>
		<div class="header-left">
			<button class="menu-btn" onclick="toggleMenu()">☰</button>
		</div>
		<h1><a href="../../index.html" style="color:inherit; text-decoration:none;">KARS</a></h1>
	</header>
	<div class="game-detail">
		<h2>{game_name}</h2>
		<div class="game-artwork-detail">
			<img src="../../artwork/{game_name}.png" alt="{game_name} Artwork">
		</div>
		<div class="download-section">
			<h3>Download Mirrors</h3>
			<ul>
{mirror_list_html}			</ul>
		</div>
	</div>
	<script src="../../script.js"></script>
</body>
</html>"""
        return content

    def update_console_page(self, console_path, console, game_name):
        with open(console_path, "r", encoding="utf-8") as f:
            content = f.read()
        new_game_item = f'''			<div class="game-item" onclick="location.href='../games/{console}/{game_name}.html'">
				<div class="game-artwork-container">
					<img src="../artwork/{game_name}.png" alt="{game_name}">
				</div>
				<h3>{game_name}</h3>
			</div>
'''
        marker = '<div id="gamesList">'
        idx = content.find(marker)
        if idx == -1:
            return
        idx_end = content.find('</div>', idx)
        if idx_end == -1:
            return
        new_content = content[:idx_end] + new_game_item + content[idx_end:]
        with open(console_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    def reset_to_startup(self):
        # Clear forms and show startup buttons again
        self.add_form.hide()
        self.update_form.hide()
        self.remove_form.hide()
        self.startup_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiteUpdater()
    window.show()
    sys.exit(app.exec_())
