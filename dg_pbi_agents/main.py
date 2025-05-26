from agents.gatekeeper1 import check_if_business_question
from agents.match_ds2 import select_dataset


def main(user_input: str):
    #查看置信度,判断用户问题是否属于业务范畴
    if_business, confidence = check_if_business_question(user_input)
    if not if_business or confidence < 0.6:
        return "该问题不是业务数据相关的问题。"
    else:
        print(f'用户提问:{user_input} 与业务相关。其置信度为{confidence}!')
        #根据用户提问定位到可能找到答案的dataset
        dataset_id, dataset_name, dataset_description = select_dataset(user_input)
        print(f'根据用户的提问可能在{dataset_name}中找到答案!"\n"{dataset_description}')
        #







if __name__ == '__main__':
    user_input = '我想查看baymax14的信息'
    main(user_input)