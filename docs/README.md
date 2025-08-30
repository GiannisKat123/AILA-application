The documentation is based on Sphinx, the documentation sources are in the source folder. This documentation is automatically built from the source code of the project and deployed to GitHub Pages by GitHub Actions whenever the main branch is pushed to.

To create sphinx documentation you first need to run:

```bash
sphinx-quickstart
```
This will kickstart a sphinx project. After setting some initial parameters, a docs folder will be created

To create the documentation for the backend run the following:

```bash
sphinx-apidoc -o docs\source\backend\api backend
```

To create the documentation for the frontend run the following:
```bash
cd frontend
npm run docs:api
```
make sure you have also downloaded the typedoc library via npm

Move the folder to the docs folder under the name frontend 

To craete the documentation for the both folders use the following line:
```bash
cd docs
sphinx-build -b html source build
```
