
import sqlite3 as db


    #clear member table
def clear_member(conn):

    delete = "DELETE FROM members"

    try:
        cur = conn.cursor()
        cur.execute(delete)
        conn.commit()
        print("CLEAR_MEMBERS SUCCESS")
    except:
        print("CLEAR_MEMBERS ERROR: failed to delete all members")



    #clear teams table
def clear_team(conn):

    delete = "DELETE FROM teams"

    try:
        cur = conn.cursor()
        cur.execute(delete)
        conn.commit()
        print("CLEAR_TEAMS SUCCESS")
    except:
        print("CLEAR_TEAMS ERROR: failed to delete all teams")



    # delete member to team connection
def delete_member(conn, ID):
    
    delete = "DELETE FROM members WHERE id=?"
    ID = (ID,)

    try:
        cur = conn.cursor()
        cur.execute(delete, ID)
        conn.commit()
        print(f"DELETE SUCCESS: deleteted {ID}")
    except:
        print(f"DELETE ERROR: failed to delete {ID}")


    #fetch all signed members of a group 
def fetch_group(conn, role):
    
    fetch = f"SELECT id FROM members WHERE team = ?"

    try:
        curs = conn.cursor()
        curs.execute(fetch, (role,))
        rows = curs.fetchall()
        print(f"FETCH_GROUP SUCCESS: fetched {rows}")
    except:
        print("FETCH_GROUP ERROR")
    finally:
        return rows


    # fetch get out of database from members
def fetch_members(conn, ID, get):

    if get not in ["name","team"]:
        print("FETCH_MEMBERS ERROR: Request denied tue to strange column name")
        return

    fetch = f"SELECT {get} FROM members WHERE id = ?"

    try:
        curs = conn.cursor()
        curs.execute(fetch, (ID,))
        rows = curs.fetchall()
        print(f"FETCH_MEMBERS SUCCESS: fetched {rows}")
    except:
        print(f"FETCH_MEMBERS ERROR: could not fetch {get} from {ID}")
    finally:
        return rows



    # fetch get out of database from team 
def fetch_teams(conn, role, get):

    if get not in ["points","round1","round2","round3","round4","voice_channel","text_channel"]:
        print("FETCH_TEAMS ERROR: Request denied due to strange column name")
        return

    fetch = f"SELECT {get} FROM teams WHERE role = ?"
    
    try:
        curs = conn.cursor()
        curs.execute(fetch, (role,))
        rows = curs.fetchall()
        print(f"FETCH_TEAMS SUCCESS: fetched {rows}")
    except:
        print(f"FETCH_TEAMS ERROR: could not fetch {get} of {role}")
    finally:
        return rows



    #update points of a team in phase X
def update_points(conn, phase, points, role):
    
    phase = "round" + str(phase)
    
    old = fetch_teams(conn, role, "points")
    new = old[0][0] + points

    info = (points, new, role)
    update = f""" UPDATE teams SET {phase} = ?, points = ? WHERE role = ?"""

    try:
        cur = conn.cursor()
        cur.execute(update, info)
        conn.commit()
        print(f"UPDATE SUCCESS: Updated {info}")
    except:
        print(f"UPDATE ERROR: Update failed with {info}")



    #get fd of db and add column to able members
def add_member(conn, ID, name, role):
    
    column = (ID, name, role)
    add = """ INSERT INTO members(id, name, team) VALUES (?,?,?) """

    try:
        curs = conn.cursor()
        curs.execute(add, column)
        conn.commit()
        print(f"MEMBER SUCCESS: Member {name} has been added to database")
    except:
        print(f"MEMBER ERROR:Failed adding member with {column}")
    finally:
        return curs.lastrowid



    #get fd of db and add column to table teams
def add_team(conn, role, name, tchannel, vchannel):
    
    column = (role,name,tchannel,vchannel, 0, 0, 0, 0, 0)
    add = """ INSERT INTO teams(role, name, text_channel, voice_channel, round1, round2, round3, round4, points) VALUES (?,?,?,?,?,?,?,?,?) """

    try:
        curs = conn.cursor()
        curs.execute(add, column)
        conn.commit()
        print(f"TEAM SUCCESS: Team {name} has been added to database")
    except:
        print(f"TEAM ERROR: Failed adding team with {column}")
    finally:
        return curs.lastrowid



    #establishing connection to sql file; returns filedescriptor
def create_connection(db_file):

    conn = None

    try:
        conn = db.connect(db_file)
        return conn
    except:
        print("CREATE ERROR: Connection was not created")
    finally:
        return conn



    #create a table in SQL (table_info) at file of fd conn
def create_table(conn, table_info):

    try:
        c = conn.cursor()
        c.execute(table_info)
        print("CREATE SUCCESS: table has been created")
    except:
        print("CREATE ERROR: Error creating table")








