# Shree Jaljala Secondary School Web Portal

Official Web Application for Shree Jaljala Secondary School (Panchkhapan-7, Bihibare, Sankhuwasabha, Nepal).

---

## 🚀 How to Run Locally in VS Code

You can run this project locally on your machine using **Method 1 (Node.js)** or **Method 2 (Python Django)**.

---

### Option 1: Run with Node.js (Recommended & Easiest)

This project includes a Node.js web server (`server.js`) that immediately renders the templates and static assets without requiring database configuration.

#### Prerequisites:
- [Node.js](https://nodejs.org/) (Version 18 or higher)
- VS Code

#### Steps:
1. **Extract the downloaded ZIP file** to a folder on your computer.
2. **Open the folder in VS Code**:
   - Open VS Code → `File` → `Open Folder...` → Select the extracted project folder.
3. **Open Terminal in VS Code**:
   - Press `Ctrl + ~` (or go to `Terminal` -> `New Terminal` in top menu).
4. **Install Dependencies**:
   ```bash
   npm install
   ```
5. **Start the local server**:
   ```bash
   npm run dev
   ```
6. **Open in Browser**:
   - Click the link shown in terminal or open: **`http://localhost:3000`**

---

### Option 2: Run with Python & Django

If you want to run the full Python Django application with Django views and models:

#### Prerequisites:
- [Python 3.10+](https://www.python.org/)
- VS Code

#### Steps:
1. **Extract the ZIP file** and open the project folder in VS Code.
2. **Open Terminal in VS Code** (`Ctrl + ~`).
3. **Create a Virtual Environment** (Optional but recommended):
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - On Mac / Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
4. **Install Python Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run Migrations** (To set up the SQLite database):
   ```bash
   python manage.py migrate
   ```
6. **Start Django Development Server**:
   ```bash
   python manage.py runserver
   ```
7. **Open in Browser**:
   - Open **`http://127.0.0.1:8000/`** or **`http://localhost:8000`** in your web browser.

---

## 🛠️ Project Structure
- `/static/` - CSS styles, JavaScript files, and school photos/emblems
- `/templates/` - HTML layout templates (Header, Footer, Preloader, Pages)
- `/website/` - Django application views and template routing
- `/school_project/` - Django project settings and URLs
- `server.js` - Express / Node.js backend server

