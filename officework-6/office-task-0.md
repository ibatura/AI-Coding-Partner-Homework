In order to run it you need to install GitHub CLI:

1. **Install GitHub CLI:**
	```sh
	brew install gh
	```
	_Authorize it after installation._

2. **Authenticate GitHub CLI:**
	```sh
	gh auth login
	```

3. **Initialize Claude:**
	```sh
	claude /init
	```
	_This will create a `claude.md` file for this repository._

4. **Install Claude GitHub App:**
	```sh
	/install-github-app