import csv
import os
from student.views import DB

class ML:

    def createCSV(self, database):
        writer = csv.writer(open('ml/Apche_Spark/ratings.csv', 'wb'))   
        # writer.writerow(['userId', 'bookId', 'rating'])             

        selectQuery = "select userSrNo, bookSrNo, rating from ratings"
        errorMsg = "Error in selecting from ratings"
        row = database.select(selectQuery, errorMsg)

        if row : 
            for i in row:
                writer.writerow([i[0], i[1], i[2]])
    
    def runRecommendations(self):
        # Run recommendation script
        # This will generate recommendation file
        projectPath = os.getcwd()
        os.system("cd " + projectPath + "\\ml\\Apche_Spark & bin\\spark-submit ..\\recommendation.py")