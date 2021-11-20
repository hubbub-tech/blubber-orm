# Blubber Attributes

## TABLES
The following subcategories are tables within the database with a corresponding Blubber object wrapper.
Primary key attributes are **bolded**.

### "addresses" - the addresses of users, items, and logistics
* "**num**" (integer) - building number
* "**street**" (varchar) - street name, 100 character limit
* "**apt**" (varchar) - apartment number, 50 character limit, default to ''
* "city" (varchar) - address city, 100 character limit
* "state" (varchar) - address state, 50 character limit
* "**zip**" (varchar) - address zip code, 10 character limit

### "users" - anyone who has created an account on Hubbub Shop
* "**id**" (SERIAL) - an integer which uniquely identifies users
* "name" (varchar) - the user's full name, 100 character limit
* "email" (text) - the user's contact email, must be unique
* "password" (varchar) - a hash of the user's password to their account, 200 character limit
* "payment" (varchar) - the user's Venmo handle or '@NA' if they don't use Venmo, 50 character limit
* "dt_joined" (timestamp) - datetime that the user joined Hubbub, defaults to UTC timezone
* "dt_last_active" (timestamp) - the last datetime that the user logged in, defaults to UTC timezone
* "is_blocked" (boolean) - T/F indicating whether or not the user was blocked, defaults to FALSE
* "session" (varchar) - token for verifying that the user logged in on server side, 20 character limit

* "address_num" (integer) - primary key to *addresses*, referencing the user's address
* "address_street" (varchar) - primary key to *addresses*, referencing the user's address
* "address_apt" (varchar) - primary key to *addresses*, referencing the user's address
* "address_zip" (varchar) - primary key to *addresses*, referencing the user's address

### "profiles" - more user information
* "phone" (varchar) - the user's phone number, 20 character limit
* "has_pic" (boolean) - the user has a visible profile picture on the Hubbub Shop, default to FALSE
* "bio" (text) - a biography for the user self-composed

* "**id**" (integer) - primary key to *users*, references which user's profile info this is

### "carts" - the items that the user is about to order, has been added to their cart
* "total" (float) - the total rental cost of the items in the cart, default to $0.00
* "total_deposit" (float) - the total rental deposit to be returned to the renter at the end of rental, defaults to $0.00
* "total_tax" (float) - the total rental tax owed by the renter for transacting on Hubbub, defaults to $0.00

* "**id**" (integer) - primary key to *users*, references which user's cart info this is

*See association table "shopping" for link between cart and items in the cart*

### "items" - items listed on Hubbub for rent
* "**id**" (SERIAL) - an integer which uniquely identifies items
* "name" (varchar) - the item's retail name, 100 character limit
* "price" (float) - the item's retail price
* "is_available" (boolean) - the item is active for rentals on Hubbub shop, defaults to TRUE
* "is_featured" (boolean) - the item is featured on Hubbub shop, defaults to FALSE,
* "dt_created" (timestamp) - datetime that the item was listed on Hubbub shop, defaults to UTC timezone
* "is_locked" (boolean) - T/F temporary state where there is a user in the process of checking out this item, default to FALSE
* "last_locked" (integer) - the user id of the renter who is currently checking out this item
* "is_routed" (boolean) - T/F temporary state where the renter has entered valid payment info for the item, default to FALSE

* "lister_id" (integer) - primary key to *users*, the user id of the user who listed the item
* "address_num" (integer) - primary key to *addresses*, referencing the item's current address
* "address_street" (varchar) - primary key to *addresses*, referencing the item's current address
* "address_apt" (varchar) - primary key to *addresses*, referencing the item's current address
* "address_zip" (varchar) - primary key to *addresses*, referencing the item's current address

### "details" - more item information
* "condition" (integer) - the condition of the item on a scale of 1 to 3
* "weight" (integer) - how heavy the item is on a scale of 1 to 3
* "volume" (integer) - how large the item is on a scale of 1 to 3
* "description" (text) -  a description of the item and its quirks

* "**id**" (integer) - primary key to *items*, references which item's details are here

### "calendars" - the item's booking calendar
* "date_started" (date) - the date that the item started being listed for rent
* "date_ended" (date) - the date that the item stops being listed for rent

* "**id**" (integer) - primary key to *items*, references which item's calendar this is

### "reservations" - date ranges for renting items on Hubbub
* "**date_started**" (date) - the start date for the reservation
* "**date_ended**" (date) - the end date for the reservation
* "is_calendared" (boolean) - T/F is this reservation official/ordered, default to FALSE
* "is_extended" (boolean) - T/F is this a reservation for an extension on an existing order, defaults to FALSE
* "is_in_cart" (boolean) - T/F temporary state, is this item in a user's cart
* "charge" (float) - how much will the rental cost the renter
* "deposit" (float) - how much deposit does the renter owe to Hubbub
* "tax" (float) - how much tax the renter will pay on the rental
* "dt_created" (timestamp) - the datetime that the reservation was first queried, defaults to UTC timezone

* "**renter_id**" (integer) - primary key to *renters*, the user id of the renter who booked the reservation
* "**item_id**" (integer) - primary key to *items*, the item id of the item that is being reserved

