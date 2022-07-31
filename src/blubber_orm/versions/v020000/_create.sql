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


CREATE TABLE from_addresses (
  line_1 varchar(100),
  line_2 varchar(100),
  country varchar(100),
  zip varchar(11),
  PRIMARY KEY (line_1, line_2, country, zip),
  FOREIGN KEY (line_1, line_2, country, zip) REFERENCES addresses (line_1, line_2, country, zip) ON DELETE CASCADE
);


CREATE TABLE to_addresses (
  line_1 varchar(100),
  line_2 varchar(100),
  country varchar(100),
  zip varchar(11),
  PRIMARY KEY (line_1, line_2, country, zip),
  FOREIGN KEY (line_1, line_2, country, zip) REFERENCES addresses (line_1, line_2, country, zip) ON DELETE CASCADE
);


CREATE TABLE users (
  id SERIAL,
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
  address_country varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (id),
  FOREIGN KEY (address_line_1, address_line_2, address_country, address_zip) REFERENCES addresses (line_1, line_2, country, zip)
);

CREATE TABLE carts (
  total_charge float DEFAULT 0.0,
  total_deposit float DEFAULT 0.0,
  total_tax float DEFAULT 0.0,
  id int,
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);



CREATE TABLE couriers (
  courier_id int,
  courier_session_key varchar(20),
  is_admin boolean DEFAULT FALSE,
  PRIMARY KEY (courier_id),
  FOREIGN KEY (courier_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE listers (
  lister_id int,
  PRIMARY KEY (lister_id),
  FOREIGN KEY (lister_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE renters (
  renter_id int,
  PRIMARY KEY (renter_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE payees (
  payee_id int,
  PRIMARY KEY (payee_id),
  FOREIGN KEY (payee_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE payers (
  payer_id int,
  PRIMARY KEY (payer_id),
  FOREIGN KEY (payer_id) REFERENCES users (id) ON DELETE CASCADE
);


CREATE TABLE senders (
  sender_id int,
  PRIMARY KEY (sender_id),
  FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE receivers (
  receiver_id int,
  PRIMARY KEY (receiver_id),
  FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
);



CREATE TABLE items (
  id SERIAL,
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
  locker_id int,
  lister_id int,
  manufacturer_id int,
  address_line_1 varchar(100),
  address_line_2 varchar(100),
  address_country varchar(100),
  address_zip varchar(11),
  PRIMARY KEY (id),
  FOREIGN KEY (address_line_1, address_line_2, address_country, address_zip) REFERENCES addresses (line_1, line_2, country, zip),
  FOREIGN KEY (lister_id) REFERENCES listers (lister_id),
  FOREIGN KEY (locker_id) REFERENCES renters (renter_id),
  FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id)
);


CREATE TABLE calendars (
  dt_started timestamp,
  dt_ended timestamp,
  id int,
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
);


CREATE TABLE item_carts (
  cart_id int,
  item_id int,
  PRIMARY KEY (cart_id, item_id),
  FOREIGN KEY (cart_id) REFERENCES carts (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);


CREATE TABLE manufacturers (
  id SERIAL,
  brand varchar(100),
  PRIMARY KEY (id)
);


CREATE TABLE reservations (
  dt_started timestamp,
  dt_ended timestamp,
  is_calendared boolean DEFAULT FALSE,
  is_extension boolean DEFAULT FALSE,
  is_in_cart boolean DEFAULT FALSE,
  renter_id int,
  item_id int,
  est_charge float,
  est_deposit float,
  est_tax float,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (dt_started, dt_ended, renter_id, item_id),
  FOREIGN KEY (renter_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

CREATE TABLE reservations_archived (
  dt_started timestamp,
  dt_ended timestamp,
  renter_id int,
  item_id int,
  notes text,
  dt_archived timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (dt_started, dt_ended, renter_id, item_id),
  FOREIGN KEY (dt_started, dt_ended, renter_id, item_id) REFERENCES reservations (dt_started, dt_ended, renter_id, item_id) ON DELETE CASCADE
);


CREATE TABLE orders (
 id SERIAL,
 dt_placed timestamp DEFAULT LOCALTIMESTAMP,
 is_canceled boolean DEFAULT FALSE,
 referral varchar(100),
 item_id int,
 renter_id int,
 res_dt_start timestamp,
 res_dt_end timestamp,
 PRIMARY KEY (id),
 FOREIGN KEY (res_dt_start, res_dt_end, renter_id, item_id) REFERENCES reservations (dt_started, dt_ended, renter_id, item_id) ON DELETE CASCADE
);


CREATE TABLE extensions (
 order_id int,
 renter_id int,
 item_id int,
 res_dt_start timestamp,
 res_dt_end timestamp,
 PRIMARY KEY (order_id, res_dt_end),
 FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
 FOREIGN KEY (res_dt_start, res_dt_end, renter_id, item_id) REFERENCES reservations (dt_started, dt_ended, renter_id, item_id) ON DELETE CASCADE
);


CREATE TABLE charges (
  id SERIAL,
  notes text,
  amount float,
  currency varchar(10),
  payment_type varchar(100),
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  external_id int,
  order_id int,
  payee_id int,
  payer_id int,
  issue_id int, -- optional
  PRIMARY KEY (id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (payee_id) REFERENCES payees (payee_id),
  FOREIGN KEY (payer_id) REFERENCES payers (payer_id),
  FOREIGN KEY (issue_id) REFERENCES issues (id)
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
  PRIMARY KEY (title)
);

CREATE TABLE order_promos (
  order_id int,
  promo_title varchar(100),
  dt_applied timestamp DEFAULT LOCALTIMESTAMP,
  PRIMARY KEY (order_id, promo_title),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (promo_title) REFERENCES promos (title) ON DELETE CASCADE
);

CREATE TABLE logistics (
  id SERIAL,
  notes text,
  dt_created timestamp DEFAULT LOCALTIMESTAMP,
  dt_sent timestamp,
  dt_received timestamp,
  sender_id int,
  receiver_id int,
  from_addr_line_1 varchar(100),
  from_addr_line_2 varchar(100),
  from_addr_country varchar(100),
  from_addr_zip varchar(11),
  to_addr_line_1 varchar(100),
  to_addr_line_2 varchar(100),
  to_addr_country varchar(100),
  to_addr_zip varchar(11),
  courier_id int,
  PRIMARY KEY (id),
  FOREIGN KEY (courier_id) REFERENCES couriers (courier_id),
  FOREIGN KEY (sender_id) REFERENCES senders (sender_id),
  FOREIGN KEY (receiver_id) REFERENCES receivers (receiver_id),
  FOREIGN KEY (from_addr_line_1, from_addr_line_2, from_addr_country, from_addr_zip) REFERENCES from_addresses (line_1, line_2, country, zip),
  FOREIGN KEY (to_addr_line_1, to_addr_line_2, to_addr_country, to_addr_zip) REFERENCES to_addresses (line_1, line_2, country, zip)
);


CREATE TABLE availabilities (
  logistics_id int,
  dt_range_start timestamp,
  dt_range_end timestamp,
  is_sched boolean,
  dt_sched_eta timestamp,
);


CREATE TABLE order_logistics (
  order_id int,
  logsitics_id int,
  PRIMARY KEY (order_id, logsitics_id),
  FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  FOREIGN KEY (logsitics_id) REFERENCES logsitics (id) ON DELETE CASCADE
);


CREATE TABLE tags (
 title varchar(75),
 PRIMARY KEY (title)
);

CREATE TABLE item_tags (
 item_id int,
 title varchar(75),
 PRIMARY KEY (item_id, title),
 FOREIGN KEY (title) REFERENCES tags (title) ON DELETE CASCADE,
 FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);


CREATE TABLE issues (
 id SERIAL,
 body text,
 slug varchar(200),
 user_id int,
 resolution text,
 is_resolved boolean DEFAULT FALSE,
 dt_created timestamp DEFAULT LOCALTIMESTAMP,
 PRIMARY KEY (id),
 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);


CREATE TABLE reviews (
 id SERIAL,
 body text,
 dt_created timestamp DEFAULT LOCALTIMESTAMP,
 rating float,
 item_id int,
 author_id int,
 PRIMARY KEY (id),
 FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
 FOREIGN KEY (author_id) REFERENCES renters (renter_id)
);

CREATE TABLE testimonials (
 dt_created timestamp DEFAULT LOCALTIMESTAMP,
 body text,
 user_id int,
 PRIMARY KEY (user_id, dt_created),
 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
