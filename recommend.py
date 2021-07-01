import pandas as pd
from math import pow, sqrt

movies = pd.read_csv(r'movies.csv')  # 注意含中文路径需要在前面加 r 转义
ratings = pd.read_csv(r'ratings.csv')
# 合并两个文件
data = pd.merge(movies,ratings,on = 'movieId')  # 通过两数据框之间的movieId连接

data[['userId','rating','movieId','title']].sort_values('userId').to_csv(r'merged.csv',index=False)
file = open(r'merged.csv','r',encoding='UTF-8')

# 读取每行中除了名字的数据
data = {}  # 存放每位用户评论的电影和评分
for line in file.readlines():  # 注意这里不是readline();是自动将文件内容分析成一个行的列表
    line = line.strip().split(',')
    # 如果字典中没有某位用户，则使用用户ID来创建这位用户
    if not line[0] in data.keys():
        data[line[0]] = {line[3]: line[1]}
    # 否则直接添加以该用户ID为key字典中
    else:
        data[line[0]][line[3]] = line[1]

def Euclidean(user1,user2):
    # 取出两位用户评论过的电影和评分
    user1_data = data[user1]
    user2_data = data[user2]
    distance = 0
    # 找到两位用户都评论过的电影，并计算欧式距离
    for key in user1_data.keys():
        if key in user2_data.keys():
            # 注意，distance越大表示两者越相似
            distance += pow(float(user1_data[key]) - float(user2_data[key]), 2)

    return 1 / (1 + sqrt(distance))  # 这里返回值越大，相似度越大

# 计算两用户之间的Pearson相关系数
def pearson_sim(user1, user2):
    # 取出两位用户评论过的电影和评分
    user1_data = data[user1]
    user2_data = data[user2]
    distance = 0
    common = {}

    # 找到两位用户都评论过的电影
    for key in user1_data.keys():
        if key in user2_data.keys():
            common[key] = 1
    if len(common) == 0:
        return 0  # 如果没有共同评论过的电影，则返回0
    n = len(common)  # 共同电影数目
    # print(n, common)

    # 计算评分和
    sum1 = sum([float(user1_data[movie]) for movie in common])
    sum2 = sum([float(user2_data[movie]) for movie in common])

    # 计算评分平方和
    sum1Sq = sum([pow(float(user1_data[movie]), 2) for movie in common])
    sum2Sq = sum([pow(float(user2_data[movie]), 2) for movie in common])

    # 计算乘积和
    PSum = sum([float(user1_data[it]) * float(user2_data[it]) for it in common])

    # 计算相关系数
    num = PSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0
    r = num / den
    return r



# 找到最相似的k个用户
def top_similar(userID):
    res = []
    for userid in data.keys():
        if not userid == userID:
            sim = Euclidean(userID, userid)  # 相似度计算
            res.append((userid, sim))  # 计算结果放入列表
    res.sort(key=lambda val: val[1], reverse=True)  # 降序排序
    return res[1:11]

def per_top_similar(userID):
    res = []
    for userid in data.keys():
        if not userid == userID:
            sim = pearson_sim(userID,userid)
            res.append((userid, sim))  # 计算结果放入列表
    res.sort(key=lambda val: val[1], reverse=True)  # 降序排序
    return res[1:11]


# 找到最相似的用户看过的电影
def recommend(user):
    # 相似度最高的用户
    top_sim_user = top_similar(user)[0][0]
    # 相似度最高的用户的观影记录
    items = data[top_sim_user]
    recommendations = []
    # 筛选出该用户未观看的电影并添加到列表中
    for item in items.keys():
        if item not in data[user].keys():
            recommendations.append((item, items[item]))
    recommendations.sort(key=lambda val: val[1], reverse=True)  # 按照评分排序
    # 返回评分最高的10部电影
    return recommendations[:20]

def per_recommend(user):
    # 相似度最高的用户
    top_sim_user = per_top_similar(user)[0][0]
    # 相似度最高的用户的观影记录
    items = data[top_sim_user]
    recommendations = []
    # 筛选出该用户未观看的电影并添加到列表中
    for item in items.keys():
        if item not in data[user].keys():
            recommendations.append((item, items[item]))
    recommendations.sort(key=lambda val: val[1], reverse=True)  # 按照评分排序
    # 返回评分最高的10部电影
    return recommendations[:20]


if __name__ == '__main__':

    User = input("请输入用户id：")
    # User = '1'
    print("欧氏距离相似用户：")
    RES = top_similar(User)
    for i in range(len(RES)):
        print(RES[i])

    print("皮尔逊计算相似用户：")
    PRES = per_top_similar(User)
    for k in range(len(PRES)):
        print(PRES[k])


    RECOM = recommend(User)
    print("欧氏推荐电影及评分：")
    for j in range(len(RECOM)):
        print(RECOM[j])

    PRECOM = per_recommend(User)
    print("皮尔逊系数推荐电影：")
    for n in range(len(PRECOM)):
        print(PRECOM[n])
