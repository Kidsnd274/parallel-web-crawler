# parallel-web-crawler
To run this program, first setup the environment (Windows commands)
```
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```
Then the following command to start the program:
```
python main.py
```
The script reads from starting_url.txt or any text file with a list of URLs you provide:
```
python main.py <file containing urls>
```
You can set these variables at the top of main.py
```
NUM_PROCESS = 4
MAX_URLS = 100
DATABASE_NAME = "crawler.db"
```