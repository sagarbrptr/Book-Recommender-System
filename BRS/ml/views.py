import csv
from student.views import DB

class ML:

    def createCSV(self, database):
        writer = csv.writer(open('ml/ratings.csv', 'wb'))   
        writer.writerow(['userId', 'bookId', 'rating'])             

        selectQuery = "select userSrNo, bookSrNo, rating from ratings"
        errorMsg = "Error in selecting from ratings"
        row = database.select(selectQuery, errorMsg)

        if row : 
            for i in row:
                writer.writerow([i[0], i[1], i[2]])
