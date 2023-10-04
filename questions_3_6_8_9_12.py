import datetime
from haversine import haversine
from DbConnector import DbConnector
from tabulate import tabulate


class Questions_3_6_8_9_12:
    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor

    def question_3(self):
        query = """SELECT User.id, COUNT(Activity.id)
                FROM User, Activity
                WHERE User.id = Activity.user_id
                GROUP BY User.id
                ORDER BY COUNT(Activity.id) DESC
                LIMIT 15;"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))

    def question_6(self):
        query = """SELECT DISTINCT a1.*
                FROM Activity a1, Activity a2
                WHERE a1.id != a2.id
                    AND a1.user_id = a2.user_id
                    AND a1.transportation_mode = a2.transportation_mode
                    AND a1.start_date_time = a2.start_date_time
                    AND a1.end_date_time = a2.end_date_time;
            """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))

    def question_9(self):
        query = """SELECT User.id, SUM(tp2.altitude-tp1.altitude)/ 3.281 AS altitude_in_meters
                FROM User, Activity, TrackPoint tp1, TrackPoint tp2
                WHERE User.id = Activity.user_id
                    AND Activity.id = tp1.activity_id
                    AND Activity.id = tp2.activity_id
                    AND tp1.id = tp2.id-1
                    AND tp1.altitude < tp2.altitude
                    AND tp1.altitude != -777
                    AND tp2.altitude != -777
                GROUP BY User.id
                ORDER BY SUM(tp2.altitude-tp1.altitude) DESC
                LIMIT 15;"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))

        def question_9(self):
            query = """SELECT User.id, SUM(tp2.altitude-tp1.altitude)/ 3.281 AS altitude_in_meters
                    FROM User, Activity, TrackPoint tp1, TrackPoint tp2
                    WHERE User.id = Activity.user_id
                        AND Activity.id = tp1.activity_id
                        AND Activity.id = tp2.activity_id
                        AND tp1.id = tp2.id-1
                        AND tp1.altitude < tp2.altitude
                        AND tp1.altitude != -777
                        AND tp2.altitude != -777
                    GROUP BY User.id
                    ORDER BY SUM(tp2.altitude-tp1.altitude) DESC
                    LIMIT 15;"""
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            print(tabulate(rows, headers=self.cursor.column_names))

    def question_12(self):
        query = """SELECT rq.u_id as id_user, rq.a1_tm as most_used_transportation_mode
                FROM User, (
                    SELECT User.id AS u_id, a1.transportation_mode AS a1_tm, COUNT(a1.transportation_mode) AS count_tm1
                    FROM User, Activity a1
                    WHERE User.id = a1.user_id
                    AND User.has_labels = 1
                    AND a1.transportation_mode IS NOT NULL
                    GROUP BY u_id, a1_tm
                    ORDER BY u_id, count_tm1 DESC
                ) rq, User u
                WHERE u.id = rq.u_id
                AND rq.count_tm1 IN (SELECT MAX(subq.count_tm) FROM (SELECT User.id AS id_u, a.transportation_mode AS a_tm, COUNT(a.transportation_mode) AS count_tm FROM User, Activity a WHERE User.id = a.user_id AND User.has_labels = 1 AND a.transportation_mode IS NOT NULL AND User.id = rq.u_id GROUP BY id_u, a_tm) subq)
                GROUP BY rq.u_id, rq.a1_tm
                ORDER BY rq.u_id;"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        keys = [a for (a, b) in rows]
        values = [b for (a, b) in rows]
        dictionary = dict(zip(keys, values))
        dictionary_as_list = [(a, b) for a, b in dictionary.items()]
        print(tabulate(dictionary_as_list, headers=self.cursor.column_names))

    def question_8(self):
        query = """SELECT User.id, Activity.id, Activity.start_date_time, Activity.end_date_time, TrackPoint.lat, TrackPoint.lon, TrackPoint.date_time
                FROM User, Activity, TrackPoint
                WHERE User.id = Activity.user_id
                    AND Activity.id = TrackPoint.activity_id"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        activity_keys = [b for (a, b, c, d, e, f, g) in rows]
        activity_values = [{"start": c, "end": d, "user_id": a} for (a, b, c, d, e, f, g) in rows]
        trackpoints_values = [{"coords": (e, f), "date_time": g} for (a, b, c, d, e, f, g) in rows]
        dictionary_of_activities = dict() # create a dictionary of activities, with start time, end time and trackpoints
        for i in range(0, len(activity_keys)):
            if not activity_keys[i] in dictionary_of_activities.keys():
                dictionary_of_activities[activity_keys[i]] = activity_values[i]
                dictionary_of_activities[activity_keys[i]]["trackpoints"] = [trackpoints_values[i]]
            else:
                dictionary_of_activities[activity_keys[i]]["trackpoints"].append(trackpoints_values[i])

        results = dict() # storing the pairs of users that have been close to eachother (in a dictionary to easily avoid duplicates)
        for x in dictionary_of_activities.values():
            for y in dictionary_of_activities.values():
                if x["user_id"] < y["user_id"] and ((x["start"] <= y["end"] and x["end"] >= y["start"]) or (
                        x["start"] >= y["end"] and x["end"] <= y["start"])): # compare start and end date to avoid useless computation
                    for v in x["trackpoints"]:
                        for w in y["trackpoints"]:
                            if abs(v["date_time"] - w["date_time"]) <= datetime.timedelta(seconds=30) and haversine(
                                    v["coords"], w["coords"]) / 3.281 < 50 * 2:
                                if not x["user_id"] in results.keys(): # other dictionary to easily avoid duplicates
                                    results[x["user_id"]] = dict()
                                results[x["user_id"]][y["user_id"]] = 1

        cpt = 0
        for r in results:
            for v in results[r]:
                cpt = cpt+1
        cpt=cpt*2 # because it takes two users to be close to each other
        print("Number of users that have been close: ", cpt)

def main():
    program = Questions_3_6_8_9_12()
    program.question_8()


if __name__ == '__main__':
    main()
