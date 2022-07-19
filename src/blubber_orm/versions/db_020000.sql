CREATE TABLE addresses (
  line_1 varchar(100),
  line_2 varchar(100) DEFAULT '',
  city varchar(100),
  state varchar(100),
  country varchar(100),
  zip varchar(11),
  lat float,
  lng float,
  PRIMARY KEY (line_1, line_2, country, zip)
);


CREATE TABLE users (
  id varchar(100),
  name varchar(100),
  phone varchar(20),
  email varchar(100) UNIQUE,
  password varchar(200),
  bio text,
  profile_pic boolean DEFAULT FALSE,
  dt_joined timestamp DEFAULT LOCALTIMESTAMP,
  dt_last_active timestamp DEFAULT LOCALTIMESTAMP,
  is_blocked boolean DEFAULT FALSE,
  session_key varchar(20),
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_city varchar(100),
  address_country varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (id),
  FOREIGN KEY (address_line_1, address_line_2, address_country, address_zip) REFERENCES addresses (line_1, line_2, country, zip)
);

CREATE TABLE carts (
  total_charge float DEFAULT 0.0,
  total_deposit float DEFAULT 0.0,
  total_tax float DEFAULT 0.0,
  id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);


CREATE TABLE items (
  id varchar(100),
  name varchar(100),
  retail_price float,
  is_visible boolean DEFAULT TRUE,
  is_transactable boolean DEFAULT TRUE,
  is_featured boolean DEFAULT FALSE,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  is_locked boolean DEFAULT FALSE,
  description text,
  weight float,
  weight_unit varchar(4),
  dim_height float,
  dim_length float,
  dim_width float,
  dim_unit varchar(4),
  locker_id varchar(100),
  lister_id varchar(100),
  manufacturer_id varchar(100),
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_city varchar(100),
  address_country varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (id),
  FOREIGN KEY (address_line_1, address_line_2, address_country, address_zip) REFERENCES addresses (line_1, line_2, country, zip),
  FOREIGN KEY (lister_id) REFERENCES listers (lister_id),
  FOREIGN KEY (locker_id) REFERENCES renters (renter_id),
  FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id)
);

CREATE TABLE manufacturers (
  id varchar(100),
  brand varchar(100),
  PRIMARY KEY (id)
);

CREATE TABLE calendars (
  dt_started timestamp,
  dt_ended timestamp,
  id varchar(100),
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
);


CREATE TABLE item_carts (
  cart_id varchar(100),
  item_id varchar(100),
  PRIMARY KEY (cart_id, item_id),
  FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);


