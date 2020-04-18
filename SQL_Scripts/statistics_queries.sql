-- Most Issued Books
select books.title as title,
    count(books.title) as count
from books,
    transaction
where  transaction.barcode = books.barcode
group by title
order by count(books.title) desc limit 20;

-- Most Requested Books
select *
from libraryRecommendation
where requestCount != 1
order by requestCount desc
limit 10;

--Most Frequent Reader
select cardnumber, count(cardnumber) as count
from transaction
group by cardnumber
order by count(cardnumber) desc;

--Highest Rated book according to rating and isuue count
select barcode, rating, count(barcode)
from ratings
group by barcode
order by rating desc, count(barcode) desc;