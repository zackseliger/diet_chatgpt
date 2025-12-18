# Diet GPT Analysis

Simple app to query GPT-5 using Context-Free Grammar https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools#3-contextfree-grammar-cfg

Technologies used:
- Flask
- Tailwind CSS
- Chart.js
- Tinybird
- ChatGPT

## Data
The data is ~3 years (2023 - 2025) worth of diet tracking via Chronometer. Each row is a serving of food, and the columns contain micro and macronutrients of that serving. I wrote a blog post with this same dataset in 2024: https://medium.com/@zackseliger/optimizing-health-markers-with-diet-test-1-1c58046a09eb

You can view the Tinybird schema in @datafile.datafile, and the full data at @servings_apr_25.csv

## How to Run
A .env file is required to run the program, with the keys `OPENAI_KEY` and `TINYBIRD_ADMIN_TOKEN`

Simply run app.py `python3 app.py`, and it will run on the local machine on port 80

It's also hosted on http://137.184.35.207/

## Limitations
The context-free grammar in @ai.py is not a complete SQL implementation. The most obvious limitations are:
- Numbers cannot have a decimal "."
- No nested queries. So queries like "SELECT * FROM (SELECT ...)" aren't supported


## About
The main page shows a graph of every day in the database, with the Y-axis being the number of calories eaten that day. Each bar is segmented into carbs, fats, and protein. Below it is 3 tabs: AI Analysis, Manual SQL, and Evals

### AI Analysis
Ask the AI any natural-language question and get a response. It will show the tool calls it makes before responding as well

### Manual SQL
Query the database yourself. Output is in table format

### Evals
Evaluation questions. They are:
- Which day was the most sugar eaten, and how much? Round to the nearest integer. Output in the format "DATE AMOUNT", for example: "2021-03-15 99g"
- What was the most Vitamin C consumed in one serving? What food item was it, and how much Vitamin C? Round to the nearest integer. Just output the food name, not the cooking method. Format the answer like this: "FOOD AMOUNT", for example: "Sweet Potato 57mg"
- What was the top 3 amounts of calories consumed per day? Output a comma-separated list of calories in descending order, rounding the calorie amounts to the nearest integer. Example: "6000, 5000, 4000"
