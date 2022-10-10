# Running PostgreSQL Commands from a File

Hi, it's been a while hasn't it?

## Questions for you

* Do you have a whole LOAD of postgres commands that you need to run sequentially?
* Are you tired of typing them out one-by-one?
* Are you a n00b?

## Well! Let me assist!

1. Open terminal.
2. You must have Postgres downloaded. Check with `psql --version`. If you don't know how, Google it.
3. Know the credentials pointing to your database. This is for testing only.
4. Try `psql -h HOST -p PORT -U username -d database -f path/to/my/file.sql`.
5. Usually, these things have passwords, but again... THIS IS JUST FOR TEST DBs!
6. Grab a beer (or apple juice!) B).

<mark>Notice</mark>: Don't be a dummy and run an untested set of commands on a production database.

You'll regret it. Script responsibly.

## CLI database functions with Python

* To create a version of the database use, `python3 path/to/blubber_cli.py --func create --version 020000`.
* To destroy a version of the database use, `python3 path/to/blubber_cli.py --func destroy --version 020000`.
* You can only destroy the version that you last created.
* You should NOT create over an existing set of database tables.

## Reset sequencers on fresh tables with old data
1. Query for the largest `id` for each table and run the following command:
2. `SELECT setval('[table_name]_[column_name]_seq', [num]);`
3. Done.
