

<?php

error_reporting(0);
$regId =  $_POST["registerationID"];


$servername = "mydemoserverbrs.mysql.database.azure.com";
$username = "sagar@mydemoserverbrs";
$password = "GroupNo13";
$dbname = "brs_db";

$conn = mysqli_init();
mysqli_ssl_set($conn,NULL,NULL, "BaltimoreCyberTrustRoot.crt.pem", NULL, NULL) ; 
mysqli_real_connect($conn,$servername, $username, $password, $dbname, 3306, MYSQLI_CLIENT_SSL);
if (mysqli_connect_errno($conn)) {
die('Failed to connect to MySQL: '.mysqli_connect_error());
}
// Create connection 
// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}


$checkUser = "select name from user where barcode_no = '" .$regId. "' ;";
$result = mysqli_query($conn, $checkUser);

if (mysqli_num_rows($result) <= 0)
{    
    exit("<h1>Enter a valid Registration number</h1>");
} 

//Donated books
$sql1 = "select distinct title, barcode from books_db where barcode in (select barcode from transaction where cardnumber='" . $regId . "') group by title;";
// get all books
$sql = "select distinct title, barcode from books where barcode in (select barcode from transaction where cardnumber='" . $regId . "') group by title "." union all ".$sql1 ;

$result = mysqli_query($conn, $sql);

?>


<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.1/css/all.css" integrity="sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf" crossorigin="anonymous">
        <link rel="stylesheet" href="//netdna.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css">
    </head>
    <style>
        div.stars {
  width: 270px;
  display: inline-block;
}

input.star { display: none; }

label.star {
  float: right;
  padding: 10px;
  font-size: 36px;
  color: #444;
  transition: all .2s;
}

input.star:checked ~ label.star:before {
  content: '\f005';
  color: #FD4;
  transition: all .25s;
}

input.star-5:checked ~ label.star:before {
  color: #FE7;
  text-shadow: 0 0 20px #952;
}

input.star-1:checked ~ label.star:before { color: #F62; }

label.star:hover { transform: rotate(-15deg) scale(1.3); }

label.star:before {
  content: '\f006';
  font-family: FontAwesome;
}
    </style>
    <body>
        <div class="instruction" style="padding-left : 20%; font-family: 'Times New Roman', Times, serif;
                                        font-size : 50px ;background-color : #8231393d; font-size : 50px; padding-bottom : 20px ">
            Enter ratings for your issued books.
        </div>
    <div class="card" style="border: 1px solid white ; width: 80%; margin-top : 5%;" >
        <div class="card-body">            
            <form name="ratingForm" action="enter-book-rating.php" method="POST" onsubmit="return checkForm()">

                <div class="form-group">

                    <?php
                        $bookCount = 0;

                        if (mysqli_num_rows($result) > 0) 
                        {
                            // output data of each row
                            
                            while($row = mysqli_fetch_assoc($result)) 
                            {                                
                                echo ($bookCount + 1). ". " .$row["title"]. "<label style='color:red'>*</label>";

                    ?>
                        <br>
                         <div class="stars" float = "right">
                            <input class="star star-5"  type="radio" name="bookRating[<?php echo $bookCount;?>]" id="star-5 <?php echo $bookCount;?>" value=5 required />
                                <label class="star star-5" for="star-5 <?php echo $bookCount;?>"></label>
                                <input class="star star-4"  type="radio" name="bookRating[<?php echo $bookCount;?>]" id="star-4 <?php echo $bookCount;?>" value=4 />
                                <label class="star star-4" for="star-4 <?php echo $bookCount;?>"></label>
                                <input class="star star-3" type="radio" name="bookRating[<?php echo $bookCount;?>]" id="star-3 <?php echo $bookCount;?>" value=3 />
                                <label class="star star-3" for="star-3 <?php echo $bookCount;?>"></label>
                                <input class="star star-2" type="radio" name="bookRating[<?php echo $bookCount;?>]" id="star-2 <?php echo $bookCount;?>" value=2 />
                                <label class="star star-2" for="star-2 <?php echo $bookCount;?>"></label>
                                <input class="star star-1" type="radio" name="bookRating[<?php echo $bookCount;?>]" id="star-1 <?php echo $bookCount;?>" value=1 />
                                <label class="star star-1" for="star-1 <?php echo $bookCount;?>"></label>

                            <br><br>                                
                        
                        </div>
                        <br>
                        <input type="hidden" name="barcode[<?php echo $bookCount;?>]" value =<?php echo $row["barcode"]; ?> >
                        <input type="hidden" name="bookTitle[<?php echo $bookCount;?>]" value =<?php echo $row["title"]; ?> >

                   

                    <?php  
                                 $bookCount++;  
                            }
                    ?>

                    <input type="hidden" name="registerationID" value =<?php echo $regId; ?> >
                    <button type="submit" class="btn btn-primary">Submit</button>
                    </div>
                    <?php       
                        }

                        else 
                        {
                            echo "<h4>You have not issued any books in this academic year.</h4>";
                            echo "<br>";
                        }

                        

                        mysqli_close($conn);
                    ?>
                    
            </form>
        </div>
    </div>
    
    <!-- <script type="text/javascript" src="submit-reg-id-script.js"></script> -->
    <script>
    function checkForm()
    {
        var bookRating = [];
        bookRating = document.forms["ratingForm"]["bookRating"];
        window.alert(bookRating[0].value);
        for(var i = 0; i < bookRating.length; i++)
        {
            
            if( bookRating[i].value == " " || bookRating[i].value == "" || bookRating[i].value < 1 || bookRating[i].value > 10)
            {
                window.alert("Rating needs to be integer in range of 1-10");
                return false;
            }
                
        }

        return true;
    }
    

    </script>

    </body>
</html>