from models import *


@Field(name="username", type_="str", optional=False, multiple=False, unique=True)
@Field(name="password", type_="str", optional=False, multiple=False, private=True)
class User(Model):
    pass


Model.setup(
    __dbfp__="database",
    __backupdir__="backups",
    loadall=True,
    __db_errs__=False,
    __db_warns__=True
)

if __name__ == '__main__':
    u1 = User(username="admin", password="admin")

    u1.save()

    print(u1)
