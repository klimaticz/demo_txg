# Fiverr Project

How do you set up the project?

1. Install Python 3.8 or above if not available
2. Create virtual environment name env in the project folder: `python -m venv env`
3. Move to the project folder and activate the virtual environment :
   - in Mac and Linux: source env/bin/activate
   - in Windows: run the activate.bat file which is inside \env\Scripts folder by running `env\Scripts\activate`
4. Install required libraries: `pip3 install -r requirements.txt`
5. After stopping the project, deactivate the virtual environment: deactivate

Run project

1. `streamlit run home.py`

Save Dependencies

1. Run `pip freeze > requirements.txt` after installing any pip package
