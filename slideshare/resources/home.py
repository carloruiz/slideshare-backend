from flask_restful import Resource
from slideshare.db import db_engine, db_metadata
from slideshare.utils.db import execute_query
from collections import defaultdict

HOME_SQL = '''SELECT  s.*, t.id as tag_id, t.tag, u.username
FROM slide_tag st
INNER JOIN slide s ON s.id = st.slide
INNER JOIN tag t ON t.id = st.tag
INNER JOIN "user" u ON u.id = s.userid
INNER JOIN (
    SELECT st.tag, count(st.tag) as counts
    FROM slide_tag AS st
    GROUP BY st.tag
    ORDER BY counts DESC
) AS c ON t.id = c.tag
ORDER BY c.counts DESC;'''


class Home(Resource):
    def order_by_tag(self, queryset):
        # TODO limit the number of tags in the query or use faster datastuct
        if not queryset:
            return 500
        columns = queryset[0].keys()
        result = defaultdict(list)
        ordering = []
        for row in queryset:
            if row['tag'] not in ordering: ordering.append(row['tag'])
            result[row['tag']].append(row)
        return result, ordering


    def get(self):
        result, code  = execute_query(db_engine, HOME_SQL, None)
        if code == 500:
            return {}, 500
        if not result:
            return {}, 200
        
        slides, ordering = self.order_by_tag(result)
        return {
            'slides': slides,
            'ordering': ordering
        }
