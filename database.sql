create database booksera 
use booksera

---user1

create table buyer 
(
username varchar(255) not null,
email varchar (255) not null,
phone bigint,
password  varchar(255) not null
)

--books info

create table books
(
isbn varchar(255)  not null,
author varchar(255) not null,
year integer not null,
title varchar(255) not null,
price varchar(255) not null
)

--for reviews

create table reviews 

(
isbn varchar(255) ,
username varchar(255),
review varchar(255) not null,
rating int not null
)


--for user2 

create table publisher
(
 username varchar(255) not null,
 phone bigint,
 address varchar(255) not null,
 password varchar(255) not null
)

--books_publish

create table publish
(
author varchar(255) ,
isbn varchar(255) not null,
year bigint not null,
details varchar(255) not null,
title varchar(255) not null
)


--admin
create table admin
( 
password varchar(15) not null,
email varchar(255) not null,
username varchar(255) not null
)


--booksorder

create table books_order
(
order_id serial ,
username varchar(255) not null,
address varchar(255) not null,
phone bigint not null,
isbn varchar(255) not null,
price int
)

--bank details

create table payment_details

(
 order_id serial ,
 card_no int not null,
 pin varchar (10) not null
)


--Primary keys
ALTER TABLE buyer
   ADD CONSTRAINT buyer_pk
   PRIMARY KEY (username);
   
ALTER TABLE books
   ADD CONSTRAINT books_pk
   PRIMARY KEY (isbn);
   
ALTER TABLE publisher
   ADD CONSTRAINT publisher_pk
   PRIMARY KEY (username);
   
ALTER TABLE books_order
   ADD CONSTRAINT orderbooks_pk
   PRIMARY KEY (order_id);
   
   
   
--Foreign keys

ALTER TABLE reviews
   ADD CONSTRAINT buyerfk
   FOREIGN KEY (username)
   REFERENCES buyer (username);
   
ALTER TABLE reviews
   ADD CONSTRAINT booksfk
   FOREIGN KEY (isbn)
   REFERENCES books (isbn);
   
ALTER TABLE publish
   ADD CONSTRAINT publishfk
   FOREIGN KEY (author)
   REFERENCES publisher(username);

ALTER TABLE books_order
   ADD CONSTRAINT userfk
   FOREIGN KEY (username)
   REFERENCES buyer(username);
   
ALTER TABLE books_order
   ADD CONSTRAINT booksfk
   FOREIGN KEY (isbn)
   REFERENCES books(isbn);

ALTER TABLE payment_details
   ADD CONSTRAINT orderfk
   FOREIGN KEY (order_id)
   REFERENCES books_order(order_id);


--admin views
create view admin_view_publish as
select title,author,isbn from publish

create view admin_view_books as 
select * from books

create  view admin_view_buyers as
select username,email from buyer


--buyer views
create view buyer_view 
as select * from books



--Publisher_books_functions
CREATE FUNCTION publisher_books(username varchar) RETURNS table(isbn varchar,title varchar)

LANGUAGE SQL

AS $$

select isbn,title from publish where author=username
$$


--Trigger function for adding buyer


 CREATE OR REPLACE FUNCTION function_copy() RETURNS TRIGGER AS
$BODY$
BEGIN
   
         INSERT INTO admin(password,email,username)
         VALUES(new.password,new.username,new.email);
		   raise notice 'new user added';

           RETURN new;
END;
$BODY$
language plpgsql;

CREATE TRIGGER trig_copy
     AFTER INSERT ON buyer
     FOR EACH ROW
     EXECUTE PROCEDURE function_copy();
  

--User buyer privileges
create user buyer password '1234'
grant select on books to buyer
grant insert on reviews to buyer
grant select on reviews to buyer
grant select, insert on buyer to buyer
grant insert,select on books_order to buyer
grant select on payment_details to buyer

--User publisher  privileges
create user publisher password 'publisher'
grant select,insert on publisher to publisher 
grant select,insert on publish to publisher

--user admin privileges
create user admin password 'admin'
grant select,insert,delete on publish to admin
grant select,insert on books to admin
grant select on publisher to admin