# Backend for the badge tracker

Handles the badge counting process, saving the cursor, the badge count

## API Endpoints 
### List of endpoints available on the [docs](https://sbc.gacek.wtf/docs)

* **GET** /api/progress/{user}
	* Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict]:
			* counting [bool] - Whether we are still counting user's badges or not
			* count [int] - Currently counted amount of badges

* **GET** /api/rank/{user}
	*  Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* rank [int] - The rank displayed as a integer

* **POST** /api/qc/{user}/{key}
	*  Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **POST** /api/blacklist/{user}/{key}
	* Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **DELETE** /api/unblacklist/{user}/{key}
	* Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **DELETE** /api/clearbadges/{user}/{key}
	* Params:
		* user - Roblox user ID
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **DELETE** /api/cleardb/{key}
	* Params:
		* key - API key set in the `.env` file
	* Returns:
		* success [bool] - Whether the request was successful or not
		* message [str] - A user-friendly message

* **GET** /api/leaderboard
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [list] - The leaderboard

* **GET** /api/first/{user}
	* Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict] - The first badge gotten by the user, provided in a Roblox-like format

* **GET** /api/last/{user}
	* Params:
		* user - Roblox user ID
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict] - The last badge gotten by the user, provided in a Roblox-like format

* **GET** /api/stats
	* Returns:
		* success [bool] - Whether the request was successful or not
		* data [dict]:
			* users [int] - Currently registered users
			* counting [int] - Users that are currently having their badges counted
			* badges [int] - Badges counted
