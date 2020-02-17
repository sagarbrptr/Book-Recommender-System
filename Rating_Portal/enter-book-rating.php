<?php

error_reporting(0);

$bookRating = $_POST['bookRating'];
$barcode = $_POST['barcode'];
$regId = $_POST['registerationID'];
$title = $_POST['bookTitle'];

// foreach($bookRating as &$value)
// {
//     echo "$value";
//     echo "<br>";
// }

// echo $regId. "<br>";

// foreach($barcode as &$value)
// {
//     echo "$value";
//     echo "<br>";
// }

// for ($i = 0; $i < count($title); $i++)
// {
//     echo "$title[$i]";
//     echo "<br>";
// }

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





for($i = 0; $i < count($bookRating); $i++)
{
    $getTitle = "select title from books where barcode = '" .$barcode[$i]. "' union all select title from books_db where barcode = '" .$barcode[$i]. "' ;";
    $result = mysqli_query($conn, $getTitle);

    if($result === FALSE)
    {
        echo "Failed";
        break;
    }

    while($row = mysqli_fetch_assoc($result))
    {
        $getTitle = $row["title"];
    }

    $getBarCodeFromBTMap = "select barcode from bt_map where title = '" .$getTitle. "' ;";
    $result = mysqli_query($conn, $getBarCodeFromBTMap);

    if($result === FALSE)
    {
        echo "Failed";
        break;
    }

    while($row = mysqli_fetch_assoc($result))
    {
        $getBarCodeFromBTMap = $row["barcode"];
    }


    // echo $barcode[$i]."<br>";
    $sql = "REPLACE INTO ratings(cardnumber,barcode,rating) VALUES ('" . $regId. "', '" . $getBarCodeFromBTMap. "', '" . $bookRating[$i]. "');";

    // echo "$getTitle <br> $getBarCodeFromBTMap <br> $sql";
    // echo $sql;
    $result = mysqli_query($conn, $sql);

    if($result === TRUE)
    {
        // echo "record " .$i. " added<br>";
    }

    else
    {
        echo "failed<br>";
        break;
    }
}

?>

<!doctype html>

<html>

    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">
    </head>

    <body>

      
                <img style="margin-left: 30%; margin-top: 10%; width: 30%;" src = "thank-you-meme.jpeg"/>

    </body>
</html>

<?php
mysqli_close($conn);
?>