    function checkForm()
    {
        var bookRating = [];
        bookRating = document.forms["ratingForm"]["bookRating"];

        for(var rating in bookRating)
        {
            
            if(isNaN(rating) || !isInteger(rating) || rating < 0 || rating > 10)
            {
                window.alert("Rating needs to be integer in range of 1-10");
                return false;
            }
                
        }
    }