import csv

def writeCSV(RDD) : 
    writer = csv.writer(open('ml/Apache_Spark/recomendations.csv', 'w'))

    for i in RDD:
        writer.writerow(RDD)