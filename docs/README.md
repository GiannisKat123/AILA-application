The documentation is based on Sphinx, the documentation sources are in the source folder. This documentation is automatically built from the source code of the project and deployed to GitHub Pages by GitHub Actions whenever the main branch is pushed to.

To create sphinx documentation you first need to install sphinx in your environment:

```bash
pip install sphinx
```

Then create a docs directory by:

```bash
mkdir docs'
cd docs
```

And run the following:
```bash
sphinx-quickstart
```
This will kickstart a sphinx project in the docs directory. After setting some initial parameters, the project will be initialized. 
In the docs folder you will see 2 files and 2 directories, namely:

-) Makefile
-) make.bat
-) source dir
-) build dir

In the **source** directory you can define different configurations and the write what you want to be displayed in the documentation page
In the **build** directory there will be the html files that will be generated from the source directory. These files will be used for the creation of the documentation page.

## To replicate our documentation 

1) Create two folders in the docs/source directory
  -) backend folder
  -) frontend folder

  To do that write the following while in the root directory:
  ```bash
  cd docs/source
  mkdir backend
  mkdir frontend
  cd ..
  ```
2) Backend Documentation

  To create the documentation for the backend return to root and run the following:
  ```bash
  sphinx-apidoc -o docs\source\backend\api backend
  ```
3) Frontend Documentation

  While in the frontend directory run the following command:
  ```bash
  npm i
  npm install typedoc typedoc-plugin-markdown
  ```
  We use this to create a typedoc documentation for the **Typescript + React** code.
  
  To create the documentation for the frontend run the following:
  ```bash
  npm run docs:api
  ```
  A file named docs will be created in the frontend directory. Copy the api folder to the docs/source/frontend directory of our documentation.
  
4) Full Documentation
   To create the full documentation go to the docs directory and run the following:
  ```bash
  sphinx-build -b html source build
  ```

  You can also see the changes you apply in real time using the following command:
  ```bash
  sphinx-autobuild source build/html
  ```

You can apply different styles and ways to automate the documentation process applying different settings in the conf.py file. More info can be found [here](https://www.sphinx-doc.org/en/master/usage/quickstart.html).

You add also text to your pages by creating .md or .rst files in the project
