from flask_restful import Resource
from slideshare.db import db_engine, db_metadata
from collections import defaultdict

HOME_SQL = '''SELECT  s.*, t.id as tag_id, t.tag, u.username
FROM slide_tag st
INNER JOIN slide s ON s.id = st.slide
INNER JOIN tag t ON t.id = st.tag
INNER JOIN "user" u ON u.id = s.user
INNER JOIN (
    SELECT st.tag, count(st.tag) as counts
    FROM slide_tag AS st
    GROUP BY st.tag
    ORDER BY counts DESC
) AS c ON t.id = c.tag
ORDER BY c.counts DESC;'''




class Home(Resource):
    def queryset_to_dict(self, queryset):
        # TODO limit the number of tags in the query or use faster datastuct
        columns = queryset.keys()
        result = defaultdict(list)
        ordering = []
        for row in queryset:
            if row.tag not in ordering: ordering.append(row.tag)
            result[row.tag].append(dict(zip(columns, row)))
        return result, ordering


    def get(self):
        result = db_engine.execute(HOME_SQL)
        slides, ordering = self.queryset_to_dict(result)
        return {
            'slides': slides,
            'ordering': ordering
        }
