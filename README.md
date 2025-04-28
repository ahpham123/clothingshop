
## About Sploosh

text here

## Deployed at
[https://clothingshop-psi.vercel.app/](https://clothingshop-psi.vercel.app/)

## How to Run Locally

1. Install Python 3.7 or later
2. Open the folder in VSCode
3. Create a virtual environment:

   ```terminal
   python3 -m venv venv
   ```

4. Activate the virtual environment:

   Linux

   ```terminal
   source venv/bin/activate
   ```

   Windows

   ```terminal
   .\venv\Scripts\activate
   ```

5. Install dependencies:

   ```terminal
   pip install -r requirements.txt
   ```

6. Run the app:

   ```terminal
   flask --app api/index.py run --debug
   ```

Run coverage tests:
   ```terminal
   pytest --cov=. --cov-report=term-missing
   ```

Run unit tests:
   ```terminal
   pytest -v api/test_index.py
   ```