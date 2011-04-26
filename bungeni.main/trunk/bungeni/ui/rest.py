import simplejson

from bungeni.rest.rest import REST

from bungeni.models import domain

from bungeni.models.schema import users
from bungeni.models.schema import groups
from bungeni.models.schema import user_group_memberships

from bungeni.alchemist import Session
import sqlalchemy as rdb
from bungeni.alchemist.security import schema as security_schema


def safeencode(v):
    if isinstance(v, unicode):
        return v.encode("utf-8")
    return v


class Users(REST):
    """ RESTful view for User object."""
    
    def GET(self):
        if "auth" in self.request.keys():
            cols = [users.c.user_id ]
            if self.request["auth"] != "None":
                cols.extend([users.c.password, users.c.salt])
            session = Session()
            connection = session.connection(domain.Group)
            res = connection.execute(rdb.select(cols,
                                rdb.and_(users.c.login == self.request["login"],
                                         users.c.active_p == "A"
                                )))
            uid_tuple = res.fetchone()
            if not uid_tuple:
                return None
            if self.request["auth"] != "None":
                return self.json_response(str(uid_tuple))
            return self.json_response(uid_tuple[0])            

        elif "login" in self.request.keys():
            session = Session()
            user = session.query(domain.User).filter(
                rdb.and_(
                    domain.User.login == self.request["login"],
                    domain.User.active_p == "A")
                ).one()
            return self.json_response(user)       
        elif "user_name" in self.request.keys():
            session = Session()
            user_values = session.query(domain.User).filter(
                domain.User.login == self.request["user_name"]).all()
            data = {}
            if len(user_values) == 1:
                b_user = user_values[0]
                data =  {
                    "fullname" : u"%s %s" %(b_user.first_name, b_user.last_name),
                    "email" : b_user.email or u"",
                    "description" : b_user.description or u"",
                    "notification": b_user.receive_notification or False,
                    }      
            return self.json_response(data)            
        else:
                user_values = users.select([users.c.login ],
                                users.c.active_p == "A").execute()
                if "user_manager_id" in self.request.keys():
                    plugin_id = self.request["user_manager_id"]
                    data = [dict(id=safeencode(r["login"]),
                                  login=safeencode(r["login"]), 
                                  pluginid=plugin_id) for r in user_values]
                else:
                    data = tuple([safeencode(r["login"]) for r in user_values])
                return self.json_response(data)

    def POST(self):
        insert = users.insert()
        insert.values(login = self.request["login"],
                       salt = self.request["salt"],
                       password = self.request["password"], type="user",
                       first_name=self.request["first_name"],
                       last_name=self.request["last_name"],
                       email=self.request["email"],
                       ).execute()        
        
    def PUT(self):
        users.update().where(users.c.user_id == self.request["uid"]).values(
            salt = self.request["salt"],
            password = self.request["password"]
            ).execute()

    def DELETE(self):
        # update user to show as inactive
        uid = self.request["uid"]
        users.update().where(users.c.user_id == uid).values(
                                                     active_p = 'I').execute()        

