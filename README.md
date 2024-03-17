# PDF AI App

PDF AI App is a question-answering application that allows users to upload documents (PDF or TXT) and ask questions related to the content of those documents.

## Features

- Upload PDF or TXT documents
- Ask questions related to the content of the uploaded documents

## Installation

Clone this repository:

```bash
git clone https://github.com/Wickypolineni/PDF_AI
cd PDF_AI
```

install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

delete the .devcontainer file and create a .env file and put your OPEN_API_KEY in the application:

'''bash
OPEN_API_KEY = "your open api key"
'''

To run the app, simply execute the following command:

```bash
streamlit run streamlit_app.py
```
