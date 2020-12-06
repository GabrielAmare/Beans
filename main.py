from core import *
from datetime import datetime

if __name__ == '__main__':
    Bean.__config__(repository="repository", debug_mode=True)


    @Field(rpy="!username[str]", length=(4, 30))
    @Field(rpy="!password[str]")
    @Field(rpy="?age[int]", range=POSITIVE)
    @Field(rpy="!email[str]", regex=r"^\S+@\S+$")
    @Field(rpy="?avatar[Avatar]")
    class User(Bean):
        pass


    @Field(rpy="!filepath[str]")
    class Avatar(Bean):
        pass


    @Field(rpy="*users[User]")
    @Field(rpy="!creation[datetime]", default=datetime.now)
    @Field(rpy="!last_update[datetime]", default=datetime.now)
    class Group(Bean):
        @property
        def duration(self):
            return self.last_update - self.creation


    def show_db():
        for bean_cls in Bean.__get_subclasses__():
            print(f"/{Bean.__repository__.root}/{bean_cls.__repo_name__}/")
            for instance in bean_cls.__get_instances__():
                print("   ", instance.to_dict(LAZY))
            print()


    def build():
        Bean.__setup__(create_db=True, reset_db=True, load_db=False)

        u1 = User(username="admin", password="admin", email="admin@contact.com",
                  avatar=Avatar(filepath="avatars/admin.png"))
        u2 = User(username="gabj", password="gabj", age=25, email="gabriel.amare.31@gmail.com")
        u3 = User(username="jpepin", password="veryverymuch", age=25, email="julien.pepin.31@gmail.com")

        g1 = Group(uid=1, users=[u1, u2, u3], last_update=datetime.now())


    def update():
        Bean.__setup__(create_db=True, reset_db=False, load_db=True)
        g1 = Group.get_by_id(1)
        g1.last_update = datetime.now()

        u1 = User.get_by('username', 'admin')
        u1.avatar.filepath = "avatars/new_admin.png"


    update()

    show_db()

    Bean.__save_all__()

    # @Field(name='username', type='str')
    # @Field(name='password', type='str')
    # @Field(name='email', type='str', optional=True, regex=r"[a-zA-Z0-9_\-\.]+\@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$")
    # @Field(name='avatar', type='Avatar', optional=True)
    # @Field(name="tags", type="str", multiple=True, optional=True)
    # @Field(name="messages", type="Message", multiple=True, optional=True)
    # @Field(name="age", type="float", range=True, min_value=0, max_value=float('inf'))
    # class User(Bean):
    #     pass
    #
    #
    # @Field(name="content", type="str")
    # @Field(name="posted_at", type="datetime", optional=False, default_value_function=datetime.now)
    # class Message(Bean):
    #     pass
    #
    #
    # @Field(name='filepath', type='str')
    # class Avatar(Bean):
    #     pass
    #
    #
    # Bean.init_repository()
    #
    # Bean.__delete_all__()
    #
    # Bean.__load_all__()
    #
    # User(
    #     username="Jean-Michel", password='Xjk45!O%m', email="jean.michel@les_bg_du_76.com",
    #     avatar=Avatar(filepath="avatars/13456.png"), messages=[
    #         Message(content="Coucou"),
    #         Message(content="Salut !")
    #     ]
    # )
    # User(username="Marco Polo", password='EU7$k63:/mz3', avatar=Avatar(filepath="avatars/47899.png"))
    # User(username="TotoLeRigolo", password="pwd", email="toto@lerigolo.com", tags=["tag1", "tag2"])
    #
    # user = User.get_by_config(username="Marco Polo")
    # assert user.username == "Marco Polo"
    #
    # user.subscribe("username", lambda old, new: print(f"Username change from '{old}' to '{new}'"))
    #
    # user.username = "Marco 'Bidule' Polo"
    #
    # user = User.get_by_id(2)
    #
    # user.subscribe("tags:append", lambda tag: print(f"Added the tag : '{tag}' to <{user.username}>"))
    #
    # user.tags.append("New tag")
    #
    # print(user.to_dict())
    #
    # user.tags.remove("New tag")
    #
    # print(user.to_dict())
    #
    # Bean.__save_all__()
    #
    # print(type(Message.load(1).posted_at))
    #
    # # for bean_cls in Bean._subclasses:
    # #     for bean in bean_cls.__get_instances__():
    # #         bean.to_json(f"data/{bean_cls.__name__.lower()}/{bean.uid}")
    #
    # for bean_cls in Bean._subclasses:
    #     print()
    #     print(bean_cls.__name__, ":")
    #     for bean in bean_cls.__get_instances__():
    #         data = bean.to_dict(mode=LAZY)
    #         uid = data.pop('uid')
    #         print("-->", uid, ":", data)
