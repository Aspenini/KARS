// Toggle side menu
function toggleMenu() {
	var menu = document.getElementById("sideMenu");
	if (menu.style.width === "250px") {
		menu.style.width = "0";
	} else {
		menu.style.width = "250px";
	}
}

// Filter games list on Nintendo Switch page
function filterGames() {
	const input = document.getElementById("searchInput");
	if (!input) return;
	const filter = input.value.toUpperCase();
	const gameItems = document.getElementsByClassName("game-item");
	
	for (let i = 0; i < gameItems.length; i++) {
		let title = gameItems[i].getElementsByTagName("h3")[0];
		if (title.innerText.toUpperCase().indexOf(filter) > -1) {
			gameItems[i].style.display = "";
		} else {
			gameItems[i].style.display = "none";
		}
	}
}
