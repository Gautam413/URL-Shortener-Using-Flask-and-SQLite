# URL-Shortener-Using-Flask-and-SQLite

This is a lightweight, privacy-aware URL shortener built using **Flask**, **SQLite**, and **Flask-Mail**, designed for secure access control through email verification.

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git (optional, for cloning)

### Clone the repository

```bash
git clone https://github.com/Gautam413/URL-Shortener-Using-Flask-and-SQLite.git
cd URL-Shortener-Using-Flask-and-SQLite
```

### Create and activate virtual environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate
```

```bash
# On Linux/macOS
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set up

Create a file named `config.py` in the root directory and add your email credentials:

```python
class Config:
    DATABASE = "database.db"

    MAIL_SERVER = "smtp.gmail.com"  # or "smtp.hostinger.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "youremail"
    MAIL_PASSWORD = "yourpassword"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
```

### Run the application

```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000/`

---

## License
This project is licensed under the MIT License.
