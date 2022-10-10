# Hubbub Blubber

Notice - this package is only compatible with Hubbub projects.

## Getting Started

Blubber is an internal object relational mapper for Hubbub's marketplace database. This is important for consistent object structure across all of Hubbub's projects. It's called 'Blubber' because it's a thick layer on raw data (lol)

### Prerequisites

Blubber requires you to define two variables in your environment: 'BLUBBER_DEBUG' and 'DATABASE_URL'.

'DATABASE_URL' must be a postgresql URL formatted as 'postgresql://NAME:PASSWORD@HOST:PORT/USER'.
'BLUBBER_DEBUG' takes a value of '0' for FALSE or '1' for TRUE. Set these before using, and Blubber will run smoothly:

```
export BLUBBER_DEBUG=1
export DATABASE_URL=postgresql://fakeUser:fakePassword@localhost:5432/fakeDB
```

### Installing

Run the following command in terminal to install the python package:

```
pip3 install blubber-orm
```

## About BLUBBER_DEBUG

In debug mode, Blubber will print all of your queries to terminal. In a future release, these outputs will also catch errors and can be configured to log to a file or email to an admin.

### Developer Tools

Create a play-version of the Hubbub database and fill it with dummy data under /src/blubber_orm/dev!

## Built With

* [psycopg2](https://www.psycopg.org/docs/) - The DBAPI for running posgresql queries

## Contributing

Blubber is currently not taking contributions. This policy may change in the future.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
