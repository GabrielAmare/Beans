from core import *

if __name__ == '__main__':
    Bean.__config__(repository="data")


    @Field(name='username', type='str')
    @Field(name='password', type='str')
    @Field(name='email', type='str', optional=True, regex=r"[a-zA-Z0-9_\-\.]+\@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$")
    @Field(name='avatar', type='Avatar', optional=True)
    @Field(name="tags", type="str", multiple=True, optional=True)
    class User(Bean):
        pass


    @Field(name='filepath', type='str')
    class Avatar(Bean):
        pass


    Bean.init_repository()

    Bean.delete_all()

    Bean.load_all()

    User(username="Jean-Michel", password='Xjk45!O%m', email="jean.michel@les_bg_du_76.com", avatar=Avatar(filepath="avatars/13456.png"))
    User(username="Marco Polo", password='EU7$k63:/mz3', avatar=Avatar(filepath="avatars/47899.png"))
    User(username="TotoLeRigolo", password="pwd", email="toto@lerigolo.com", tags=["tag1", "tag2"])

    Bean.save_all()


    # for bean_cls in Bean._subclasses:
    #     for bean in bean_cls.__get_instances__():
    #         bean.to_json(f"data/{bean_cls.__name__.lower()}/{bean.uid}")

    for bean_cls in Bean._subclasses:
        print()
        print(bean_cls.__name__, ":")
        for bean in bean_cls.__get_instances__():
            data = bean.to_dict(mode=LAZY)
            uid = data.pop('uid')
            print("-->", uid, ":", data)

