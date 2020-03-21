delimiter $$

create trigger after_bookRequest_insert 
after insert 
on  bookRequest for each row

begin

    update libraryRecommendation set requestCount = requestCount + 1 where srNo = new.srNo;

end $$

delimiter ;