CREATE TABLE couriers (
  courier_id varchar(100),
  courier_session_key varchar(20),
  is_admin boolean DEFAULT FALSE,
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

CREATE TABLE payees (
  payee_id varchar(100),
  PRIMARY KEY (payee_id),
  FOREIGN KEY (payee_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE payers (
  payer_id varchar(100),
  PRIMARY KEY (payer_id),
  FOREIGN KEY (payer_id) REFERENCES users (id) ON DELETE CASCADE
);


CREATE TABLE reservations (
  dt_started timestamp,
  dt_ended timestamp,
  is_calendared boolean DEFAULT FALSE,
  is_extended boolean DEFAULT FALSE,
  is_in_cart boolean DEFAULT FALSE,
  renter_id varchar(100),
  item_id varchar(100),
  charge float,
  deposit float,
  tax float,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  is_valid boolean DEFAULT TRUE,
  PRIMARY KEY (dt_started, dt_ended, renter_id, item_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE res_history (
  dt_started timestamp,
  dt_ended timestamp,
  renter_id varchar(100),
  item_id varchar(100),
  next_dt_start timestamp,
  next_dt_end timestamp,
  next_renter_id varchar(100),
  next_item_id varchar(100),
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (dt_started, dt_ended, renter_id, item_id),
  FOREIGN KEY (dt_started, dt_ended, renter_id, item_id) REFERENCES reservations (dt_started, dt_ended, renter_id, item_id) ON DELETE CASCADE
);


CREATE TABLE orders (
 id varchar(100),
 dt_placed timestamp DEFAULT LOCALTIMESTAMP,
 is_canceled boolean DEFAULT FALSE,
 is_dropoff_sched boolean DEFAULT FALSE,
 is_pickup_sched boolean DEFAULT FALSE,
 lister_id varchar(100),
 item_id varchar(100),
 renter_id varchar(100),
 res_dt_start timestamp,
 res_dt_end timestamp,
 PRIMARY KEY (id),
 FOREIGN KEY (lister_id) REFERENCES listers (lister_id),
 FOREIGN KEY (res_dt_start, res_dt_end, renter_id, item_id) REFERENCES reservations (dt_started, dt_ended, renter_id, item_id) ON DELETE CASCADE
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
 dt_created DEFAULT LOCALTIMESTAMP,
 body text,
 user_id varchar(100),
 PRIMARY KEY (user_id, dt_created),
 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE extensions (
 order_id varchar(100),
 renter_id varchar(100),
 item_id varchar(100),
 res_dt_start timestamp,
 res_dt_end timestamp,
 PRIMARY KEY (order_id, res_dt_end),
 FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
 FOREIGN KEY (res_dt_start, res_dt_end, renter_id, item_id) REFERENCES reservations (dt_started, dt_ended, renter_id, item_id) ON DELETE CASCADE
);


CREATE TABLE charges (
  id varchar(100),
  notes text
  amount float,
  payment_type varchar(100),
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  order_id varchar(100),
  payee_id varchar(100),
  payer_id varchar(100),
  issue_id varchar(100), -- optional
  PRIMARY KEY (id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (payee_id) REFERENCES payees (payee_id),
  FOREIGN KEY (payer_id) REFERENCES payers (payer_id),
  FOREIGN KEY (issue_id) REFERENCES issues (id)
);


CREATE TABLE logistics (
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  notes text,
  referral varchar(100),
  timeslots text,
  renter_id varchar(100),
  time_chosen time,
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_city varchar(100),
  address_country varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (dt_created, renter_id),
  FOREIGN KEY (renter_id) REFERENCES renters (renter_id),
  FOREIGN KEY (address_line_1, address_line_2, address_country, address_zip) REFERENCES addresses (line_1, line_2, country, zip)
);

CREATE TABLE pickups (
  date_sched date CHECK (date_sched > dt_created),
  dt_created timestamp,
  renter_id varchar(100),
  PRIMARY KEY (date_sched, dt_created, renter_id),
  FOREIGN KEY (dt_created, renter_id) REFERENCES logistics (dt_created, renter_id) ON DELETE CASCADE
);

CREATE TABLE dropoffs (
  date_sched date CHECK (date_sched > dt_created),
  dt_created timestamp,
  renter_id varchar(100),
  PRIMARY KEY (date_sched, dt_created, renter_id),
  FOREIGN KEY (dt_created, renter_id) REFERENCES logistics (dt_created, renter_id) ON DELETE CASCADE
);

CREATE TABLE tags (
 title varchar(75),
 PRIMARY KEY (title)
);

CREATE TABLE item_tags (
 item_id varchar(100),
 title varchar(75),
 PRIMARY KEY (item_id, title),
 FOREIGN KEY (title) REFERENCES tags (title) ON DELETE CASCADE,
 FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE order_pickups (
 order_id varchar(100),
 date_sched date,
 renter_id varchar(100),
 dt_sched timestamp,
 dt_completed timestamp,
 PRIMARY KEY (order_id),
 FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
 FOREIGN KEY (date_sched, dt_created, renter_id) REFERENCES pickups (date_sched, dt_created, renter_id) ON DELETE CASCADE
);

CREATE TABLE order_dropoffs (
 order_id varchar(100),
 date_sched date,
 renter_id varchar(100),
 dt_sched timestamp,
 dt_completed timestamp,
 PRIMARY KEY (order_id),
 FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
 FOREIGN KEY (date_sched, dt_created, renter_id) REFERENCES dropoffs (date_sched, dt_created, renter_id) ON DELETE CASCADE
);

CREATE TABLE issues (
 id varchar(100),
 body text,
 slug varchar(200),
 user_id varchar(100),
 resolution text,
 is_resolved boolean DEFAULT FALSE,
 dt_created timestamp DEFAULT LOCALTIMESTAMP,
 PRIMARY KEY (id),
 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE promos (
  title varchar(100),
  description text,
  sku integer,
  discount_value float,
  discount_unit varchar(50),
  discount_type varchar(50),
  dt_activated timestamp,
  dt_expired timestamp,
  is_active boolean,
  PRIMARY KEY (title)
)

CREATE TABLE order_promos (
  order_id varchar(100),
  promo_title varchar(100),
  dt_applied timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (order_id, promo_title),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (promo_title) REFERENCES promos (title) ON DELETE CASCADE
)
