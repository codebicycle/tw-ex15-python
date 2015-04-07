drop table if exists votes;
create table votes (
  id integer primary key autoincrement,
  date integer not null,
  first_name text not null,
  last_name text not null,
  vote text not null
);
create unique index name on votes(first_name, last_name);