--User table

DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    token BINARY,
    money REAL
);

INSERT INTO users (user_id, password, email, money)
VALUES ('James19', 'pbkdf2:sha256:150000$afW4Q44w$a52720eb70132b5afb0fbd7519fabdabae0d9fcd4068507585a8120951965f9b', 'james@gmail.com', 100), --password123
        ('test1', 'pbkdf2:sha256:150000$qOuIWFlC$12a067187aa1f98fbc1f5ec68ca9716a430ed88dca2cbc7886c8144502da25f5', 'notarealemail@gmail.com', 560), --notarealpassword
        ('paddy', 'pbkdf2:sha256:150000$9gBfLwwh$bc4cd5bb2fe8316bfc4c03a3711c211c31b3e34de1844009062bf6bfa779a8d8', 'paddy@gmail.com', 45), --drowssap


--admin table

DROP TABLE IF EXISTS admins;

CREATE TABLE admins
(
    admin_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

INSERT INTO admins (admin_id, password)
VALUES ('REDACTED', 'pbkdf2:sha256:150000$t4AhEeTz$c2353e3fffbf53515667401bbd96f4a4f8332e315a7f0b3b9be1d123d7edc470'); --ihatewombats


--item table

DROP TABLE IF EXISTS items;

CREATE TABLE items
(
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    description TEXT
);

INSERT INTO items (item, price, stock, description)
VALUES
('Colt 45', 6.99, 15, 'A malt liquor beer. With only 5.6% alcohol content and a cheap price of €6.99 for a 40oz bottle, this is a perfect brew for the underaged boozer.'),
('Linden Village', 7.99, 15, 'Another underaged classic. This inexpensive brew packs a powerful punch, despite its relatively low alcohol percentage. (2 litres)'),
('Absinthe', 69.99, 5, 'A powerful concoction containing over 90% alcohol per volume. This dangerous spirit is a friend of the seasoned boozer. (500 ml)'),
('Nascar Gasoline', 119.99, 3, 'Lovingly crafted from the high quality X16 5Gal brand of fuel, this drink belongs in the hands of a classy boozer. (Sold by the gallon)'),
('Pure Ethanol', 79.99, 5, 'You asked. We delivered. 100% pure. For those who enjoy their ethanol without a modicum of impurity. (1 litre)'),
('Hand Sanitiser', 14.99, 15, 'Perfect for the pandemic! With this trusty brew you will never skip a chance to wash your hands. (500 ml)'),
('Listerene', 7.99, 15, 'For those early morning risers looking for a quick buzz to start the morning strong! (500ml)'),
('Monke Gin', 64.99, 5, 'Return to Monke. (500ml)'),
('Fermented Cat', 249.99, 3, 'Fermented from the finest cats by our expert fermenters over a gruelling 6 month period. (500ml)'),
('Moonshine', 39.99, 10, 'Our own special brew of moonshine. For the exerienced boozer. (500 ml)'),
('Isopropyl', 14.99, 15, 'Taken straight from a college laboratory, this intense brew is fitting for expert boozers looking for cheap thrills. (1 litre)'),
('Wood Alcohol', 29.99, 10, 'A favourite among our staff, this potent brew is for veteran boozers ONLY. Killed my son, cousin, and uncle. (500 ml)');


-- review table

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    review_number INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    user_id TEXT,
    rating INTEGER,
    review TEXT
);

INSERT INTO reviews (item_id, user_id, rating, review)
VALUES (1, 'James19', 4, 'yummy');

-- suggestions table

DROP TABLE IF EXISTS suggestions;

CREATE TABLE suggestions
(
    suggestion_number integer PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    suggestion TEXT
);

INSERT INTO suggestions( user_id, suggestion)
VALUES ('James19', 'cool');

DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    order_number integer PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    address TEXT,
    items TEXT
);

SELECT * FROM orders;