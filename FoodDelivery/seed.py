"""
Seed script: populate demo data for FoodDelivery.
Run: python seed.py
"""
from database import SessionLocal, engine, Base
import models  # register all models
from models.user import User, UserRole
from models.restaurant import Restaurant
from models.menu import Category, MenuItem
from core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ---- Users ----
def get_or_create_user(phone, name, password, role, address=None):
    u = db.query(User).filter(User.phone == phone).first()
    if not u:
        u = User(
            name=name, phone=phone, email=f"{phone}@demo.com",
            password_hash=hash_password(password),
            role=role, address=address,
        )
        db.add(u)
        db.flush()
    return u

customer1 = get_or_create_user("13800000001", "张小明", "123456", UserRole.customer, "北京市朝阳区建国路88号")
customer2 = get_or_create_user("13800000002", "李小红", "123456", UserRole.customer, "上海市浦东新区张江高科")
merchant1 = get_or_create_user("13900000001", "王老板", "123456", UserRole.merchant)
merchant2 = get_or_create_user("13900000002", "陈老板", "123456", UserRole.merchant)
rider1    = get_or_create_user("13700000001", "赵骑手", "123456", UserRole.rider)
rider2    = get_or_create_user("13700000002", "钱骑手", "123456", UserRole.rider)

db.commit()
print("✅ 用户创建完成")

# ---- Restaurants ----
def get_or_create_restaurant(owner_id, name, **kwargs):
    r = db.query(Restaurant).filter(Restaurant.name == name).first()
    if not r:
        r = Restaurant(owner_id=owner_id, name=name, **kwargs)
        db.add(r)
        db.flush()
    return r

r1 = get_or_create_restaurant(
    merchant1.id, "川味小厨",
    description="正宗四川风味，麻辣鲜香，每日新鲜食材",
    address="北京市朝阳区工体北路4号", cuisine_type="川菜",
    rating=4.8, rating_count=236, delivery_fee=3.0, min_order=20.0,
)
r2 = get_or_create_restaurant(
    merchant1.id, "老北京炸酱面",
    description="传统手工面，地道北京味道，30年老店",
    address="北京市东城区鼓楼大街128号", cuisine_type="北京菜",
    rating=4.6, rating_count=152, delivery_fee=2.0, min_order=15.0,
)
r3 = get_or_create_restaurant(
    merchant2.id, "寿司之家",
    description="新鲜日料，每日空运食材，米其林主厨坐镇",
    address="上海市黄浦区南京东路100号", cuisine_type="日料",
    rating=4.9, rating_count=89, delivery_fee=5.0, min_order=50.0,
)
r4 = get_or_create_restaurant(
    merchant2.id, "汉堡工坊",
    description="现做手工汉堡，澳洲牛肉，酥脆外皮",
    address="上海市静安区南京西路1号", cuisine_type="西式快餐",
    rating=4.5, rating_count=314, delivery_fee=4.0, min_order=30.0,
)

db.commit()
print("✅ 餐厅创建完成")

# ---- Menus ----
menu_data = {
    r1.id: {
        "热菜": [
            ("麻婆豆腐", "嫩豆腐配麻辣肉末，经典川菜", 22.0),
            ("回锅肉", "五花肉爆炒青蒜，香气四溢", 28.0),
            ("鱼香肉丝", "猪里脊配泡椒，酸甜微辣", 24.0),
            ("宫保鸡丁", "嫩鸡丁配花生，鲜辣爽口", 25.0),
        ],
        "主食": [
            ("米饭", "东北大米蒸制", 3.0),
            ("担担面", "芝麻花生香辣浓汤面", 18.0),
        ],
        "汤类": [
            ("番茄蛋花汤", "鲜番茄配嫩蛋花", 12.0),
            ("酸辣汤", "经典川味酸辣汤", 15.0),
        ],
    },
    r2.id: {
        "面条": [
            ("炸酱面", "手工面配老北京炸酱，配时蔬", 22.0),
            ("阳春面", "清汤素面，清淡养胃", 16.0),
            ("麻酱面", "芝麻酱拌面，香浓醇厚", 20.0),
        ],
        "小吃": [
            ("豆汁儿", "老北京传统发酵饮料", 8.0),
            ("焦圈", "油炸焦圈，酥脆可口", 10.0),
            ("卤煮火烧", "猪肠猪肺豆腐火烧，浓汤卤制", 28.0),
        ],
    },
    r3.id: {
        "握寿司": [
            ("三文鱼握寿司", "挪威新鲜三文鱼，配醋饭", 18.0),
            ("金枪鱼握寿司", "蓝鳍金枪鱼大腹，顶级食材", 28.0),
            ("甜虾握寿司", "北海道甜虾，鲜甜爽口", 16.0),
        ],
        "卷物": [
            ("龙虾沙拉卷", "波士顿龙虾配特调沙拉酱", 48.0),
            ("加州卷", "蟹柳牛油果黄瓜卷", 32.0),
        ],
        "套餐": [
            ("10貫握寿司拼盘", "主厨精选10种握寿司", 88.0),
            ("刺身盛合", "三文鱼金枪鱼甜虾刺身", 128.0),
        ],
    },
    r4.id: {
        "汉堡": [
            ("经典芝士堡", "澳洲牛肉饼配车打芝士", 42.0),
            ("BBQ烟熏猪肉堡", "慢烤猪肉配烟熏BBQ酱", 45.0),
            ("蘑菇瑞士芝士堡", "蘑菇配瑞士芝士，素食友好", 38.0),
        ],
        "配餐": [
            ("薯条（大）", "现炸黄金薯条", 18.0),
            ("洋葱圈", "酥脆金黄洋葱圈", 16.0),
            ("可乐", "经典碳酸饮料", 10.0),
        ],
        "套餐": [
            ("汉堡+薯条+饮料", "超值套餐优惠10元", 58.0),
        ],
    },
}

for rest_id, cats in menu_data.items():
    for sort_i, (cat_name, items) in enumerate(cats.items()):
        cat = db.query(Category).filter(
            Category.restaurant_id == rest_id, Category.name == cat_name
        ).first()
        if not cat:
            cat = Category(restaurant_id=rest_id, name=cat_name, sort_order=sort_i)
            db.add(cat)
            db.flush()
        for item_name, item_desc, item_price in items:
            exists = db.query(MenuItem).filter(
                MenuItem.restaurant_id == rest_id, MenuItem.name == item_name
            ).first()
            if not exists:
                db.add(MenuItem(
                    restaurant_id=rest_id, category_id=cat.id,
                    name=item_name, description=item_desc, price=item_price,
                    sales_count=__import__('random').randint(50, 800),
                ))

db.commit()
print("✅ 菜单创建完成")

print("\n🎉 演示数据初始化完成！")
print("\n账号信息（密码均为 123456）：")
print("  顾客：13800000001 / 13800000002")
print("  商家：13900000001 / 13900000002")
print("  骑手：13700000001 / 13700000002")
db.close()
