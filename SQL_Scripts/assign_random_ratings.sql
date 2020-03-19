DELIMITER //
For a particular user(reg_id) retrieve distinct books issued 
DROP PROCEDURE IF EXISTS IterateOverBooks//
CREATE PROCEDURE IterateOverBooks(IN reg_id VARCHAR(255))
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE book_id VARCHAR(255);
    DECLARE book_id_from_bt_map VARCHAR(255);
    DECLARE book_title VARCHAR(255);
    DECLARE random_rating INT;
    DECLARE booklist CURSOR FOR (SELECT DISTINCT title, barcode FROM books where barcode in (select barcode from transaction where cardnumber=reg_id) group by title) UNION ALL (SELECT DISTINCT title, barcode FROM books_db where barcode in (select barcode from transaction where cardnumber=reg_id) group by title);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
        
    OPEN booklist;
    
    get_book:LOOP
        FETCH booklist into book_title,book_id;
        IF done THEN 
	        LEAVE get_book;
        END IF;    
        -- Get random rating in between [1-5]
        SELECT FLOOR(RAND()*(5-1+1))+1 INTO random_rating;
        SELECT barcode FROM bt_map WHERE title = book_title  limit 1 INTO book_id_from_bt_map;
        -- SELECT book_title,book_id,book_id_from_bt_map;
        IF NOT EXISTS (SELECT * FROM ratings 
                   WHERE barcode = book_id_from_bt_map
                   AND cardnumber = reg_id)
            THEN
                INSERT INTO ratings(cardnumber,barcode,rating,valid) VALUES (reg_id,book_id_from_bt_map,random_rating,0);
            END IF;
        END LOOP;
    
    CLOSE booklist;
END//
DELIMITER ;

DELIMITER //
-- Main procedure to get list of all users who have issued any books from transaction table
DROP PROCEDURE IF EXISTS AssignRandomRatings//
CREATE PROCEDURE AssignRandomRatings()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE reg_id VARCHAR(255);
    DECLARE userlist CURSOR FOR SELECT DISTINCT cardnumber FROM transaction;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
        
    OPEN userlist;
    
    get_user:LOOP
        FETCH userlist into reg_id;
        IF done THEN 
	        LEAVE get_user;
        END IF;    
        CALL IterateOverBooks(reg_id);        
    
        END LOOP;
    
    CLOSE userlist;
END//

--------------------------------------------------------------------------
DELIMITER ;

CALL AssignRandomRatings();