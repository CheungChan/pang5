class 家具:

    def __init__(self, 编号):
        self.编号 = 编号

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "家具对象" + str(self.编号)


class 房子:
    def __init__(self):
        # 初始化所有属性
        self.家具们 = []

    def 添加家具(self, 家具):
        self.家具们.append(家具)

    def __str__(self):
        return "房子里有" + str(self.家具们)


if __name__ == '__main__':
    家具1 = 家具(1)
    家具2 = 家具(2)
    房子1 = 房子()
    房子1.添加家具(家具1)
    房子1.添加家具(家具2)
    print(房子1)
