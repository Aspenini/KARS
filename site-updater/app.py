import sys, os, shutil
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
        self.layout = QVBoxLayout()
        central.setLayout(self.layout)
        form = QFormLayout()
        self.layout.addLayout(form)
        
        # Console dropdown: scan for HTML files in consoles folder.
        self.console_cb = QComboBox()
        consoles = [f for f in os.listdir(self.console_dir) if f.endswith(".html")]
        self.console_cb.addItems([os.path.splitext(f)[0] for f in consoles])
        form.addRow("Select Console:", self.console_cb)
        
        # Game name
        self.game_name_le = QLineEdit()
        form.addRow("Game Name:", self.game_name_le)
        
        # Artwork file picker with 'Browse' button
        hbox = QHBoxLayout()
        self.artwork_le = QLineEdit()
        self.artwork_btn = QPushButton("Browse...")
        self.artwork_btn.clicked.connect(self.browse_artwork)
        hbox.addWidget(self.artwork_le)
        hbox.addWidget(self.artwork_btn)
        form.addRow("Artwork:", hbox)
        
        # Number of Download Mirrors (1-5)
        self.mirror_count_sb = QSpinBox()
        self.mirror_count_sb.setRange(1, 5)
        self.mirror_count_sb.valueChanged.connect(self.update_mirror_fields)
        form.addRow("Number of Download Mirrors:", self.mirror_count_sb)
        
        # Container for mirror name/link fields
        self.mirror_fields = []
        self.mirrors_layout = QVBoxLayout()
        form.addRow("Download Mirrors:", self.mirrors_layout)
        self.update_mirror_fields(self.mirror_count_sb.value())
        
        # Complete button
        self.complete_btn = QPushButton("Complete")
        self.complete_btn.setStyleSheet("background-color: blue; color: white;")
        self.complete_btn.clicked.connect(self.complete_update)
        self.layout.addWidget(self.complete_btn)

    def update_mirror_fields(self, count):
        # Clear existing mirror fields
        for i in reversed(range(self.mirrors_layout.count())):
            widget = self.mirrors_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.mirror_fields = []
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
            self.mirrors_layout.addWidget(container)
            self.mirror_fields.append((mirror_name, mirror_link))

    def browse_artwork(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Artwork", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.artwork_le.setText(file_path)

    def complete_update(self):
        # Gather user inputs
        console = self.console_cb.currentText()
        game_name = self.game_name_le.text().strip()
        artwork_path = self.artwork_le.text().strip()
        if not (console and game_name and artwork_path):
            QMessageBox.warning(self, "Missing Info", "Please fill all required fields.")
            return
        mirrors = []
        for name_field, link_field in self.mirror_fields:
            mirror_name = name_field.text().strip()
            mirror_link = link_field.text().strip()
            if mirror_name and mirror_link:
                mirrors.append((mirror_name, mirror_link))
        # Show confirmation dialog
        info = f"Console: {console}\nGame Name: {game_name}\nArtwork: {artwork_path}\nMirrors:\n"
        for i, (mname, mlink) in enumerate(mirrors, start=1):
            info += f"  {i}. {mname}: {mlink}\n"
        reply = QMessageBox.question(self, "Confirm", f"Are You Sure?\n\n{info}", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        # Copy artwork to artwork folder and rename it as game name.png
        new_artwork_path = os.path.join(self.artwork_dir, f"{game_name}.png")
        shutil.copy(artwork_path, new_artwork_path)
        # Create game page under games/(console)/(game_name).html
        game_console_folder = os.path.join(self.games_dir, console)
        os.makedirs(game_console_folder, exist_ok=True)
        game_page_path = os.path.join(game_console_folder, f"{game_name}.html")
        game_page_content = self.generate_game_page(game_name, mirrors)
        with open(game_page_path, "w", encoding="utf-8") as f:
            f.write(game_page_content)
        # Update console page: insert new game item in the games list with updated path
        console_path = os.path.join(self.console_dir, f"{console}.html")
        self.update_console_page(console_path, console, game_name)
        QMessageBox.information(self, "Success", "Game added successfully!")

    def generate_game_page(self, game_name, mirrors):
        # Generate the game page's HTML content with updated relative paths (two levels up)
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
        # Insert a new game item into the console page's games list with updated link
        with open(console_path, "r", encoding="utf-8") as f:
            content = f.read()
        new_game_item = f'''			<div class="game-item" onclick="location.href='../games/{console}/{game_name}.html'">
				<div class="game-artwork-container">
					<img src="../artwork/{game_name}.png" alt="{game_name}">
				</div>
				<h3>{game_name}</h3>
			</div>
'''
        # Locate the insertion point (before the closing tag of the #gamesList container)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiteUpdater()
    window.show()
    sys.exit(app.exec_())
