-- If the table has a multiple-column index, 
-- any leftmost prefix of the index can be used by the optimizer
-- to look up rows. 
-- For example, if you have a three-column index
-- on (col1, col2, col3), 
-- you have indexed search capabilities on (col1), (col1, col2),
-- and (col1, col2, col3).

-- bt_map
create index titleIndex
on bt_map(title);

-- books
create index barcodeTitleIndex
on books(barcode, title);

-- libraryRecommendation
create index titleAuthorIndex
on libraryRecommendation(bookTitle, author);

create index srNoRequestCountIndex
on libraryRecommendation(srNo, requestCount);

-- transaction
create index barcodeCardnumberIndex
on transaction(barcode, cardnumber);

-- ratings
create index barcodeCardnumberIndex
on ratings(barcode, cardnumber);

-- user
create index cardnumberPasswordIndex
on user(cardnumber, password);