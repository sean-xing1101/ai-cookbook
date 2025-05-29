from dg_pbi_agents.agents.gatekeeper1 import BusinessClassifier
from dg_pbi_agents.agents.match_ds2 import select_dataset


def main(user_input: str):
    #1·查看置信度,判断用户问题是否属于业务范畴
    if_business, confidence = check_if_business_question(user_input)
    if not if_business or confidence < 0.6:
        return "该问题不是业务数据相关的问题。"
    else:
        print(f'用户提问:{user_input} 与业务相关。其置信度为{confidence}!')
        #2·根据用户提问定位到可能找到答案的dataset
        dataset_id, dataset_name, dataset_description = select_dataset(user_input)
        print(f'根据用户的提问可能在{dataset_name}中找到答案!"\n"{dataset_description}')
        #3·查询根据dataset_id定位到metadata (function call)
        #4·结合user_input + metadata作为提示词，识别问题中的关键实体,定位到解决用户问题需要查询dataset中的哪些table和cloumn,如果有filter条件也要选出来
        #5·结合user_input + 第四步输出的结构化数据(eg:{})为提示词生成相关dax公式
        #6·连接power bi client执行dax,返还结果(function call)
        #7·llm校验结果是否可以输出,如果执行报错或者查询结果比较离谱，llm会判断是dax生成有错还是dataset和metadata选取有误进行replan操作
