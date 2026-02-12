# Setting up a Python Virtual Environment and installing Dependencies for the Lab

## Jupyter Notebooks
1. Download & Install VSCode: https://code.visualstudio.com/download
2. Install the ```Jupyter``` and ```Python``` Extensions



---

# Virtual Environments

### Windows (PowerShell):
1. ```python3 -m venv .RAG_lab```

2. ```Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned``` (use this is running scripts is disabled for some reason)

3. ```.\.RAG_lab\Scripts\Activate.ps1```

4. ```python3 -m pip install -U pip```

5. ```python3 -m pip install -r requirements.txt```

##### to turn it off: ```deactivate```


### Streamlit
```streamlit run app\lotr_app.py```

ctrl + C to exit

---
### macOS/Linux

1. ```python3 -m venv .RAG_lab```

2. ```. .RAG_lab/bin/activate```

3. ```python -m pip install -U pip```

4. ```python -m pip install -r requirements.txt```

##### to turn it off: ```deactivate```

### Streamlit
```streamlit run app/lotr_app.py```

ctrl + C to exit



