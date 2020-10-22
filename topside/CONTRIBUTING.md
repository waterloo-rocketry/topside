# Contributing
Welcome to Topside! To get started, follow these steps:

1. Clone the repo.
    * If you have git configured with SSH, run `git clone git@github.com:waterloo-rocketry/topside.git`
    * If you don't have git configured with SSH (or you're not sure what that means), run `git clone https://github.com/waterloo-rocketry/topside.git`
2. Enter the newly-cloned repo with `cd topside`
3. Run `pip install wheel`, which will help install the rest of the packages more quickly.
4. Install Python dependencies with `pip install -r requirements.txt`. If you get a permissions error, try `pip install -U -r requirements.txt` instead.
5. Install the Topside library locally with `pip install -e .`. Don't forget the `.`! This will allow you to import Topside from other Python scripts or files.

You should now be ready to start developing!

* To run unit tests: `pytest`
* To launch the Topside application: `python main.py`
* To build a standalone application: `./tools/build_pyinstaller.sh`. The resulting executable will be at `dist/Topside/Topside.exe` (on Windows).

# Style guide
If you'd like to contribute to Topside, please take a moment to read through this style guide. Otherwise, happy devving :)

### Python
We generally conform to [PEP8](https://pep8.org/) guidelines for how we format our Python code. The repository contains a custom formatting script (`tools/format.sh`) - you should run this optionally before commits, and definitely before creating pull requests and/or merging to master.

When adding code, make sure to add unit tests to match! It's generally a good idea to run the full suite of unit tests before creating a PR (which can be done with the `pytest` command). If you don't, CI will run it for you, but it'll take much longer. This generally shouldn't be an issue, but please don't merge to master until the CI checks complete. We'll get a Slack notification if a failing build makes it to master, though, so don't be too scared of breaking things. They're always fixable :).

### Qt/QML
Our QML code follows standard guidelines provided [here](https://doc.qt.io/qt-5/qml-codingconventions.html).

### Git
Generally, commit messages should follow guidelines laid out by Chris Beams [here](https://chris.beams.io/posts/git-commit/). Additionally,
* Pull requests should be squashed and merged to be added as commits to master. If the PR pertains to code inside the `topside/` directory (_not_ the main repo), the commit message should be of the form `<subsystem>: <Commit message>`, where `subsystem` is the folder that the code is relevant to. `Commit message` is the commit message as normal, following regular message guidelines (capital first letter, no period, etc). 

    An example commit message could be `plumbing: Add solving algorithm`, for a PR that affects code inside the `topside/plumbing/` directory.
    Commit messages for code outside the `topside/` directory don't need to follow this format. This is mainly to ensure that changes are immediately recognizable reading commit messages from the top level of the repository.
* Version increments are done as standalone PRs. The commit message takes the form `Designate <version> release` (where `version` is the version), for example `Designate 0.2.0 release`. We add GitHub tags on these commits as well (for example, `v0.2.0`); these are visible under the `releases` tab. 

    The workflow for incrementing a version is to upload to TestPyPi, create the PR, merge to master, then upload to actual PyPi. Steps for doing so are located [here](https://packaging.python.org/tutorials/packaging-projects/).
