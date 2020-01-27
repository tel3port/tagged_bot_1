import heroku3

heroku_conn = heroku3.from_key('b477d2e0-d1ba-48b1-a2df-88d87db973e7')
app = heroku_conn.apps()['tagged-bot-2-usa']
app.restart()
