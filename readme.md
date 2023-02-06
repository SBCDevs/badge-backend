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
* Setup the database (Follow the [documentation](docs/database.md))
* Type in `cp .env.example .env` and edit the `.env` file to suit your needs
* Start the server with `python main.py`
