import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import psycopg2

dbSettings = {
    "host": settings.DATABASES["default"]["HOST"],
    "database": "postgres",
    "user": settings.DATABASES["default"]["USER"],
    "password": settings.DATABASES["default"]["PASSWORD"],
    "port": settings.DATABASES["default"]["PORT"],
}

def checkConnection(request):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**dbSettings)
		
        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
	    # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return HttpResponse(error, status=500)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    
    return HttpResponse("Worked")

##############################################
def createTable(request):
    """ create tables in the PostgreSQL database"""
    # TODO get name of db from request
    commands = (
        """
        CREATE TABLE profiles (
            name VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            type VARCHAR(255) NOT NULL
        )
        """,
    )
    conn = None
    try:
        # read the connection parameters
        # connect to the PostgreSQL server
        config = dbSettings
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return HttpResponse(error, status=500)
    finally:
        if conn is not None:
            conn.close()
    return HttpResponse("Worked")


##############################################
# profile is in json format
def insertUser(profile):
    name = "testguy" #profile["nickname"]
    email = "testguy@test.com" #profile["email"]
    typeOfUser = "user" #profile["role"]


    sql = """INSERT INTO profiles(name,email,type)
    VALUES(%s,%s,%s);"""
    conn = None
    try:
        # read database configuration
        params = dbSettings
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (name,email,typeOfUser,))
        # get the generated id back
        # student_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return HttpResponse(error, status=500)
    finally:
        if conn is not None:
            conn.close()
    
    return HttpResponse("Worked")