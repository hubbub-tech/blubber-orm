--\i Projects/hubbub/blubber/src/blubber_orm/dev/create.sql

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
  dt_joined timestamp,
  dt_last_active timestamp,
  is_blocked boolean,
  address_num real,
  address_street varchar(100),
  address_apt varchar(50),
  address_zip varchar(10),
  PRIMARY KEY (id),
  FOREIGN KEY (address_num, address_street, address_apt, address_zip) REFERENCES addresses (num, street, apt, zip)
);

CREATE TABLE profiles (
  phone varchar(10),
  birthday date, /* HMM no birthday actually */
  has_pic boolean,
  bio text,
  id integer, /* HMM changed this for easy referencing */
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id)
);

CREATE TABLE carts (
  total float,
  id integer, /* HMM changed this for easy referencing */
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id)
);

CREATE TABLE items (
  id SERIAL,
  name varchar(100),
  price float,
  is_available boolean,
  is_featured boolean,
  dt_created timestamp,
  is_locked boolean,
  last_locked integer,
  is_routed boolean,
  lister_id integer, /* toSELF coming from users table not listers table */
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
  id integer, /* HMM changed this for easy referencing */
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id)
);

CREATE TABLE calendars (
  date_started date,
  date_ended date,
  id integer, /* HMM changed this for easy referencing */
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id)
);

CREATE TABLE shopping (
  cart_id integer,
  item_id integer,
  PRIMARY KEY (cart_id, item_id),
  FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE reservations (
  date_started date,
  date_ended date,
  is_calendared boolean,
  is_extended boolean,
  is_expired boolean,
  charge float,
  renter_id integer, /* HMM changed this attribute */
  item_id integer,
  PRIMARY KEY (date_started, date_ended, renter_id, item_id),
  FOREIGN KEY (renter_id) REFERENCES users (id),
  FOREIGN KEY (item_id) REFERENCES items (id)
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

CREATE TABLE reviews (
  id SERIAL,
  body text,
  dt_created timestamp,
  rating float,
  item_id integer,
  author_id integer,
  PRIMARY KEY (id),
  FOREIGN KEY (item_id) REFERENCES items (id),
  FOREIGN KEY (author_id) REFERENCES renters (renter_id)
);

CREATE TABLE testimonials (
  date_created date,
  description text,
  user_id integer,
  PRIMARY KEY (user_id, date_created)
);

CREATE TABLE orders (
  id integer,
  date_placed date,
  is_online_pay boolean,
  is_dropoff_sched boolean,
  is_pick_sched boolean,
  renter_id integer,
  lister_id integer,
  item_id integer,
  res_date_start date,
  res_date_end date,
  PRIMARY KEY (id),
  FOREIGN KEY (lister_id) REFERENCES listers (lister_id),
  FOREIGN KEY (res_date_start, res_date_end, renter_id, item_id) REFERENCES reservations (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE
);

CREATE TABLE extensions (
  res_date_start date,
  res_date_end date,
  renter_id integer,
  item_id integer,
  ext_charge float,
  ext_date_end date CHECK (ext_date_end > res_date_end),
  PRIMARY KEY (renter_id, item_id, ext_date_end),
  FOREIGN KEY (res_date_start, res_date_end, renter_id, item_id) REFERENCES reservations (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE
);

CREATE TABLE logistics (
  dt_sched timestamp,
  notes text,
  referral varchar(100),
  timeslots varchar(100),
  renter_id integer,
  address_num real,
  address_street varchar(100),
  address_apt varchar(50),
  address_zip varchar(10),
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
  PRIMARY KEY (order_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (pickup_date, dt_sched, renter_id) REFERENCES pickups (pickup_date, dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE order_dropoffs (
  order_id integer,
  dropoff_date date,
  renter_id integer,
  dt_sched timestamp,
  PRIMARY KEY (order_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (dropoff_date, dt_sched, renter_id) REFERENCES dropoffs (dropoff_date, dt_sched, renter_id) ON DELETE CASCADE
);

ALTER TABLE extensions ADD CONSTRAINT chk_ext_date CHECK (ext_date_end > localtimestamp);