### "orders" - the orders placed by users to rent items, 1 item/rental to 1 order
* "**id**" (SERIAL) - the unique id for the order
* "date_placed" (date) - the date when the order was placed
* "is_online_pay" (boolean) - T/F will the renter pay online
* "is_dropoff_sched" (boolean) - has the renter scheduled when they are available to have the item dropped off, defaults to FALSE
* "is_pickup_sched" (boolean) - has the renter scheduled when they are available to have the item picked up, defaults to FALSE

* "lister_id" (integer) - primary key to *listers*, the user id of the lister who is leasing the item
* "item_id" (integer) - primary key to *reservations*, calls the reservation which contains order metadata
* "renter_id" (integer) - primary key to *reservations*, calls the reservation which contains order metadata
* "res_date_start" (date) - primary key to *reservations*, calls the reservation which contains order metadata
* "res_date_end" (date) - primary key to *reservations*, calls the reservation which contains order metadata

### "reviews" - reviews left on an item by previous renters
* "**id**" (SERIAL) - the id for the review
* "body" (text) - the content of the review
* "dt_created" (timestamp) - the datetime that the review was submitted, defaults to UTC timezone
* "rating" (float) - numerical rating for the quality of the item

* "item_id" (integer) - primary key to *items*, references which item this review is about
* "author_id" (integer) - primary key to *renters*, references who wrote this review

### "testimonials" - users tell us about their Hubbub experience
* "**date_created**" (date) - when was this testimonial given, defaults to UTC timezone
* "description" (text) - the content of the testimonial

* "**user_id**" (integer) - primary key to *users*, references who gave the testimonial

### "extensions" - an association between an order and a reservation for a rental extension
* "**order_id**" (integer) primary key to *orders*, references which order has been extended
* "item_id" (integer) - primary key to *reservations*, calls the reservation which contains the new ext. metadata
* "renter_id" (integer) - primary key to *reservations*, calls the reservation which contains the new ext. metadata
* "res_date_start" (date) - primary key to *reservations*, calls the reservation which contains the new ext. metadata
* "**res_date_end**" (date) - primary key to *reservations*, calls the reservation which contains the new ext. metadata

### "logistics" - a table containing core information about dropoff/pickup logistics
* "**dt_sched**" (timestamp) - when was the dropoff/pickup request submitted, defaults to UTC timezone
* "notes" (text) - user provides additional notes to make dropoff/pickup easier
* "referral" (varchar) - how did the user hear about Hubbub, 100 character limit
* "timeslots" (text) - when is the user available for dropoff/pickup
* chosen_time time,

* "**renter_id**" (integer) - primary key to *renters*, who requested the dropoff/pickup
* "address_num" (integer) - primary key to *addresses*, referencing where to dropoff/pickup the item
* "address_street" (varchar) - primary key to *addresses*, referencing where to dropoff/pickup the item
* "address_apt" (varchar) - primary key to *addresses*, referencing where to dropoff/pickup the item
* "address_zip" (varchar) - primary key to *addresses*, referencing where to dropoff/pickup the item

### "pickups" - decorator on top of *logistics* data
* "**pickup_date**" (date) - when should the item be picked up, CHECK that pickup_date > dt_sched

* "**dt_sched**" (timestamp) - primary key to *logistics*, referencing where core data is
* "**renter_id**" (integer) - primary key to *logistics*, referencing where core data is

### "dropoffs" - decorator on top of *logistics* data
  * "**dropoff_date**" (date) - when should the item be dropped off, CHECK that dropoff_date > dt_sched

  * "**dt_sched**" (timestamp) - primary key to *logistics*, referencing where core data is
  * "**renter_id**" (integer) - primary key to *logistics*, referencing where core data is

### "issues" - for reporting issues with Hubbub as a service
* "**id**" (SERIAL) - id for issue
* "complaint" (text) - the content for the issue
* "link" (varchar) - the part of the Hubbub website ecosystem where the issue occurred
* "user_id" (integer) - the user submitting the issue report
* "resolution" (text) - how was the issue resolved
* "is_resolved" (boolean) - T/F has the issue been resolved, defaults to FALSE,
* "dt_created" (timestamp) - datetime of when the issue was reported, defaults to UTC timezone

### "tags" - for categorizing items
* "**tag_name**" (varchar) - the name of the item category

## ASSOCIATIONS
The following tables do not have their own Blubber objects.
They help define the relationships or 'associations' between multiple tables

### "tagging" -  associates items to tags in a many to many relationship
* "item_id" integer
* "tag_name" varchar (75)

### "order_pickups" - associates a pickup scheduling to orders in a one to many relationship
* "order_id" (integer)
* "pickup_date" (date)
* "renter_id" (integer)
* "dt_sched" (timestamp)

* "dt_completed" (timestamp) - when was the pickup completed by a courier

### "order_dropoffs" - associates a dropoff scheduling to orders in a one to many relationship
* "order_id" (integer)
* "dropoff_date" (date)
* "renter_id" (integer)
* "dt_sched" (timestamp)

* "dt_completed" (timestamp) - when was the pickup completed by a courier

### "shopping" - associates items to user carts in a many to many relationship
* "cart_id" (integer)
* "item_id" (integer)

### "listers" - subtype of *users*
* "lister_id" (integer)

### "couriers" - subtype of *users*
* "courier_id" (integer)

### "renters" - subtype of *users*
* "renter_id" (integer)
