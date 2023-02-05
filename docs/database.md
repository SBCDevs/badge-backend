# Database setup

## Install [SurrealDB](https://surrealdb.com/)

### Docker
```sh
docker run --rm -p 8000:8000 surrealdb/surrealdb:latest start
```
---
### macOS
```sh
brew install surrealdb/tap/surreal
```
---
### Linux
```sh
curl -sSf https://install.surrealdb.com | sh
```
---
### Windows
```bash
iwr https://windows.surrealdb.com -useb | iex
```

## Start the database

#### ⚠️ If you're using Docker the database is already started ⚠️ 

```sh
surreal start --log trace --user ${USERNAME} --pass ${PASSWORD} memory
```
