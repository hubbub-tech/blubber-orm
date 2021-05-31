--\i Projects/hubbub/hubbub_ops/create.sql

 CREATE TABLE addresses (
  num real,
  street varchar(100),
  apt varchar(10) DEFAULT '',
  city varchar(100),
  state varchar(50),
  zip varchar(10),
  PRIMARY KEY (num, street, apt, zip)
);

CREATE TABLE users (
  id SERIAL,
  name varchar(100),
  email text UNIQUE,
  password varchar(100),
  payment varchar(50),
  dt_joined timestamp DEFAULT LOCALTIMESTAMP,
  dt_last_active timestamp DEFAULT LOCALTIMESTAMP,
  is_blocked boolean DEFAULT FALSE,
  address_num real,
  address_street varchar(100),
  address_apt varchar(50),
  address_zip varchar(10),
  PRIMARY KEY (id),
  FOREIGN KEY (address_num, address_street, address_apt, address_zip) REFERENCES addresses (num, street, apt, zip)
);

CREATE TABLE profiles (
  phone varchar(20),
  has_pic boolean DEFAULT FALSE,
  bio text,
  id integer, --user id
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE carts (
  total float DEFAULT 0.0,
  total_deposit float DEFAULT 0.0, -- Ade 5/4 - needed a way to track deposits as well
  id integer, -- user id
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE items (
  id SERIAL,
  name varchar(100),
  price float,
  is_available boolean DEFAULT TRUE,
  is_featured boolean DEFAULT FALSE,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  is_locked boolean DEFAULT FALSE,
  last_locked integer,
  is_routed boolean DEFAULT FALSE,
  lister_id integer,
  address_num real,
  address_street varchar(100),
  address_apt varchar(50),
  address_zip varchar(10),
  PRIMARY KEY (id),
  FOREIGN KEY (address_num, address_street, address_apt, address_zip) REFERENCES addresses (num, street, apt, zip),
  FOREIGN KEY (lister_id) REFERENCES users (id)
);

CREATE TABLE details (
  condition integer,
  weight integer,
  volume integer,
  description text,
  id integer, -- item id
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE calendars (
  date_started date,
  date_ended date,
  id integer, -- item id
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE shopping (
  cart_id integer,
  item_id integer,
  PRIMARY KEY (cart_id, item_id),
  FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE listers (
  lister_id integer,
  PRIMARY KEY (lister_id),
  FOREIGN KEY (lister_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE renters (
  renter_id integer,
  PRIMARY KEY (renter_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE
);


CREATE TABLE reservations (
  date_started date,
  date_ended date,
  is_calendared boolean DEFAULT FALSE,
  is_extended boolean DEFAULT FALSE,
  is_in_cart boolean DEFAULT FALSE, -- ade 5/5 - needed to tell which res is in cart
  charge float,
  renter_id integer,
  item_id integer,
  deposit float,
  dt_created timestamp,
  PRIMARY KEY (date_started, date_ended, renter_id, item_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE orders (
  id SERIAL,
  date_placed date,
  is_online_pay boolean,
  is_dropoff_sched boolean DEFAULT FALSE,
  is_pickup_sched boolean DEFAULT FALSE,
  lister_id integer,
  item_id integer,
  renter_id integer,
  res_date_start date,
  res_date_end date,
  PRIMARY KEY (id),
  FOREIGN KEY (lister_id) REFERENCES listers (lister_id),
  FOREIGN KEY (res_date_start, res_date_end, renter_id, item_id) REFERENCES reservations (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE
);


CREATE TABLE reviews (
  id SERIAL,
  body text,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  rating float,
  item_id integer,
  author_id integer,
  PRIMARY KEY (id),
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES renters (renter_id)
);

CREATE TABLE testimonials (
  date_created date DEFAULT LOCALTIMESTAMP,
  description text,
  user_id integer,
  PRIMARY KEY (user_id, date_created),
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE extensions (
  order_id integer,
  renter_id integer, --must be same as order renter_id
  item_id integer, --must be same as order item_id
  res_date_start date, --this must equal either order end date or end date of last extension
  res_date_end date, --this is the extension end date
  PRIMARY KEY (order_id, res_date_end),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (res_date_start, res_date_end, renter_id, item_id) REFERENCES reservations (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE
);

CREATE TABLE logistics (
  dt_sched timestamp DEFAULT LOCALTIMESTAMP,
  notes text,
  referral varchar(100),
  timeslots varchar(100),
  renter_id integer,
  address_num real,
  address_street varchar(100),
  address_apt varchar(50),
  address_zip varchar(10),
  chosen_time time,
  PRIMARY KEY (dt_sched, renter_id),
  FOREIGN KEY (renter_id) REFERENCES renters (renter_id),
  FOREIGN KEY (address_num, address_street, address_apt, address_zip) REFERENCES addresses (num, street, apt, zip)
);

CREATE TABLE pickups (
  pickup_date date CHECK (pickup_date > dt_sched),
  dt_sched timestamp,
  renter_id integer,
  PRIMARY KEY (pickup_date, dt_sched, renter_id),
  FOREIGN KEY (dt_sched, renter_id) REFERENCES logistics (dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE dropoffs (
  dropoff_date date CHECK (dropoff_date > dt_sched),
  dt_sched timestamp,
  renter_id integer,
  PRIMARY KEY (dropoff_date, dt_sched, renter_id),
  FOREIGN KEY (dt_sched, renter_id) REFERENCES logistics (dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE tags (
  tag_name varchar(75),
  PRIMARY KEY (tag_name)
);

CREATE TABLE tagging (
  item_id integer,
  tag_name varchar(75),
  PRIMARY KEY (item_id, tag_name),
  FOREIGN KEY (tag_name) REFERENCES tags (tag_name) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE order_pickups (
  order_id integer,
  pickup_date date,
  renter_id integer,
  dt_sched timestamp,
  dt_completed timestamp,
  PRIMARY KEY (order_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (pickup_date, dt_sched, renter_id) REFERENCES pickups (pickup_date, dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE order_dropoffs (
  order_id integer,
  dropoff_date date,
  renter_id integer,
  dt_sched timestamp,
  dt_completed timestamp,
  PRIMARY KEY (order_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (dropoff_date, dt_sched, renter_id) REFERENCES dropoffs (dropoff_date, dt_sched, renter_id) ON DELETE CASCADE
);
-- needed to drop the following--see data migration notes - caro 5/4
-- ALTER TABLE extensions ADD CONSTRAINT chk_ext_date CHECK (ext_date_end > localtimestamp);
