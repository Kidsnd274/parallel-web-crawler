# parallel-web-crawler
To run this program, first setup the environment (Windows commands)
```
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```
Then run this command to start the script. The script reads from starting_url.txt or any text file with a list of URLs you provide
```
python main.py
```

To test crawler with one url, run the following command: (might not work now)
```
python crawler.py https://google.com
```
