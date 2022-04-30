--\i Projects/hubbub/hubbub_ops/create.sql

 CREATE TABLE addresses (
  line_1 varchar(100),
  line_2 varchar(100) DEFAULT '',
  city varchar(100),
  state varchar(50),
  zip varchar(11),
  PRIMARY KEY (line_1, line_2, zip)
);

CREATE TABLE users (
  id varchar(100),
  name varchar(100),
  email text UNIQUE,
  password varchar(200),
  payment varchar(50),
  pubkey varchar(200), -- ade 11/16
  privkey varchar(200), -- ade 11/16
  dt_joined timestamp DEFAULT LOCALTIMESTAMP,
  dt_last_active timestamp DEFAULT LOCALTIMESTAMP,
  is_blocked boolean DEFAULT FALSE,
  session varchar(20),
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (id),
  FOREIGN KEY (address_line_1, address_line_2, address_zip) REFERENCES addresses (line_1, line_2, zip)
);

CREATE TABLE profiles (
  phone varchar(20),
  has_pic boolean DEFAULT FALSE,
  bio text,
  id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE carts (
  total float DEFAULT 0.0,
  total_deposit float DEFAULT 0.0,
  total_tax float DEFAULT 0.0,
  id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE items (
  id varchar(100),
  name varchar(100),
  price float,
  is_available boolean DEFAULT TRUE,
  is_featured boolean DEFAULT FALSE,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  is_locked boolean DEFAULT FALSE,
  last_locked integer,
  is_routed boolean DEFAULT FALSE,
  lister_id varchar(100),
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (id),
  FOREIGN KEY (address_line_1, address_line_2, address_zip) REFERENCES addresses (line_1, line_2, zip),
  FOREIGN KEY (lister_id) REFERENCES users (id)
);

CREATE TABLE details (
  condition integer,
  weight integer,
  volume integer,
  description text,
  id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE calendars (
  date_started date,
  date_ended date,
  id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE shopping (
  cart_id varchar(100),
  item_id varchar(100),
  PRIMARY KEY (cart_id, item_id),
  FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE couriers (
  courier_id varchar(100),
  session varchar(20), -- ade 11/16
  is_admin boolean DEFAULT FALSE, -- ade 11/16
  PRIMARY KEY (courier_id),
  FOREIGN KEY (courier_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE listers (
  lister_id varchar(100),
  PRIMARY KEY (lister_id),
  FOREIGN KEY (lister_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE renters (
  renter_id varchar(100),
  PRIMARY KEY (renter_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ade 11/16
CREATE TABLE payers (
  payer_id varchar(100),
  PRIMARY KEY (payer_id),
  FOREIGN KEY (payer_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ade 11/16
CREATE TABLE payees (
  payee_id varchar(100),
  PRIMARY KEY (payee_id),
  FOREIGN KEY (payee_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE reservations (
  date_started date,
  date_ended date,
  is_calendared boolean DEFAULT FALSE,
  is_extended boolean DEFAULT FALSE,
  is_in_cart boolean DEFAULT FALSE,
  renter_id varchar(100),
  item_id varchar(100),
  charge float,
  deposit float,
  tax float,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  is_valid boolean DEFAULT TRUE, -- ade 11/16
  hist_renter_id varchar(100), --must be same as order renter_id -- ade 11/16
  hist_item_id varchar(100), --must be same as order item_id -- ade 11/16
  hist_date_start date, --this must equal either order end date or end date of last extension -- ade 11/16
  hist_date_end date, --this is the extension end date -- ade 11/16
  PRIMARY KEY (date_started, date_ended, renter_id, item_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
  FOREIGN KEY (hist_date_start, hist_date_end, hist_renter_id, hist_item_id) REFERENCES history (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE -- ade 11/16
);

-- ade 11/16
CREATE TABLE history (
  date_started date,
  date_ended date,
  renter_id varchar(100),
  item_id varchar(100),
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (date_started, date_ended, renter_id, item_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE orders (
  id varchar(100),
  date_placed date,
  is_online_pay boolean,
  is_cancelled boolean DEFAULT FALSE, -- ade 11/16
  is_dropoff_sched boolean DEFAULT FALSE,
  is_pickup_sched boolean DEFAULT FALSE,
  lister_id varchar(100),
  item_id varchar(100),
  renter_id varchar(100),
  res_date_start date,
  res_date_end date,
  PRIMARY KEY (id),
  FOREIGN KEY (lister_id) REFERENCES listers (lister_id),
  FOREIGN KEY (res_date_start, res_date_end, renter_id, item_id) REFERENCES reservations (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE
);

CREATE TABLE reviews (
  id varchar(100),
  body text,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  rating float,
  item_id varchar(100),
  author_id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES renters (renter_id)
);

CREATE TABLE testimonials (
  date_created date DEFAULT LOCALTIMESTAMP,
  description text,
  user_id varchar(100),
  PRIMARY KEY (user_id, date_created),
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE extensions (
  order_id varchar(100),
  renter_id varchar(100),
  item_id varchar(100),
  res_date_start date,
  res_date_end date,
  PRIMARY KEY (order_id, res_date_end),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (res_date_start, res_date_end, renter_id, item_id) REFERENCES reservations (date_started, date_ended, renter_id, item_id) ON DELETE CASCADE
);

-- ade 11/16
CREATE TABLE charges (
  id varchar(100),
  notes text
  amount float,
  processor_id varchar(100),
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  order_id varchar(100),
  payee_id varchar(100),
  payer_id varchar(100),
  issue_id varchar(100), -- optional
  PRIMARY KEY (id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (payee_id) REFERENCES payees (payee_id) ON DELETE CASCADE,
  FOREIGN KEY (payer_id) REFERENCES payers (payer_id) ON DELETE CASCADE,
  FOREIGN KEY (issue_id) REFERENCES issues (id)
);

CREATE TABLE logistics (
  dt_sched timestamp DEFAULT LOCALTIMESTAMP,
  notes text,
  referral varchar(100),
  timeslots text,
  renter_id varchar(100),
  chosen_time time,
  courier_id varchar(100), -- ade 11/16
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (dt_sched, renter_id),
  FOREIGN KEY (renter_id) REFERENCES renters (renter_id),
  FOREIGN KEY (courier_id) REFERENCES couriers (courier_id), -- ade 11/16
  FOREIGN KEY (address_line_1, address_line_2, address_zip) REFERENCES addresses (line_1, line_2, zip)
);

CREATE TABLE pickups (
  pickup_date date CHECK (pickup_date > dt_sched),
  dt_sched timestamp,
  renter_id varchar(100),
  PRIMARY KEY (pickup_date, dt_sched, renter_id),
  FOREIGN KEY (dt_sched, renter_id) REFERENCES logistics (dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE dropoffs (
  dropoff_date date CHECK (dropoff_date > dt_sched),
  dt_sched timestamp,
  renter_id varchar(100),
  PRIMARY KEY (dropoff_date, dt_sched, renter_id),
  FOREIGN KEY (dt_sched, renter_id) REFERENCES logistics (dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE tags (
  tag_name varchar(75),
  PRIMARY KEY (tag_name)
);

CREATE TABLE tagging (
  item_id varchar(100),
  tag_name varchar(75),
  PRIMARY KEY (item_id, tag_name),
  FOREIGN KEY (tag_name) REFERENCES tags (tag_name) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE order_pickups (
  order_id varchar(100),
  pickup_date date,
  renter_id varchar(100),
  dt_sched timestamp,
  dt_completed timestamp,
  PRIMARY KEY (order_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (pickup_date, dt_sched, renter_id) REFERENCES pickups (pickup_date, dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE order_dropoffs (
  order_id varchar(100),
  dropoff_date date,
  renter_id varchar(100),
  dt_sched timestamp,
  dt_completed timestamp,
  PRIMARY KEY (order_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (dropoff_date, dt_sched, renter_id) REFERENCES dropoffs (dropoff_date, dt_sched, renter_id) ON DELETE CASCADE
);

CREATE TABLE issues (
  id varchar(100),
  complaint text,
  link varchar(100),
  user_id varchar(100),
  resolution text,
  is_resolved boolean DEFAULT FALSE,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
