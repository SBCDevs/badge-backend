# Backend for the badge tracker

Handles the badge counting process, saving the cursor, the badge count

## Setup the repository for local development

* [Download GitHub CLI](https://cli.github.com/)
* [Download Git](https://git-scm.com/downloads)
* [Download Python 3.8.10](https://www.python.org/downloads/release/python-3810/) (Scroll down and you should be able to see the download links)
* Authenticate Git with GitHub CLI (Use the `gh auth login` and it should guide you thru the process)
* Clone the repo with `git clone https://github.com/SBCDevs/badge-backend`
* Change the directory into the folder with `cd badge-backend`
* Type in `pip install -r requirements.txt` to install all the needed packages
* Type in `cp .env.example .env` and edit the `.env` file to suit your needs
* Start the server with `python main.py`

## API Endpoints 
### List of endpoints available on the [docs](https://sbc.gacek.wtf/docs)

* **GET** /api/progress/{user} - Gets the progress on wheter a user is being counted or not, with which method and whats their current badge count
	* Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict]:
			* counting [bool] - Whether we are still counting user's badges or not
			* count [int] - Currently counted amount of badges

* **GET** /api/rank/{user} - Gets the user's leaderboard rank
	*  Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* rank [int] - The rank displayed as a integer

* **POST** /api/quickcount/{user} - Quick counts user's badges
	*  Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **POST** /api/count/{user} - Counts user's badges (Ignores the cursor)
	*  Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **POST** /api/blacklist/{user}?key={key} - Blacklists a user from being counted
	* Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **DELETE** /api/unblacklist/{user}?key={key} - Unblacklists a user from being counted
	* Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **DELETE** /api/clearbadges/{user}?key={key} - Clears user's badges
	* Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **DELETE** /api/cleardb?key={key} - Clears the whole storage and starts recounting everyone
	* Params:
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **GET** /api/leaderboard - Gets the whole storage and creates a leaderboard out of it
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [list] - The leaderboard

* **GET** /api/first/{user} - Gets a user's first badge
	* Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict] - The first badge gotten by the user, provided in a Roblox-like format

* **GET** /api/last/{user} - Gets a user's last badge
	* Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict] - The last badge gotten by the user, provided in a Roblox-like format

* **GET** /api/stats - Returns the API stats
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict]:
			* users [int] - Currently registered users
			* counting [int] - Users that are currently having their badges counted
			* badges [int] - Badges counted