class enumerateUsers(REST):
    """ RESTful view for Users listing."""        

    def GET(self):
        id = self.request["id"]
        login = self.request["login"]
        exact_match = self.request["exact_match"]
        sort_by = self.request["sort_by"]
        max_results = self.request["max_results"]
        kw = eval(self.request["kw"])
        plugin_id = self.request["user_manager_id"]
        
        # try to normalize the list of ids/logins into single sequence
        if isinstance(login, (list, tuple)):
            if isinstance(id, (list, tuple)):
                ids = []
                ids.extend(id)
                ids.extend(login)
            else:
                ids = list(login)
                ids.append(id)
            id = ids
        elif isinstance(id,(list,tuple)) and login != "None":
            id = list(id)
            id.append(login)
        elif id !="None" and login != "None":
            id = [id, login]
            
        if id =="None" and exact_match=="True":
            return []
        elif id == "None":
            clause = None
            for key, value in kw.items():
                column = getattr(users.c, key, None)
                if column:
                    clause = rdb.and_(clause, column.contains(value))
                else:
                    like_val ='%' + str(value) +'%'
                    clause = rdb.and_(clause, 
                        rdb.or_(users.c.login.like(like_val),
                                users.c.first_name.like(like_val),
                                users.c.last_name.like(like_val)
                            )
                        )
        elif isinstance(id, (list, tuple)) and exact_match == "True":
            statements = []
            for i in id:
                statements.append(users.c.login == i)
            clause = rdb.or_(*statements)
        elif isinstance( id, (list, tuple)) and exact_match != "True":
            like_val ="%" + str(id) +"%"
            clause = rdb.or_(*(map(users.c.login.like, like_val)))
        elif exact_match!="True":
            like_val ="%" + str(id) +"%"
            clause = rdb.or_(users.c.login.like(like_val),
                             users.c.first_name.like(like_val),
                             users.c.last_name.like(like_val)
                            )
        else:
            clause = users.c.login == id
        session = Session()
        
        query = session.query(domain.User).filter(
                        rdb.and_(clause,
                            users.c.active_p == "A",
                            users.c.login != None
                                ))
        if sort_by != "None":
            assert sort_by in ("login", "last_name")
            query = query.order_by(getattr(users.c, sort_by))
        else:
            query = query.order_by(users.c.last_name, users.c.first_name)
                    
        if max_results != "None" and isinstance(max_results, int):
            query =query.limit(max_results)
            
        uservalues = [dict(id=safeencode(r.login), 
                title= u"%s %s" %(r.first_name, r.last_name),
                fullname= u"%s %s" %(r.first_name, r.last_name),
                email = (r.email),
                login=safeencode(r.login), pluginid=plugin_id) 
                for r in query.all()]
        return self.json_response(uservalues)


class Groups(REST):
    """ RESTful view for a Users groups."""
    
    def GET(self):
        session = Session()
        if "name" in self.request.keys():
            group_values = session.query(domain.Group).filter(
                rdb.and_(domain.Group.status == "active", 
                         domain.Group.group_principal_id == self.request["name"])
                ).all()
            data ={}
            if len(group_values) == 1:
                group = group_values[0]
                data =  {
                    "group_principal_id": group.group_principal_id,
                    "groupid" :  group.group_principal_id,
                    "title" : group.short_name or u"",
                    "description" : group.description or u"",
                    }
            return self.json_response(data) 
        elif "user_name" in self.request.keys():
            group_values = session.query(domain.Group).filter(
                domain.Group.group_principal_id == self.request["user_name"]).all()
            data ={}
            if len(group_values) == 1:
                group = group_values[0]
                data =  {
                    "groupid" :  group.group_principal_id,
                    "title" : group.short_name or u"",
                    "description" : group.description or u"",
                    }
            return self.json_response(data)                
        else:
            group_values = [
                (r.group_principal_id) for
                r in session.query(domain.Group).filter
                (domain.Group.status == "active").all()
            ]
            return self.json_response(group_values)


class enumerateGroups(REST):
    """ RESTful view for Groups listing."""            

    def GET(self):
        session = Session()
        gid = self.request["gid"]
        exact_match = self.request["exact_match"]
        sort_by = self.request["sort_by"]
        max_results = self.request["max_results"]
        plugin_id = self.request["group_manager_id"]
        if gid == "None":
            clause = None
        elif isinstance( gid, (list, tuple)) and exact_match:
            statements = []
            for i in gid:
                statements.append(domain.Group.group_principal_id == i)
            clause = rdb.or_(*statements)
        elif isinstance( gid,(list, tuple)) and not exact_match:
            clause = rdb.or_(*(map(domain.Group.group_principal_id.contains, gid)))
        elif not exact_match:
            clause = domain.Group.group_principal_id.contains(gid)
        else:
            clause = domain.Group.group_principal_id == gid
        query = session.query(domain.Group).filter(
                        rdb.and_(clause,
                            domain.Group.status == "active")
                        )
        if clause:
            query = query.filter(clause)
        if sort_by != "None":
            assert sort_by in ("group_id", "short_name")
            query = query.order_by(getattr(groups.c, sort_by))

        if exact_match !="False":
            max_results = 1
            
        if max_results !="None" and isinstance(max_results, int):
            query = query.limit(max_results)
        grouplist = [dict(id=r.group_principal_id,
                                         title=r.short_name,plugin=plugin_id)
                                   for r in query.all()]
        return self.json_response(grouplist)


