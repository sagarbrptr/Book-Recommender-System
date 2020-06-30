# BRS

## Running Project
1. Run requirements.txt
    ```
    pip install -r requirements.txt
    ```
2. In BRS source folder run following command
    ```
    python manage.py runserver
    ```

## Functionalities
### For Students
1. Issue History
2. Rating the books
3. Checking personalized recommendation
4. Recommending the libraries

### For Librarian
1. Issuing Book
2. Managing Book Inventory 
   - Add Book
   - Remove Book
3. Check statistics using bar graphs 


## Salient Features
1. ALS algorithm used for recommendations
2. All Database Transactions done as transactions.
3. Indexing done on database for faster operations.
4. MemCached used as caching server
5. Responsive UI


## Dependency : 

1. PyMySql   : pip install PyMySQL
2. MemCached : sudo apt-get install memcached
3. python-memcached : pip install python-memcached
3. Requests : pip install requests
4. scikit-learn : pip install -U scikit-learn
5. numpy : pip install numpy
6. Django Rest Framework : pip install djangorestframework
