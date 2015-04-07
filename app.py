#! /usr/bin/env python3

import sqlite3
from flask import Flask, render_template
from datetime import datetime
import os.path

app = Flask(__name__)

# config
DATABASE = 'database.db'

# db
def connect_db():
  rv = sqlite3.connect(DATABASE)
  rv.row_factory = sqlite3.Row
  return rv

#  initialize db
def init_db():
  db = connect_db()
  with app.open_resource('schema.sql', mode='r') as f:
    db.cursor().executescript(f.read())
  db.commit()


def parse_line(line):
  date_raw = line[8:14]
  date = datetime.strptime(date_raw, '%b %d').date()
  name = line[15:50].rstrip()
  last_name, first_name = name.split(maxsplit=1)
  vote = line[63:64]

  return(date, first_name, last_name, vote)


@app.route('/')
def show_chart():
  db = connect_db()
  c = db.cursor()

  # populate database
  with open('vot.dat', encoding='utf-8') as f:
    data = [parse_line(line) for line in f]

  for row in data:
    try:
      c.execute('insert into votes (date, first_name, last_name, vote) \
                  values (?,?,?,?)', row)
    except sqlite3.IntegrityError:
      # print("Integrity Error: Can't add twice %s %s" % (row[1], row[2]) )
      pass

  db.commit()

  # database dump
  # c.execute('select * from votes')
  # for row in c:
  #   print(tuple(row))

  # query votes count
  c.execute('select count(vote) as nr, max(date) as "last_vote_date [date]", vote \
              from votes \
              group by vote')

  votes = { r['vote']: dict(nr=r['nr'], last_vote_date=r['last_vote_date']) for r in c }
  
  # query last voters
  for vote in votes:
    last_vote_date = votes[vote]['last_vote_date']
    c.execute('select first_name from votes where vote = ? and date = ?', (vote, last_vote_date))
    votes[vote]['last_voters'] = [ r['first_name'] for r in c ]

  c.close()
  db.close()

  # view
  view = {}
  view['votes'] = votes
  view['sorted'] = sorted(votes)
  # scale factor, to exaggerate graph dimensions
  view['scale'] = 30

  return render_template('chart.html', view=view)


if __name__ == '__main__':
  if not os.path.exists(DATABASE):
    init_db()

  # init_db()
  app.run()