class Roles(REST):
    """
    RESTful view for listing, adding, editing and deletion
    of users's Roles.
    """    

    def GET(self):
        session = Session()
        connection = session.connection(domain.Group)
        principal_id = self.request["principal_id"]
        mappings = connection.execute(rdb.select(
            [security_schema.principal_role_map.c.role_id],
            rdb.and_(
                rdb.or_(
                    security_schema.principal_role_map.c.object_type==None,
                    security_schema.principal_role_map.c.object_type==
                    "parliament"
                    ),
                security_schema.principal_role_map.c.principal_id==principal_id,
                security_schema.principal_role_map.c.setting==True)))         

        role_names = []
        for (role_id,) in mappings:
            role_names.append(role_id)

        return self.json_response(role_names)

    def POST(self):
        session = Session()
        setting = simplejson.loads(self.request["setting"])
        roles = simplejson.loads(self.request["roles"])
        principal_id = simplejson.loads(self.request["principal_id"])
        connection = session.connection(domain.Group)

        # insert new global mappings
        for role_id in tuple(roles):
            connection.execute(
                security_schema.principal_role_map.insert().values(
                    principal_id=principal_id,
                    role_id=role_id,
                    setting=setting,
                    object_type=None,
                    object_id=None))
            
            # remove from roles so other plugins won't attempt to
            # assign as well
            roles.remove(role_id)            

    def PUT(self):
        session = Session()
        principal_id = simplejson.loads(self.request["principal_id"])
        connection = session.connection(domain.Group)
        # update existing
        connection.execute(
            security_schema.principal_role_map.update().where(
                rdb.and_(
                    security_schema.principal_role_map.c.principal_id==principal_id,
                    security_schema.principal_role_map.c.object_type==None,
                    security_schema.principal_role_map.c.object_id==None)).values(
                setting=False))

    def DELETE(self):
        simplejson.loads
        session = Session
        principal_id = simplejson.loads(self.request["principal_id"])
        connection = session.connection(domain.Group)
        connection.execute(security_schema.principal_role_map.delete().where(
            rdb.and_(
                security_schema.principal_role_map.c.principal_id == principal_id,
                security_schema.principal_role_map.c.object_id == None,
                security_schema.principal_role_map.c.object_type == None)))        
        

class enumerateRoles(REST):
    """ RESTful view for Roles listing."""
    
    def GET(self):
        session = Session()
        connection = session.connection(domain.Group)
        plugin_id = self.request["plugin_id"]
        mappings = connection.execute(rdb.select(
            [security_schema.principal_role_map.c.role_id]))

        role_ids = []
        for (role_id,) in mappings:
            role_ids.append(role_id)
       
        role_ids = []
        for (role_id,) in mappings:
            role_ids.append(role_id)
        
        return self.json_response([{
            "id": role_id,
            "pluginid": plugin_id,
            } for role_id in role_ids])        


        return self.json_response(mappings)

        
class Memberships(REST):
    """ RESTful view for Users memberships."""    

    def GET(self):
        session = Session()
        return self.json_response([r.group_principal_id
                for r in session.query(domain.Group).filter(
                    rdb.and_(
                        users.c.login == self.request["principal_id"],
                        user_group_memberships.c.user_id == users.c.user_id,
                        groups.c.group_id == user_group_memberships.c.group_id,
                        groups.c.status == "active",
                        user_group_memberships.c.active_p == True)).all()])


class GroupMembers(REST):
    """ RESTful view for Group Membership listing."""
    def GET(self):
        session = Session()
        ugm = user_group_memberships
        user_values = session.query(domain.User).filter(
            rdb.and_(users.c.user_id == ugm.c.user_id,
                     groups.c.group_id == ugm.c.group_id,
                     domain.Group.group_principal_id == self.request["group_id"],
                     ugm.c.active_p == True)).all()
        return self.json_response([r.login for r in user_values])
    

        
        values=[r.group_principal_id
                for r in session.query(domain.Group).filter(
                    rdb.and_(
                        users.c.login == self.request["principal_id"],
                        user_group_memberships.c.user_id == users.c.user_id,
                        groups.c.group_id == user_group_memberships.c.group_id,
                        groups.c.status == "active",
                        user_group_memberships.c.active_p == True)).all() ]
        return self.json_response(values)
